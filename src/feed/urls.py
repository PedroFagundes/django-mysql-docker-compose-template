from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .api import (
    PostViewset, CommentViewSet, ActivityViewSet, ImageViewSet, VideoViewSet,
    GetPostLikes)

post_router = DefaultRouter()
post_router.register('', PostViewset)

comment_router = DefaultRouter()
comment_router.register('', CommentViewSet)

activity_router = DefaultRouter()
activity_router.register('', ActivityViewSet)

image_router = DefaultRouter()
image_router.register('', ImageViewSet)

video_router = DefaultRouter()
video_router.register('', VideoViewSet)

urlpatterns = [
    path('post/', include(post_router.urls)),
    path('comment/', include(comment_router.urls)),
    path('activity/', include(activity_router.urls)),
    path('image/', include(image_router.urls)),
    path('video/', include(video_router.urls)),
    path('post/<uuid:post_id>/likes', GetPostLikes.as_view()),
]
