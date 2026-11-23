# Content Personalizer

شخصی‌سازی محتوا بر اساس مخاطب، Intent و سطح تخصص

## 📋 Table of Contents

- [Installation and Setup](#installation-and-setup)
- [استفاده](#استفاده)
- [Features](#features)
- [پیکربندی](#پیکربندی)
- [مثال‌ها](#مثال‌ها)

---

## 🚀 Installation and Setup

### 1. Install Dependencies

```bash
pip install openai
```

### 2. تنظیم API Key (اختیاری)

In the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

**نکته:** اگر API key ندارید، از rule-based personalization استفاده می‌شود.

---

## 💻 استفاده

### مثال ساده

```python
from content_personalizer import ContentPersonalizer

personalizer = ContentPersonalizer()

target_audience = {
    'type': 'B2B',
    'expertise_level': 'intermediate',
    'industry': 'ecommerce'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای پایه...",
    target_audience=target_audience,
    user_intent='commercial',
    language='fa'
)
```

### مثال پیشرفته

```python
target_audience = {
    'type': 'Technical',
    'expertise_level': 'advanced',
    'industry': 'healthcare',
    'role': 'CTO'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای کامل...",
    target_audience=target_audience,
    user_intent='informational',
    language='fa'
)
```

---

## ✨ Features

### 1. شخصی‌سازی بر اساس مخاطب

- **B2B**: تمرکز بر ROI، مزایای کسب‌وکار، کارایی تیم
- **B2C**: تمرکز بر مزایای شخصی، صرفه‌جویی در زمان
- **Technical**: جزئیات فنی بیشتر، معماری سیستم
- **General**: محتوای عمومی

### 2. شخصی‌سازی بر اساس سطح تخصص

- **Beginner**: توضیحات بیشتر، مثال‌های ساده
- **Intermediate**: محتوای متعادل
- **Advanced**: جزئیات فنی بیشتر، فرض بر دانش قبلی

### 3. شخصی‌سازی بر اساس Intent

- **Informational**: تمرکز بر آموزش و اطلاعات
- **Commercial**: تمرکز بر مقایسه و مزایا
- **Transactional**: تمرکز بر CTA و اقدام

### 4. شخصی‌سازی بر اساس صنعت

- مثال‌های مرتبط با صنعت
- اصطلاحات تخصصی
- کاربردهای خاص

### 5. پشتیبانی از AI و Rule-based

- **AI-based**: استفاده از OpenAI GPT-4 (اگر API key موجود باشد)
- **Rule-based**: استفاده از قوانین (fallback)

---

## ⚙️ پیکربندی

### انواع مخاطب (Audience Type)

- `B2B`: کسب‌وکار به کسب‌وکار
- `B2C`: کسب‌وکار به مصرف‌کننده
- `Technical`: مخاطب فنی
- `General`: مخاطب عمومی

### سطوح تخصص (Expertise Level)

- `beginner`: مبتدی
- `intermediate`: متوسط
- `advanced`: پیشرفته

### انواع Intent

- `informational`: اطلاعاتی
- `commercial`: تجاری
- `transactional`: تراکنشی

### زبان‌های پشتیبانی شده

- `fa`: فارسی
- `en`: انگلیسی

---

## 📊 ساختار target_audience

```python
target_audience = {
    'type': str,              # 'B2B' | 'B2C' | 'Technical' | 'General'
    'expertise_level': str,    # 'beginner' | 'intermediate' | 'advanced'
    'industry': str,          # اختیاری: 'ecommerce', 'healthcare', 'education', etc.
    'role': str               # اختیاری: 'Marketing Manager', 'Developer', etc.
}
```

---

## 📝 مثال‌ها

### مثال 1: B2B با Intent Commercial

```python
target_audience = {
    'type': 'B2B',
    'expertise_level': 'intermediate',
    'industry': 'ecommerce',
    'role': 'Marketing Manager'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای پایه...",
    target_audience=target_audience,
    user_intent='commercial',
    language='fa'
)
```

### مثال 2: B2C با Intent Informational

```python
target_audience = {
    'type': 'B2C',
    'expertise_level': 'beginner',
    'role': 'Individual User'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای پایه...",
    target_audience=target_audience,
    user_intent='informational',
    language='fa'
)
```

### مثال 3: Technical با سطح Advanced

```python
target_audience = {
    'type': 'Technical',
    'expertise_level': 'advanced',
    'role': 'Developer'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای پایه...",
    target_audience=target_audience,
    user_intent='informational',
    language='fa'
)
```

### مثال 4: Transactional Intent

```python
target_audience = {
    'type': 'B2B',
    'expertise_level': 'intermediate',
    'industry': 'healthcare'
}

personalized = await personalizer.personalize_content(
    base_content="محتوای پایه...",
    target_audience=target_audience,
    user_intent='transactional',
    language='fa'
)
```

---

## 🔧 عیب‌یابی

### مشکل: "openai package not installed"

**Solution:**
```bash
pip install openai
```

### مشکل: "Could not initialize OpenAI client"

**Solution:**
1. بررسی API key در `.env`
2. یا استفاده از rule-based personalization (بدون API key)

### مشکل: محتوای شخصی‌سازی شده مناسب نیست

**Solution:**
1. بررسی صحت `target_audience`
2. بررسی صحت `user_intent`
3. استفاده از AI-based personalization (با API key)

---

## 📈 بهینه‌سازی

### 1. استفاده از AI

برای بهترین نتایج، از OpenAI API استفاده کنید:

```env
OPENAI_API_KEY=your_key
```

### 2. تنظیم دقیق target_audience

هرچه اطلاعات بیشتری ارائه دهید، شخصی‌سازی بهتر می‌شود:

```python
target_audience = {
    'type': 'B2B',
    'expertise_level': 'intermediate',
    'industry': 'ecommerce',  # مهم
    'role': 'Marketing Manager'  # مهم
}
```

### 3. انتخاب Intent مناسب

- **Informational**: برای مقالات آموزشی
- **Commercial**: برای صفحات محصول
- **Transactional**: برای صفحات فراخوان به اقدام

---

## 🔗 منابع

- [OpenAI API](https://platform.openai.com/docs)
- [Content Personalization Best Practices](https://www.hubspot.com/marketing-statistics)

---

## 📝 نکات مهم

1. **API Key**: برای استفاده از AI، نیاز به OpenAI API key دارید
2. **Fallback**: در صورت عدم وجود API key، از rule-based استفاده می‌شود
3. **هزینه**: استفاده از OpenAI API هزینه دارد
4. **کیفیت**: AI-based personalization معمولاً بهتر از rule-based است

---

## ✅ چک‌لیست استفاده

- [ ] نصب وابستگی‌ها
- [ ] تنظیم API key (اختیاری)
- [ ] تست شخصی‌سازی ساده
- [ ] تست با انواع مختلف مخاطب
- [ ] تست با سطوح مختلف تخصص
- [ ] تست با Intentهای مختلف
- [ ] بررسی کیفیت محتوای شخصی‌سازی شده

