from django.urls import path

from .public_api import PublicRegisterLead

urlpatterns = [
    path('register/', PublicRegisterLead.as_view()),
]
