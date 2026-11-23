# راهنمای استقرار - AI Content Factory Pro

## 📋 Prerequisites

### Infrastructure
- Docker و Docker Compose
- حداقل 4GB RAM
- 20GB فضای دیسک
- دسترسی به اینترنت برای APIهای خارجی

### API Keys مورد نیاز
- OpenAI API Key (برای تولید محتوا)
- Google API Key (برای Google APIs)
- سایر API Keys بر اساس نیاز

---

## 🚀 استقرار با Docker Compose

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-SEO-Content-
```

### 2. Set Environment Variables
```bash
# کپی فایل .env
cp backend/.env.example backend/.env

# ویرایش و تنظیم مقادیر
nano backend/.env
```

### 3. راه‌اندازی
```bash
# Build و Start تمام سرویس‌ها
docker-compose up -d

# View logs
docker-compose logs -f

# Check the status
docker-compose ps
```

### 4. بررسی Health
```bash
# Health Check
curl http://localhost:8000/health

# API Docs
open http://localhost:8000/api/docs
```

---

## 🔧 تنظیمات Production

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/content_factory

# Security
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
```

### Security
1. **HTTPS:** استفاده از Reverse Proxy (Nginx/Traefik)
2. **Rate Limiting:** تنظیم در `RateLimitMiddleware`
3. **CORS:** محدود کردن Origins
4. **Secrets:** استفاده از Secret Management (Vault, AWS Secrets Manager)

### Scaling
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
    # ...
  
  worker:
    deploy:
      replicas: 5
    # ...
```

---

## 📊 Monitoring

### Prometheus Metrics
```bash
# دسترسی به Metrics
curl http://localhost:8000/metrics
```

### Logs
```bash
# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Health Checks
```bash
# Health Check Endpoint
curl http://localhost:8000/health
```

---

## 🔄 Backup و Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U postgres content_factory > backup.sql

# Restore
docker-compose exec -T db psql -U postgres content_factory < backup.sql
```

### MongoDB Backup
```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup

# Restore
docker-compose exec mongodb mongorestore /backup
```

---

## 🆘 Troubleshooting

### مشکل: سرویس‌ها Start نمی‌شوند
```bash
# بررسی لاگ‌ها
docker-compose logs

# بررسی Ports
netstat -tulpn | grep -E '8000|3000|5432'
```

### مشکل: خطای Connection به Database
```bash
# بررسی اجرای Database
docker-compose ps db

# تست Connection
docker-compose exec db psql -U postgres -d content_factory
```

### مشکل: Memory کم
```bash
# افزایش Memory Limit در docker-compose.yml
services:
  api:
    mem_limit: 2g
```

---

## 📈 Performance Tuning

### Database
```sql
-- ایجاد Indexes
CREATE INDEX idx_analysis_id ON site_analyses(analysis_id);
CREATE INDEX idx_site_url ON site_analyses(site_url);
```

### Redis Cache
```python
# تنظیم TTL مناسب
cache_manager.set(key, value, ttl=3600)  # 1 hour
```

### Worker Scaling
```bash
# افزایش تعداد Workers
docker-compose up -d --scale worker=5
```

---

## 🔐 Security Checklist

- [ ] HTTPS فعال است
- [ ] CORS محدود شده
- [ ] Rate Limiting فعال است
- [ ] Security Headers تنظیم شده
- [ ] API Keys در Environment Variables هستند
- [ ] Database Password قوی است
- [ ] Firewall تنظیم شده
- [ ] Logs مانیتور می‌شوند
- [ ] Backup منظم انجام می‌شود

---

## 📝 Maintenance

### به‌روزرسانی
```bash
# Pull آخرین تغییرات
git pull

# Rebuild Images
docker-compose build --no-cache

# Restart Services
docker-compose up -d
```

### Cleanup
```bash
# حذف Containers و Volumes قدیمی
docker-compose down -v

# حذف Images قدیمی
docker image prune -a
```

---

## 🆘 پشتیبانی

برای مشکلات و سوالات:
- Issue در Repository
- Email: support@example.com
- Documentation: `/docs`

---

**آخرین به‌روزرسانی:** 2024

