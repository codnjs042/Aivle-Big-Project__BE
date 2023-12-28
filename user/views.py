from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, \
    TokenObtainPairView, TokenRefreshView
import requests

from backend.settings import GOOGLE_RECAPTCHA, SIMPLE_JWT
from user.serializer import MyTokenObtainPairSerializer, RegisterSerializer, \
    UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # recaptcha 검증
        data = {
            'secret': GOOGLE_RECAPTCHA['SECRET_KEY'],
            'response': request.data.get('captcha')
        }
        verification_response = requests.post(GOOGLE_RECAPTCHA['URL'], data=data)
        verification_result = verification_response.json()
        print('reCAPTCHA verification result: ', verification_result)
        if not verification_result.get('success'):
            return Response({'detail': 'Go Home ROBOT'}, status=status.HTTP_403_FORBIDDEN)

        response = super().post(request, *args, **kwargs)
        print('created', response.data['refresh'])
        response.set_cookie(
            'refresh_token',
            response.data['refresh'],
            httponly=True,
            samesite='Lax',
            max_age=SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        )
        return response


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': '로그인 상태가 아닙니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        return response


class MyTokenBlacklistView(TokenBlacklistView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is not None:
            token = RefreshToken(refresh_token)
            token.blacklist()
        response = Response({'detail': '로그인 상태가 아닙니다.'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class EmailVerificationView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    @extend_schema(parameters=[
        OpenApiParameter(name="email", description="이메일 주소", required=True,
                         type=str)])
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            return Response({'detail': '이메일을 입력해주세요.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.filter(email=email).first()
        if user:
            return Response({'detail': '이미 존재하는 이메일입니다.'},
                            status=status.HTTP_409_CONFLICT)
        return Response({'detail': '사용 가능한 이메일입니다.'}, status=status.HTTP_200_OK)


class UserInfoView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = {
            'secret': GOOGLE_RECAPTCHA['SECRET_KEY'],
            'response': request.data.get('captcha')
        }
        verification_response = requests.post(GOOGLE_RECAPTCHA['URL'], data=data)
        verification_result = verification_response.json()
        if not verification_result.get('success'):
            return Response({'detail': 'Go Home ROBOT'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': "요청에 문제가 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        get_user_model().objects.create_user(**serializer.validated_data)
