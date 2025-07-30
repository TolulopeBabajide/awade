# Security Guidelines for Awade Project

## 🔒 Core Security Principles

### 1. Never Hard-code Secrets
**CRITICAL RULE: Never hard-code secrets, API keys, passwords, or sensitive configuration in code, configuration files, or documentation.**

#### What NOT to do:
```yaml
# ❌ NEVER do this in CI/CD workflows
env:
  DATABASE_URL: postgresql://user:password@localhost:5432/db
  SECRET_KEY: my_secret_key_here
  OPENAI_API_KEY: sk-1234567890abcdef
```

```python
# ❌ NEVER do this in code
DATABASE_URL = "postgresql://user:password@localhost:5432/db"
SECRET_KEY = "my_secret_key_here"
```

#### What TO do:
```yaml
# ✅ Use environment variables and secrets management
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

```python
# ✅ Use environment variables
import os
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

### 2. Environment Variable Management

#### Local Development:
- Use `.env` files for local development (never commit these)
- Copy from `.env.example` and fill in your values
- Add `.env` to `.gitignore`

#### CI/CD Environments:
- Use GitHub Secrets for sensitive data
- Use environment variables for non-sensitive configuration
- Never expose secrets in logs or error messages

#### Required Secrets for CI/CD:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET_KEY`: JWT signing key

### 3. Configuration Files

#### Allowed in Repository:
- `.env.example` (template with placeholder values)
- Configuration templates
- Documentation with placeholder examples

#### Never in Repository:
- `.env` files with real values
- Hard-coded secrets in any file
- API keys, passwords, or tokens

### 4. Code Review Checklist

Before merging any code, verify:
- [ ] No hard-coded secrets in code
- [ ] No hard-coded secrets in configuration files
- [ ] No hard-coded secrets in CI/CD workflows
- [ ] Environment variables are used for sensitive data
- [ ] `.env` files are in `.gitignore`
- [ ] Documentation uses placeholder examples

### 5. Testing with Secrets

#### Local Testing:
```bash
# Create a test .env file
cp .env.example .env.test
# Edit .env.test with test values
python scripts/contract_testing.py --env-file .env.test
```

#### CI/CD Testing:
- Use GitHub Secrets for test environment variables
- Use test-specific secrets when possible
- Ensure test secrets are different from production

### 6. Emergency Procedures

If secrets are accidentally committed:
1. **IMMEDIATELY** rotate/regenerate the exposed secrets
2. Remove the secrets from git history
3. Update all environments with new secrets
4. Review access logs for unauthorized usage
5. Document the incident and lessons learned

## 🛡️ Additional Security Practices

### Code Security:
- Use parameterized queries to prevent SQL injection
- Validate and sanitize all user inputs
- Use HTTPS in production
- Implement proper authentication and authorization
- Regular security dependency updates

### Infrastructure Security:
- Use least privilege principle
- Regular security audits
- Monitor for suspicious activities
- Keep dependencies updated
- Use secure communication channels

### Data Protection:
- Encrypt sensitive data at rest
- Use secure transmission protocols
- Implement data retention policies
- Regular backup and recovery testing

## 📚 Resources

- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

---

**Remember: Security is everyone's responsibility. When in doubt, ask for review before committing sensitive information.** 