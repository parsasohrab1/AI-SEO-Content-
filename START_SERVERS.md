# راه‌اندازی سرویس‌ها - AI Content Factory Pro

## 🚀 راه‌اندازی سریع (Windows)

### روش 1: استفاده از Script (توصیه می‌شود)

```bash
# فقط این فایل را دوبار کلیک کنید یا اجرا کنید:
start-all.bat
```

این Script به صورت خودکار:
1. Backend را روی Port 8000 راه‌اندازی می‌کند
2. Frontend را روی Port 3002 راه‌اندازی می‌کند
3. پنجره‌های جداگانه برای هر سرویس باز می‌کند

---

### روش 2: راه‌اندازی دستی

#### Terminal 1: Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev -- -p 3002
```

---

## 🔍 بررسی وضعیت

### Backend
باز کنید: http://localhost:8000/health

باید این پاسخ را ببینید:
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

## ⚠️ اگر Port 8000 اشغال است

اگر محصول دیگری روی Port 8000 در حال اجرا است:

### گزینه 1: تغییر Port Backend

1. فایل `backend/main.py` را باز کنید
2. خط آخر را تغییر دهید:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # تغییر به 8001
```

3. در `start-backend.bat` هم Port را تغییر دهید:
```batch
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

4. در `frontend/app/page.tsx` و `frontend/app/dashboard/[id]/page.tsx`:
```typescript
const response = await fetch('http://localhost:8001/analyze-site', {
```

### گزینه 2: متوقف کردن سرویس دیگر

```bash
# پیدا کردن Process
netstat -ano | findstr :8000

# Kill کردن (PID را از خروجی بالا بگیرید)
taskkill /PID <PID> /F
```

---

## 📝 Checklist

قبل از اجرا:
- [ ] Python 3.11+ نصب است (`python --version`)
- [ ] Node.js 20+ نصب است (`node --version`)
- [ ] Port 8000 آزاد است (یا تغییر دهید)
- [ ] Port 3002 آزاد است (یا تغییر دهید)
- [ ] در دایرکتوری اصلی پروژه هستید

---

## 🆘 مشکلات رایج

### Backend Start نمی‌شود
```bash
# بررسی Python
python --version

# نصب Dependencies
cd backend
pip install -r requirements.txt

# اجرای مستقیم
python -m uvicorn main:app --reload
```

### Frontend Start نمی‌شود
```bash
# نصب Dependencies
cd frontend
npm install

# اجرای مجدد
npm run dev -- -p 3002
```

### CORS Error
- مطمئن شوید Backend روی `0.0.0.0` اجرا می‌شود (نه `127.0.0.1`)
- بررسی کنید که `NEXT_PUBLIC_API_URL` درست است

---

**موفق باشید!** 🚀

