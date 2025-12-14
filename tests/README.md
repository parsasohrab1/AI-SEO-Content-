# تست‌های سیستم - AI Content Factory Pro

این پوشه شامل تمام تست‌های سیستم برای فاز 3 است.

## 📁 ساختار

```
tests/
├── unit/              # تست‌های واحد
├── integration/       # تست‌های یکپارچه‌سازی
│   ├── test_pipeline_e2e.py
│   └── test_service_communication.py
├── e2e/              # تست‌های End-to-End
├── performance/      # تست‌های عملکرد
│   ├── load_test.py
│   └── k6_load_test.js
├── security/         # تست‌های امنیتی
│   └── security_tests.py
└── fixtures/         # داده‌های تست
    └── mock_data.py
```

## 🧪 انواع تست‌ها

### Unit Tests
تست‌های واحد برای هر کامپوننت به صورت جداگانه

### Integration Tests
تست ارتباط بین سرویس‌ها و ماژول‌ها

### E2E Tests
تست کامل Pipeline از URL تا Dashboard

### Performance Tests
Load Testing برای 100، 500، 1000 سایت همزمان

### Security Tests
تست‌های امنیتی شامل SQL Injection، XSS، Authentication

## 🚀 اجرای تست‌ها

### نصب Dependencies
```bash
pip install -r tests/requirements.txt
```

### اجرای تمام تست‌ها
```bash
pytest
```

### اجرای تست‌های خاص
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Security tests
pytest tests/security/ -v

# Performance tests
pytest tests/performance/ -v
```

### اجرای با Coverage
```bash
pytest --cov=. --cov-report=html
```

### Load Testing با Locust
```bash
locust -f tests/performance/load_test.py --host=http://localhost:8000
```

### Load Testing با K6
```bash
k6 run tests/performance/k6_load_test.js
```

## 📊 Coverage

هدف: حداقل 80% Code Coverage

برای مشاهده Coverage Report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 🔒 Security Testing

### Bandit (Static Analysis)
```bash
bandit -r . -f json
```

### Safety (Dependency Check)
```bash
safety check
```

## 📝 Test Data

داده‌های Mock در `tests/fixtures/mock_data.py` قرار دارند.

## ⚙️ Configuration

تنظیمات pytest در `pytest.ini` قرار دارد.

## 🔄 CI/CD

تست‌ها به صورت خودکار در GitHub Actions اجرا می‌شوند.
فایل تنظیمات: `.github/workflows/test.yml`
