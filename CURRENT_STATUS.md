# وضعیت فعلی سرویس‌ها

## ✅ تغییرات انجام شده

به دلیل اینکه Port 8000 در حال استفاده است، Backend روی **Port 8001** راه‌اندازی می‌شود.

---

## 🌐 آدرس‌های دسترسی

- **Frontend Dashboard**: http://localhost:3002
- **Backend API**: http://localhost:8001  
- **API Documentation**: http://localhost:8001/api/docs
- **Health Check**: http://localhost:8001/health

---

## 🚀 راه‌اندازی

### اگر سرویس‌ها در حال اجرا نیستند:

#### روش 1: استفاده از Script (توصیه می‌شود)
```bash
start-all.bat
```

#### روش 2: راه‌اندازی دستی

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- -p 3002
```

---

## 🔍 بررسی وضعیت

### Backend
باز کنید: http://localhost:8001/health

باید ببینید:
```json
{
  "status": "healthy",
  "service": "AI Content Factory Pro",
  "version": "1.0.0"
}
```

### Frontend
باز کنید: http://localhost:3002

باید صفحه اصلی با فرم ورود URL را ببینید.

---

## ⚠️ اگر هنوز خطا می‌بینید

1. **بررسی کنید که سرویس‌ها در حال اجرا هستند:**
   ```bash
   netstat -ano | findstr ":8001 :3002"
   ```

2. **بررسی کنید که Virtual Environment فعال است:**
   ```bash
   cd backend
   venv\Scripts\activate
   ```

3. **بررسی کنید که Dependencies نصب شده‌اند:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

4. **اجرای مجدد:**
   ```bash
   start-all.bat
   ```

---

## 📝 تغییرات انجام شده

- ✅ Backend Port: 8000 → 8001
- ✅ Frontend Port: 3000 → 3002
- ✅ تمام فایل‌های Frontend به‌روز شدند
- ✅ Scripts به‌روز شدند

---

**برای راهنمای کامل**: `README_QUICK_START.md` یا `TROUBLESHOOTING.md`

