from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()


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