from django.db import models


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE,
                             related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def writer(self):
        return self.user.nickname

    def is_admin(self):
        return self.user.is_admin


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE,
                             related_name='comments')
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def writer(self):
        return self.user.nickname

    def is_admin(self):
        return self.user.is_admin
