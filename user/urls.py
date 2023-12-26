from django.urls import path

from user.views import MyTokenBlacklistView, MyTokenObtainPairView, \
    MyTokenRefreshView, RegisterView, UserInfoView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('refresh/', MyTokenRefreshView.as_view(),
         name='token_refresh'),
    path('logout/', MyTokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('info/', UserInfoView.as_view(), name='user_info'),
    path('signup/', RegisterView.as_view(), name='register'),
]
