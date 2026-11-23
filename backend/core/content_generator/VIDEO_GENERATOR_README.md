# Video Content Generator

تولید ویدیو بهینه برای SEO با استفاده از Lumen5، Synthesia یا MoviePy (Fallback)

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
pip install moviepy pillow httpx aiofiles
```

### 2. نصب FFmpeg

برای استفاده از MoviePy، نیاز به FFmpeg دارید:

**Windows:**
```bash
# دانلود از https://ffmpeg.org/download.html
# یا استفاده از chocolatey
choco install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. تنظیم API Keys (اختیاری)

In the `.env` file:

```env
# برای Lumen5
LUMEN5_API_KEY=your_lumen5_api_key

# برای Synthesia
SYNTHESIA_API_KEY=your_synthesia_api_key
```

**نکته:** اگر API keys ندارید، از MoviePy (fallback) استفاده می‌شود.

---

## 💻 استفاده

### مثال ساده

```python
from video_generator import VideoContentGenerator

generator = VideoContentGenerator()

# تولید ویدیو
result = await generator.generate_video(
    article_content="محتوای مقاله...",
    keyword="سئو سایت",
    duration=60,
    language="fa"
)

print(f"Video URL: {result['video_url']}")
print(f"Title: {result['title']}")
```

### مثال پیشرفته

```python
result = await generator.generate_video(
    article_content="محتوای کامل مقاله...",
    keyword="بهینه‌سازی موتور جستجو",
    duration=90,
    model="lumen5",  # یا "synthesia" یا "moviepy"
    language="fa",
    include_subtitles=True,
    style="professional"
)
```

---

## ✨ Features

### 1. تولید ویدیو با Lumen5

- استفاده از Lumen5 API
- کیفیت بالا
- استایل‌های مختلف

### 2. تولید ویدیو با Synthesia

- استفاده از Synthesia API
- پشتیبانی از زبان‌های مختلف
- آواتارهای AI

### 3. تولید ویدیو با MoviePy (Fallback)

- بدون نیاز به API
- رایگان
- مناسب برای ویدیوهای ساده

### 4. زیرنویس خودکار

- فرمت SRT
- همگام‌سازی با ویدیو
- پشتیبانی از چند زبان

### 5. Thumbnail Generator

- تولید خودکار thumbnail
- بهینه برای YouTube
- شامل عنوان و keyword

### 6. بهینه‌سازی YouTube SEO

- عنوان بهینه
- توضیحات کامل
- تگ‌های مرتبط
- فرمت مناسب

---

## ⚙️ پیکربندی

### مدل‌های موجود

- `lumen5`: Lumen5 API (نیاز به API key)
- `synthesia`: Synthesia API (نیاز به API key)
- `moviepy`: MoviePy (fallback، رایگان)

### استایل‌های موجود

- `professional`: حرفه‌ای
- `modern`: مدرن
- `creative`: خلاقانه
- `educational`: آموزشی

### زبان‌های پشتیبانی شده

- `fa`: فارسی
- `en`: انگلیسی

---

## 📊 ساختار خروجی

```python
{
    'video_url': str,              # URL ویدیو
    'video_path': str,             # مسیر فایل
    'thumbnail_url': str,           # URL thumbnail
    'thumbnail_path': str,          # مسیر thumbnail
    'subtitles_path': str,          # مسیر فایل زیرنویس (SRT)
    'title': str,                   # عنوان بهینه برای YouTube
    'description': str,             # توضیحات بهینه برای YouTube
    'tags': List[str],              # تگ‌های YouTube
    'duration': int,                # مدت زمان (ثانیه)
    'format': str,                  # فرمت (mp4)
    'file_size': int,               # حجم فایل (bytes)
    'youtube_optimized': bool,      # بهینه برای YouTube
    'model_used': str,              # مدل استفاده شده
    'keyword': str,                 # کلمه کلیدی
    'width': int,                   # عرض
    'height': int                   # ارتفاع
}
```

---

## 📝 مثال‌ها

### مثال 1: ویدیو ساده

```python
result = await generator.generate_video(
    article_content="محتوای مقاله...",
    keyword="سئو سایت",
    duration=60,
    language="fa"
)
```

