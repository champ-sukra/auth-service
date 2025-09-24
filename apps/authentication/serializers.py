from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        max_length=255,
        help_text="Username or email address"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError(
                {"code": "invalid_request", "message": "Must include identifier and password."},
                code='invalid_request'
            )

        # Try to find user by username or email
        user = None
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"code": "invalid_credentials", "message": "Invalid username or password"},
                code='invalid_credentials'
            )

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                {"code": "account_disabled", "message": "User's status is inactive."},
                code='account_disabled'
            )

        # Authenticate user
        if user.check_password(password):
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                {"code": "invalid_credentials", "message": "Invalid username or password"},
                code='invalid_credentials'
            )

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        
        # Add user roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles = [user_role.role.name for user_role in user_roles if user_role.role.is_active]
        token['roles'] = roles
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        # Add user roles
        user_roles = UserRole.objects.filter(user=self.user).select_related('role')
        data['user']['roles'] = [
            user_role.role.name for user_role in user_roles 
            if user_role.role.is_active
        ]
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'roles', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        return [user_role.role.name for user_role in user_roles if user_role.role.is_active]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Machine-readable error code")
    message = serializers.CharField(help_text="Human-readable error message")


class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(help_text="JWT access token")
    token_type = serializers.CharField(default="Bearer", help_text="Token type")
    expires_in = serializers.IntegerField(help_text="Token expiration time in seconds")
    user = serializers.DictField(help_text="User information")


class SuccessResponseSerializer(serializers.Serializer):
    code = serializers.CharField(default="success", help_text="Success code")
    data = serializers.JSONField(help_text="Response data")