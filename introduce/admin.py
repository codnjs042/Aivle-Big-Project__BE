from django.contrib import admin
from .models import Notice

# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'created_at', 'updated_at']
    list_display_links = ['title', 'content', 'created_at', 'updated_at']

admin.site.register(Notice, NoticeAdmin)