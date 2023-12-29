from django.urls import path
from .views import ShortsView, StreamShortFileView

urlpatterns = [
    path('', ShortsView.as_view(), name='shorts'),
    path('stream/', StreamShortFileView.as_view(), name='short_stream'),
]
