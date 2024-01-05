from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import *
from user.models import User

import urllib3
import json
import base64

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
    
    def post(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        email = request.user.email
        #email = 'admin@naver.com' #test
        user = User.objects.get(email=email)
        user_id = user.id
        bookmarked_sentence_ids = Bookmark.objects.filter(email=user_id, is_bookmarked=True).values_list('ko_text', flat=True)

        # 북마크된 문장들만 가져오기
        sentences = Sentence.objects.filter(id__in=bookmarked_sentence_ids)

        page = paginator.paginate_queryset(sentences, request)
        if page is not None:
            serializer = SentenceSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = SentenceSerializer(sentences, many=True, context={'request': request})
        return Response(serializer.data)
    

class SentenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        sentence = get_object_or_404(Sentence, pk=pk)
        serializer = SentenceSerializer(sentence)
        try:
            bookmark = Bookmark.objects.get(ko_text=sentence)
            is_bookmarked = bookmark.is_bookmarked #북마크가 있으면 북마크의 값을 출력(T/F)
        except Bookmark.DoesNotExist: # Bookmark 객체가 없을 경우에 대한 처리
            is_bookmarked = False  # 북마크를 한번도 표시하지 않은 경우 False 입력
        send = {
                'data': serializer.data,
                'is_bookmarked': is_bookmarked
            }
        return Response(send)
    
    def post(self, request, pk):
        if request.FILES['audio_file']: #POST에 오디오파일이 존재
            audio_file = request.FILES['audio_file']
            openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/PronunciationKor" # 한국어
            accessKey = "35c70df0-da4e-43e8-b927-473b1c4c43a4"
            languageCode = "korean"
            script = "PRONUNCIATION_SCRIPT"

            audioContents = base64.b64encode(audio_file.read()).decode("utf8")

            requestJson = {
                "argument": {
                    "language_code": languageCode,
                    "script": script,
                    "audio": audioContents
                    }
            }
            http = urllib3.PoolManager()
            response = http.request(
                "POST",
                openApiURL,
                headers={"Content-Type": "application/json; charset=UTF-8","Authorization": accessKey},
                body=json.dumps(requestJson)
            )
            print("[responseCode] " + str(response.status))
            print("[responBody]")
            print(str(response.data,"utf-8"))
            response_data = json.loads(response.data.decode("utf-8"))

            if "return_object" in response_data and "score" in response_data["return_object"]:
                score_str = response_data["return_object"]["score"]
                try:
                    score = float(score_str) if '.' in score_str else int(score_str)
                except ValueError:
                    print("평가 점수를 부동 소수점 숫자로 변환할 수 없습니다.")
                    score = 0

                PronunProfEval = score.get("pronunciation", 0)  # 발음 평가 점수
                FluencyEval = score.get("fluency", 0)  # 유창성 평가 점수
                ComprehendEval = score.get("comprehension", 0)  # 이해도 평가 점수

                # 적절한 Sentence 모델 인스턴스를 가져오는 코드 (예시)
                sentence_instance = Sentence.objects.get(pk=pk)

                # Result 모델에 저장
                result_instance = Result.objects.create(
                    email=request.user.email,  # 유저 이메일 또는 사용자 인증에 따라 맞게 변경
                    ko_text=sentence_instance,  # 적절한 Sentence 모델 인스턴스
                    PronunProfEval=PronunProfEval,
                    FluencyEval=FluencyEval,
                    ComprehendEval=ComprehendEval
                )
                print("Result 객체가 성공적으로 생성되었습니다.")
                return Response("Result 객체가 성공적으로 생성되었습니다.", status=status.HTTP_201_CREATED)
            else:
                print("JSON 응답에서 평가 점수를 찾을 수 없습니다.")
                return Response("JSON 응답에서 평가 점수를 찾을 수 없습니다.", status=status.HTTP_400_BAD_REQUEST)
        else: #즐겨찾기 체크
            try:
                sentence = get_object_or_404(Sentence, pk=pk)
                bookmark, created = Bookmark.objects.get_or_create(ko_text=sentence)
                bookmark.is_bookmarked = not bookmark.is_bookmarked
                bookmark.save()

                serializer = SentenceSerializer(sentence)
                bookmark = get_object_or_404(Bookmark, ko_text=sentence).is_bookmarked
                send = {
                    'data': serializer.data,
                    'is_bookmarked': bookmark
                }
                print("success")
                return Response(send)
            except Exception as e:
                print("error")
                return Response({'success':False, 'error':str(e)})
        

class ResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        email = request.user.email
        text = get_object_or_404(Sentence, pk=pk).ko_text
        result = Result.objects.filter(ko_text=pk, email=email)
        serializer = ResultSerializer(result, many=True)
        send = {
            "ko_text":text,
            "data": serializer.data
        }
        return Response(send)


class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        email = request.user.id
        try:
            bookmark = Bookmark.objects.filter(email=email, is_bookmarked=True)
            
        except Bookmark.DoesNotExist:
            return Response({'message': 'Bookmark is not found'},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookmarkSerializer(bookmark, many=True)
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
        
        data = {  # 발음 숙련도, 유창성, 이해가능도 각 평균 + 음절별 점수 
            "pronun_prof_eval_avg": round(pronun_prof_eval_avg*20, 1),
            "fluency_eval_avg": round(fluency_eval_avg*20, 1),
            "comprehend_eval_avg": round(comprehend_eval_avg*20, 1),
            # "syllable_scores": syllable_scores,
        }
        return Response(data)