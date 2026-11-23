# راهنمای راه‌اندازی - AI Content Factory Pro

## 🚀 Quick Start

### Prerequisites
- Docker و Docker Compose
- Python 3.11+ (برای توسعه محلی)
- Node.js 20+ (برای توسعه Frontend)

### راه‌اندازی با Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd AI-SEO-Content-

# راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# View logs
docker-compose logs -f
```

### دسترسی به سرویس‌ها
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Frontend Dashboard:** http://localhost:3002
- **RabbitMQ Management:** http://localhost:15672 (admin/admin)
- **PostgreSQL:** localhost:5432
- **MongoDB:** localhost:27017
- **Redis:** localhost:6379

## 🛠️ توسعه محلی

### Backend

```bash
cd backend

# ایجاد Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# نصب Dependencies
pip install -r requirements.txt

# کپی فایل .env
cp .env.example .env
# ویرایش .env و تنظیم مقادیر

# اجرای سرور
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

# نصب Dependencies
npm install

# اجرای Development Server
npm run dev
```

## 📝 تست‌ها

```bash
# نصب Dependencies تست
pip install -r tests/requirements.txt

# اجرای تست‌ها
pytest

# با Coverage
pytest --cov=. --cov-report=html
```

## 🔧 تنظیمات

### Environment Variables

فایل `.env.example` را کپی کرده و مقادیر را تنظیم کنید:

```bash
cp backend/.env.example backend/.env
```

### Database Migration

```bash
# در آینده اضافه می‌شود
```

## 📚 Documentation

- **فازبندی:** `PHASE_PLAN.md`
- **چک‌لیست:** `IMPLEMENTATION_CHECKLIST.md`
- **خلاصه اجرایی:** `EXECUTIVE_SUMMARY.md`

## ⚠️ مشکلات رایج

### Port در حال استفاده است
```bash
# تغییر Port در docker-compose.yml
# یا توقف سرویس استفاده‌کننده از Port
```

### خطای Connection به Database
```bash
# بررسی اجرای سرویس‌ها
docker-compose ps

# Restart
docker-compose restart
```

## 🆘 پشتیبانی

برای مشکلات و سوالات، Issue ایجاد کنید.

