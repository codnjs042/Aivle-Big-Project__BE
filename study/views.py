from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Avg
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import *
from user.models import User

import librosa
import numpy as np
import os
from pydub import AudioSegment
from django.core.files import File
from jamo import h2j, j2hcj

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

# Create your views here.
class SentencesListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[
        OpenApiParameter(name="sentence", description="문장", required=False,
                         type=str)])
    def get(self, request):
        if request.GET.get('sentence'):
            sentence = get_list_or_404(Sentence, ko_text__contains=request.GET.get('sentence'))
            print(sentence[0].ko_text)
            return Response({"id": sentence[0].id}, status=status.HTTP_200_OK)

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

# 오디오에서 MFCC 특성 추출하는 함수
def process_audio(audio_path, n_mfcc=13):
    y, sr = librosa.load(audio_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfccs, axis=1).reshape(1, -1)

def map_phone_to_number(phone):
    phoneme_mapping = {
        'ㄱ': 1, 'ㄲ': 2, 'ㄴ': 3, 'ㄷ': 4, 'ㄸ': 5, 'ㄹ': 6, 'ㅁ': 7, 'ㅂ': 8, 'ㅃ': 9, 'ㅅ': 10,
        'ㅆ': 11, 'ㅇ': 12, 'ㅈ': 13, 'ㅉ': 14, 'ㅊ': 15, 'ㅋ': 16, 'ㅌ': 17, 'ㅍ': 18, 'ㅎ': 19,
        'ㅏ': 20, 'ㅐ': 21, 'ㅑ': 22, 'ㅒ': 23, 'ㅓ': 24, 'ㅔ': 25, 'ㅕ': 26, 'ㅖ': 27, 'ㅗ': 28,
        'ㅘ': 29, 'ㅙ': 30, 'ㅚ': 31, 'ㅛ': 32, 'ㅜ': 33, 'ㅝ': 34, 'ㅞ': 35, 'ㅟ': 36, 'ㅠ': 37,
        'ㅡ': 38, 'ㅢ': 39, 'ㅣ': 40, 'ㄳ': 41, 'ㄵ': 42, 'ㄶ': 43, 'ㄺ': 44, 'ㄻ': 45, 'ㄼ': 46,
        'ㄽ': 47, 'ㄾ': 48, 'ㄿ': 49, 'ㅀ': 50, 'ㅄ': 51
    }
    return phoneme_mapping.get(phone, 0)

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
        
        audio_data = request.data['audio_path']
        file_extension = str(audio_data.name).split('.')[-1].lower()
        
        if file_extension == 'webm':  # .webm > .wav 변환
            audio_segment = AudioSegment.from_file(audio_data, 'webm')
            wav_path = audio_data.name.replace('.webm', '.wav')
            
            audio_segment.export(wav_path, format='wav')
            audio_file = AudioFile.objects.create(email=request.user, sentence=sentence)
            with open(wav_path, 'rb') as f:
                audio_file.audio_path.save(os.path.basename(wav_path), File(f))
        elif file_extension == 'wav':  # .wav 파일 바로 저장
            AudioFile.objects.create(email=request.user, sentence=sentence, audio_path=request.data['audio_path'])
        else :  # 파일이 없거나 이상한 형식이거나
            return Response({'message': 'No audio_path provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_paths = get_list_or_404(AudioFile, sentence=pk, email=request.user)
        file_path = file_paths[-1].audio_path

        #----model1---------
        # 음성 데이터 전처리 및 모델 예측(model1)
        audio_data = process_audio_file(file_path)
        mel_spectrogram = extract_mel_spectrogram(audio_data)
        preprocessed_data = np.expand_dims(mel_spectrogram, axis=0)
        # 모델에 데이터 입력 및 예측
        model = tf.keras.models.load_model("my_model.h5")
        predictions = model.predict(preprocessed_data)

        #----model2---------
        # 모델 훈련 오디오 입력 모양
        n_mfcc = 13
        audio_data2 = process_audio("media/"+str(file_path), n_mfcc=n_mfcc)
        text_data = "안녕하세요"
        phoneme_mapping = {
            'ㄱ': 1, 'ㄲ': 2, 'ㄴ': 3, 'ㄷ': 4, 'ㄸ': 5, 'ㄹ': 6, 'ㅁ': 7, 'ㅂ': 8, 'ㅃ': 9, 'ㅅ': 10,
            'ㅆ': 11, 'ㅇ': 12, 'ㅈ': 13, 'ㅉ': 14, 'ㅊ': 15, 'ㅋ': 16, 'ㅌ': 17, 'ㅍ': 18, 'ㅎ': 19,
            'ㅏ': 20, 'ㅐ': 21, 'ㅑ': 22, 'ㅒ': 23, 'ㅓ': 24, 'ㅔ': 25, 'ㅕ': 26, 'ㅖ': 27, 'ㅗ': 28,
            'ㅘ': 29, 'ㅙ': 30, 'ㅚ': 31, 'ㅛ': 32, 'ㅜ': 33, 'ㅝ': 34, 'ㅞ': 35, 'ㅟ': 36, 'ㅠ': 37,
            'ㅡ': 38, 'ㅢ': 39, 'ㅣ': 40, 'ㄳ': 41, 'ㄵ': 42, 'ㄶ': 43, 'ㄺ': 44, 'ㄻ': 45, 'ㄼ': 46,
            'ㄽ': 47, 'ㄾ': 48, 'ㄿ': 49, 'ㅀ': 50, 'ㅄ': 51
            }
        # 전화 데이터를 모델 입력 형식으로 변환
        phone_data = j2hcj(h2j(text_data))
        mapped_phone_data = [map_phone_to_number(phone) for phone in phone_data]
        
        # Text 데이터 전처리
        max_text_length = len(text_data.split())  # 단어 수를 계산하여 최대 길이 설정
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts([text_data])
        encoded_text = tokenizer.texts_to_sequences([text_data])
        padded_text = pad_sequences(encoded_text, maxlen=max_text_length, padding='post')

        # 모델에 입력 데이터 전달
        model_input = [
            np.array([padded_text[0]]),          # 형태: (1, max_text_length)
            np.array([audio_data2[0]]),            # 형태: (1, n_mfcc)
            np.array([mapped_phone_data[0]])      # 형태: (1, 1)
            ]
        model2 = load_model("my_model_phone_error1.h5")
        predictions2 = model2.predict(model_input)

        # 예측 결과 중 확률이 일정 임계값 이상인 부분을 오류로 간주
        threshold = 0.5
        errors = predictions2 > threshold

        # 각 음소에 대한 예측 확률
        phone_probabilities = predictions2

        # 각 음소에서 가장 높은 확률을 가진 인덱스 찾기
        max_prob_indices = np.argmax(phone_probabilities, axis=-1)

        # 예측된 음소 출력
        predicted_phones = [list(phoneme_mapping.keys())[i] for i in max_prob_indices.flatten()]

        # 오류 부분 및 해당 음소 출력
        error_indices = np.where(errors)
        error_phones = [predicted_phones[i] for i in error_indices[1]]

        for i, index in enumerate(error_indices[1]):
            predicted_word = text_data.split()[index]
            print(f"Error {i + 1}:")
            print(f" - Error Position (Word): {predicted_word}")
            print(type(predicted_word))
            print(f" - Predicted Phones: {error_phones[i]}")
            print(type(error_phones))
            print(f" - Text Data: {text_data}")
            print()

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
        serializer = ResultScoreSerializer(result_instance)
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

        data = {  # 발음 숙련도, 유창성, 이해가능도 각 평균(100% 단위)  # + 음절별 점수 
            "pronun_prof_eval_avg": round(pronun_prof_eval_avg*20, 1),
            "fluency_eval_avg": round(fluency_eval_avg*20, 1),
            "comprehend_eval_avg": round(comprehend_eval_avg*20, 1),
        }
        return Response(data)