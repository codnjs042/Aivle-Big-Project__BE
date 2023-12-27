from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Notice
from .serializers import NoticeListSerializer

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def notice_list(request):
    if request.method == "GET":
        notices = Notice.objects.all()
        serializer = NoticeListSerializer(notices, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        serializer = NoticeListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def notice(request, pk):
    notice_instance = get_object_or_404(Notice, pk=pk)
    if request.method == "GET":
        serializer = NoticeListSerializer(notice_instance)
        return Response(serializer.data)
    
    elif request.method == "PATCH":
        serializer = NoticeListSerializer(notice_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        notice_instance.delete()
        return Response({'message': '삭제되었습니다.'})