from django.contrib import admin
from .models import *

# Register your models here.
class SentenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'ko_text', 'en_text', 'pronunciation','tag']#, 'Gtag', 'Atag']
    list_display_links = ['id', 'title','ko_text', 'en_text', 'pronunciation','tag']#, 'Gtag', 'Atag']

class ResultAdmin(admin.ModelAdmin):
    list_display = ['email','sentence','PronunProfEval', 'FluencyEval', 'ComprehendEval']
    list_display_links = ['email','sentence','PronunProfEval', 'FluencyEval', 'ComprehendEval']

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['email','sentence', 'is_bookmarked']
    list_display_links = ['email','sentence', 'is_bookmarked']

class AudioAdmin(admin.ModelAdmin):
    list_display = ['email', 'sentence','audio_path']
    list_display_links = ['email', 'sentence','audio_path']

admin.site.register(Sentence, SentenceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(AudioFile, AudioAdmin)