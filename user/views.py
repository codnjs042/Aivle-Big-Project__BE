from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView, TokenVerifyView, TokenBlacklistView
from user.serializer import CustomTokenVerifySerializer, \
    MyTokenObtainPairSerializer, RegisterSerializer
from django.contrib.auth import get_user_model

class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.set_cookie(
            'access_token',
            response.data['access'],
            httponly=True,
            samesite='Strict',
        )
        response.set_cookie(
            'refresh_token',
            response.data['refresh'],
            httponly=True,
            samesite='Strict',
        )
        del response.data['access']
        del response.data['refresh']
        return response


class MyTokenVerifyView(TokenVerifyView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenVerifySerializer

    def post(self, request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        if not token:
            return Response({'detail': '발급된 토큰이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['token'] = token
        return super().post(request, *args, **kwargs)

class MyTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': '로그아웃 되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        response.set_cookie(
            'access_token',
            response.data['access'],
            httponly=True,
            samesite='Strict',
        )
        del response.data['access']
        response = Response({'detail': '토큰이 갱신되었습니다.'})
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

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        get_user_model().objects.create_user(**serializer.validated_data)