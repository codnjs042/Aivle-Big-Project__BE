from django.http import FileResponse, Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
import os

from .serializers import *


class ShortsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShortsSerializer
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['author'] = current_user
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # 유효한 데이터 저장
        serializer.save()


class ShortFormView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id, *args, **kwargs):
        short_id = id
        if short_id is None:
            return Response({'message': 'No short ID provided'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            short_form = ShortForm.objects.get(pk=short_id)
            short_form.update_counter  # 조회수 증가
        except ShortForm.DoesNotExist:
            return Response({'message': 'ShortForm not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ShortFormSerializer(short_form)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id, *args, **kwargs):
        short_id = id
        if not short_id:
            return Response({'message': 'No short ID provided'},
                            status=status.HTTP_400_BAD_REQUEST)
            
        short_form = get_object_or_404(ShortForm, pk=short_id)
        if request.user != short_form.author:
            return Response({'message': 'No User permissions'},
                            status=status.HTTP_403_FORBIDDEN)
        
        file_path = short_form.file_path.path
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            short_form.delete()
            return Response({"message": "삭제되었습니다."}, 
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class StreamShortFileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[
        OpenApiParameter(name="path", description="쇼츠 경로", required=True,
                         type=str)])
    def get(self, request, format=None):
        file_path = request.query_params.get('path')
        try:
            short_form = ShortForm.objects.get(file_path=file_path)
        except ShortForm.DoesNotExist:
            raise Http404
        content_type = 'video/webm'
        file_handle = short_form.file_path.open('rb')
        response = FileResponse(file_handle, content_type=content_type)
        response[
            'Content-Disposition'] = f'inline; filename="{short_form.file_path.name}"'

        return response


class ShortsListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        shorts = ShortForm.objects.all()
        page = paginator.paginate_queryset(shorts, request)
        if page is not None:
            serializer = ShortsListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = ShortsListSerializer(shorts, many=True, context={'request': request})
        return Response(serializer.data)