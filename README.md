# Django AuthService

## Project Overview
This is a Django-based authentication and authorization microservice that provides REST API endpoints for user management, role-based access control (RBAC), and SQL Server integration.

## Project Structure

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
│   └── users/             # User management & RBAC models
├── tests/                 # Test modules
└── templates/             # Django templates (minimal)
```

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
# Create migrations
python manage.py makemigrations users

# Apply migrations
python manage.py migrate

# Create default roles and permissions
python manage.py create_default_roles

# Create superuser (or use admin/admin123)
python manage.py createsuperuser
```

### 3. Database Setup (SQL Server - Production)
```bash
# Copy environment template and configure
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

### 4. Run the Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login with JWT tokens
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - Logout (blacklist token)
- `GET /api/auth/me/` - Get current user profile
- `PUT /api/auth/me/update/` - Update user profile
- `POST /api/auth/me/change-password/` - Change password

### User Management
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `POST /api/users/{id}/assign_role/` - Assign role to user
- `DELETE /api/users/{id}/remove_role/` - Remove role from user

### Roles & Permissions
- `GET /api/roles/` - List roles
- `GET /api/permissions/` - List permissions
- `GET /api/user-roles/` - List user-role assignments

## Default Credentials
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@example.com`
- **Role:** ADMIN (full system access)

## Docker Deployment

```bash
# Build image
docker build -t auth-service .

# Run with SQLite
docker run -p 8000:8000 auth-service

# Run with SQL Server
docker run -p 8000:8000 \
  -e USE_SQLITE=False \
  -e DB_SERVER=your-server \
  -e DB_NAME=auth_db \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-pass \
  auth-service
```

## Testing

```bash
# Run test suite
python manage.py test

# Test API is working
curl http://localhost:8000/api/auth/login/
```

## Features

- ✅ JWT Authentication with role-based claims
- ✅ Role-Based Access Control (RBAC)
- ✅ SQL Server integration with SQLite fallback
- ✅ Complete user management API
- ✅ Docker deployment ready
- ✅ Comprehensive test coverage
- ✅ Admin interface included