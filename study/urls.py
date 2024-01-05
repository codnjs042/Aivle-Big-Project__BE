from django.urls import path
from .views import *

urlpatterns = [
    path('sentence/', SentencesListView.as_view(), name='sentence_list'),
    path('sentence/<int:pk>/', SentenceView.as_view(), name='sentence'),
    path('sentence/<int:pk>/result', ResultView.as_view(), name='result'),
    path('bookmark/', BookmarkView.as_view(), name='bookmart'),
    path('aireport/', AIReportView.as_view(), name='aireport'),
]