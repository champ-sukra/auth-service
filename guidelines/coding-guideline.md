# Django Auth Service Coding Guidelines

**ROLE:** You are an expert Django developer applying **Layered Architecture with Service Layer Pattern** using Django & Django REST Framework for authentication and authorization services.

## Technology Stack

* **Framework**: Django 5.x with Django REST Framework (DRF)
* **Authentication**: JWT tokens with django-rest-framework-simplejwt
* **Persistence**: Django ORM (SQLServer)
* **Validation**: Django forms/serializers + DRF validators
* **Architecture**: Layered Architecture with Service Layer Pattern
* **Python Version**: 3.12
---

## Project Structure & Naming Conventions

### Django Apps Architecture (Current Implementation)

```plaintext
auth-service/
├── auth-service/          # Main Django project
│   ├── settings.py        # Configuration
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # WSGI application
├── apps/                 # Django applications
│   ├── authentication/   # Auth logic app
│   │   ├── views.py      # Controllers (API endpoints)
│   │   ├── services.py   # Business logic (use cases)
│   │   ├── serializers.py # DTOs (request/response)
│   │   ├── urls.py       # URL patterns
│   │   └── __init__.py
│   └── users/           # User domain app
│       ├── models.py    # Domain entities (User, Role, Permission)
│       ├── admin.py     # Django admin integration
│       ├── serializers.py # User-specific DTOs
│       └── views.py     # User management controllers
├── tests/               # Test modules
│   ├── test_authentication.py
│   └── test_users.py
└── requirements.txt     # Dependencies
```

### Auth Service Specific Structure

Each Django app follows layered architecture principles:

### File Naming Pattern (Exact Sequence Diagram Match)

**CRITICAL RULE: Each sequence diagram class MUST have its own folder and file structure**

```plaintext
apps/authentication/
├── AuthController/           # AuthController class folder
│   ├── __init__.py          # Export AuthController class
│   └── AuthController.py    # AuthController implementation
├── AuthService/             # AuthService class folder
│   ├── __init__.py          # Export AuthService class
│   └── AuthService.py       # AuthService implementation
├── serializers.py           # LoginRequestSerializer, ErrorResponseSerializer
└── urls.py                  # URL routing

apps/users/
├── UserRepository/          # UserRepository class folder
│   ├── __init__.py          # Export UserRepository class
│   └── UserRepository.py    # UserRepository implementation
├── models.py                # User, Role, Permission, UserRole models
├── serializers.py           # UserProfileSerializer
└── views.py                 # User management controllers
```

**Mandatory Folder/File Structure Rules:**

1. **Each Sequence Diagram Class = Own Folder**
   - Class `AuthController` → Folder `AuthController/`
   - Class `AuthService` → Folder `AuthService/`
   - Class `UserRepository` → Folder `UserRepository/`

2. **File Naming Inside Class Folder**
   - Main file: `{ClassName}/{ClassName}.py`
   - Init file: `{ClassName}/__init__.py` (exports the class)

3. **Import Structure**
   ```python
   # Correct import from class folder
   from apps.authentication.AuthController import AuthController
   from apps.authentication.AuthService import AuthService
   from apps.users.UserRepository import UserRepository

   # NOT from generic file names like:
   # from apps.authentication.controllers import AuthController  # WRONG
   # from apps.authentication.services import AuthService       # WRONG
   ```

**Class Implementation Rules (Exact Sequence Diagram Match):**
* **AuthController**: `login()`, `validateInput()` methods
* **AuthService**: `authenticateUser()`, `validatePassword()`, `generateJWTToken()` methods
* **UserRepository**: `findByIdentifier()`, `getUserRoles()` methods
* **Models**: `User`, `Role`, `Permission` (Django ORM entities)
* **Serializers (DTOs)**:
  * Requests: `LoginRequestSerializer`
  * Responses: `LoginResponseSerializer`, `ErrorResponseSerializer`

---

## Layer Rules & Auth Service Examples

### Model (Entity Layer) - `apps/users/models.py`

* Use Django's `AbstractUser` for custom user models
* Naming: snake_case DB columns, PascalCase class names
* Foreign keys: `models.ForeignKey(..., on_delete=models.CASCADE, related_name=...)`
* Auth-specific relationships: User ↔ Role ↔ Permission

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')
```

### DTO (Serializer Layer) - `apps/authentication/serializers.py`

* Use **DRF Serializers** as DTOs matching OpenAPI schemas
* Authentication-specific validation patterns
* Consistent error response format

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255, help_text="Username or email")
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError({
                "code": "invalid_request",
                "message": "Must include identifier and password."
            })
        return attrs

class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Machine-readable error code")
    message = serializers.CharField(help_text="Human-readable error message")
```

