import json

from django.template.loader import render_to_string
from django.http.response import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from datetime import timedelta

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from core.mediators.mail import Mail
from workspace.models import Workspace
from workspace.serializers import WorkspaceSerializer
from core.authentication.oauth import create_user_with_google
from core.authentication.tokens import token_generator

from .serializers import (
    CustomTokenObtainPairSerializer,
    PasswordResetTokenSerializer, UserSerializer, _UserSerializer)
from .models import User, PasswordResetToken


class CustomTokenObtainPaisView(TokenObtainPairView):
    """ Custom Obtain Pair View that uses our Custom Serializer """

    serializer_class = CustomTokenObtainPairSerializer


@csrf_exempt
def create_password_reset_token(request):
    """ Validates the user, creates the token and send it to email """

    if not request.method == 'POST':
        return HttpResponseNotAllowed(f"{request.method} method not allowed")

    data = json.loads(request.body)

    email = data.get('email')

    if not email:
        return HttpResponseBadRequest("'email' is required")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return HttpResponseNotFound('User with this email does not exists')

    token_valid_through = timezone.now() + timedelta(hours=1)

    data = {
        'user': user.id,
        'valid_through': token_valid_through
    }

    serializer = PasswordResetTokenSerializer(data=data)

    if not serializer.is_valid():
        errors = dict()
        for key, message in serializer.errors.items():
            errors[key] = str(message[0])

        return HttpResponseBadRequest(f"{errors}")

    PasswordResetToken.objects.filter(user=user).delete()
    token = serializer.save()

    email_context = {
        'user': token.user,
        'url': f'{settings.FRONTEND_URL}/reset-password/{token.id}'
    }

    email_template = render_to_string(
        'email/reset-password.html', email_context)

    Mail.send_email(subject='[HelloTeam] Password Reset',
                    recipient_list=[user.email], html_message=email_template)

    return JsonResponse('OK', safe=False)


