from django.core.management.base import BaseCommand
from apps.users.models import Role, Permission, RolePermission


def create_default_roles():
    """Create default roles if they don't exist"""
    # Create ADMIN role
    admin_role, created = Role.objects.get_or_create(
        name='ADMIN',
        defaults={
            'description': 'Full system access',
            'is_active': True
        }
    )
    
    # Create USER role
    user_role, created = Role.objects.get_or_create(
        name='USER',
        defaults={
            'description': 'Standard user access',
            'is_active': True
        }
    )
    
    # Create basic permissions
    permissions_data = [
        ('User Management', 'manage_users', 'Can create, update, and delete users'),
        ('Role Management', 'manage_roles', 'Can create, update, and delete roles'),
        ('View Users', 'view_users', 'Can view user list and details'),
        ('Edit Profile', 'edit_profile', 'Can edit own profile'),
    ]
    
    for name, codename, description in permissions_data:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            defaults={
                'name': name,
                'description': description
            }
        )
    
    # Assign all permissions to ADMIN role
    admin_permissions = Permission.objects.all()
    for permission in admin_permissions:
        RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission
        )
    
    # Assign basic permissions to USER role
    user_permissions = Permission.objects.filter(
        codename__in=['view_users', 'edit_profile']
    )
    for permission in user_permissions:
        RolePermission.objects.get_or_create(
            role=user_role,
            permission=permission
        )


class Command(BaseCommand):
    help = 'Create default roles and permissions'
    
    def handle(self, *args, **options):
        create_default_roles()
        self.stdout.write(
            self.style.SUCCESS('Successfully created default roles and permissions')
        )