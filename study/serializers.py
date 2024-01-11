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

class ResultScoreSerializer(serializers.ModelSerializer):
    sentence = serializers.SerializerMethodField()
    PronunProfEval = serializers.SerializerMethodField()
    FluencyEval = serializers.SerializerMethodField()
    ComprehendEval = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ['sentence', 'PronunProfEval', 'FluencyEval', 'ComprehendEval']

    def get_sentence(self, obj):
        return obj.sentence.ko_text
    
    def get_PronunProfEval(self, obj):
        return obj.PronunProfEval * 20
    
    def get_FluencyEval(self, obj):
        return obj.FluencyEval * 20
    
    def get_ComprehendEval(self, obj):
        return obj.ComprehendEval * 20


class BookmarkSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = ['text', 'is_bookmarked']
        
    def get_text(self, obj):
        return obj.ko_text.ko_text
    
class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['audio_path']