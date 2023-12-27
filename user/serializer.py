from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import User
from user.validators import CustomPasswordValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'nickname', 'genre_preferences',
                  'singer_preferences')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,
                                     validators=[CustomPasswordValidator()])
    nickname = serializers.CharField(validators=[MaxLengthValidator(30)])
    genre_preferences = serializers.IntegerField(
        validators=[MinValueValidator(0)])
    singer_preferences = serializers.IntegerField(
        validators=[MinValueValidator(0)])

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'nickname', 'genre_preferences',
                  'singer_preferences')
