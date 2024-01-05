from django.contrib import admin
from .models import *

# Register your models here.
class SentenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'ko_text', 'en_text', 'pronunciation','tag']#, 'Gtag', 'Atag']
    list_display_links = ['title','ko_text', 'en_text', 'pronunciation','tag']#, 'Gtag', 'Atag']

class ResultAdmin(admin.ModelAdmin):
    list_display = ['email','ko_text','PronunProfEval', 'FluencyEval', 'ComprehendEval']
    list_display_links = ['email','ko_text','PronunProfEval', 'FluencyEval', 'ComprehendEval']

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['email','ko_text', 'is_bookmarked']
    list_display_links = ['email','ko_text', 'is_bookmarked']

class AudioAdmin(admin.ModelAdmin):
    list_display = ['email', 'ko_text','audio_path']
    list_display_links = ['email', 'ko_text','audio_path']

admin.site.register(Sentence, SentenceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(AudioFile, AudioAdmin)