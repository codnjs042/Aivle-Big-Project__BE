from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import requests
from backend.settings import GOOGLE_RECAPTCHA
from user.models import User
from user.validators import CustomPasswordValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'nickname', 'selectedGenres',
                  'selectedArtist')


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
    selectedGenres = serializers.IntegerField(
        validators=[MinValueValidator(0)])
    selectedArtist = serializers.IntegerField(
        validators=[MinValueValidator(0)])

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'nickname', 'selectedGenres',
                  'selectedArtist')


class ReCaptchaSerializer(serializers.Serializer):
    captcha = serializers.CharField(write_only=True)

    def validate_capcha(self, value):
        data = {
            'secret': GOOGLE_RECAPTCHA['SECRET_KEY'],
            'response': value
        }
        verification_response = requests.post(GOOGLE_RECAPTCHA['URL'],
                                              data=data)
        verification_result = verification_response.json()
        print('reCAPTCHA verification result: ', verification_result)
        if not verification_result.get('success'):
            raise serializers.ValidationError('Go Home ROBOT')
        return value
