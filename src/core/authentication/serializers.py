from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from rest_framework import exceptions

from workspace.models import Workspace, WorkspaceStaff
from core.authentication.models import User

from .models import PasswordResetToken


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar',
                  'password', 'is_active', 'phone', 'country', 'zip_code',
                  'timezone', 'verified_email']

    def create(self, validated_data):
        user = super().create(validated_data)
        password = validated_data.get('password')

        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        instance = super().update(validated_data)
        password = validated_data.get('password')

        if password:
            instance.set_password(password)
            instance.save()
        return instance


class _UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar', 'phone',
                  'is_active', 'country', 'zip_code', 'timezone',
                  'verified_email']


class WorkspaceSerializer(ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom Obtain Pair Serializer that adds Workspace to the JWT """

    workspace_id = CharField(required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if hasattr(user, 'workspace_id'):
            token['workspace_id'] = user.workspace_id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        workspace_id = attrs.get('workspace_id')

        if workspace_id:
            workspace_query = Workspace.objects.filter(pk=workspace_id)
            if not workspace_query.exists():
                raise exceptions.NotFound('Invalid Workspace ID')

            workspace = workspace_query.first()
            workspace_staff_ids = WorkspaceStaff.objects.filter(
                workspace=workspace, user=self.user).values_list(
                    'user_id', flat=True)

            if (not self.user.is_superuser and self.user != workspace.owner and
                    self.user.id not in workspace_staff_ids):
                raise exceptions.PermissionDenied(
                    'User is not allowed to login on this Workspace')

            self.user.workspace_id = workspace_id

        if not self.user.is_superuser and not workspace_id:
            workspace_id = self.user.get_default_workspace_id()

            workspace = Workspace.objects.filter(pk=workspace_id).first()

            if not workspace_id:
                raise exceptions.NotFound('Workspace ID is required')

            self.user.workspace_id = workspace_id

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = _UserSerializer(instance=self.user).data

        if workspace_id:
            data['workspace'] = WorkspaceSerializer(instance=workspace).data

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class PasswordResetTokenSerializer(ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ['user']
