from rest_framework import serializers
from .models import Notice

class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'