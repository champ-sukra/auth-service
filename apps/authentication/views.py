from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .serializers import (
    LoginRequestSerializer, CustomTokenObtainPairSerializer,
    UserProfileSerializer, ChangePasswordSerializer,
    ErrorResponseSerializer, SuccessResponseSerializer
)
from .services import AuthenticationService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=LoginRequestSerializer,
    responses={
        200: openapi.Response('Login successful', SuccessResponseSerializer),
        400: openapi.Response('Login failed', ErrorResponseSerializer),
        500: openapi.Response('Server error', ErrorResponseSerializer),
    },
    operation_description="Authenticate user with credentials and return JWT token",
    operation_id="login"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User Login endpoint following the sequence diagram flow:
    1. Validate input
    2. Authenticate user
    3. Generate JWT token
    4. Return success response
    """
    try:
        # Parse and validate request data
        serializer = LoginRequestSerializer(data=request.data)

        if not serializer.is_valid():
            # Return validation errors in standard format
            errors = serializer.errors
            if 'non_field_errors' in errors:
                error_data = errors['non_field_errors'][0]
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'code': 'invalid_request',
                    'message': 'Invalid input provided.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        # Use authentication service for login flow
        response_data = AuthenticationService.login(identifier, password)

        return Response(response_data, status=status.HTTP_200_OK)

    except serializers.ValidationError as e:
        # Handle validation errors from service layer
        if hasattr(e, 'detail') and isinstance(e.detail, dict):
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'code': 'invalid_request',
                'message': 'Invalid request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle unexpected errors
        return Response({
            'code': 'server_error',
            'message': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except TokenError as e:
            return Response(
                {'error': 'Invalid or expired refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except InvalidToken as e:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={}
    ),
    responses={
        200: openapi.Response('Logout successful', SuccessResponseSerializer),
        400: openapi.Response('Logout failed', ErrorResponseSerializer),
    },
    operation_description="Invalidate JWT token and logout user",
    operation_id="logout"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User Logout endpoint - invalidates JWT token
    """
    try:
        # For JWT-only implementation, we don't need to blacklist tokens
        # The frontend should discard the token
        return Response({
            'code': 'success',
            'data': {}
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'code': 'invalid_request',
            'message': 'An error occurred during logout'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_view(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    serializer = UserProfileSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'}, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)