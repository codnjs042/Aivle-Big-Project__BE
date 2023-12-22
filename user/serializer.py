from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.state import token_backend

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'genre_preferences',
                  'singer_preferences')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nickname'] = user.nickname
        token['genre_preferences'] = user.genre_preferences
        token['singer_preferences'] = user.singer_preferences
        return token


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        super().validate(attrs)
        token = attrs['token']
        decoded_payload = token_backend.decode(token, verify=False)
        attrs['email'] = decoded_payload.get('email')
        attrs['nickname'] = decoded_payload.get('nickname')
        attrs['genre_preferences'] = decoded_payload.get('genre_preferences')
        attrs['singer_preferences'] = decoded_payload.get('singer_preferences')
        return attrs
