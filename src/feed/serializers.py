from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField, IntegerField)
from decouple import config

from core.authentication.models import User

from .models import Post, Comment, Activity, Image, Video


class ImageSerializer(ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'file', 'file_thumb',
                  'file_landscape', 'file_portrait', 'file_square']


class VideoSerializer(ModelSerializer):
    url = SerializerMethodField()

    def get_url(self, instance):
        url = f"{config('SWAGGER_SCHEME_URL')}{instance.file.url}"

        return url

    class Meta:
        model = Video
        fields = '__all__'


class AuthorSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class ActivityListSerializer(ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'activity_type', 'user']


class ActivitySerializer(ModelSerializer):

    content_object = SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'


class CommentListSerializer(ModelSerializer):
    author = AuthorSerializer(read_only=True)
    replies = SerializerMethodField()
    is_liked = SerializerMethodField()
    like_id = SerializerMethodField()
    likes_count = IntegerField()

    def get_replies(self, instance):
        replies = instance.comment_set.all()

        serializer = CommentListSerializer(
            instance=replies, many=True, context=self.context)

        return serializer.data

    def get_is_liked(self, instance):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            user = request.user

            like = instance.likes.filter(
                user=user)

            return like.exists()

        return False

    def get_like_id(self, instance):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            user = request.user

            like = instance.likes.filter(
                user=user)

            if like.exists():
                return like.first().id

        return None

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class PostListSerializer(ModelSerializer):
    author = AuthorSerializer()
    likes_count = IntegerField()
    comments_count = SerializerMethodField()
    comments = SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    is_liked = SerializerMethodField()
    like_id = SerializerMethodField()

    def get_comments_count(self, instance):
        return instance.post_comments.count()

    def get_comments(self, instance):
        comments = instance.post_comments.filter(
            parent=None).order_by('-created_at')

        serializer = CommentListSerializer(
            instance=comments, many=True, context=self.context)

        return serializer.data

    def get_is_liked(self, instance):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            user = request.user

            like = instance.likes.filter(
                user=user)

            return like.exists()

        return False

    def get_like_id(self, instance):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            user = request.user

            like = instance.likes.filter(
                user=user)

            if like.exists():
                return like.first().id

        return None

    class Meta:
        model = Post
        fields = ['id', 'author', 'workspace', 'likes_count', 'is_liked',
                  'like_id', 'comments', 'comments_count', 'content', 'images',
                  'videos', 'created_at']
