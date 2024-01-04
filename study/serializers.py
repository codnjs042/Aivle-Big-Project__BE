from rest_framework import serializers
from .models import *


class SentenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sentence
        fields = ['title', 'ko_text', 'en_text', 'pronunciation','tag']

class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ['email', 'ko_text', 'PronunProfEval', 'FluencyEval', 'ComprehendEval']

class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ['ko_text', 'is_bookmarked']