from rest_framework import serializers
from .models import *


class SentenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sentence
        fields = ['title', 'ko_text', 'en_text', 'pronunciation','tag']

class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ['email', 'sentence', 'PronunProfEval', 'FluencyEval', 'ComprehendEval']

class BookmarkSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = ['text', 'is_bookmarked']
        
    def get_text(self, obj):
        return obj.ko_text.ko_text
    
class AudioFileSerializer(serializers.ModelSerializer):
    audio_path = serializers.SerializerMethodField()
    class Meta:
        model = AudioFile
        fields = ['audio_path']

    def get_file_path(self, obj):
        return str(obj.audio_path)