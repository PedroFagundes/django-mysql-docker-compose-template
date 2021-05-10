from django.urls import path

from .public_api import PublicOganizationTypesListView

urlpatterns = [
    path('organization-types', PublicOganizationTypesListView.as_view()),
]
