from django.db import models
from shorts.validators import VideoFileValidator
from django.contrib.auth import get_user_model

class ShortForm(models.Model):
    title = models.CharField(max_length=50)  # 제목
    file_path = models.FileField(upload_to='videos/', validators=[VideoFileValidator])  # 영상파일경로
    view = models.IntegerField(default=0)  # 조회수
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='short_forms')
    
    def __str__(self):
        return self.title
    
    @property
    def update_counter(self):
        self.view = self.view + 1
        self.save()