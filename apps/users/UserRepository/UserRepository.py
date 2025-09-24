from django.contrib.auth import get_user_model
from ..models import UserRole

User = get_user_model()


class UserRepository:
    """
    User Repository - matches sequence diagram exactly

    Handles user data operations as called from AuthService:
    AuthService -> UserRepository: findByIdentifier
    UserRepository --> AuthService: user
    """

    @staticmethod
    def findByIdentifier(identifier: str):
        """
        Find user by username or email - matches sequence diagram method name exactly

        Called from sequence diagram:
        AuthService -> UserRepository: findByIdentifier

        Args:
            identifier: Username or email address

        Returns:
            User object if found, None if not found (matches "user == null" check in diagram)
        """
        try:
            if '@' in identifier:
                return User.objects.get(email=identifier)
            else:
                return User.objects.get(username=identifier)
        except User.DoesNotExist:
            # Return None to match sequence diagram "user == null" condition
            return None

    @staticmethod
    def getUserRoles(user):
        """
        Get user roles - supporting method for JWT token generation

        Args:
            user: User object

        Returns:
            List of role names (strings)
        """
        if user is None:
            return []

        user_roles = UserRole.objects.filter(
            user=user,
            role__is_active=True
        ).select_related('role')
        return [user_role.role.name for user_role in user_roles]

    @staticmethod
    def getUserById(user_id: int):
        """
        Get user by ID - supporting method

        Args:
            user_id: User primary key

        Returns:
            User object if found, None if not found
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def isUserActive(user):
        """
        Check if user is active - supporting method

        Args:
            user: User object

        Returns:
            Boolean indicating if user is active
        """
        return user.is_active if user else False