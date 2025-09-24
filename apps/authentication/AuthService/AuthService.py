from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from datetime import timedelta
from django.conf import settings
from apps.users.UserRepository import UserRepository

User = get_user_model()


class AuthService:
    """
    Authentication Service - matches sequence diagram exactly

    Flow from sequence diagram:
    AuthController -> AuthService: authenticateUser
    AuthService -> UserRepository: findByIdentifier
    AuthService -> AuthService: validatePassword
    AuthService -> AuthService: generateJWTToken
    AuthController <-- AuthService: (final result)
    """

    def authenticateUser(self, identifier: str, password: str):
        """
        Authenticate user - matches sequence diagram method name exactly

        This method handles the complete authentication flow as shown in diagram:
        1. AuthService -> UserRepository: findByIdentifier
        2. Check user == null condition
        3. Check user's status == inactive condition
        4. AuthService -> AuthService: validatePassword
        5. AuthService -> AuthService: generateJWTToken
        6. Return to AuthController

        Returns: Complete LoginResponse data
        """
        # Step 1: AuthService -> UserRepository: findByIdentifier
        user_repository = UserRepository()
        user = user_repository.findByIdentifier(identifier)

        # Step 2: Check user == null (sequence diagram condition)
        if user is None:
            # Direct client response as shown in diagram
            raise serializers.ValidationError({
                "code": "resource_not_found",
                "message": "No user is found."
            })

        # Step 3: Check user's status == inactive (sequence diagram condition)
        if not user.is_active:
            # Direct client response as shown in diagram
            raise serializers.ValidationError({
                "code": "account_disabled",
                "message": "User's status is inactive."
            })

        # Step 4: AuthService -> AuthService: validatePassword
        if not self.validatePassword(user, password):
            # Direct client response as shown in diagram
            raise serializers.ValidationError({
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            })

        # Step 5: AuthService -> AuthService: generateJWTToken
        token_data = self.generateJWTToken(user)

        # Step 6: Return complete LoginResponse to AuthController
        return token_data

    def validatePassword(self, user, password: str) -> bool:
        """
        Validate password - matches sequence diagram self-call

        This is a self-call as shown in the sequence diagram:
        AuthService -> AuthService: validatePassword
        """
        return user.check_password(password)

    def generateJWTToken(self, user):
        """
        Generate JWT token - matches sequence diagram self-call

        This is a self-call as shown in the sequence diagram:
        AuthService -> AuthService: generateJWTToken

        Returns: LoginResponse data structure
        """
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add custom claims
        access_token['username'] = user.username
        access_token['email'] = user.email

        # Get token expiration time from settings
        expires_in = getattr(settings, 'SIMPLE_JWT', {}).get(
            'ACCESS_TOKEN_LIFETIME',
            timedelta(hours=1)
        ).total_seconds()

        # Return LoginResponse structure matching OpenAPI schema
        return {
            'access_token': str(access_token),
            'token_type': 'Bearer',
            'expires_in': int(expires_in),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'fullname': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        }