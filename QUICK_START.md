# راهنمای راه‌اندازی سریع - AI Content Factory Pro

## ⚠️ مشکل: ERR_CONNECTION_REFUSED

اگر این خطا را می‌بینید، سرویس‌ها در حال اجرا نیستند.

---

## 🚀 راه‌اندازی سریع

### روش 1: با Docker (اگر Docker Desktop نصب است)

```bash
# 1. راه‌اندازی Docker Desktop
# (از Start Menu اجرا کنید)

# 2. راه‌اندازی سرویس‌ها
docker-compose up -d

# 3. بررسی وضعیت
docker-compose ps

# 4. مشاهده لاگ‌ها
docker-compose logs -f frontend
docker-compose logs -f api
```

**دسترسی:**
- Frontend: http://localhost:3002
- Backend: http://localhost:8000

---

### روش 2: بدون Docker (Development محلی)

#### گام 1: راه‌اندازی Backend

```bash
cd backend

# ایجاد Virtual Environment
python -m venv venv

# فعال‌سازی (Windows)
venv\Scripts\activate

# نصب Dependencies
pip install -r requirements.txt

# اجرای Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend روی: http://localhost:8000

#### گام 2: راه‌اندازی Frontend (در Terminal جدید)

```bash
cd frontend

# نصب Dependencies (اگر قبلاً نصب نشده)
npm install

# اجرای Frontend
npm run dev -- -p 3002
```

Frontend روی: http://localhost:3002

---

## 🔍 Troubleshooting

### مشکل 1: Docker Desktop اجرا نمی‌شود
**راهکار:**
- Docker Desktop را از Start Menu اجرا کنید
- منتظر بمانید تا Docker Engine شروع شود
- سپس `docker-compose up -d` را اجرا کنید

### مشکل 2: Port در حال استفاده است
**راهکار:**
```bash
# بررسی Port 8000
netstat -ano | findstr :8000

# بررسی Port 3002
netstat -ano | findstr :3002

# اگر در حال استفاده است، Process را Kill کنید یا پورت را تغییر دهید
```

### مشکل 3: Backend Start نمی‌شود
**راهکار:**
```bash
# بررسی Dependencies
cd backend
pip install -r requirements.txt

# بررسی Python Version (باید 3.11+ باشد)
python --version

# اجرای مستقیم
python -m uvicorn main:app --reload
```

### مشکل 4: Frontend Start نمی‌شود
**راهکار:**
```bash
# حذف node_modules و نصب مجدد
cd frontend
rm -rf node_modules package-lock.json
npm install

# اجرای مجدد
npm run dev -- -p 3002
```

### مشکل 5: CORS Error
**راهکار:**
- مطمئن شوید Backend روی Port 8000 اجرا می‌شود
- در `backend/main.py` CORS تنظیم شده است
- اگر مشکل ادامه داشت، بررسی کنید که `NEXT_PUBLIC_API_URL` درست تنظیم شده باشد

---

## ✅ بررسی وضعیت

### Backend
```bash
# تست Health Check
curl http://localhost:8000/health

# یا در Browser
open http://localhost:8000/health
```

### Frontend
```bash
# تست در Browser
open http://localhost:3002
```

---

## 📝 نکات مهم

1. **اول Backend، بعد Frontend**: همیشه Backend را قبل از Frontend Start کنید
2. **Ports**: 
   - Backend: 8000
   - Frontend: 3002
3. **Dependencies**: مطمئن شوید تمام Dependencies نصب شده‌اند
4. **Environment**: در Development، Backend باید روی `0.0.0.0` اجرا شود

---

## 🆘 اگر هنوز مشکل دارید

1. بررسی کنید که هیچ Firewall یا Antivirus مانع نمی‌شود
2. بررسی کنید که Ports آزاد هستند
3. لاگ‌ها را بررسی کنید:
   - Backend: Terminal که uvicorn را اجرا می‌کند
   - Frontend: Terminal که npm run dev را اجرا می‌کند

---

**موفق باشید!** 🚀

