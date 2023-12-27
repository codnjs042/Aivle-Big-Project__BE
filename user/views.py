from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, \
    TokenObtainPairView, TokenRefreshView

from user.serializer import MyTokenObtainPairSerializer, RegisterSerializer, \
    UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        print('created', response.data['refresh'])
        response.set_cookie(
            'refresh_token',
            response.data['refresh'],
            httponly=True,
            samesite='None', # todo 보안에 취약하니 업데이트 필요
        )
        del response.data['refresh']
        refresh = request.COOKIES.get('refresh_token')
        print('cookie exist', refresh)
        response.data['refresh'] = refresh
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

    def perform_create(self, serializer):
        get_user_model().objects.create_user(**serializer.validated_data)
