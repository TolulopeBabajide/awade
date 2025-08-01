# Authentication and Authorization System

## Overview

The Awade platform implements a comprehensive authentication and authorization system using JWT (JSON Web Tokens) with role-based access control (RBAC). The system supports both email/password authentication and Google OAuth integration.

## Architecture

### Components

1. **Authentication Router** (`apps/backend/routers/auth.py`)
   - Handles user registration, login, and password reset
   - Supports Google OAuth integration
   - Issues JWT tokens for authenticated sessions

2. **Dependencies** (`apps/backend/dependencies.py`)
   - Provides authentication and authorization dependencies
   - Implements role-based access control
   - Handles JWT token validation

3. **User Management Router** (`apps/backend/routers/users.py`)
   - Admin-only user management operations
   - User profile updates
   - User listing and deletion

4. **User Model** (`apps/backend/models.py`)
   - Extended with role and profile fields
   - Supports educator and admin roles

## User Roles

### Educator
- Default role for new users
- Can create and manage lesson plans
- Can generate AI-powered lesson resources
- Can update their own profile
- Access to curriculum data (read-only)

### Admin
- Full system access
- Can manage all users
- Can create and modify curriculum data
- Can delete lesson plans and resources
- Can update any user's profile

## Authentication Endpoints

### Public Endpoints (No Authentication Required)

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/google` - Google OAuth login
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/reset-password` - Password reset

### Authenticated Endpoints (All Users)

- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Logout (client-side)
- `PUT /api/users/profile` - Update own profile
- `GET /api/users/profile` - Get own profile
- `GET /api/lesson-plans/` - List lesson plans
- `GET /api/lesson-plans/{id}` - Get lesson plan
- `GET /api/curriculum/` - List curricula
- `GET /api/curriculum/topics` - List topics
- `GET /api/curriculum/topics/{id}` - Get topic
- `GET /api/countries/` - List countries
- `GET /api/countries/{id}` - Get country
- `GET /api/grade-levels/` - List grade levels
- `GET /api/grade-levels/{id}` - Get grade level
- `GET /api/subjects/` - List subjects
- `GET /api/subjects/{id}` - Get subject
- `GET /api/curriculum-structures/` - List curriculum structures
- `GET /api/curriculum-structures/{id}` - Get curriculum structure

### Educator-Only Endpoints

- `POST /api/lesson-plans/generate` - Generate lesson plan
- `POST /api/lesson-plans/{id}/resources/generate` - Generate lesson resources
- `PUT /api/lesson-plans/resources/{id}/review` - Review lesson resources

### Admin-Only Endpoints

- `GET /api/users/` - List all users
- `GET /api/users/{id}` - Get specific user
- `PUT /api/users/{id}` - Update user profile
- `DELETE /api/users/{id}` - Delete user
- `POST /api/curriculum/` - Create curriculum
- `POST /api/curriculum/topics` - Create topic
- `POST /api/curriculum/learning-objectives` - Create learning objective
- `POST /api/curriculum/contents` - Create content
- `PUT /api/curriculum/learning-objectives/{id}` - Update learning objective
- `PUT /api/curriculum/contents/{id}` - Update content
- `DELETE /api/curriculum/learning-objectives/{id}` - Delete learning objective
- `DELETE /api/curriculum/contents/{id}` - Delete content
- `POST /api/countries/` - Create country
- `PUT /api/countries/{id}` - Update country
- `DELETE /api/countries/{id}` - Delete country
- `POST /api/grade-levels/` - Create grade level
- `PUT /api/grade-levels/{id}` - Update grade level
- `DELETE /api/grade-levels/{id}` - Delete grade level
- `POST /api/subjects/` - Create subject
- `PUT /api/subjects/{id}` - Update subject
- `DELETE /api/subjects/{id}` - Delete subject
- `POST /api/curriculum-structures/` - Create curriculum structure
- `PUT /api/curriculum-structures/{id}` - Update curriculum structure
- `DELETE /api/curriculum-structures/{id}` - Delete curriculum structure

### Admin or Educator Endpoints

- `PUT /api/lesson-plans/{id}` - Update lesson plan
- `DELETE /api/lesson-plans/{id}` - Delete lesson plan

## JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": "expiration_timestamp"
}
```

## Environment Variables

### Required Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_MINUTES=60

# Password Security
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/awade_db
```

### Optional Variables
```bash
# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-oauth-client-id

# Test User Configuration (Development Only)
ADMIN_EMAIL=admin@awade.com
ADMIN_PASSWORD=admin123
EDUCATOR_EMAIL=educator@awade.com
EDUCATOR_PASSWORD=educator123

# Email Configuration (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@awade.com
```

## Security Features

### Password Security
- Passwords are hashed using bcrypt with salt
- Configurable minimum and maximum length via environment variables
- Common weak passwords are rejected
- Password validation on both registration and reset

### Token Security
- JWT tokens expire after configurable time (default: 60 minutes)
- Tokens are signed with HMAC-SHA256
- Invalid tokens return 401 Unauthorized
- Secret key configurable via environment variable

