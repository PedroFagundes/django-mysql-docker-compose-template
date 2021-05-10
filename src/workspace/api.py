from core.mixins import CustomModelViewset

from .models import StaffInvitation
from .serializers import StaffInvitationSerializer


class StaffInvitationViewSet(CustomModelViewset):

    queryset = StaffInvitation.objects
    serializer_class = StaffInvitationSerializer

    def create(self, request, *args, **kwargs):
        request.data.setdefault('created_by', str(request.user.id))

        return super().create(request, *args, **kwargs)
