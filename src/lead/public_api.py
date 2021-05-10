from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import LeadSerializer
from .models import Lead


class PublicRegisterLead(APIView):
    """
    Public view used to check if an email is availably for new users.
    """

    permission_classes = [AllowAny]
    allowed_methods = ['post']

    def post(self, request):
        lead_serializer = LeadSerializer(data=request.data)

        try:
            lead = Lead.objects.get(email=request.data.get('email'))

            lead_serializer.instance = lead
        except Lead.DoesNotExist:
            pass

        lead_serializer.is_valid(raise_exception=True)
        lead_serializer.save()

        return Response(lead_serializer.data,
                        status=status.HTTP_201_CREATED)
