# Security Guidelines for Awade

## 🔐 Environment Variables and Credentials

### Never Commit Sensitive Data
- **Never** commit `.env` files containing real credentials
- **Never** hardcode passwords, API keys, or secrets in source code
- **Always** use environment variables for sensitive configuration

### Environment File Setup
1. Copy the example file: `cp env.example .env`
2. Edit `.env` with your actual values
3. Keep `.env` in your `.gitignore` (already configured)

### Required Environment Variables

#### Database Credentials
```bash
POSTGRES_DB=awade
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
```

#### API Keys
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

#### Security Keys
```bash
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

## 🛡️ Security Best Practices

### Password Requirements
- Use strong, unique passwords (12+ characters)
- Include uppercase, lowercase, numbers, and symbols
- Never reuse passwords across services
- Consider using a password manager

### API Key Security
- Store API keys in environment variables
- Rotate keys regularly
- Use different keys for development and production
- Monitor API usage for unusual activity

### Database Security
- Use dedicated database users with minimal privileges
- Enable SSL connections in production
- Regularly backup databases
- Monitor database access logs

### Docker Security
- Use non-root users in containers
- Keep base images updated
- Scan images for vulnerabilities
- Use secrets management for production

## 🚀 Production Deployment

### Environment Variables
For production, use a secure secrets management system:
- **Docker Swarm**: Use Docker secrets
- **Kubernetes**: Use Kubernetes secrets
- **Cloud Platforms**: Use platform-specific secret management
- **Self-hosted**: Use tools like HashiCorp Vault

### Example Production Setup
```bash
# Generate secure secrets
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For JWT_SECRET_KEY

# Use strong database password
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### Security Checklist
- [ ] All sensitive data in environment variables
- [ ] Strong, unique passwords for all services
- [ ] SSL/TLS enabled for all connections
- [ ] Regular security updates applied
- [ ] Access logs monitored
- [ ] Backups encrypted and secure
- [ ] API rate limiting configured
- [ ] CORS properly configured

## 🔍 Security Monitoring

### Log Monitoring
- Monitor application logs for suspicious activity
- Set up alerts for failed login attempts
- Track API usage patterns
- Monitor database access

### Vulnerability Scanning
- Regularly scan dependencies for vulnerabilities
- Keep all packages updated
- Use security scanning tools in CI/CD
- Monitor security advisories

## 📞 Security Contacts

For security issues or questions:
- Create a private GitHub issue
- Contact the development team
- Follow responsible disclosure practices

## 📚 Additional Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) 