### Repository Layer - `apps/users/repositories.py`

* Encapsulate all database access and ORM queries
* Used by service layer, never called directly from controllers
* Follows exact sequence diagram method names

```python
from django.contrib.auth import get_user_model
from .models import UserRole

User = get_user_model()

class AuthRepository:
    @staticmethod
    def findByIdentifier(identifier: str):
        """Find user by username or email - matches sequence diagram"""
        try:
            if '@' in identifier:
                return User.objects.get(email=identifier)
            else:
                return User.objects.get(username=identifier)
        except User.DoesNotExist:
            return None

    @staticmethod
    def getUserRoles(user):
        """Get user roles - matches sequence diagram"""
        user_roles = UserRole.objects.filter(
            user=user,
            role__is_active=True
        ).select_related('role')
        return [user_role.role.name for user_role in user_roles]
```

### Service Layer - `apps/authentication/services.py`

* Implements business logic following exact sequence diagram flow
* Uses repository layer for data access
* Matches sequence diagram method names

```python
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from apps.users.repositories import AuthRepository

class AuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()

    def authenticateUser(self, identifier: str, password: str):
        """Authenticate user - matches sequence diagram method name"""
        # Step 1: Find user by identifier
        user = self.auth_repository.findByIdentifier(identifier)

        if user is None:
            raise serializers.ValidationError({
                "code": "resource_not_found",
                "message": "No user is found."
            })

        # Step 2: Check user status
        if not user.is_active:
            raise serializers.ValidationError({
                "code": "account_disabled",
                "message": "User's status is inactive."
            })

        # Step 3: Validate password
        if not self.validatePassword(user, password):
            raise serializers.ValidationError({
                "code": "invalid_credentials",
                "message": "Invalid username or password"
            })

        return user

    def validatePassword(self, user, password: str) -> bool:
        """Validate password - matches sequence diagram"""
        return user.check_password(password)

    def generateJWTToken(self, user):
        """Generate JWT token - matches sequence diagram"""
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add custom claims
        access_token['username'] = user.username
        access_token['email'] = user.email

        # Get user roles
        roles = self.auth_repository.getUserRoles(user)
        access_token['roles'] = roles

        return {
            'access_token': str(access_token),
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': roles
            }
        }
```

### Controller Layer - `apps/authentication/controllers.py`

* Matches exact sequence diagram class and method names
* Orchestrates: **validateInput → AuthService.authenticateUser → response**
* Follows sequence diagram flow precisely

```python
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers
from .serializers import LoginRequestSerializer
from .services import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def validateInput(self, request_data):
        """Validate input - matches sequence diagram"""
        serializer = LoginRequestSerializer(data=request_data)
        if not serializer.is_valid():
            raise serializers.ValidationError({
                'code': 'invalid_request',
                'message': 'Invalid input provided.'
            })
        return serializer.validated_data

    def login(self, request):
        """Login method - matches sequence diagram exactly"""
        try:
            # Step 1: Validate input
            validated_data = self.validateInput(request.data)

            # Step 2: Authenticate user
            identifier = validated_data['identifier']
            password = validated_data['password']
            user = self.auth_service.authenticateUser(identifier, password)

            # Step 3: Generate JWT token
            token_data = self.auth_service.generateJWTToken(user)

            # Step 4: Return success response
            return Response({
                'code': 'success',
                'data': token_data
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                'code': 'server_error',
                'message': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Django view wrapper for URL routing
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Django view wrapper - delegates to AuthController"""
    controller = AuthController()
    return controller.login(request)
```

---

## Authentication & Authorization Patterns

### JWT Token Management

