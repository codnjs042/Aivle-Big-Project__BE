from django.urls import path
from .views import ShortsView, StreamShortFileView, ShortsListView, ShortFormView

urlpatterns = [
    path('', ShortsView.as_view(), name='shorts_upload'),
    path('<int:id>/', ShortFormView.as_view(), name='shorts_id'),
    path('stream/', StreamShortFileView.as_view(), name='short_stream'),
    path('list/', ShortsListView.as_view(), name='short_list'),
]
