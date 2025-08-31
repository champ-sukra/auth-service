from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    user_profile_view,
    update_profile_view,
    change_password_view
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('me/', user_profile_view, name='user_profile'),
    path('me/update/', update_profile_view, name='update_profile'),
    path('me/change-password/', change_password_view, name='change_password'),
]