# Authentication & Security Implementation

## Overview

The AWADE platform implements a comprehensive authentication and authorization system using JWT (JSON Web Tokens) to secure all profile management endpoints and user data.

## 🔐 Authentication System

### JWT Token Implementation
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Configurable via `JWT_SECRET_KEY` environment variable
- **Expiration**: Configurable via `JWT_EXPIRES_MINUTES` environment variable (default: 60 minutes)
- **Token Format**: Bearer token in Authorization header

### Token Structure
```json
{
  "sub": "user_id",
  "exp": "expiration_timestamp",
  "iat": "issued_at_timestamp"
}
```

## 🛡️ Security Features

### 1. Endpoint Protection
All profile management endpoints require valid JWT authentication:

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/profile/upload-image` - Upload profile image
- `DELETE /api/users/profile/delete-image` - Delete profile image
- `GET /api/users/` - List all users (admin only)
- `GET /api/users/{user_id}` - Get specific user (admin only)
- `PUT /api/users/{user_id}` - Update user (admin or self)
- `DELETE /api/users/{user_id}` - Delete user (admin only)

### 2. Role-Based Access Control
- **EDUCATOR**: Can manage their own profile and lesson plans
- **ADMIN**: Can manage all users and system settings

### 3. User Isolation
- Users can only modify their own profiles
- Profile images are stored in user-specific directories
- File paths are validated to prevent directory traversal attacks

## 🔒 Authentication Flow

### 1. Login Process
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "EDUCATOR"
  }
}
```

### 2. Using Protected Endpoints
```http
GET /api/users/profile
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 3. Token Refresh
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token_here"
}
```

## 🚫 Security Responses

### Missing Authentication
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "detail": "Not authenticated"
}
```

### Invalid Token
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Invalid token",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

### Expired Token
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Token has expired",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

### Insufficient Permissions
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "detail": "Access denied. Required role: ADMIN"
}
```

## 🔐 File Upload Security

### Profile Image Security
- **File Types**: JPEG, PNG, WebP only
- **File Size**: Maximum 5MB
- **Dimensions**: Auto-resized to 800x800px maximum
- **Storage**: User-specific directories with UUID filenames
- **Validation**: Server-side file type and content validation

### Security Measures
```python
# File type validation
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg', 
    'image/png': '.png',
    'image/webp': '.webp'
}

# Size limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Path security
if not str(file_path).startswith('uploads/'):
    raise ValueError("Invalid file path")
```

## 🧪 Testing Authentication

### Test Script
Use the provided `test_authentication.py` script to verify security:

```bash
python test_authentication.py
```

### Manual Testing
```bash
# Test without authentication (should return 403)
curl http://localhost:8000/api/users/profile

# Test with invalid token (should return 401)
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:8000/api/users/profile

# Test with valid token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/users/profile
```

## 🔧 Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_EXPIRES_MINUTES=60

# Password Security
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128

# File Upload
UPLOAD_MAX_SIZE=5242880  # 5MB
UPLOAD_MAX_DIMENSIONS=800
```

### Dependencies
```python
# Required Python packages
fastapi>=0.109.0
PyJWT>=2.0.0
python-multipart>=0.0.6
Pillow>=10.0.0  # For image processing
```

## 🚨 Security Best Practices

### 1. Token Management
- Store tokens securely (localStorage for web, secure storage for mobile)
- Implement token refresh before expiration
- Clear tokens on logout
- Use HTTPS in production

### 2. Password Security
- Minimum 8 characters, maximum 128 characters
- Block common weak passwords
- Implement password strength requirements
- Use bcrypt for password hashing

### 3. File Upload Security
- Validate file types server-side
- Implement size limits
- Use secure file paths
- Scan for malware (recommended for production)

### 4. API Security
- Rate limiting (recommended)
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for web clients

## 🔍 Monitoring & Logging

### Security Events
- Failed authentication attempts
- Invalid token usage
- File upload violations
- Permission denied actions

### Log Format
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "event": "authentication_failed",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/api/users/profile",
  "reason": "invalid_token"
}
```

## 🚀 Production Considerations

### 1. Enhanced Security
- Implement rate limiting
- Add IP whitelisting/blacklisting
- Use Redis for session management
- Implement audit logging

### 2. Monitoring
- Set up alerts for failed authentication
- Monitor file upload patterns
- Track API usage metrics
- Implement health checks

### 3. Backup & Recovery
- Regular database backups
- File storage redundancy
- Disaster recovery procedures
- Incident response plan

## 📚 Additional Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [OWASP Security Guidelines](https://owasp.org/www-project-api-security/)
- [File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)

## 🆘 Troubleshooting

### Common Issues
1. **403 Forbidden**: Missing or invalid Authorization header
2. **401 Unauthorized**: Expired or invalid JWT token
3. **File Upload Fails**: Check file type, size, and permissions
4. **Database Connection**: Verify PostgreSQL connection and credentials

### Debug Steps
1. Check JWT token expiration
2. Verify environment variables
3. Check database connectivity
4. Review application logs
5. Test with authentication test script
