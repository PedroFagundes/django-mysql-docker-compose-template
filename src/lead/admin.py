from django.contrib import admin

from .models import Lead


class LeadAdmin(admin.ModelAdmin):
    list_display = ['email', 'last_interaction', 'created_at', 'updated_at']


admin.site.register(Lead, LeadAdmin)
