from rest_framework import serializers
from .models import *

class ShortFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortForm
        fields = ('title', 'file_path')

class ShortsListSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='user.nickname')  # 작성자의 username 필드를 반환
    
    class Meta:
        model = ShortForm
        fields = ('id', 'title', 'view', 'created_at', 'author_name')
