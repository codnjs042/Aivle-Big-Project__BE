from rest_framework import serializers
from .models import Post, Comment

class PostListSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'writer', 'is_admin', 'comments_count', 'created_at', 'updated_at')

    def get_writer(self, obj):
        return obj.user.nickname

    def get_is_admin(self, obj):
        return obj.user.is_admin

    def get_comments_count(self, obj):
        return obj.comments.count()
class PostSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['title', 'content', 'writer', 'is_admin', 'created_at', 'updated_at', 'comments']
    def get_writer(self, obj):
        return obj.writer()
    def get_is_admin(self, obj):
        return obj.is_admin()

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True, context=self.context).data
    def create(self, validated_data):
        print(validated_data)
        validated_data.pop('user', None)
        user = self.context['request'].user
        print(user)
        post = Post.objects.create(user=user, **validated_data)
        return post

class CommentSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['content', 'writer', 'is_admin', 'created_at', 'updated_at']

    def get_writer(self, obj):
        return obj.writer()
    def get_is_admin(self, obj):
        return obj.is_admin()