# Awade Deployment Guide

This guide covers production deployment instructions for the Awade platform, an AI-powered educator support system.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- At least 2GB RAM available
- PostgreSQL database (included in Docker setup)

### Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TolulopeBabajide/awade.git
   cd awade
   ```

2. **Configure Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env with your production values
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

## 🐳 Docker Deployment

### Production Docker Compose

The project includes a production-ready Docker Compose configuration:

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: awade
      POSTGRES_USER: awade_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./apps/backend
    environment:
      DATABASE_URL: postgresql://awade_user:${DB_PASSWORD}@postgres:5432/awade
      SECRET_KEY: ${SECRET_KEY}
      JWT_ALGORITHM: HS256
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs

  frontend:
    build: ./apps/frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://awade_user:your_secure_password@postgres:5432/awade

# Security
SECRET_KEY=your_very_long_secret_key_here
JWT_ALGORITHM=HS256

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

## 🗄️ Database Setup

### Initial Database Migration

1. **Run Database Migrations**
   ```bash
   docker-compose exec backend python -c "
   from database import engine
   from models import Base
   Base.metadata.create_all(bind=engine)
   print('Database tables created successfully')
   "
   ```

2. **Initialize Database with Seed Data**
   ```bash
   docker-compose exec backend python init_db.py
   ```

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U awade_user awade > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U awade_user awade < backup_file.sql
```

## 🔧 Backend Deployment

### FastAPI Application

The backend is a FastAPI application with the following features:

- **Authentication**: JWT-based authentication
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: GPT-powered lesson plan generation
- **File Export**: PDF and DOCX export functionality
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check API documentation
curl http://localhost:8000/docs
```

### Logs and Monitoring

```bash
# View backend logs
docker-compose logs backend

# View real-time logs
docker-compose logs -f backend

# Check resource usage
docker stats
```

## 🎨 Frontend Deployment

### React Application

The frontend is a React application with:

- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Vite**: Fast build tool
- **React Router**: Client-side routing
- **Context API**: State management

### Build and Deploy

```bash
# Development mode
docker-compose up frontend

# Production build
docker-compose -f docker-compose.prod.yml up --build
```

## 🔒 Security Configuration

### SSL/HTTPS Setup

For production, configure SSL certificates:

```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com

# Or self-signed for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx.key -out nginx.crt
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring and Logging

### Application Monitoring

```bash
# Check application status
docker-compose ps

# Monitor resource usage
docker stats

# View application logs
docker-compose logs -f
```

### Database Monitoring

```bash
# Check database connections
docker-compose exec postgres psql -U awade_user -d awade -c "
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
"
```

## 🔄 Scaling Strategy

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/awade
```

### Load Balancing

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U awade_user
   
   # Restart database
   docker-compose restart postgres
   ```

2. **Backend Won't Start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Rebuild backend
   docker-compose build backend
   docker-compose up backend
   ```

3. **Frontend Build Fails**
   ```bash
   # Clear node modules
   docker-compose exec frontend rm -rf node_modules
   docker-compose exec frontend npm install
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_lesson_plans_user_id ON lesson_plans(user_id);
   CREATE INDEX idx_lesson_resources_plan_id ON lesson_resources(lesson_plan_id);
   ```

2. **Caching Strategy**
   ```python
   # Add Redis for caching
   redis_cache = redis.Redis(host='redis', port=6379, db=0)
   ```

## 📞 Support

### Getting Help

- **Documentation**: Check the [API Documentation](../api/README.md)
- **Development Guide**: See [Development Setup](../development/README.md)
- **Issues**: Report bugs on GitHub
- **Community**: Join our developer community

### Emergency Contacts

- **Database Issues**: Check PostgreSQL logs and connection settings
- **API Issues**: Verify environment variables and service health
- **Frontend Issues**: Check build logs and API connectivity

---

*This deployment guide covers the current production-ready setup. For development deployment, see the [Development Guide](../development/README.md).*

*Last updated: January 2024*
*Maintainer: Awade Development Team* 