from django.urls import path

from .public_api import (PublicCheckEmailAvailability,
                         PublicCheckWorkspaceNameAvailability)

urlpatterns = [
    path('check-email-availability', PublicCheckEmailAvailability.as_view()),
    path('check-workspace-name-availability',
         PublicCheckWorkspaceNameAvailability.as_view()),
]
