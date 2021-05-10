from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from core.mixins import CustomModelViewset

from .models import Post, Comment, Activity, Image, Video
from .serializers import (
    PostSerializer, PostListSerializer, CommentSerializer,
    CommentListSerializer, ActivitySerializer, ActivityListSerializer,
    ImageSerializer, VideoSerializer)


class PostViewset(CustomModelViewset):

    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostListSerializer

    def create(self, request, *args, **kwargs):
        data = self._get_data(request)

        serializer = PostSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        image_ids = request.data.get('image_ids')

        if image_ids:
            images = Image.objects.filter(pk__in=image_ids)

            serializer.instance.images.set(images)

        video_ids = request.data.get('video_ids')

        if video_ids:
            videos = Video.objects.filter(pk__in=video_ids)

            serializer.instance.videos.set(videos)

        serializer = PostListSerializer(instance=serializer.instance)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GetPostLikes(ListModelMixin, GenericAPIView):
    """
    View to list Post likes
    """

    serializer_class = ActivityListSerializer

    def get(self, request, post_id):
        queryset = Activity.objects.filter(
            activity_type='L', object_id=post_id, content_type=6)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class CommentViewSet(CustomModelViewset):

    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CommentSerializer(data=self._get_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = CommentListSerializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ActivityViewSet(CustomModelViewset):

    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def create(self, request, *args, **kwargs):
        serializer = ActivitySerializer(data=self._get_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = ActivityListSerializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ImageViewSet(CustomModelViewset):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # parser_classes = [FileUploadParser, MultiPartParser]


class VideoViewSet(CustomModelViewset):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
