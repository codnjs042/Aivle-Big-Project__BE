from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import TokenError, UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from user.serializer import CustomTokenVerifySerializer, \
    MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class MyTokenVerifyView(TokenVerifyView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenVerifySerializer

class HelloView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        data = {'message': 'Hello, World!'}
        return Response(data)
