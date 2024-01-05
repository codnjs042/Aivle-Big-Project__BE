from django.contrib import admin
from .models import *

# Register your models here.
class ShortFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'author_name', 'title', 'file_path']
    list_display_links = ['id', 'title']
    
    def author_name(self, instance):
        return instance.author.nickname
    
admin.site.register(ShortForm, ShortFormAdmin)
