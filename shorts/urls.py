from django.urls import path
from .views import UploadShortsView

urlpatterns = [
    path('upload/', UploadShortsView.as_view(), name='short_upload'),
]
