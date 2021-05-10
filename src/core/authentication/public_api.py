from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from workspace.models import Workspace
from .models import User


class PublicCheckEmailAvailability(APIView):
    """
    Public view used to check if an email is availably for new users.
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        email = request.GET.get('email')

        if not email:
            return Response({'detail': 'Missing e-mail to query'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            return Response({
                'detail': 'This email is already in use',
                'email': user.email, 'first_name': user.first_name
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'Email is available'},
                            status=status.HTTP_202_ACCEPTED)


class PublicCheckWorkspaceNameAvailability(APIView):
    """
    Public view used to check if an email is availably for new users.
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        name = request.GET.get('name')

        if not name:
            return Response({'detail': 'Missing name to query'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Workspace.objects.filter(name=name).exists():
            return Response({'detail': 'The Workspace name is already in use'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response({'detail': 'Workspace name is available'},
                        status=status.HTTP_202_ACCEPTED)
