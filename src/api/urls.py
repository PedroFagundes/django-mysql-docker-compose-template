from django.urls import path, include, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from decouple import config
from rest_framework.routers import DefaultRouter

from app.health_check import health_check
from core.authentication.api import (
    UserViewSet, VerifyUserEmail, UserWorkspacesListView, switch_workspace)

SWAGGER_SCHEME_URL = config("SWAGGER_SCHEME_URL")

schema_view = get_schema_view(
    openapi.Info(
        title="HelloTeam API",
        default_version="v1",
        description="The Hello Team API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="pedrofagundesb@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    url=SWAGGER_SCHEME_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


user_router = DefaultRouter()
user_router.register('', UserViewSet)


urlpatterns = [
    path("health-check", health_check),
    path("feed/", include('feed.urls')),

    path("auth/", include('core.authentication.urls')),

    path("user/", include(user_router.urls)),
    path("user/verify-email/<str:token>/", VerifyUserEmail.as_view()),
    path("user/workspaces", UserWorkspacesListView.as_view()),
    path("user/switch-workspace", switch_workspace),

    path("workspace/", include('workspace.urls')),

    path("public/users/", include('core.authentication.public_urls')),
    path("public/workspace/", include('workspace.public_urls')),
    path("public/lead/", include('lead.public_urls')),

    re_path(
        r"^docs(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
