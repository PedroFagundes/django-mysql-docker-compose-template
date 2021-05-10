import uuid

from django.db import models
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import truncatechars

from simple_history.models import HistoricalRecords


class Activity(models.Model):
    """Model definition for Activity."""

    LIKE = 'L'
    ACTIVITY_TYPE_CHOICES = (
        (LIKE, 'Like'),
    )

    workspace = models.ForeignKey(
        'workspace.Workspace', related_name='workspace_activity',
        on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    activity_type = models.CharField(
        max_length=1, choices=ACTIVITY_TYPE_CHOICES)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey()

    class Meta:
        """Meta definition for Activity."""

        verbose_name = 'Activity'
        verbose_name_plural = 'Activitys'
        db_table = 'activity'
        unique_together = ['object_id', 'activity_type', 'user']

    def __str__(self):
        """Unicode representation of Activity."""
        return self.user.email


class Post(models.Model):
    """Model definition for Post."""

    workspace = models.ForeignKey(
        'workspace.Workspace', related_name='workspace_posts',
        on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    history = HistoricalRecords()

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    likes = GenericRelation(Activity, related_query_name='pictures')

    class Meta:
        """Meta definition for Post."""

        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        db_table = 'post'
        unique_together = (('workspace', 'id'),)

    def __str__(self):
        """Unicode representation of Post."""
        return f'{self.author} {self.created_at}'

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def short_content(self):
        return truncatechars(self.content, 150)


class Image(models.Model):
    """Model definition for Image."""

    VALID_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

    workspace = models.ForeignKey(
        'workspace.Workspace', related_name='workspace_images',
        on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(
        upload_to='images/',
        validators=[FileExtensionValidator(VALID_IMAGE_EXTENSIONS)])
    post = models.ForeignKey(
        Post, related_name='images', on_delete=models.CASCADE, blank=True,
        null=True)
    size_in_bytes = models.PositiveIntegerField(blank=True, null=True)
    is_temporary_file = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for Image."""

        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        db_table = 'image'
        unique_together = (('workspace', 'id'),)

    def __str__(self):
        """Unicode representation of Image."""
        return self.post.author.email or self.file

    def get_image_handler_data(self):
        image_handler_data = {
            "bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "key": f"media/{self.file.name}",
            "edits": {
                "resize": {
                    "width": 0,
                    "height": 0,
                    "fit": "cover"
                },
            }
        }

        return image_handler_data

    @property
    def file_thumb(self):
        import base64
        import json

        image_handler_data = self.get_image_handler_data()

        image_handler_data[
            'edits']['resize']['width'] = settings.IMAGE_THUMB_WIDTH
        image_handler_data[
            'edits']['resize']['height'] = settings.IMAGE_THUMB_HEIGHT

        stringfied_image_handler_data = json.dumps(image_handler_data)

        encoded_data = base64.b64encode(
            stringfied_image_handler_data.encode('utf-8'))

        return f'{settings.AWS_IMAGE_HANDLER_URL}/{str(encoded_data, "utf-8")}'

    @property
    def file_landscape(self):
        import base64
        import json

        image_handler_data = self.get_image_handler_data()

        image_handler_data[
            'edits']['resize']['width'] = settings.IMAGE_LANDSCAPE_WIDTH
        image_handler_data[
            'edits']['resize']['height'] = settings.IMAGE_LANDSCAPE_HEIGHT

        stringfied_image_handler_data = json.dumps(image_handler_data)

        encoded_data = base64.b64encode(
            stringfied_image_handler_data.encode('utf-8'))

        return f'{settings.AWS_IMAGE_HANDLER_URL}/{str(encoded_data, "utf-8")}'

    @property
    def file_portrait(self):
        import base64
        import json

        image_handler_data = self.get_image_handler_data()

        image_handler_data[
            'edits']['resize']['width'] = settings.IMAGE_PORTRAIT_WIDTH
        image_handler_data[
            'edits']['resize']['height'] = settings.IMAGE_PORTRAIT_HEIGHT

        stringfied_image_handler_data = json.dumps(image_handler_data)

        encoded_data = base64.b64encode(
            stringfied_image_handler_data.encode('utf-8'))

        return f'{settings.AWS_IMAGE_HANDLER_URL}/{str(encoded_data, "utf-8")}'

    @property
    def file_square(self):
        import base64
        import json

        image_handler_data = self.get_image_handler_data()

        image_handler_data[
            'edits']['resize']['width'] = settings.IMAGE_SQUARE_WIDTH
        image_handler_data[
            'edits']['resize']['height'] = settings.IMAGE_SQUARE_HEIGHT

        stringfied_image_handler_data = json.dumps(image_handler_data)

        encoded_data = base64.b64encode(
            stringfied_image_handler_data.encode('utf-8'))

        return f'{settings.AWS_IMAGE_HANDLER_URL}/{str(encoded_data, "utf-8")}'


class Video(models.Model):
    """Model definition for Video."""

    workspace = models.ForeignKey(
        'workspace.Workspace', related_name='workspace_videos',
        on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='videos/')
    post = models.ForeignKey(
        Post, related_name='videos', on_delete=models.CASCADE, blank=True,
        null=True)
    thumbnail_url = models.URLField(max_length=200, blank=True)
    duration_in_seconds = models.PositiveSmallIntegerField(
        blank=True, null=True)
    size_in_bytes = models.PositiveIntegerField(blank=True, null=True)
    is_temporary_file = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for Video."""

        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        db_table = 'video'
        unique_together = (('workspace', 'id'),)

    def __str__(self):
        """Unicode representation of Video."""
        return self.post.author.email or self.file


class Comment(models.Model):
    """Model definition for Comment."""

    workspace = models.ForeignKey(
        'workspace.Workspace', related_name='workspace_comments',
        on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=254)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_comments')

    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    likes = GenericRelation(Activity)

    class Meta:
        """Meta definition for Comment."""

        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = 'comment'
        unique_together = (('workspace', 'id'),)

    def __str__(self):
        """Unicode representation of Comment."""
        return f'{self.author} {self.created_at}'

    @property
    def likes_count(self):
        return self.likes.count()
