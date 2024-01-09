from django.urls import path
from . import views
from .views import CommentView, PostListView, PostView

urlpatterns = [
    path('post/', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
    path('post/<int:pk>/comment/', CommentView.as_view(), name='comment'),
]
