from django.urls import path

from user.views import MyTokenBlacklistView, MyTokenObtainPairView, \
    MyTokenRefreshView, MyTokenVerifyView, RegisterView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('refresh/', MyTokenRefreshView.as_view(),
         name='token_refresh'),
    path('verify/', MyTokenVerifyView.as_view(), name='token_verify'),
    path('logout/', MyTokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('signup/', RegisterView.as_view(), name='register'),
]
