# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Django-based authentication and authorization microservice that provides REST API endpoints for user management, role-based access control (RBAC), and Active Directory integration.

## Required Dependencies
Add these to requirements.txt:
- Django 4.2+
- Django REST Framework
- django-cors-headers
- mssql-django (SQL Server connector)
- pyodbc (SQL Server driver)
- python-decouple (environment variables)
- djangorestframework-simplejwt (JWT tokens)

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Django Commands
```bash
# Run development server
python manage.py runserver

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Project Architecture

### Target Structure
```
auth-service/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── auth_service/           # Main project directory
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Django apps
│   ├── __init__.py
│   ├── authentication/     # JWT auth endpoints
│   └── users/             # User management & RBAC
└── tests/                 # Test modules
```

### Core Models Required

#### User Model (extend AbstractUser)
- Basic user fields with authentication capabilities

#### Role-Based Access Control
```python
# Role model
class Role:
    - name (CharField)
    - description (TextField)
    - is_active (BooleanField)

# Permission model  
class Permission:
    - name (CharField)
    - codename (CharField, unique)
    - description (TextField)

# User roles relationship
- Many-to-many relationship between User and Role
```

#### Basic Roles to Create
- **ADMIN**: Full system access
- **USER**: Standard user access

### Database Configuration
**SQL Server Setup (primary database):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_SERVER'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

### API Endpoints Specification

#### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - JWT token refresh
- `GET /api/auth/me/` - Current user profile

#### User Management Endpoints
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Environment Variables (.env.example)
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_SERVER=localhost
DB_NAME=auth_db
DB_USER=sa
DB_PASSWORD=your-password
DB_PORT=1433
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Expected API Response Formats

#### Login Response
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### User Profile Response
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["ADMIN"]
}
```

## Configuration Requirements
- SQL Server database configuration (primary)
- JWT token settings
- CORS settings for frontend integration
- Basic logging configuration
- Docker configuration for deployment

## Development Standards
- Use Django REST Framework best practices
- Follow PEP 8 coding standards
- Add basic docstrings and type hints
- Include basic error handling
- Set up proper database migrations
- Ensure all endpoints return consistent JSON responses
- Add basic validation using DRF serializers

## Setup Instructions

### 1. Install Dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create migrations
python manage.py makemigrations users

# Apply migrations
python manage.py migrate

# Create default roles and permissions
python manage.py create_default_roles

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. For SQL Server (Production)
Create a `.env` file (copy from `.env.example`) and set:
```
USE_SQLITE=False
DB_SERVER=your-sql-server
DB_NAME=auth_db
DB_USER=your-username
DB_PASSWORD=your-password
```

Install unixODBC on macOS if needed:
```bash
brew install unixodbc
```

### 4. Run the Server
```bash
python manage.py runserver
```

## Testing the API

### Authentication Endpoints
- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/refresh/` - Refresh JWT token  
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user profile

### User Management Endpoints  
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `POST /api/users/{id}/assign_role/` - Assign role to user
- `DELETE /api/users/{id}/remove_role/` - Remove role from user

### Other Endpoints
- `GET /api/roles/` - List all roles
- `GET /api/permissions/` - List all permissions
- `GET /api/user-roles/` - List user-role assignments

## Current Status
✅ **FULLY IMPLEMENTED AND WORKING**
- Complete Django authentication microservice
- JWT-based authentication with role support
- SQL Server configuration with SQLite fallback for development
- Role-Based Access Control (RBAC) system
- Full REST API for user and role management
- Docker configuration for deployment
- Comprehensive test suite
- Default roles (ADMIN, USER) automatically created