import uuid

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .utils import generate_random_code


class OrganizationType(models.Model):
    """Model definition for OrganizationType."""

    name = models.CharField(_('name'), max_length=50)
    is_active = models.BooleanField(_('is active'), default=True)

    created_at = models.DateTimeField(
        _('created at'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for OrganizationType."""

        verbose_name = 'Organization type'
        verbose_name_plural = 'Organization types'
        db_table = 'organization_type'

    def __str__(self):
        """Unicode representation of OrganizationType."""
        return self.name


class Workspace(models.Model):
    """Model definition for Workspace."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=50, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              verbose_name=_('owner'), blank=True, null=True,
                              on_delete=models.CASCADE)
    organization_type = models.ForeignKey(
        OrganizationType, verbose_name=_('organization type'), max_length=50,
        on_delete=models.SET_NULL, blank=True, null=True)
    country = models.CharField(_('country'), max_length=64, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=64, blank=True)
    timezone = models.CharField(_('timezone'), max_length=50, blank=True)

    created_at = models.DateTimeField(
        _('created at'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for Workspace."""

        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
        db_table = 'workspace'

    def __str__(self):
        """Unicode representation of Workspace."""
        return self.name


class WorkspaceStaff(models.Model):
    """Model definition for WorkspaceStaff."""

    COACH = 'C'
    ASSISTANT = 'A'
    STAFF_ROLE_OPTIONS = (
        (COACH, 'Coach'),
        (ASSISTANT, 'Assistant'),
    )

    workspace = models.OneToOneField(
        Workspace, related_name='workspace_staff', on_delete=models.CASCADE,
        primary_key=True, verbose_name=_('workspace'))
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    role = models.CharField(_('role'), max_length=1,
                            choices=STAFF_ROLE_OPTIONS)
    created_at = models.DateTimeField(
        _('created at'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for WorkspaceStaff."""

        verbose_name = 'WorkspaceStaff'
        verbose_name_plural = 'WorkspaceStaffs'
        db_table = 'workspace_staff'
        unique_together = (('workspace', 'user'),)

    def __str__(self):
        """Unicode representation of WorkspaceStaff."""
        return self.user.email


class WorkspaceAthlete(models.Model):
    """Model definition for WorkspaceAthlete."""

    workspace = models.OneToOneField(
        Workspace, related_name='workspace_athletes', on_delete=models.CASCADE,
        primary_key=True, unique=True, verbose_name=_('workspace'))
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    created_at = models.DateTimeField(
        _('created at'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, auto_now_add=False)

    class Meta:
        """Meta definition for WorkspaceAthlete."""

        verbose_name = 'WorkspaceAthlete'
        verbose_name_plural = 'WorkspaceAthletes'
        db_table = 'workspace_athlete'
        unique_together = (('workspace', 'user'),)

    def __str__(self):
        """Unicode representation of WorkspaceAthlete."""
        return self.user.email


class StaffInvitation(models.Model):
    """Model definition for StaffInvitation."""

    code = models.CharField(_('code'), max_length=32,
                            default=generate_random_code, unique=True,
                            primary_key=True)
    email = models.EmailField(_('email'), max_length=256)
    created_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL,
        null=True, verbose_name=_('created by'))
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, verbose_name=_('workspace'))

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        """Meta definition for StaffInvitation."""

        verbose_name = 'Staff Invitation'
        verbose_name_plural = 'Staff Invitations'
        db_table = 'staff_invitation'

    def __str__(self):
        """Unicode representation of StaffInvitation."""
        return f'{self.email} invited to {self.workspace.name}'

    @property
    def is_valid(self):
        return (self.created_at + timedelta(hours=24)) > timezone.now()
