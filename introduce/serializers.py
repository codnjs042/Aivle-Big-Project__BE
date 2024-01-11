from rest_framework import serializers

from .models import Comment, Post
from django.utils import timezone
from django.utils.timesince import timesince

def get_time_difference(self, datetime_field):
    time_difference = timezone.now() - datetime_field
    if time_difference.days == 0:
        time_since = timesince(datetime_field).split(',')[0]
        if time_since == "0 minutes":
            return "방금 전"
        else:
            return f"{time_since} 전"
    else:
        return datetime_field.astimezone(timezone.get_default_timezone()).strftime('%y년 %m월 %d일')
    
class PostListSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    formatted_created_at = serializers.SerializerMethodField()
    formatted_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'writer', 'is_admin', 'comments_count',
            'formatted_created_at',
            'formatted_updated_at')

    def get_writer(self, obj):
        return obj.user.nickname

    def get_is_admin(self, obj):
        return obj.user.is_admin

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_formatted_created_at(self, obj):
        now = timezone.localtime(timezone.now())
        created_at_localtime = timezone.localtime(obj.created_at)
        if now - created_at_localtime < timezone.timedelta(days=1):
            if now - created_at_localtime < timezone.timedelta(minutes=1):
                return "방금 전"
            return get_time_difference(self, obj.created_at)
        return created_at_localtime.strftime('%y년 %m월 %d일')

    def get_formatted_updated_at(self, obj):
        now = timezone.localtime(timezone.now())
        updated_at_localtime = timezone.localtime(obj.updated_at)
        if now - updated_at_localtime < timezone.timedelta(days=1):
            if now - updated_at_localtime < timezone.timedelta(minutes=1):
                return "방금 전"
            return get_time_difference(self, obj.created_at)
        return updated_at_localtime.strftime('%y년 %m월 %d일')


class PostSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    formatted_created_at = serializers.SerializerMethodField()
    formatted_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['title', 'content', 'writer', 'is_admin',
                  'formatted_created_at',
                  'formatted_updated_at', 'comments']

    def get_writer(self, obj):
        return obj.writer()

    def get_is_admin(self, obj):
        return obj.is_admin()

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True, context=self.context).data

    def get_formatted_created_at(self, obj):
        now = timezone.localtime(timezone.now())
        created_at_localtime = timezone.localtime(obj.created_at)
        if now - created_at_localtime < timezone.timedelta(days=1):
            if now - created_at_localtime < timezone.timedelta(minutes=1):
                return "방금 전"
            return get_time_difference(self, obj.created_at)
        return created_at_localtime.strftime('%y년 %m월 %d일')

    def get_formatted_updated_at(self, obj):
        now = timezone.localtime(timezone.now())
        updated_at_localtime = timezone.localtime(obj.updated_at)
        if now - updated_at_localtime < timezone.timedelta(days=1):
            if now - updated_at_localtime < timezone.timedelta(minutes=1):
                return "방금 전"
            return get_time_difference(self, obj.created_at)
        return updated_at_localtime.strftime('%y년 %m월 %d일')

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
        fields = ['post', 'content', 'writer', 'is_admin', 'created_at', 'updated_at']

    def get_writer(self, obj):
        return obj.writer()

    def get_is_admin(self, obj):
        return obj.is_admin()

    def create(self, validated_data):
        print(validated_data)
        post = validated_data.pop('post')
        validated_data.pop('user', None)
        user = self.context['request'].user
        print(user)
        comment = Comment.objects.create(post=post, user=user, **validated_data)
        return comment

