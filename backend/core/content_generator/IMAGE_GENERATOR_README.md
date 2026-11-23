# Image Content Generator

تولید تصاویر بهینه برای SEO با استفاده از DALL-E 3 یا Stable Diffusion

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
pip install openai replicate pillow httpx
```

### 2. تنظیم API Keys

In the `.env` file:

```env
# برای DALL-E 3
OPENAI_API_KEY=your_openai_api_key

# برای Stable Diffusion (Replicate)
REPLICATE_API_TOKEN=your_replicate_api_token
```

### 3. نصب PIL (Pillow)

برای بهینه‌سازی تصاویر:

```bash
pip install pillow
```

---

## 💻 استفاده

### مثال ساده

```python
from image_generator import ImageContentGenerator

generator = ImageContentGenerator()

# تولید تصویر
result = await generator.generate_seo_image(
    keyword="سئو سایت",
    style="professional",
    language="fa"
)

print(f"Image URL: {result['image_url']}")
print(f"Alt Text: {result['alt_text']}")
```

### مثال پیشرفته

```python
result = await generator.generate_seo_image(
    keyword="بهینه‌سازی موتور جستجو",
    article_content="مقاله کامل درباره سئو...",
    style="modern",
    size="1792x1024",
    model="dalle",  # یا "stable_diffusion"
    language="fa"
)
```

---

## ✨ Features

### 1. تولید تصویر با DALL-E 3

- استفاده از مدل `dall-e-3`
- کیفیت بالا
- پشتیبانی از ابعاد مختلف

### 2. تولید تصویر با Stable Diffusion

- استفاده از Replicate API
- مدل: `stability-ai/stable-diffusion`
- گزینه جایگزین برای DALL-E

### 3. تولید Alt Text خودکار

- استخراج از keyword و محتوا
- محدود به 125 کاراکتر
- بهینه برای SEO

### 4. نام فایل بهینه

- استفاده از keyword
- حذف کاراکترهای غیرمجاز
- فرمت: `keyword-timestamp.webp`

### 5. بهینه‌سازی تصویر

- تبدیل به فرمت WebP
- فشرده‌سازی با کیفیت 85%
- کاهش حجم فایل

### 6. ابعاد مناسب

- `1024x1024` (مربع)
- `1792x1024` (عریض)
- `1024x1792` (بلند)

---

## ⚙️ پیکربندی

### استایل‌های موجود

- `professional`: حرفه‌ای و تمیز
- `artistic`: هنری و خلاقانه
- `modern`: مدرن و معاصر
- `minimalist`: مینیمال و ساده
- `illustrated`: تصویرسازی دستی
- `photorealistic`: فوتورئالیستیک

### مدل‌های موجود

- `dalle`: DALL-E 3 (پیش‌فرض)
- `stable_diffusion`: Stable Diffusion

### زبان‌های پشتیبانی شده

- `fa`: فارسی
- `en`: انگلیسی

---

## 📊 ساختار خروجی

```python
{
    'image_url': str,          # URL تصویر
    'image_path': str,         # مسیر فایل
    'alt_text': str,           # Alt text
    'filename': str,           # نام فایل
    'width': int,              # عرض
    'height': int,             # ارتفاع
    'format': str,             # فرمت (webp)
    'file_size': int,          # حجم فایل (bytes)
    'seo_optimized': bool,     # بهینه برای SEO
    'model_used': str,         # مدل استفاده شده
    'keyword': str             # کلمه کلیدی
}
```

---

## 📝 مثال‌ها

### مثال 1: تصویر ساده

```python
result = await generator.generate_seo_image(
    keyword="سئو سایت",
    style="professional",
    language="fa"
)
```

### مثال 2: تصویر با محتوا

```python
article_content = """
سئو سایت یکی از مهم‌ترین روش‌های بازاریابی دیجیتال است.
"""

result = await generator.generate_seo_image(
    keyword="بهینه‌سازی موتور جستجو",
    article_content=article_content,
    style="modern",
    language="fa"
)
```

### مثال 3: تصویر با ابعاد خاص

```python
result = await generator.generate_seo_image(
    keyword="طراحی وب",
    style="artistic",
    size="1792x1024",
    language="fa"
)
```

### مثال 4: استفاده از Stable Diffusion

```python
result = await generator.generate_seo_image(
    keyword="محتوای دیجیتال",
    style="illustrated",
    model="stable_diffusion",
    language="fa"
)
```

---

## 🔧 عیب‌یابی

### مشکل: "No image generation model available"

**Solution:**
1. بررسی API keys در `.env`
2. نصب پکیج‌های لازم:
   ```bash
   pip install openai replicate
   ```

### مشکل: "PIL not available"

**Solution:**
```bash
pip install pillow
```

### مشکل: تصویر به WebP تبدیل نمی‌شود

**Solution:**
- بررسی نصب Pillow
- بررسی دسترسی نوشتن در پوشه `generated_content/images`

---

## 📈 بهینه‌سازی SEO

### 1. Alt Text

- حداکثر 125 کاراکتر
- شامل keyword
- توصیفی و واضح

### 2. نام فایل

- استفاده از keyword
- حذف کاراکترهای خاص
- فرمت: `keyword-timestamp.webp`

### 3. ابعاد تصویر

- مناسب برای وب
- نسبت مناسب
- کیفیت بالا

### 4. فرمت WebP

- حجم کمتر
- کیفیت بهتر
- پشتیبانی از مرورگرهای مدرن

---

## 🔗 منابع

- [OpenAI DALL-E 3](https://platform.openai.com/docs/guides/images)
- [Replicate Stable Diffusion](https://replicate.com/stability-ai/stable-diffusion)
- [WebP Format](https://developers.google.com/speed/webp)

---

## 📝 نکات مهم

1. **هزینه API**: DALL-E 3 و Stable Diffusion API هزینه دارند
2. **Rate Limiting**: مراقب محدودیت‌های API باشید
3. **ذخیره‌سازی**: تصاویر در `backend/generated_content/images` ذخیره می‌شوند
4. **بهینه‌سازی**: تصاویر به صورت خودکار به WebP تبدیل می‌شوند

---

## ✅ چک‌لیست استفاده

- [ ] نصب وابستگی‌ها
- [ ] تنظیم API keys
- [ ] تست تولید تصویر ساده
- [ ] بررسی Alt text
- [ ] بررسی نام فایل
- [ ] بررسی فرمت WebP
- [ ] تست با استایل‌های مختلف

