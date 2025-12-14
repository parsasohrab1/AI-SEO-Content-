# پورت‌های نهایی - AI Content Factory Pro

## 🌐 آدرس‌های دسترسی

- **Frontend Dashboard**: http://localhost:3002
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/api/docs
- **Health Check**: http://localhost:8002/health

---

## ⚠️ چرا Port 8002؟

- Port 8000: در حال استفاده توسط محصول دیگر
- Port 8001: در حال استفاده توسط محصول دیگر (INEsCape)
- Port 8002: آزاد - برای Backend ما استفاده می‌شود
- Port 3002: آزاد - برای Frontend ما استفاده می‌شود

---

## 🚀 راه‌اندازی

### روش سریع:
```bash
start-all.bat
```

### یا دستی:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- -p 3002
```

---

## ✅ بررسی

1. **Backend**: http://localhost:8002/health
   - باید ببینید: `{"status":"healthy","service":"AI Content Factory Pro"}`

2. **Frontend**: http://localhost:3002
   - باید صفحه اصلی را ببینید

---

**سرویس‌ها در حال راه‌اندازی هستند...** 🚀

