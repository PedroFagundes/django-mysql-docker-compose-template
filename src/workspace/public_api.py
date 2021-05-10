from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import OrganizationType
from .serializers import OrganizationTypeSerializer


class PublicOganizationTypesListView(ListAPIView):
    permission_classes = [AllowAny, ]
    queryset = OrganizationType.objects.filter(is_active=True)
    serializer_class = OrganizationTypeSerializer
