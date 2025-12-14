# راهنمای نگهداری - AI Content Factory Pro

## 📋 نگهداری روزانه

### بررسی سلامت سرویس‌ها
```bash
# اجرای Health Check Script
./scripts/monitor.sh

# یا دستی
curl http://localhost:8000/health
```

### بررسی لاگ‌ها
```bash
# لاگ API
docker-compose logs -f api --tail=100

# لاگ Worker
docker-compose logs -f worker --tail=100

# لاگ تمام سرویس‌ها
docker-compose logs --tail=50
```

### بررسی Metrics
```bash
# Prometheus Metrics
curl http://localhost:9090

# Grafana Dashboard
open http://localhost:3001
```

---

## 📅 نگهداری هفتگی

### Backup
```bash
# اجرای Backup Script
./scripts/backup.sh

# یا دستی
docker-compose exec -T db pg_dump -U postgres content_factory > backup.sql
```

### بررسی Disk Space
```bash
df -h
docker system df
```

### Cleanup
```bash
# حذف Containers متوقف شده
docker-compose down

# حذف Images قدیمی
docker image prune -a

# حذف Volumes غیراستفاده
docker volume prune
```

### بررسی Security Updates
```bash
# بررسی Updates برای Dependencies
cd backend
pip list --outdated

cd ../frontend
npm outdated
```

---

## 📆 نگهداری ماهانه

### به‌روزرسانی Dependencies
```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### بررسی و به‌روزرسانی Docker Images
```bash
docker-compose pull
docker-compose up -d
```

### بررسی Performance
- بررسی Metrics در Grafana
- بررسی Slow Queries در Database
- بررسی Memory و CPU Usage

### بررسی Security
- بررسی Logs برای Suspicious Activity
- بررسی Rate Limiting
- بررسی API Keys و Secrets

---

## 🔧 Troubleshooting

### مشکل: سرویس Start نمی‌شود
```bash
# بررسی لاگ‌ها
docker-compose logs <service_name>

# بررسی Ports
netstat -tulpn | grep <port>

# Restart سرویس
docker-compose restart <service_name>
```

### مشکل: Database Connection Error
```bash
# بررسی اجرای Database
docker-compose ps db

# تست Connection
docker-compose exec db psql -U postgres -d content_factory

# بررسی Logs
docker-compose logs db
```

### مشکل: High Memory Usage
```bash
# بررسی Memory Usage
docker stats

# Restart Containers
docker-compose restart

# افزایش Memory Limit در docker-compose.yml
```

### مشکل: Slow Performance
```bash
# بررسی Metrics
curl http://localhost:8000/metrics

# بررسی Database Queries
docker-compose exec db psql -U postgres -d content_factory -c "SELECT * FROM pg_stat_activity;"

# بررسی Cache Hit Rate
docker-compose exec redis redis-cli INFO stats
```

---

## 🔄 به‌روزرسانی

### به‌روزرسانی Application
```bash
# Pull آخرین تغییرات
git pull origin main

# Rebuild Images
docker-compose -f docker-compose.prod.yml build --no-cache

# Restart Services
docker-compose -f docker-compose.prod.yml up -d

# اجرای Migrations (اگر نیاز باشد)
docker-compose exec api python -m alembic upgrade head
```

### به‌روزرسانی Database Schema
```bash
# ایجاد Migration جدید
docker-compose exec api python -m alembic revision --autogenerate -m "description"

# اجرای Migration
docker-compose exec api python -m alembic upgrade head

# Rollback (در صورت نیاز)
docker-compose exec api python -m alembic downgrade -1
```

---

## 📊 Monitoring

### Prometheus
- URL: http://localhost:9090
- بررسی Metrics
- بررسی Alerts

### Grafana
- URL: http://localhost:3001
- Default User: admin
- Default Password: (از Environment Variable)

### Key Metrics to Monitor
- API Request Rate
- API Response Time (P95, P99)
- Error Rate
- Pipeline Success Rate
- Database Connection Pool
- Cache Hit Rate
- Memory Usage
- CPU Usage
- Disk Space

---

## 🔐 Security

### بررسی Security Headers
```bash
curl -I http://localhost:8000/health
```

### بررسی Rate Limiting
```bash
# تست Rate Limit
for i in {1..70}; do curl http://localhost:8000/health; done
```

### به‌روزرسانی Secrets
```bash
# تغییر Environment Variables
nano .env

# Restart Services
docker-compose restart
```

---

## 📝 Logs

### مکان Logs
- Application Logs: `./logs/`
- Nginx Logs: `./logs/nginx/`
- Docker Logs: `docker-compose logs`

### Log Rotation
```bash
# تنظیم Log Rotation در docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 🆘 Emergency Procedures

### Restart تمام سرویس‌ها
```bash
docker-compose restart
```

### Restore از Backup
```bash
./scripts/restore.sh backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

### Rollback به Version قبلی
```bash
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📞 پشتیبانی

برای مشکلات و سوالات:
- Issue در Repository
- Email: support@example.com
- Documentation: `/docs`

---

**آخرین به‌روزرسانی:** 2024

