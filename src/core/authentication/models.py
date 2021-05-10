import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords
from django.template.loader import render_to_string
from django.conf import settings

from core.mediators.mail import Mail

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Model definition for User."""

    id = models.UUIDField(_('id'), unique=True,
                          primary_key=True, default=uuid.uuid4)
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(_('password'), max_length=128, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_superuser = models.BooleanField(_('superuser'), default=False)
    avatar = models.ImageField(
        _('avatar'), upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True)
    country = models.CharField(_('country'), max_length=64, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=64, blank=True)
    timezone = models.CharField(_('timezone'), max_length=50, blank=True)

    verified_email = models.BooleanField(_('verified email'), default=False)

    mail = Mail

    history = HistoricalRecords()

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        """Meta definition for User."""

        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'user'

    def __str__(self):
        """Unicode representation of User."""
        return self.email

    def get_default_workspace_id(self):
        if self.is_superuser:
            return None

        workspace = self.workspace_set.order_by('created_at').first()

        if workspace:
            return str(workspace.id)

        return None

    def generate_jwt_token(self, workspace_id: str = None) -> dict:
        """
        Generates a JWT token for the User instance. If a workspace_id is not
        passed, the 'get_default_workspace_id' is called to set a default one.
        """

        from .serializers import CustomTokenObtainPairSerializer

        self.workspace_id = workspace_id

        if not workspace_id:
            default_workspace_id = self.get_default_workspace_id()

            if not default_workspace_id:
                raise Exception("User doesn't belong to any Workspace")

            self.workspace_id = str(default_workspace_id)

        refresh = CustomTokenObtainPairSerializer.get_token(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def send_verification_email(self):
        from .tokens import token_generator

        verification_token = token_generator.make_token(self)

        email_context = {
            'user': self,
            'url': (f'{settings.FRONTEND_URL}/panel/verify-email'
                    f'/{verification_token}')
        }

        email_template = render_to_string(
            'email/verify-email.html', email_context)

        self.mail.send_email(
            subject='Welcome to HelloTeam!',
            recipient_list=[self.email], html_message=email_template)


class PasswordResetToken(models.Model):
    """Model definition for PasswordResetToken."""

    id = models.UUIDField(_('id'), unique=True,
                          primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, verbose_name=_(
        'user'), on_delete=models.CASCADE)
    valid_through = models.DateTimeField(_('valid through'), blank=True)

    class Meta:
        """Meta definition for PasswordResetToken."""

        verbose_name = 'PasswordResetToken'
        verbose_name_plural = 'PasswordResetTokens'
        db_table = 'password_recover_token'

    def __str__(self):
        """Unicode representation of PasswordResetToken."""
        return self.user.email
