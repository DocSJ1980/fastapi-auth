# FastAPI Auth

A robust authentication and user management system built with FastAPI and SQLModel.

## Features

- User registration with email verification
- JWT-based authentication with access and refresh tokens
- Secure password hashing using bcrypt
- Email verification using custom SMTP configuration
- PostgreSQL database integration using SQLModel
- Environment-based configuration
- Secure password reset with time-limited tokens

## Project Structure

```
fastapi_auth/
├── models/
│   ├── user_model.py         # User data model
│   └── verification_model.py # Email verification token model
├── router/
│   └── user_router.py       # User-related endpoints
├── schemas/
│   └── user_schema.py       # Pydantic schemas for request/response
├── services/
│   ├── auth.py             # Authentication logic
│   └── email_service.py    # Email sending functionality
├── db.py                   # Database configuration
├── main.py                # FastAPI application setup
└── settings.py           # Environment configuration
```

## Technical Details

### FastAPI Setup

- Uses FastAPI's dependency injection for session management and authentication
- Implements async context manager for database initialization
- Custom middleware for error handling and authentication

### Database Management (SQLModel)

- SQLModel for type-safe database operations
- Automatic table creation on application startup
- Session management with connection pooling
- PostgreSQL database with SSL support

### Authentication System

- JWT-based token authentication
- Access token for API access
- Refresh token for token renewal
- Password hashing using bcrypt
- Email verification workflow
- Secure password reset with time-limited tokens

### Environment Configuration

Required environment variables:

```env
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
EXPIRY_TIME=1
REFRESH_TOKEN_EXPIRY_TIME=7
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=your-from-email
```

## API Endpoints

### Authentication

- `POST /user/register` - Register new user
- `POST /token` - Get access token
- `POST /refresh-token` - Refresh access token
- `GET /user/verify/{token}` - Verify email address
- `POST /user/forgot-password` - Request password reset
- `POST /user/reset-password` - Reset password with token

### User Management

- `GET /user/me` - Get current user profile

## Frontend Integration

This backend is designed to work seamlessly with:

- Next.js 15.1.0
- next-auth v5

### Frontend Setup

- Configure next-auth to use JWT authentication
- Set up API routes for token management
- Handle refresh token rotation
- Implement protected routes using next-auth session

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/fastapi-auth.git
   cd fastapi-auth
   ```

2. Install Poetry (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

4. Create `.env` file with required environment variables (see Environment Configuration section)

5. Run the application:

   ```bash
   poetry run uvicorn fastapi_auth.main:app --reload
   ```

6. Run tests:
   ```bash
   poetry run pytest
   ```

## Git Usage Guidelines

### Commit Message Format

```
<type>: <summary>
<BLANK LINE>
<description>
```

### Types

- fix: Bug fixes
- feat: New features
- perf: Performance improvements
- docs: Documentation changes
- style: Formatting changes
- refactor: Code refactoring
- test: Adding missing tests
- chore: Maintenance tasks

### Rules

- Use lowercase for commit messages
- Keep the summary line concise
- Create two -m commits per commit
- Include description for non-obvious changes
- Reference issue numbers when applicable

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens with configurable expiry
- Email verification required
- Timezone-aware token expiration
- Automatic cleanup of expired tokens
- Rate limiting on authentication endpoints
