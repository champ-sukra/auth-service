from django.urls import path
from .AuthController import login_view  # Proper sequence diagram structure
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    user_profile_view,
    update_profile_view,
    change_password_view
)

urlpatterns = [
    # Main login endpoint following sequence diagram (AuthController)
    path('login/', login_view, name='login'),

    # Alternative JWT endpoints (for backward compatibility)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Other authentication endpoints
    path('logout/', logout_view, name='logout'),
    path('profile/', user_profile_view, name='user_profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('change-password/', change_password_view, name='change_password'),
]