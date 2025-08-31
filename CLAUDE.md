# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Django-based authentication and authorization microservice that provides REST API endpoints for user management, role-based access control (RBAC), and SQL Server integration. This is a backend-only service designed to be consumed by frontend applications.

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

### Current Structure
```
auth-service/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── CLAUDE.md
├── auth-service/           # Main Django project directory
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # Django apps
│   ├── __init__.py
│   ├── authentication/     # JWT auth endpoints & views
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── users/             # User management & RBAC models
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       └── management/commands/create_default_roles.py
├── tests/                 # Test modules
│   ├── __init__.py
│   ├── test_authentication.py
│   └── test_users.py
└── templates/             # Django templates (minimal)
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
USE_SQLITE=True
DB_SERVER=localhost
DB_NAME=auth_db
DB_USER=sa
DB_PASSWORD=your-password
DB_PORT=1433
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=*
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

## Docker Deployment

### Build and Run with Docker
```bash
# Build Docker image
docker build -t auth-service .

# Run container (SQLite)
docker run -p 8000:8000 auth-service

# Run container (SQL Server)
docker run -p 8000:8000 \
  -e USE_SQLITE=False \
  -e DB_SERVER=your-server \
  -e DB_NAME=auth_db \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-pass \
  auth-service
```

## Default Credentials
- **Username:** `admin`
- **Password:** `admin123`  
- **Email:** `admin@example.com`
- **Role:** ADMIN (full permissions)

## Development Notes
- **Backend-only** REST API microservice (no frontend)
- JWT token-based authentication with role claims
- Role-Based Access Control (RBAC) system
- SQL Server primary database with SQLite development fallback
- Docker deployment configuration included
- Comprehensive test coverage for all endpoints
- CORS configured for API consumption by external frontend applications

## Installation & Setup

### Prerequisites
- Python 3.11+
- Virtual environment (already created in `.venv/`)
- For SQL Server: unixODBC driver on macOS (`brew install unixodbc`)

### 1. Install Dependencies
```bash
# Activate virtual environment
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Database Setup (SQLite - Development)
```bash
# Create migrations for users app
python manage.py makemigrations users

# Apply all migrations
python manage.py migrate

# Create default roles and permissions
python manage.py create_default_roles

# Create superuser
python manage.py createsuperuser
# Or use existing: admin/admin123 (already created)
```

### 3. Database Setup (SQL Server - Production)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# USE_SQLITE=False
# DB_SERVER=your-sql-server-host
# DB_NAME=auth_db
# DB_USER=your-username  
# DB_PASSWORD=your-password

# Run migrations on SQL Server
python manage.py migrate
python manage.py create_default_roles
```

### 4. Start the Server
```bash
# Development server
python manage.py runserver

# Or specify host/port
python manage.py runserver 0.0.0.0:8000
```

### 5. Test Installation
```bash
# Run tests
python manage.py test

# Check API endpoints are working
curl http://localhost:8000/api/roles/
# Should return: {"detail":"Authentication credentials were not provided."}
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