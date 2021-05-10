from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .api import StaffInvitationViewSet

staff_invitation_router = DefaultRouter()
staff_invitation_router.register('', StaffInvitationViewSet)

urlpatterns = [
    path('invitation/staff', include(staff_invitation_router.urls)),
]