```python
# settings.py - JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # 3600 seconds
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Permission Decorators & Classes

```python
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """Custom permission for admin-only endpoints"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.user_roles.filter(role__name='ADMIN').exists()

# Usage in views
@permission_classes([IsAdminUser])
def admin_only_view(request):
    pass
```

### Domain-Based Error Codes

```python
# Authentication domain error codes
AUTH_ERROR_CODES = {
    # REQUEST domain
    'invalid_request': 'Invalid or malformed request data',

    # CREDENTIALS domain
    'invalid_credentials': 'Invalid username or password',
    'unauthorized_access': 'Authentication required',

    # ACCOUNT domain
    'account_disabled': 'User account is disabled',
    'account_expired': 'User account has expired',
    'account_protected': 'Account is protected due to security measures',

    # PROFILE domain
    'duplicate_resource': 'Resource already exists',
    'resource_not_found': 'Resource not found',
    'resource_in_use': 'Resource is currently in use'
}
```

---

## Unit Testing Patterns

### Test Structure

```plaintext
tests/
├── test_authentication.py    # Auth flow tests
├── test_users.py             # User model tests
├── fixtures/                 # Test data
│   ├── users.json
│   └── roles.json
└── __init__.py
```

### Authentication Testing Patterns

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import Role, UserRole

User = get_user_model()

class AuthenticationServiceTest(TestCase):
    """Unit tests for AuthenticationService"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        from apps.authentication.services import AuthenticationService

        user = AuthenticationService.authenticate_user('testuser', 'testpass123')
        self.assertEqual(user, self.user)

    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        from apps.authentication.services import AuthenticationService
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError) as context:
            AuthenticationService.authenticate_user('testuser', 'wrongpass')

        self.assertEqual(context.exception.detail['code'], 'invalid_credentials')

class LoginAPITest(APITestCase):
    """Integration tests for login endpoint"""

    def setUp(self):
        self.login_url = '/auth/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful login"""
        data = {
            'identifier': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'success')
        self.assertIn('access_token', response.data['data'])

    def test_login_invalid_request(self):
        """Test login with missing fields"""
        data = {'identifier': 'testuser'}  # missing password
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_request')