@csrf_exempt
def reset_password(request, token_id):
    """
    Validates if the token exists and is valid and sets the new password to the
    User
    """

    if request.method not in ['GET', 'POST']:
        return HttpResponseNotAllowed('Method not allowed')

    try:
        # TODO: Fix the expiration time query
        # expiration_time = timezone.now() + timedelta(hours=2)
        # , valid_through__gte=expiration_time
        token = PasswordResetToken.objects.get(
            id=token_id)
    except PasswordResetToken.DoesNotExist:
        return HttpResponseNotFound('Token does not exists')

    if request.method == 'GET':
        return JsonResponse('OK', safe=False)

    if request.method == 'POST':
        data = json.loads(request.body)

        password = data.get('new_password')

        if not password:
            return HttpResponseBadRequest("'new_password' is required")

        token.user.set_password(password)
        token.user.save()

        token.delete()

        return JsonResponse('Password set successfully', safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    """
    Public function used to sign users up creating the Workspace and the User.
    """

    data = request.data

    required_fields = [
        "email",
        "password",
        "workspace_name",
        "organization_type",
    ]

    missing_fields = []

    for required_field in required_fields:
        if not data.get(required_field):
            missing_fields.append(required_field)

    if len(missing_fields) > 0:
        return Response({
            'detail': (
                'The following required fields are '
                f'missing: {missing_fields}')
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data.get('email')).exists():
        return Response({'detail': 'This email is already in use'},
                        status=status.HTTP_400_BAD_REQUEST)

    if Workspace.objects.filter(name=data.get('workspace_name')).exists():
        return Response({'detail': 'This Workspace name is already in use'},
                        status=status.HTTP_400_BAD_REQUEST)

    user_data = {
        "email": data.get('email'),
        "password": data.get('password', ''),
        "is_active": True,
        "is_staff": True,
    }

    workspace_data = {
        "name": data.get('workspace_name'),
        "organization_type": data.get('organization_type'),
    }

    user_serializer = UserSerializer(data=user_data)
    workspace_serializer = WorkspaceSerializer(data=workspace_data)

    with transaction.atomic():
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        workspace_serializer.is_valid(raise_exception=True)
        workspace = workspace_serializer.save()

        workspace.owner = user
        workspace.save()

    token = user.generate_jwt_token()
    response = {**token, 'user': user_serializer.data}

    return Response(
        response, status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def social_sign_up(request):
    """
    Public function used to sign users up creating the Workspace and the User.
    """

    data = request.data

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "workspace_name",
        "organization_type",
        "phone_number",
        "social_provider",
        "social_token",
    ]

    missing_fields = []

    for required_field in required_fields:
        if not data.get(required_field):
            missing_fields.append(required_field)

    if len(missing_fields) > 0:
        return Response({
            'detail': (
                'The following required fields are '
                f'missing: {missing_fields}')
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data.get('email')).exists():
        return Response({'detail': 'This email is already in use'},
                        status=status.HTTP_400_BAD_REQUEST)

    if Workspace.objects.filter(name=data.get('workspace_name')).exists():
        return Response({'detail': 'This Workspace name is already in use'},
                        status=status.HTTP_400_BAD_REQUEST)

    workspace_data = {
        "name": data.get('workspace_name'),
        "organization_type": data.get('organization_type'),
    }

    workspace_serializer = WorkspaceSerializer(data=workspace_data)

    with transaction.atomic():
        user = create_user_with_google(
            data['social_token'], data.get('phone_number'))

        password = data.get('password')

        if password:
            user.set_password(password)
            user.save()

        workspace_serializer.is_valid(raise_exception=True)
        workspace = workspace_serializer.save()

        workspace.owner = user
        workspace.save()

    user_serializer = UserSerializer(instance=user)

    token = user.generate_jwt_token()
    response = {**token, 'user': user_serializer.data}

    return Response(
        response, status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def switch_workspace(request):
    """
    Public function used to sign users up creating the Workspace and the User.
    """

    data = request.data

    required_fields = [
        "workspace_id",
    ]

    missing_fields = []

    for required_field in required_fields:
        if not data.get(required_field):
            missing_fields.append(required_field)

    if len(missing_fields) > 0:
        return Response({
            'detail': (
                'The following required fields are '
                f'missing: {missing_fields}')
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        workspace = Workspace.objects.get(
            Q(id=data.get('workspace_id')) &
            (
                Q(owner=request.user) |
                Q(workspace_staff__user=request.user)
            )
        )
    except Workspace.DoesNotExist:
        raise NotFound("Workspace not found or the user doesn't belongs to it")

    workspace_serializer = WorkspaceSerializer(instance=workspace)

    user_serializer = UserSerializer(instance=request.user)

    token = request.user.generate_jwt_token(str(workspace.id))
    response = {**token, 'user': user_serializer.data,
                'workspace': workspace_serializer.data}

    return Response(
        response, status=status.HTTP_201_CREATED
    )


class VerifyUserEmail(APIView):
    allowed_methods = ['get']

    def get(self, request, token):
        if token_generator.check_token(request.user, token):
            request.user.verified_email = True

            request.user.save()

            user_serializer = _UserSerializer(instance=request.user)

            return Response(user_serializer.data)

        return Response({'detail': 'Invalid token'},
                        status=status.HTTP_403_FORBIDDEN)


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = _UserSerializer
    http_method_names = ['put', 'patch']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        workspace_id = request.data.get('workspace')

        if not request.user.is_superuser:
            if request.user != instance:
                if not request.user.is_staff:
                    raise PermissionDenied(
                        "Request's User is not a staff member")

                if not instance.workspace_set.filter(id=workspace_id).exists():
                    raise PermissionDenied(
                        "User doesn't belongs to the Workspace")

        user = super().update(request, *args, **kwargs)

        if request.data.get('update_workspace'):
            try:
                workspace = Workspace.objects.get(id=workspace_id)
                workspace_serializer = WorkspaceSerializer(
                    data=request.data, instance=workspace, partial=True)
                if workspace_serializer.is_valid():
                    workspace_serializer.save()
            except Workspace.DoesNotExist:
                pass

        if request.data.get('is_signing_up'):
            instance = self.get_object()

            instance.send_verification_email()

        return user


class UserWorkspacesListView(ListAPIView):
    """
    List the request's User related Workspaces
    """

    model = Workspace
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        queryset = self.model.objects.filter(
            Q(owner=self.request.user) |
            Q(workspace_staff__user=self.request.user)
        )

        return queryset
