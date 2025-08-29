# Auth Service

A Django REST API service for authentication and user management, built with Django REST Framework and JWT authentication.

## Features

- **User Registration & Authentication**: Email-based user registration and login
- **JWT Token Management**: Access and refresh token authentication with token blacklisting
- **Password Reset**: Secure password reset functionality with token-based verification
- **Rate Limiting**: Comprehensive throttling on all endpoints (registration, login, password reset)
- **API Documentation**: Interactive Swagger/OpenAPI and ReDoc documentation
- **Redis Caching**: Redis caching for improved performance
- **Database Flexibility**: Support for SQLite (development) and PostgreSQL (production)
- **Production Ready**: Gunicorn deployment, WhiteNoise static files, environment-based configuration

## Setup Instructions

### Prerequisites

- Python 3.10+
- Redis (for caching)
- PostgreSQL (for production database)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sim-codes/intern-task.git
   cd intern-task
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Running Tests

```bash
python manage.py test users
```

Or use the provided test script:
```bash
./run_tests.sh
```

### API Documentation

Once the server is running, access the API documentation at:
- **Swagger UI**: `http://localhost:8000/api/doc/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | Yes | - | `django-insecure-abc123...` |
| `DEBUG` | Enable/disable debug mode | No | `True` | `False` |
| `REDIS_URL` | Redis connection URL for caching | No | `redis://127.0.0.1:6379/1` | `redis://localhost:6379/1` |
| `DATABASE_URL` | Database connection URL | No | SQLite database | `postgresql://user:pass@localhost:5432/dbname` |

### Database Configuration

- **SQLite (default)**: No additional setup required
  ```env
  DATABASE_URL=sqlite:///db.sqlite3
  ```

- **PostgreSQL**: Set `DATABASE_URL` to your PostgreSQL connection string
  ```env
  DATABASE_URL=postgresql://username:password@localhost:5432/database_name
  ```

### Redis Configuration

Redis is used for caching and password reset token storage. If not configured, the application will work but caching will be disabled and password reset tokens will be stored in memory.

```env
REDIS_URL=redis://127.0.0.1:6379/1
```

## API Endpoints

The API provides the following endpoints under `/api/users/`:

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login (returns JWT tokens)
- `POST /api/users/forgot-password/` - Request password reset
- `POST /api/users/reset-password/` - Reset password with token

### Rate Limiting
- **Registration**: 10 requests per hour per IP
- **Login**: 5 requests per minute per IP
- **Password Reset**: 3 requests per hour per IP
- **Password Reset Confirm**: 10 requests per hour per IP
- **General**: 100 requests per hour for anonymous users, 1000 for authenticated users

## Deployment

Use the provided `build.sh` script for deployment:

```bash
./build.sh
```

This script will:
- Install dependencies
- Collect static files
- Run database migrations
