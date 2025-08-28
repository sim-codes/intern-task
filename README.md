# Auth Service

A Django REST API service for authentication and user management, built with Django REST Framework and JWT authentication.

## Features

- User registration and authentication
- JWT token-based authentication
- Password reset functionality
- User profile management
- Rate limiting and throttling
- API documentation with Swagger/OpenAPI
- Redis caching support
- PostgreSQL/SQLite database support

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis (optional, for caching)
- PostgreSQL (optional, for production database)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sim-codes/intern-task.git
   cd intern-task
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   Create a `.env` file in the project root with the following variables:

   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   REDIS_URL=redis://127.0.0.1:6379/1
   DATABASE_URL=sqlite:///db.sqlite3
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

The API will be available at `http://localhost:8000`

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
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | Yes | - |
| `DEBUG` | Enable/disable debug mode | No | `True` |
| `REDIS_URL` | Redis connection URL for caching | No | `redis://127.0.0.1:6379/1` |
| `DATABASE_URL` | Database connection URL | No | SQLite database |

### Database Configuration

- **SQLite (default):** No additional setup required
- **PostgreSQL:** Set `DATABASE_URL` to your PostgreSQL connection string
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/dbname
  ```

### Redis Configuration

Redis is used for caching. If not configured, the application will work but caching will be disabled.

## Deployment

Use the provided `build.sh` script for deployment:

```bash
./build.sh
```

This script will:
- Install dependencies
- Collect static files
- Run database migrations

For production deployment, make sure to:
- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Configure proper database and Redis URLs
- Set up proper ALLOWED_HOSTS

## Project Structure

```
intern-task/
├── auth_service/          # Django project settings
├── users/                 # User management app
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── build.sh             # Build script
├── run_tests.sh         # Test runner script
└── README.md            # This file
```

## API Endpoints

The API provides endpoints for:
- User registration (`/api/v1/auth/register/`)
- User login (`/api/v1/auth/login/`)
- Token refresh (`/api/v1/auth/refresh/`)
- Password reset (`/api/v1/auth/password-reset/`)
- User profile management (`/api/v1/users/`)

Refer to the API documentation for complete endpoint details.