### مثال 2: ویدیو با Lumen5

```python
result = await generator.generate_video(
    article_content="محتوای کامل...",
    keyword="بهینه‌سازی",
    duration=90,
    model="lumen5",
    style="modern",
    language="fa"
)
```

### مثال 3: ویدیو با زیرنویس

```python
result = await generator.generate_video(
    article_content="محتوای مقاله...",
    keyword="آموزش سئو",
    duration=60,
    include_subtitles=True,
    language="fa"
)
```

### مثال 4: ویدیو انگلیسی

```python
result = await generator.generate_video(
    article_content="Article content...",
    keyword="SEO optimization",
    duration=120,
    language="en",
    include_subtitles=True
)
```

---

## 🎬 ساختار ویدیو

### اسکریپت ویدیو

ویدیو به صورت خودکار از محتوای مقاله استخراج می‌شود:

1. **تقسیم محتوا**: محتوا به بخش‌های مختلف تقسیم می‌شود
2. **محاسبه مدت زمان**: مدت زمان هر بخش بر اساس تعداد کلمات محاسبه می‌شود
3. **ایجاد صحنه‌ها**: هر بخش به یک صحنه تبدیل می‌شود

### زیرنویس

- فرمت: SRT
- همگام‌سازی: خودکار با صحنه‌های ویدیو
- زبان: مطابق با language parameter

### Thumbnail

- ابعاد: 1280x720 (YouTube standard)
- شامل: عنوان و keyword
- فرمت: JPEG

---

## 🔧 عیب‌یابی

### مشکل: "MoviePy not available"

**Solution:**
```bash
pip install moviepy
```

### مشکل: "FFmpeg not found"

**Solution:**
1. نصب FFmpeg (به بخش نصب مراجعه کنید)
2. اضافه کردن FFmpeg به PATH

### مشکل: "No video generation model available"

**Solution:**
1. نصب MoviePy (fallback)
2. یا تنظیم API keys برای Lumen5/Synthesia

### مشکل: ویدیو خیلی بزرگ است

**Solution:**
- استفاده از `_optimize_video` برای فشرده‌سازی
- کاهش duration
- کاهش کیفیت در MoviePy

---

## 📈 بهینه‌سازی YouTube SEO

### 1. عنوان

- شامل keyword
- حداکثر 100 کاراکتر
- جذاب و واضح

### 2. توضیحات

- شامل خلاصه محتوا
- فهرست مطالب
- تگ‌ها و هشتگ‌ها
- لینک‌های مرتبط

### 3. تگ‌ها

- شامل keyword
- کلمات مرتبط از محتوا
- تگ‌های عمومی
- حداکثر 15 تگ

### 4. Thumbnail

- ابعاد مناسب (1280x720)
- شامل عنوان
- جذاب و واضح

### 5. زیرنویس

- فرمت SRT
- همگام‌سازی دقیق
- کامل و بدون خطا

---

## 🔗 منابع

- [Lumen5 API](https://lumen5.com/api)
- [Synthesia API](https://www.synthesia.io/api)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [YouTube SEO Guide](https://support.google.com/youtube/answer/98772)

---

## 📝 نکات مهم

1. **هزینه API**: Lumen5 و Synthesia API هزینه دارند
2. **مدت زمان**: تولید ویدیو ممکن است چند دقیقه طول بکشد
3. **ذخیره‌سازی**: ویدیوها در `backend/generated_content/videos` ذخیره می‌شوند
4. **بهینه‌سازی**: ویدیوها به صورت خودکار بهینه می‌شوند
5. **FFmpeg**: برای MoviePy نیاز به FFmpeg دارید

---

## ✅ چک‌لیست استفاده

- [ ] نصب وابستگی‌ها
- [ ] نصب FFmpeg
- [ ] تنظیم API keys (اختیاری)
- [ ] تست تولید ویدیو ساده
- [ ] بررسی زیرنویس
- [ ] بررسی Thumbnail
- [ ] تست با مدل‌های مختلف
- [ ] بررسی بهینه‌سازی YouTube

