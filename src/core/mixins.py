from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions
from django.db.models import Q

from workspace.models import Workspace


class CustomModelViewset(ModelViewSet):
    """
    A custom ViewSet that handles the workspace_id in the JWT token to
    querysets
    """

    def create(self, request, *args, **kwargs):
        if hasattr(request, 'workspace_id'):
            request.data.setdefault('workspace', request.workspace_id)

        return super().create(request, *args, **kwargs)

    def _get_data(self, request):
        try:
            workspace_id = request.workspace_id
        except Exception:
            workspace_id = None

        if workspace_id:
            data = {**request.data, 'workspace': workspace_id}

            return data

        return data

    def get_queryset(self):
        queryset = super().get_queryset()
        workspace_id = None

        if hasattr(self.request, 'workspace_id'):
            workspace_id = self.request.workspace_id

        if not workspace_id and (
                not self.request.user.is_superuser or
                not self.request.user.is_staff):
            raise exceptions.PermissionDenied(
                "User should inform the desired workspace_id")

        if not Workspace.objects.get(
            Q(id=workspace_id) & (
                Q(owner=self.request.user) |
                Q(workspace_staff__user=self.request.user)
            )
        ):
            raise exceptions.PermissionDenied(
                "Not allowed to query data from a workspace that user "
                "doesn't belongs to")

        queryset = queryset.filter(workspace_id=workspace_id)

        return queryset
