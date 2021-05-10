from django.contrib.auth import get_user_model
from django.conf import settings

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from workspace.models import Workspace

from .serializers import UserSerializer

User = get_user_model()


@api_view(['POST', ])
@permission_classes((AllowAny,))
def login_with_google(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    data = id_token.verify_oauth2_token(
        request.data['code'], google_requests.Request(), client_id)

    if data['iss'] not in [
            'accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')

    user = User.objects.filter(email=data['email'])

    if not user.exists():
        return Response(
            {'detail': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = user.first()

    is_workspace_owner = Workspace.objects.filter(owner=user).exists()
    is_workspace_staff = Workspace.objects.filter(workspace_staff__user=user)

    if not is_workspace_owner and not is_workspace_staff:
        return Response(
            {'detail': 'User is not associated to any Workspace'},
            status=status.HTTP_403_FORBIDDEN
        )

    jwt_token = user.generate_jwt_token()
    user_serializer = UserSerializer(instance=user)

    response = {**jwt_token, 'user': user_serializer.data}

    return Response(
        response, status=status.HTTP_200_OK
    )


def create_user_with_google(token, phone='', password=None):
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    oauth_data = id_token.verify_oauth2_token(
        token, google_requests.Request(), client_id)

    if oauth_data['iss'] not in [
            'accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')

    user_data = {
        "first_name": oauth_data.get('given_name'),
        "last_name": oauth_data.get('family_name'),
        "email": oauth_data.get('email'),
        "phone": phone,
        "is_active": True,
    }

    if password:
        user_data['password'] = password

    user_serializer = UserSerializer(data=user_data)
    user_serializer.is_valid(raise_exception=True)
    user = user_serializer.save()

    return user
