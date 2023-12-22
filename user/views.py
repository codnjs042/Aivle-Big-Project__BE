from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from backend import settings
from user.models import User
from user.serializer import MyTokenObtainPairSerializer, UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class VerifyToken(TokenVerifyView):
    permission_classes = (AllowAny,)

class HelloView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        data = {'message': 'Hello, World!'}
        return Response(data)
