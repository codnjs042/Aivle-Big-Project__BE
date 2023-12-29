from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .serializers import *


class UploadShortsView(generics.CreateAPIView):
    # permission_classes = [AllowAny]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShortFormSerializer
    
    def post(self, request, *args, **kwargs):
        current_user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.validated_data['author'] = current_user.id
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        # 유효한 데이터 저장
        serializer.save()