class UserRoleTest(TestCase):
    """Test user role assignments"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.admin_role = Role.objects.create(name='ADMIN', is_active=True)

    def test_user_role_assignment(self):
        """Test assigning role to user"""
        user_role = UserRole.objects.create(user=self.user, role=self.admin_role)

        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.admin_role)
        self.assertTrue(self.user.user_roles.filter(role__name='ADMIN').exists())
```

### Testing Policies (Testable Requirements)

1. **Authentication Flows Must Be Testable**
   - Every authentication endpoint must have unit tests
   - All error scenarios must be covered
   - JWT token generation must be verified

2. **Role-Based Access Control Testing**
   - Permission checks must be unit tested
   - Role assignments must be verified
   - Access denial scenarios must be tested

3. **Data Validation Testing**
   - All serializer validation must be tested
   - Error response format must be consistent
   - Edge cases (empty fields, invalid data) must be covered

4. **Service Layer Testing**
   - Business logic must be isolated and tested
   - Dependencies should be mocked when necessary
   - Error propagation must be verified

---

## OpenAPI Integration

* Use **drf-yasg** for schema generation and documentation
* DTO serializers must align 1:1 with OpenAPI request/response schemas
* Add Swagger decorators for comprehensive API documentation

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    request_body=LoginRequestSerializer,
    responses={
        200: openapi.Response('Login successful', SuccessResponseSerializer),
        400: openapi.Response('Login failed', ErrorResponseSerializer),
    },
    operation_description="Authenticate user with credentials and return JWT token",
)
@api_view(['POST'])
def login_view(request):
    pass
```

---

## Error Handling Standards

* Use DRF exception handler with unified `ErrorResponse` format
* Domain-based error codes for consistent error handling
* Standard HTTP status codes: **200** (success), **400** (client errors), **500** (server errors)

```python
# Standard error response format
{
  "code": "invalid_credentials",
  "message": "Invalid username or password"
}

# Standard success response format
{
  "code": "success",
  "data": {
    "access_token": "eyJ...",
    "user": {...}
  }
}
```

---

## Sequence Diagram Validation Rules

### Mandatory Validation Before Implementation

**ALWAYS validate sequence diagrams before coding. REJECT diagrams that fail these requirements:**

### ✅ Required Elements Checklist

1. **Complete Class Naming**
   - [ ] All classes consistently named throughout diagram
   - [ ] No contradictions (e.g., UserRepository vs AuthRepository)
   - [ ] Class names match intended implementation

2. **Complete Method Definitions**
   - [ ] All method names clearly specified
   - [ ] Method parameters shown where critical
   - [ ] Return values indicated for complex flows
   - [ ] Self-calls properly documented

3. **Business Logic Completeness**
   - [ ] All required business operations shown
   - [ ] Authentication flow includes role/permission retrieval
   - [ ] JWT token generation includes all required claims
   - [ ] Error scenarios cover all domain error codes

4. **Response Flow Clarity**
   - [ ] Clear indication of which class handles client responses
   - [ ] Consistent response format throughout
   - [ ] Error responses properly attributed to correct layer

### ❌ Rejection Criteria

**STOP IMPLEMENTATION and request diagram revision if ANY of these are found:**

1. **Class Inconsistencies**
   - Different class names used for same entity (UserRepository vs AuthRepository)
   - Missing class definitions for referenced objects
   - Ambiguous class responsibilities

2. **Incomplete Method Specifications**
   - Critical methods missing parameters
   - Unclear method return values
   - Self-calls without implementation details

3. **Missing Business Logic**
   - Authentication without role/permission handling
   - JWT generation without required claims
   - Incomplete error handling coverage

4. **Response Flow Ambiguity**
   - Unclear which layer returns responses to client
   - Inconsistent error response handling
   - Missing controller orchestration

### 🔄 Rejection Process

When rejecting a sequence diagram:

1. **Document specific issues** found using the checklist above
2. **List missing elements** that prevent implementation
3. **Provide clear requirements** for diagram revision
4. **DO NOT PROCEED** with coding until diagram is fixed

### Example Rejection Response

```
SEQUENCE DIAGRAM REJECTED: Critical inconsistencies found

Issues identified:
- Line 17: Uses 'UserRepository' but should be consistent with 'AuthRepository'
- Missing 'getUserRoles' method call required for JWT token generation
- Unclear response handling - AuthController should orchestrate all client responses
- validatePassword method lacks parameter specification

Required fixes:
- Standardize repository naming throughout diagram
- Add getUserRoles method call in JWT generation flow
- Clarify AuthController response handling responsibility
- Add method parameters for critical operations

Cannot proceed with implementation until these issues are resolved.
```

---

## Development Rules (Auth Service Specific)

### Core Principles

1. **Sequence Diagram First** → Validate and follow sequence diagrams exactly
2. **OpenAPI First** → Serializers must exactly match OpenAPI schemas
3. **Layered Architecture** → Clear separation between presentation, business, and data layers
4. **Service Layer Pattern** → Business logic encapsulated in service classes
5. **Domain-Based Organization** → Use domain-based error codes and logical grouping
6. **Authentication Security** → Follow JWT best practices and secure token handling

### Implementation Rules

1. **Layer Separation**
   - **Presentation Layer (Views)**: Handle HTTP request/response, orchestrate service calls
   - **Service Layer**: Encapsulate business logic and authentication workflows
   - **Data Layer (Models)**: Django ORM entities with database relationships
   - **DTO Layer (Serializers)**: Data transfer objects matching OpenAPI specifications

2. **Authentication Patterns**
   - Use `@permission_classes([permissions.AllowAny])` for public endpoints
   - Use custom permission classes for role-based access
   - Always validate JWT tokens in protected endpoints
   - Handle authentication errors with domain-specific error codes

3. **Error Handling**
   - Use domain-based error codes: `invalid_request`, `invalid_credentials`, `account_disabled`, etc.
   - Return consistent error format: `{"code": "error_code", "message": "description"}`
   - Use `serializers.ValidationError` for business logic errors
   - Map all client errors to **400**, server errors to **500**

4. **Testing Requirements**
   - Every authentication endpoint must have unit tests
   - Test both success and failure scenarios
   - Mock external dependencies in service tests
   - Use `APITestCase` for integration tests

5. **Security Standards**
   - Never log sensitive data (passwords, tokens)
   - Use secure password validation
   - Implement proper token expiration
   - Follow OWASP authentication guidelines

6. **Code Quality**
   - Use type hints for all service methods
   - Add docstrings for complex business logic
   - Follow PEP 8 naming conventions
   - Keep methods focused and testable

### Auth Service File Organization

```python
# apps/authentication/views.py - Controllers only
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    # Validate → Service → Response

# apps/authentication/services.py - Business logic
class AuthenticationService:
    @staticmethod
    def authenticate_user(identifier: str, password: str) -> User:
        # Authentication business logic

# apps/authentication/serializers.py - DTOs
class LoginRequestSerializer(serializers.Serializer):
    # Matches OpenAPI LoginRequest schema exactly

# apps/users/models.py - Domain entities
class User(AbstractUser):
    # Domain model with business relationships
```

---

## Quick Reference

### Standard Response Patterns

```python
# Success Response
return Response({
    'code': 'success',
    'data': {...}
}, status=status.HTTP_200_OK)

# Error Response
return Response({
    'code': 'invalid_credentials',
    'message': 'Invalid username or password'
}, status=status.HTTP_400_BAD_REQUEST)
```

### Authentication Flow

```python
# 1. Validate input (serializer)
# 2. Authenticate user (service)
# 3. Generate JWT token (service)
# 4. Return success response (view)
```

This guideline ensures consistent, secure, and maintainable authentication service development following layered architecture with service layer patterns.