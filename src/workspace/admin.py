from django.contrib import admin

from .models import OrganizationType, Workspace, WorkspaceStaff


class StaffInline(admin.TabularInline):
    model = WorkspaceStaff


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    inlines = [
        StaffInline
    ]


admin.site.register(OrganizationType)
admin.site.register(Workspace, WorkspaceAdmin)
