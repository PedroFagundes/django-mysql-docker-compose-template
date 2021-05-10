from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):

    list_display = ['short_content', 'author', 'updated_at']
    search_fields = ('content', 'author__first_name',
                     'author__last_name', 'author__email')
    ordering = ['-updated_at']


admin.site.register(Post, PostAdmin)
