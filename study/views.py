from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Avg

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import *
from user.models import User

import tensorflow as tf
import librosa
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Create your views here.
class SentencesListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        sentences = Sentence.objects.all()
        page = paginator.paginate_queryset(sentences, request)
        if page is not None:
            serializer = SentenceSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = SentenceSerializer(sentences, many=True, context={'request': request})
        return Response(serializer.data)
    
    
# 음성 데이터 전처리 함수 정의
def process_audio_file(file_path, target_sr=20000):
    audio, sr = librosa.load(file_path, sr=target_sr)
    target_length = int(target_sr * 10)
    if len(audio) < target_length:
        padding = target_length - len(audio)
        audio = np.pad(audio, (0, padding), mode='constant')
    else:
        audio = audio[:target_length]
    scaler = MinMaxScaler()
    audio = scaler.fit_transform(audio.reshape(-1, 1)).flatten()
    return audio
def extract_mel_spectrogram(audio, target_sr=20000):
    mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=target_sr, n_mels=128)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
    return mel_spectrogram

class SentenceView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AudioFileSerializer
    parser_classes = (MultiPartParser,)
    
    def get(self, request, pk):
        sentence = get_object_or_404(Sentence, pk=pk)
        serializer = SentenceSerializer(sentence)
        try:
            bookmark = Bookmark.objects.get(sentence=sentence)
            is_bookmarked = bookmark.is_bookmarked #북마크가 있으면 북마크의 값을 출력(T/F)
        except Bookmark.DoesNotExist: # Bookmark 객체가 없을 경우에 대한 처리
            is_bookmarked = False  # 북마크를 한번도 표시하지 않은 경우 False 입력
        send = {
                'data': serializer.data,
                'is_bookmarked': is_bookmarked
            }
        return Response(send)
    
    def patch(self, request, pk, *args, **kwargs):
        try:
            sentence = get_object_or_404(Sentence, pk=pk)
            serializer = SentenceSerializer(sentence)
            user = request.user
            bookmark, created = Bookmark.objects.get_or_create(sentence=sentence, email=user)
            bookmark.is_bookmarked = not bookmark.is_bookmarked
            bookmark.save()
            
            bookmark = get_object_or_404(Bookmark, sentence=sentence).is_bookmarked
            send = {
                'data': serializer.data,
                'is_bookmarked': bookmark
            }
            print("success")
            return Response(send)
        except Exception as e:
            print("error")
            return Response({'success':False, 'error':str(e)})
    
    def post(self, request, pk, *args, **kwargs):
        sentence = get_object_or_404(Sentence, pk=pk)
        print(sentence)
        print(request.data)
        AudioFile.objects.create(email=request.user, sentence=sentence, audio_path=request.data['audio_path'])
        file_paths = get_list_or_404(AudioFile, sentence=pk, email=request.user)
        file_path = file_paths[-1].audio_path
        
        # 음성 데이터 전처리 및 모델 예측
        audio_data = process_audio_file(file_path)
        mel_spectrogram = extract_mel_spectrogram(audio_data)
        preprocessed_data = np.expand_dims(mel_spectrogram, axis=0)
        
        # 모델에 데이터 입력 및 예측
        model = tf.keras.models.load_model("my_model.h5")
        predictions = model.predict(preprocessed_data)
        
        # 적절한 Sentence 모델 인스턴스를 가져오는 코드 (예시)
        sentence_instance = Sentence.objects.get(pk=pk)
        
        # Result 모델에 저장
        result_instance = Result.objects.create( #반환 필요 시 변수 바로 사용 가능
            email=request.user,  # 유저 이메일 또는 사용자 인증에 따라 맞게 변경
            sentence=sentence_instance,  # 적절한 Sentence 모델 인스턴스
            PronunProfEval=round(max(0, float(predictions[0][0][0])), 2),
            FluencyEval=round(max(0, float(predictions[1][0][0])), 2),
            ComprehendEval=round(max(0, float(predictions[2][0][0])), 2)
        )
        serializer = ResultSerializer(result_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        email = request.user.id
        text = get_object_or_404(Sentence, pk=pk).ko_text
        result = Result.objects.filter(sentence=pk, email=email)
        serializer = ResultSerializer(result, many=True)
        send = {
            "ko_text":text,
            "data": serializer.data
        }
        return Response(send)


class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        email = request.user.email
        #email = 'admin@naver.com' #test
        user = User.objects.get(email=email)
        user_id = user.id
        bookmarked_sentence_ids = Bookmark.objects.filter(email=user_id, is_bookmarked=True).values_list('sentence', flat=True)

        # 북마크된 문장들만 가져오기
        sentences = Sentence.objects.filter(id__in=bookmarked_sentence_ids)

        page = paginator.paginate_queryset(sentences, request)
        if page is not None:
            serializer = SentenceSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = SentenceSerializer(sentences, many=True, context={'request': request})
        return Response(serializer.data)
    
    
class AIReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        auth = request.user.id
        data = Result.objects.filter(email=auth)
        pronun_prof_eval_avg = data.aggregate(Avg('PronunProfEval'))['PronunProfEval__avg']
        fluency_eval_avg = data.aggregate(Avg('FluencyEval'))['FluencyEval__avg']
        comprehend_eval_avg = data.aggregate(Avg('ComprehendEval'))['ComprehendEval__avg']
        
        if pronun_prof_eval_avg is None or fluency_eval_avg is None or comprehend_eval_avg is None:
            return Response({'message': 'Ai Report score not found'},
                            status=status.HTTP_404_NOT_FOUND)
        # 음절별 점수와 전체 평균 점수
        # user_syllable_reports = SyllableReport.objects.filter(user=user_id)
        # syllable_averages = SyllableReport.objects.values('syllable').annotate(avg_score=Avg('score'))
        
        # syllable_scores = []
        # for report in user_syllable_reports:
        #     average_score = None
        #     for item in syllable_averages:
        #         if item['syllable'] == report.syllable:
        #             average_score = item['avg_score']  # 같은 음절의 전체 사용자 평균 점수
        #             break
            
        #     syllable_data = {
        #         "syllable": report.syllable,  # 현재 음절
        #         "score": report.score,  # 현재 사용자의 점수
        #         "avg": round(average_score)  # 전체 사용자들의 평균 점수
        #     }
        #     syllable_scores.append(syllable_data)
        
        data = {  # 발음 숙련도, 유창성, 이해가능도 각 평균(100% 단위)  # + 음절별 점수 
            "pronun_prof_eval_avg": round(pronun_prof_eval_avg*20, 1),
            "fluency_eval_avg": round(fluency_eval_avg*20, 1),
            "comprehend_eval_avg": round(comprehend_eval_avg*20, 1),
            # "syllable_scores": syllable_scores,
        }
        return Response(data)