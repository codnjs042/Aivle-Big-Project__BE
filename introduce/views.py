from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Post
from .serializers import CommentSerializer, PostListSerializer, \
    PostSerializer


class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        posts = Post.objects.annotate(
            is_admin_order=Case(
                When(user__is_admin=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-is_admin_order')
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostListSerializer(page, many=True,
                                            context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = PostListSerializer(posts, many=True,
                                        context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=PostSerializer)
    def post(self, request):
        serializer = PostSerializer(data=request.data,
                                    context={'request': request})
        print(request.headers)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        notice = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(notice)
        return Response(serializer.data)

    @extend_schema(request=PostSerializer)
    def patch(self, request, pk):
        notice = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notice = get_object_or_404(Post, pk=pk)
        notice.delete()
        return Response({'message': '삭제되었습니다.'},
                        status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CommentSerializer)
    def post(self, request, pk):
        serializer = CommentSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=CommentSerializer)
    def patch(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        return Response({'message': '삭제되었습니다.'},
                        status=status.HTTP_204_NO_CONTENT)
