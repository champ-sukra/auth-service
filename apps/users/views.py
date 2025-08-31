from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserRole
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, PermissionSerializer, UserRoleSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        return User.objects.prefetch_related('user_roles__role')
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response(
                {'error': 'role_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found or inactive'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )
        
        if created:
            serializer = UserRoleSerializer(user_role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'message': 'Role already assigned to user'}, 
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['delete'])
    def remove_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response(
                {'error': 'role_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id)
            user_role.delete()
            return Response(
                {'message': 'Role removed from user'}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Role assignment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Role.objects.filter(is_active=True)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserRole.objects.select_related('user', 'role', 'assigned_by')