# وضعیت سرویس‌ها

## ✅ سرویس‌ها در حال راه‌اندازی هستند

Backend و Frontend در پس‌زمینه راه‌اندازی شده‌اند.

---

## 🌐 دسترسی

### Frontend Dashboard
**URL**: http://localhost:3002

باید صفحه اصلی با فرم ورود URL را ببینید.

### Backend API
**URL**: http://localhost:8002

**Health Check**: http://localhost:8002/health
**API Docs**: http://localhost:8002/api/docs

---

## 🔍 بررسی وضعیت

### اگر Frontend باز نمی‌شود:

1. **بررسی کنید که Frontend در حال اجرا است:**
   ```bash
   netstat -ano | findstr :3002
   ```

2. **اگر نیست، دستی راه‌اندازی کنید:**
   ```bash
   cd frontend
   npm run dev -- -p 3002
   ```

### اگر Backend پاسخ نمی‌دهد:

1. **بررسی کنید که Backend در حال اجرا است:**
   ```bash
   netstat -ano | findstr :8002
   ```

2. **بررسی Health Check:**
   ```bash
   curl http://localhost:8002/health
   ```

3. **اگر نیست، دستی راه‌اندازی کنید:**
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

---

## 🚀 راه‌اندازی مجدد (اگر نیاز است)

### استفاده از Script:
```bash
start-all.bat
```

### یا دستی:

**Terminal 1:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**Terminal 2:**
```bash
cd frontend
npm run dev -- -p 3002
```

---

## 📝 پورت‌های استفاده شده

- **Backend**: 8002 (به دلیل اشغال بودن 8000 و 8001)
- **Frontend**: 3002 (به دلیل اشغال بودن 3000)

---

**لطفاً چند لحظه صبر کنید و سپس http://localhost:3002 را باز کنید.**

