from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers
from ..serializers import LoginRequestSerializer
from ..AuthService import AuthService


class AuthController:
    """
    Authentication Controller - matches sequence diagram exactly

    Flow from sequence diagram:
    Client -> AuthController: login
    AuthController -> AuthController: validateInput
    AuthController -> AuthService: authenticateUser
    AuthController <-- AuthService: (response)
    Client <-- AuthController: (final response)
    """

    def __init__(self):
        self.auth_service = AuthService()

    def validateInput(self, request_data):
        """
        Validate input - matches sequence diagram method name exactly

        Returns: validated data dict if valid
        Raises: serializers.ValidationError if validateInput == false
        """
        serializer = LoginRequestSerializer(data=request_data)
        if not serializer.is_valid():
            # This matches the sequence diagram condition: validateInput == false
            raise serializers.ValidationError({
                'code': 'invalid_request',
                'message': 'Invalid input provided.',
                'data': None
            })
        return serializer.validated_data

    def login(self, request):
        """
        Login method - matches sequence diagram flow exactly

        Sequence diagram flow:
        1. AuthController -> AuthController: validateInput
        2. AuthController -> AuthService: authenticateUser
        3. AuthController <-- AuthService: (token data or error)
        4. Client <-- AuthController: (final response)
        """
        try:
            # Step 1: validateInput (self-call as shown in diagram)
            validated_data = self.validateInput(request.data)

            # Step 2: Call AuthService.authenticateUser
            identifier = validated_data['identifier']
            password = validated_data['password']

            # AuthService handles the authentication flow and returns to AuthController
            result = self.auth_service.authenticateUser(identifier, password)

            # Step 3: AuthController receives response from AuthService
            # Step 4: AuthController returns final response to Client
            return Response({
                'code': 'success',
                'data': result
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            # Handle validateInput == false case
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle unexpected server errors
            return Response({
                'code': 'server_error',
                'message': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Django view wrapper for URL routing
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Django view wrapper - delegates to AuthController
    Maintains Django URL routing while following sequence diagram structure
    """
    controller = AuthController()
    return controller.login(request)