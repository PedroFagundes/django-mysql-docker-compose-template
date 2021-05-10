from django.urls import path

from rest_framework_simplejwt import views as jwt_views

from .api import (
    CustomTokenObtainPaisView, create_password_reset_token, reset_password,
    sign_up, social_sign_up)
from .oauth import login_with_google


urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('social-sign-up/', social_sign_up, name='social-sign-up'),

    path("token/", CustomTokenObtainPaisView.as_view(),
         name='token_obtain_pair'),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),

    path("recover-password/", create_password_reset_token,
         name='recover_password'),
    path("reset-password/<uuid:token_id>",
         reset_password, name='reset_password'),

    path("login-with-google/", login_with_google),
]
