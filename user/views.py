from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    permission_classes = (AllowAny,)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.Nickname
        token['Nickname'] = user.Nickname
        token['genre_preferences'] = user.genre_preferences
        token['singer_preferences'] = user.singer_preferences
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class HelloView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        data = {'message': 'Hello, World!'}
        return Response(data)
