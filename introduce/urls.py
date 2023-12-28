from django.urls import path
from . import views
from .views import PostListView, PostView

urlpatterns = [
    path('post/', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
]
