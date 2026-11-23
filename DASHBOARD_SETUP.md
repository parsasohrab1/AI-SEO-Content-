# راهنمای راه‌اندازی داشبورد

## 🚀 Quick Start

### روش 1: با Docker Compose (توصیه می‌شود)

```bash
# راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# View logs
docker-compose logs -f frontend
docker-compose logs -f api
```

**دسترسی:**
- Frontend Dashboard: http://localhost:3002
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

### روش 2: Development محلی

#### Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📱 صفحات داشبورد

### صفحه اصلی
- URL: `/`
- عملکرد: ورود URL سایت برای تحلیل

### داشبورد تحلیل
- URL: `/dashboard/[analysis_id]`
- عملکرد: نمایش نتایج تحلیل، Summary Cards، Navigation

### صفحات فرعی:
- `/dashboard/[id]/analysis` - تحلیل قوت/ضعف
- `/dashboard/[id]/recommendations` - پیشنهادات
- `/dashboard/[id]/seo` - مانیتورینگ سئو

---

## 🔧 Troubleshooting

### مشکل: Frontend Start نمی‌شود
```bash
# حذف node_modules و نصب مجدد
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### مشکل: Backend Start نمی‌شود
```bash
# بررسی Port 8000
netstat -ano | findstr :8000

# بررسی Dependencies
cd backend
pip install -r requirements.txt
```

### مشکل: CORS Error
- بررسی کنید که Backend روی Port 8000 اجرا می‌شود
- در `backend/main.py` CORS تنظیم شده است

---

## 📝 نکات

1. **اولین بار**: Backend باید قبل از Frontend Start شود
2. **Docker**: تمام سرویس‌ها به صورت خودکار Start می‌شوند
3. **Development**: Frontend به `http://localhost:8000` متصل می‌شود

---

**آماده استفاده!** 🎉

