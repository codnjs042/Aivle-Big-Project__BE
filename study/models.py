from django.db import models
from korean_romanizer.romanizer import Romanizer
from googletrans import Translator

class Sentence(models.Model):
    title = models.TextField(null=True, blank=True)
    ko_text = models.TextField()
    en_text = models.TextField(null=True, blank=True)
    pronunciation = models.TextField(null=True, blank=True)
    tag = models.CharField(max_length=100, null=True, blank=True)
    
    def trans_eng(self, text):
        translator = Translator()
        trans = translator.translate(text, src='ko', dest='en')
        return trans.text

    def save(self, *args, **kwargs):
        # Check if the Romanizer class requires some text in its __init__ method
        romanizer = Romanizer(self.ko_text)  # Adjust this line based on the Romanizer class

        # Romanize the Korean text
        self.pronunciation = romanizer.romanize()
        self.en_text = self.trans_eng(self.ko_text)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Result(models.Model):
    email = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='results')
    ko_text = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='results')
    PronunProfEval = models.IntegerField()
    FluencyEval = models.IntegerField()
    ComprehendEval = models.IntegerField()

class Bookmark(models.Model):
    email = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='bookmarks')
    ko_text = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='bookmarks')
    is_bookmarked = models.BooleanField(default=False)