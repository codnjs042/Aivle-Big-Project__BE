from rest_framework import serializers
from shorts.models import ShortForm
from user.models import User

class ShortFormSerializer(serializers.ModelSerializer):
    file_path = serializers.SerializerMethodField()
    
    class Meta:
        model = ShortForm
        fields = ('title', 'file_path')
        
    def get_file_path(self, obj):
        return str(obj.file_path)

class ShortsListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ShortForm
        fields = ('id', 'title', 'author_name', 'view', 'created_at')

    def get_author_name(self, obj):
        return obj.author.nickname