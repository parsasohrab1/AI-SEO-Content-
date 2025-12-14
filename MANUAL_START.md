# راه‌اندازی دستی سرویس‌ها

## ⚠️ سرویس‌ها در حال اجرا نیستند

لطفاً به صورت دستی راه‌اندازی کنید:

---

## 🚀 راه‌اندازی Backend

### Terminal 1 (PowerShell یا CMD):

```bash
# رفتن به دایرکتوری Backend
cd "c:\Users\asus\Documents\companies\ithub\AI\products\clones\ai seo & content\AI-SEO-Content-\backend"

# فعال‌سازی Virtual Environment
.\venv\Scripts\activate

# نصب Dependencies (اگر نصب نشده)
pip install fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml

# راه‌اندازی Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**باید ببینید:**
```
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**سپس در Browser تست کنید:**
- http://localhost:8002/health

---

## 🎨 راه‌اندازی Frontend

### Terminal 2 (PowerShell یا CMD جدید):

```bash
# رفتن به دایرکتوری Frontend
cd "c:\Users\asus\Documents\companies\ithub\AI\products\clones\ai seo & content\AI-SEO-Content-\frontend"

# نصب Dependencies (اگر نصب نشده)
npm install

# راه‌اندازی Frontend
npm run dev -- -p 3002
```

**باید ببینید:**
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3002
  - Ready in Xs
```

**سپس در Browser باز کنید:**
- http://localhost:3002

---

## ✅ بررسی

### 1. Backend
باز کنید: http://localhost:8002/health

باید ببینید:
```json
{
  "status": "healthy",
  "service": "AI Content Factory Pro",
  "version": "1.0.0"
}
```

### 2. Frontend
باز کنید: http://localhost:3002

باید صفحه اصلی با فرم ورود URL را ببینید.

---

## 🔧 اگر خطا می‌بینید

### Backend خطا می‌دهد:

**خطا: Module not found**
```bash
pip install -r requirements.txt
```

**خطا: Port already in use**
```bash
# تغییر Port
uvicorn main:app --reload --host 0.0.0.0 --port 8003
# سپس در Frontend هم Port را تغییر دهید
```

### Frontend خطا می‌دهد:

**خطا: Port 3002 already in use**
```bash
# تغییر Port
npm run dev -- -p 3003
```

**خطا: Cannot find module**
```bash
# حذف و نصب مجدد
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 نکات مهم

1. **هر سرویس در Terminal جداگانه**: Backend و Frontend باید در Terminal‌های جداگانه اجرا شوند
2. **Virtual Environment**: برای Backend باید فعال باشد
3. **Ports**: 
   - Backend: 8002
   - Frontend: 3002
4. **اول Backend، بعد Frontend**: همیشه Backend را قبل از Frontend Start کنید

---

## 🆘 اگر هنوز مشکل دارید

1. **بررسی Python:**
   ```bash
   python --version  # باید 3.10+ باشد
   ```

2. **بررسی Node.js:**
   ```bash
   node --version  # باید 20+ باشد
   ```

3. **بررسی Ports:**
   ```bash
   netstat -ano | findstr ":8002 :3002"
   ```

4. **لاگ‌ها را بررسی کنید:**
   - Backend: Terminal که uvicorn را اجرا می‌کند
   - Frontend: Terminal که npm run dev را اجرا می‌کند

---

**لطفاً این مراحل را دنبال کنید و Terminal‌ها را باز نگه دارید!** 🚀

