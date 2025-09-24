from django.urls import path
from .views import (
    login_view,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    user_profile_view,
    update_profile_view,
    change_password_view
)

urlpatterns = [
    # Main login endpoint following OpenAPI specification
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