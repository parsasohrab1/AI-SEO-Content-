# نحوه دسترسی به داشبورد

## 🚀 سرویس‌ها راه‌اندازی شدند

Backend و Frontend در پنجره‌های جداگانه باز شده‌اند.

---

## 🌐 آدرس‌های دسترسی

### 1. Frontend Dashboard
**URL**: http://localhost:3002

این صفحه اصلی است که می‌توانید:
- URL سایت را وارد کنید
- تحلیل را شروع کنید
- به Dashboard دسترسی پیدا کنید

### 2. Backend API
**URL**: http://localhost:8002

**Endpoints مهم:**
- Health Check: http://localhost:8002/health
- API Docs: http://localhost:8002/api/docs
- Analyze Site: http://localhost:8002/analyze-site (POST)

---

## 📱 استفاده از داشبورد

### گام 1: باز کردن Frontend
```
http://localhost:3002
```

### گام 2: وارد کردن URL سایت
مثلاً: `https://example.com`

### گام 3: کلیک روی "شروع تحلیل"

### گام 4: مشاهده Dashboard
بعد از شروع تحلیل، می‌توانید به Dashboard دسترسی پیدا کنید:
```
http://localhost:3002/dashboard/[analysis_id]
```

---

## 🔍 بررسی وضعیت

### اگر Frontend باز نمی‌شود:

1. **بررسی پنجره Terminal:**
   - باید پیام "Ready" را ببینید
   - باید "Local: http://localhost:3002" را ببینید

2. **بررسی Port:**
   ```bash
   netstat -ano | findstr :3002
   ```

3. **راه‌اندازی مجدد:**
   ```bash
   cd frontend
   npm run dev -- -p 3002
   ```

### اگر Backend پاسخ نمی‌دهد:

1. **بررسی پنجره Terminal:**
   - باید پیام "Uvicorn running on http://0.0.0.0:8002" را ببینید

2. **بررسی Health:**
   ```
   http://localhost:8002/health
   ```

3. **راه‌اندازی مجدد:**
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

---

## ⚠️ مشکلات رایج

### CORS Error
- مطمئن شوید Backend روی `0.0.0.0` اجرا می‌شود (نه `127.0.0.1`)
- بررسی کنید که `NEXT_PUBLIC_API_URL` درست است

### Connection Refused
- بررسی کنید که هر دو سرویس در حال اجرا هستند
- بررسی کنید که Ports درست هستند (8002 و 3002)

### Module Not Found
- Dependencies را نصب کنید:
  ```bash
  # Backend
  cd backend
  pip install -r requirements.txt
  
  # Frontend
  cd frontend
  npm install
  ```

---

## 📝 پورت‌های نهایی

- **Frontend**: 3002
- **Backend**: 8002

---

**لطفاً http://localhost:3002 را در Browser باز کنید!** 🌐

