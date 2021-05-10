from rest_framework.serializers import ModelSerializer, ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .models import OrganizationType, Workspace, StaffInvitation


class OrganizationTypeSerializer(ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = ('id', 'name')


class WorkspaceSerializer(ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__'


class WorkspaceListSerializer(ModelSerializer):
    organization_type = OrganizationTypeSerializer(read_only=True)

    class Meta:
        model = Workspace
        fields = '__all__'


class StaffInvitationSerializer(ModelSerializer):

    def validate(self, attrs):
        super().validate(attrs)

        workspace = attrs.get('workspace')
        email = attrs.get('email')

        if attrs.get('created_by') != workspace.owner:
            raise ValidationError('Only Workspace owners can invite Staff')

        try:
            if workspace.workspace_staff.fitler(email=email).exists():
                raise ValidationError('This email belongs to a user that is '
                                      'already part of this Workspace Staff')
        except ObjectDoesNotExist:
            pass

        return attrs

    class Meta:
        model = StaffInvitation
        fields = '__all__'
