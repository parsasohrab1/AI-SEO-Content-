# تغییر پورت Backend

## ⚠️ توجه

به دلیل اینکه Port 8000 در حال استفاده است، Backend روی **Port 8001** راه‌اندازی می‌شود.

---

## 🌐 آدرس‌های جدید

- **Frontend Dashboard**: http://localhost:3002
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/api/docs
- **Health Check**: http://localhost:8001/health

---

## 🔧 تغییرات انجام شده

### فایل‌های به‌روز شده:
- ✅ `start-backend.bat` - Port به 8001 تغییر کرد
- ✅ `start-all.bat` - Port به 8001 تغییر کرد
- ✅ `frontend/app/page.tsx` - API URL به 8001 تغییر کرد
- ✅ `frontend/app/dashboard/[id]/page.tsx` - API URL به 8001 تغییر کرد
- ✅ `frontend/app/dashboard/[id]/analysis/page.tsx` - API URL به 8001 تغییر کرد

---

## 🚀 راه‌اندازی

### روش 1: استفاده از Script
```bash
start-all.bat
```

### روش 2: دستی
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev -- -p 3002
```

---

## ✅ بررسی

بعد از راه‌اندازی:
1. Backend: http://localhost:8001/health
2. Frontend: http://localhost:3002

---

**نکته**: اگر می‌خواهید Port را به 8000 برگردانید، باید ابتدا Process روی Port 8000 را متوقف کنید.

