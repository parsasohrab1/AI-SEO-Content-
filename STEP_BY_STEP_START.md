# راه‌اندازی گام به گام - AI Content Factory Pro

## ⚠️ مشکل: ERR_CONNECTION_REFUSED

این خطا یعنی سرویس‌ها در حال اجرا نیستند. لطفاً این مراحل را دنبال کنید:

---

## 🚀 راه‌اندازی Backend (گام 1)

### Terminal 1: PowerShell یا CMD را باز کنید

```powershell
# 1. رفتن به دایرکتوری Backend
cd "c:\Users\asus\Documents\companies\ithub\AI\products\clones\ai seo & content\AI-SEO-Content-\backend"

# 2. فعال‌سازی Virtual Environment
.\venv\Scripts\activate

# اگر venv وجود ندارد:
# python -m venv venv
# .\venv\Scripts\activate

# 3. نصب Dependencies (فقط اولین بار)
pip install fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml

# 4. راه‌اندازی Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**باید ببینید:**
```
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**✅ اگر این پیام را دیدید، Backend در حال اجرا است!**

**تست کنید:**
- Browser باز کنید: http://localhost:8002/health
- باید ببینید: `{"status":"healthy","service":"AI Content Factory Pro"}`

---

## 🎨 راه‌اندازی Frontend (گام 2)

### Terminal 2: PowerShell یا CMD جدید باز کنید

```powershell
# 1. رفتن به دایرکتوری Frontend
cd "c:\Users\asus\Documents\companies\ithub\AI\products\clones\ai seo & content\AI-SEO-Content-\frontend"

# 2. نصب Dependencies (فقط اولین بار)
npm install

# 3. راه‌اندازی Frontend
npm run dev -- -p 3002
```

**باید ببینید:**
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3002
  - Ready in Xs
```

**✅ اگر این پیام را دیدید، Frontend در حال اجرا است!**

**تست کنید:**
- Browser باز کنید: http://localhost:3002
- باید صفحه اصلی با فرم ورود URL را ببینید

---

## ✅ بررسی نهایی

### 1. Backend
```
http://localhost:8002/health
```
باید ببینید: `{"status":"healthy"}`

### 2. Frontend
```
http://localhost:3002
```
باید صفحه اصلی را ببینید

---

## 🔧 مشکلات رایج

### Backend Start نمی‌شود:

**خطا: Module not found**
```bash
pip install fastapi uvicorn[standard] pydantic httpx beautifulsoup4 lxml
```

**خطا: Port already in use**
```bash
# تغییر Port
uvicorn main:app --reload --host 0.0.0.0 --port 8003
# سپس در Frontend هم Port را تغییر دهید
```

**خطا: Virtual Environment فعال نیست**
```bash
.\venv\Scripts\activate
# باید (venv) در ابتدای خط ببینید
```

### Frontend Start نمی‌شود:

**خطا: Cannot find module**
```bash
npm install
```

**خطا: Port 3002 already in use**
```bash
# تغییر Port
npm run dev -- -p 3003
```

---

## 📝 نکات مهم

1. **دو Terminal جداگانه**: Backend و Frontend باید در Terminal‌های جداگانه باشند
2. **اول Backend**: همیشه Backend را قبل از Frontend Start کنید
3. **Terminal‌ها را باز نگه دارید**: اگر Terminal را ببندید، سرویس متوقف می‌شود
4. **Virtual Environment**: برای Backend باید فعال باشد (باید `(venv)` ببینید)

---

## 🎯 خلاصه

1. ✅ Terminal 1: Backend روی Port 8002
2. ✅ Terminal 2: Frontend روی Port 3002
3. ✅ Browser: http://localhost:3002

---

**لطفاً این مراحل را دنبال کنید و Terminal‌ها را باز نگه دارید!** 🚀

اگر هنوز مشکل دارید، لاگ‌های Terminal را بررسی کنید.

