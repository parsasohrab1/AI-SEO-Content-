# تنظیمات پورت‌ها - AI Content Factory Pro

## 📋 پورت‌های استفاده شده

### Development (docker-compose.yml)
- **Frontend Dashboard**: `http://localhost:3002`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/api/docs`
- **RabbitMQ Management**: `http://localhost:15672`
- **PostgreSQL**: `localhost:5432`
- **MongoDB**: `localhost:27017`
- **Redis**: `localhost:6379`

### Production (docker-compose.prod.yml)
- **Frontend Dashboard**: `http://localhost:3002`
- **Backend API**: `http://localhost:8000`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001`
- **Nginx**: `http://localhost:80` و `https://localhost:443`
- **RabbitMQ Management**: `http://localhost:15672`

---

## 🔧 تغییر پورت Frontend

اگر پورت 3002 هم در حال استفاده است، می‌توانید آن را تغییر دهید:

### در docker-compose.yml
```yaml
frontend:
  ports:
    - "YOUR_PORT:3000"  # YOUR_PORT را با پورت مورد نظر جایگزین کنید
```

### در docker-compose.prod.yml
```yaml
frontend:
  ports:
    - "YOUR_PORT:3000"
```

سپس فایل‌های زیر را به‌روز کنید:
- `README_SETUP.md`
- `DASHBOARD_SETUP.md`
- `scripts/monitor.sh`

---

## ⚠️ Important Notes

1. **پورت داخلی Container**: همیشه `3000` است (تغییر ندهید)
2. **پورت خارجی Host**: می‌توانید تغییر دهید (مثلاً `3002`, `3003`, ...)
3. **Grafana**: روی پورت `3001` است - با Frontend تداخل ندارد
4. **Backend**: روی پورت `8000` است

---

**آخرین به‌روزرسانی:** 2024

