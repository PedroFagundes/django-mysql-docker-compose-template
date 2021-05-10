from django.db import models
from django.utils.translation import ugettext_lazy as _


class Lead(models.Model):
    """Model definition for Lead."""

    email = models.EmailField(_('email'), max_length=256, unique=True)
    last_interaction = models.CharField(
        _('last interaction'), max_length=50, default='step-1')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        """Meta definition for Lead."""

        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        """Unicode representation of Lead."""
        return self.email
