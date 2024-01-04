from django.urls import path
from .views import ShortsView, StreamShortFileView, ShortsListView

urlpatterns = [
    path('', ShortsView.as_view(), name='shorts'),
    path('stream/', StreamShortFileView.as_view(), name='short_stream'),
    path('list/', ShortsListView.as_view(), name='short_list'),
]
