from django.contrib import admin
from .models import *

# Register your models here.
class ShortFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'file_path']
    list_display_links = ['id', 'title']
    
admin.site.register(ShortForm, ShortFormAdmin)
