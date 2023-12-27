from django.urls import path
from . import views

urlpatterns = [
    path('notice/', views.notice_list, name='notice_list'),
    path('notice/<int:pk>/', views.notice, name='notice'),
]
