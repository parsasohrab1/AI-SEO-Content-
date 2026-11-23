# راهنمای رفع مشکلات - ERR_CONNECTION_REFUSED

## 🔍 تشخیص مشکل

اگر خطای `ERR_CONNECTION_REFUSED` می‌بینید، یعنی:
- سرویس در حال اجرا نیست
- یا روی پورت دیگری اجرا می‌شود
- یا Firewall مانع می‌شود

---

## ✅ راه‌حل‌های سریع

### روش 1: استفاده از Scripts (Windows)

```bash
# راه‌اندازی Backend و Frontend با یک کلیک
start-all.bat
```

یا به صورت جداگانه:
```bash
# فقط Backend
start-backend.bat

# فقط Frontend (در Terminal جدید)
start-frontend.bat
```

---

### روش 2: راه‌اندازی دستی

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (در Terminal جدید)
```bash
cd frontend
npm install
npm run dev -- -p 3002
```

---

## 🔍 بررسی وضعیت

### بررسی Backend
```bash
# در Browser
http://localhost:8000/health

# یا با curl
curl http://localhost:8000/health
```

### بررسی Frontend
```bash
# در Browser
http://localhost:3002
```

### بررسی Ports
```bash
# Windows PowerShell
netstat -ano | findstr :8000
netstat -ano | findstr :3002
```

---

## ⚠️ مشکلات رایج

### مشکل 1: Port در حال استفاده است

**علائم:**
- خطای "Address already in use"
- یا سرویس Start نمی‌شود

**راهکار:**
```bash
# پیدا کردن Process
netstat -ano | findstr :8000

# Kill کردن Process (PID را از خروجی بالا بگیرید)
taskkill /PID <PID> /F

# یا تغییر Port در docker-compose.yml
```

### مشکل 2: Python یا Node.js نصب نیست

**راهکار:**
- Python 3.11+ نصب کنید: https://www.python.org/downloads/
- Node.js 20+ نصب کنید: https://nodejs.org/

### مشکل 3: Dependencies نصب نشده

**راهکار:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### مشکل 4: Virtual Environment فعال نیست

**راهکار:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### مشکل 5: Docker Desktop اجرا نیست

**راهکار:**
- Docker Desktop را از Start Menu اجرا کنید
- منتظر بمانید تا Docker Engine شروع شود
- سپس `docker-compose up -d` را اجرا کنید

---

## 🚀 راه‌اندازی سریع (Recommended)

### Windows
```bash
# فقط این فایل را اجرا کنید
start-all.bat
```

### Linux/Mac
```bash
# Backend
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload &

# Frontend
cd frontend && npm install && npm run dev -- -p 3002 &
```

---

## 📊 Checklist

قبل از اجرا، مطمئن شوید:
- [ ] Python 3.11+ نصب است
- [ ] Node.js 20+ نصب است
- [ ] Port 8000 آزاد است
- [ ] Port 3002 آزاد است
- [ ] Dependencies نصب شده‌اند
- [ ] Virtual Environment فعال است (برای Backend)

---

## 🆘 اگر هنوز مشکل دارید

1. **لاگ‌ها را بررسی کنید:**
   - Backend: Terminal که uvicorn را اجرا می‌کند
   - Frontend: Terminal که npm run dev را اجرا می‌کند

2. **Firewall را بررسی کنید:**
   - Windows Firewall ممکن است مانع شود
   - Antivirus را بررسی کنید

3. **Ports را بررسی کنید:**
   ```bash
   netstat -ano | findstr "8000 3002"
   ```

4. **از Scripts استفاده کنید:**
   - `start-all.bat` برای راه‌اندازی سریع

---

**موفق باشید!** 🚀

