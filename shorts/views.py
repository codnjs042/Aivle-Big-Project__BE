from django.http import FileResponse, Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class ShortsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShortFormSerializer
    parser_classes = (MultiPartParser,)

    @extend_schema(parameters=[
        OpenApiParameter(name="id", description="쇼츠 아이디", required=True,
                         type=int)])
    def get(self, request, *args, **kwargs):
        short_id = request.query_params.get('id')
        if not short_id:
            return Response({'message': 'No short ID provided'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            short_form = ShortForm.objects.get(pk=short_id)
        except ShortForm.DoesNotExist:
            return Response({'message': 'ShortForm not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ShortFormSerializer(short_form)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
