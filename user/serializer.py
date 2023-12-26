from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.utils import timezone
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

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        data['email'] = self.user.email
        data['nickname'] = self.user.nickname
        data['genre_preferences'] = self.user.genre_preferences
        data['singer_preferences'] = self.user.singer_preferences
        return data


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        super().validate(attrs)
        token = attrs['token']
        decoded_payload = token_backend.decode(token, verify=False)
        attrs['email'] = decoded_payload.get('email')
        attrs['nickname'] = decoded_payload.get('nickname')
        attrs['genre_preferences'] = decoded_payload.get('genre_preferences')
        attrs['singer_preferences'] = decoded_payload.get('singer_preferences')
        del attrs['token']
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])
    nickname = serializers.CharField(validators=[MaxLengthValidator(30)])
    genre_preferences = serializers.IntegerField(
        validators=[MinValueValidator(0)])
    singer_preferences = serializers.IntegerField(
        validators=[MinValueValidator(0)])

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'nickname', 'genre_preferences',
                  'singer_preferences')