### Role-Based Access Control
- Users can only access endpoints appropriate for their role
- Admin users have full system access
- Educators can only manage their own content
- Role validation on all protected endpoints

### Input Validation
- All user inputs are validated using Pydantic schemas
- Email addresses are validated
- Password strength requirements enforced
- Weak password detection

### Environment-Based Configuration
- All sensitive settings configurable via environment variables
- No hardcoded secrets in code
- Development and production configurations separated
- Test user credentials configurable

### Data Integrity Protection
- Prevents deletion of entities that have associated data
- Validates foreign key relationships before operations
- Checks for duplicate entries before creation
- Validates referenced entities exist before creating relationships

### Complete Authentication Coverage
- All GET endpoints require authentication
- No public data access without authentication
- Consistent security across all endpoints
- User context available for all authenticated requests

## Usage Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.com",
    "password": "securepassword123",
    "full_name": "John Doe",
    "role": "educator",
    "country": "Nigeria",
    "region": "Lagos",
    "school_name": "Test School"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.com",
    "password": "securepassword123"
  }'
```

### Authenticated Request
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Lesson Plans (Requires Authentication)
```bash
curl -X GET "http://localhost:8000/api/lesson-plans/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Lesson Plan (Educator Only)
```bash
curl -X POST "http://localhost:8000/api/lesson-plans/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "grade_level": "Grade 4",
    "topic": "Fractions",
    "duration_minutes": 45
  }'
```

### Create Country (Admin Only)
```bash
curl -X POST "http://localhost:8000/api/countries/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country_name": "Ghana",
    "iso_code": "GH",
    "region": "West Africa"
  }'
```

### Create Subject (Admin Only)
```bash
curl -X POST "http://localhost:8000/api/subjects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Physics"
  }'
```

## Database Schema

### User Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role userrole NOT NULL DEFAULT 'educator',
    country VARCHAR(100),
    region VARCHAR(100),
    school_name VARCHAR(200),
    subjects TEXT,
    grade_levels TEXT,
    languages_spoken TEXT,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Testing

### Test Users
Run the test user creation script:
```bash
python scripts/create_admin_user.py
```

This creates:
- Admin user: `admin@awade.com` / `admin123` (configurable)
- Educator user: `educator@awade.com` / `educator123` (configurable)

### Environment Configuration
Set environment variables for testing:
```bash
export ADMIN_EMAIL=admin@awade.com
export ADMIN_PASSWORD=secureadmin123
export EDUCATOR_EMAIL=educator@awade.com
export EDUCATOR_PASSWORD=secureeducator123
export PASSWORD_MIN_LENGTH=8
export JWT_SECRET_KEY=your-test-secret-key
```

### Testing Authentication
1. Start the backend server
2. Create test users using the script
3. Test login endpoints
4. Test protected endpoints with valid/invalid tokens
5. Test role-based access control

## Migration

To apply the database changes:
```bash
# Run the migration to add user fields
alembic upgrade head
```

## Best Practices

### For Developers
1. Always use the appropriate dependency for authentication
2. Test both authenticated and unauthenticated scenarios
3. Validate user permissions before performing operations
4. Use proper error handling for authentication failures
5. Never hardcode secrets in code
6. Use environment variables for all configuration

### For Administrators
1. Change default passwords immediately
2. Use strong JWT secret keys
3. Monitor authentication logs
4. Regularly rotate JWT secrets
5. Set appropriate password policies
6. Configure email settings for password reset

### For Users
1. Use strong passwords
2. Keep JWT tokens secure
3. Log out when using shared devices
4. Report suspicious activity

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check if JWT token is valid and not expired
   - Verify token format: `Bearer <token>`
   - Ensure user exists in database
   - Check JWT_SECRET_KEY configuration

2. **403 Forbidden**
   - Check user role permissions
   - Verify endpoint requires specific role
   - Ensure user has required permissions

3. **Token Expired**
   - Re-authenticate to get new token
   - Check JWT_EXPIRES_MINUTES setting

4. **Password Validation Errors**
   - Check PASSWORD_MIN_LENGTH setting
   - Ensure password meets strength requirements
   - Avoid common weak passwords

5. **Database Connection Issues**
   - Verify database is running
   - Check DATABASE_URL configuration
   - Ensure migrations are applied

6. **Environment Variable Issues**
   - Check all required environment variables are set
   - Verify JWT_SECRET_KEY is configured
   - Ensure PASSWORD_MIN_LENGTH is set

7. **Data Integrity Errors**
   - Check if entity has associated data before deletion
   - Verify foreign key relationships
   - Ensure referenced entities exist

## Future Enhancements

1. **Refresh Tokens**
   - Implement refresh token mechanism
   - Extend session duration securely

2. **Multi-Factor Authentication**
   - Add SMS/email verification
   - Implement TOTP support

3. **Session Management**
   - Track active sessions
   - Allow session revocation

4. **Audit Logging**
   - Log authentication events
   - Track user actions

5. **Rate Limiting**
   - Implement login attempt limits
   - Add API rate limiting

6. **Password Policies**
   - Configurable password complexity rules
   - Password history tracking
   - Force password change on first login 