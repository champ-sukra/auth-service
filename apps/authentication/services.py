from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from apps.users.models import UserRole
from datetime import timedelta
from django.conf import settings

User = get_user_model()


class AuthenticationService:
    """
    Service layer for authentication operations following the sequence diagram flow
    """

    @staticmethod
    def validate_input(identifier, password):
        """
        Validate login input data
        Returns: True if valid, raises ValidationError if invalid
        """
        if not identifier or not password:
            raise serializers.ValidationError({
                "code": "invalid_request",
                "message": "Must include identifier and password."
            })
        return True

    @staticmethod
    def authenticate_user(identifier, password):
        """
        Authenticate user by identifier (username or email) and password
        Returns: User object if successful, raises ValidationError if failed
        """
        # Find user by identifier
        user = AuthenticationService.find_user_by_identifier(identifier)

        # Check user status
        if not user.is_active:
            raise serializers.ValidationError({
                "code": "account_disabled",
                "message": "User's status is inactive."
            })

        # Validate password
        if not AuthenticationService.validate_password(user, password):
            raise serializers.ValidationError({
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            })

        return user

    @staticmethod
    def find_user_by_identifier(identifier):
        """
        Find user by username or email
        Returns: User object if found, raises ValidationError if not found
        """
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            })

    @staticmethod
    def validate_password(user, password):
        """
        Validate user password
        Returns: True if valid, False if invalid
        """
        return user.check_password(password)

    @staticmethod
    def generate_jwt_token(user):
        """
        Generate JWT token for authenticated user
        Returns: dict with access_token, token_type, expires_in
        """
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add custom claims
        access_token['username'] = user.username
        access_token['email'] = user.email

        # Add user roles
        user_roles = AuthenticationService.get_user_roles(user)
        access_token['roles'] = user_roles

        # Get token expiration time from settings
        expires_in = getattr(settings, 'SIMPLE_JWT', {}).get(
            'ACCESS_TOKEN_LIFETIME',
            timedelta(hours=1)
        ).total_seconds()

        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': int(expires_in)
        }

    @staticmethod
    def get_user_roles(user):
        """
        Get user roles for JWT token
        Returns: list of role names
        """
        user_roles = UserRole.objects.filter(
            user=user,
            role__is_active=True
        ).select_related('role')
        return [user_role.role.name for user_role in user_roles]

    @staticmethod
    def format_user_response(user, roles=None):
        """
        Format user data for response
        Returns: dict with user information
        """
        if roles is None:
            roles = AuthenticationService.get_user_roles(user)

        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'roles': roles
        }

    @staticmethod
    def login(identifier, password):
        """
        Complete login flow following sequence diagram
        Returns: dict with success response format
        """
        # Step 1: Validate input
        AuthenticationService.validate_input(identifier, password)

        # Step 2: Authenticate user
        user = AuthenticationService.authenticate_user(identifier, password)

        # Step 3: Generate JWT token
        token_data = AuthenticationService.generate_jwt_token(user)

        # Step 4: Get user roles (already included in token generation)
        user_roles = AuthenticationService.get_user_roles(user)

        # Step 5: Format response
        return {
            'code': 'success',
            'data': {
                'access_token': token_data['access_token'],
                'token_type': token_data['token_type'],
                'expires_in': token_data['expires_in'],
                'user': AuthenticationService.format_user_response(user, user_roles)
            }
        }