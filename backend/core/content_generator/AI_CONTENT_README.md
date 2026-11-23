# راهنمای AI Content Generator

## 📋 معرفی

این ماژول تولید محتوا با استفاده از OpenAI GPT-4 را انجام می‌دهد. با تحلیل محتوای رقبا و معیارهای کلمات کلیدی، محتوای بهینه برای SEO تولید می‌کند.

## ✨ Features

- ✅ استفاده از OpenAI GPT-4
- ✅ تحلیل محتوای رقبا
- ✅ تولید محتوای بهینه برای SEO
- ✅ استفاده طبیعی از کلمات کلیدی
- ✅ محاسبه SEO Score
- ✅ محاسبه Keyword Density
- ✅ محاسبه Readability
- ✅ تولید خودکار FAQ
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 نصب

### وابستگی‌های مورد نیاز

```bash
pip install openai
```

یا از requirements.txt:
```bash
pip install -r requirements.txt
```

### تنظیمات

```bash
# در فایل .env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview  # اختیاری
```

## 📖 استفاده

### مثال 1: تولید ساده

```python
from backend.core.content_generator import AIContentGenerator

generator = AIContentGenerator()

result = await generator.generate_article(
    keyword="seo optimization",
    target_length=1500,
    language='en'
)

print(f"Title: {result['title']}")
print(f"Content: {result['content']}")
print(f"SEO Score: {result['seo_score']}/100")
```

### مثال 2: تولید با معیارهای کلمه کلیدی

```python
keyword_metrics = {
    'search_volume': 12000,
    'difficulty': 65,
    'competition': 'high',
    'cpc': 2.5
}

result = await generator.generate_article(
    keyword="seo optimization",
    keyword_metrics=keyword_metrics,
    target_length=2000,
    language='en'
)
```

### مثال 3: تولید با تحلیل رقبا

```python
competitor_content = [
    {
        'title': 'SEO Optimization Guide',
        'content': 'Basic SEO tips...',
        'word_count': 1200
    }
]

result = await generator.generate_article(
    keyword="seo optimization",
    competitor_content=competitor_content,
    target_length=2000,
    language='en'
)
```

### مثال 4: تولید محتوای فارسی

```python
result = await generator.generate_article(
    keyword="بهینه‌سازی سئو",
    target_length=1500,
    language='fa',
    tone='professional'
)
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'content': str,                    # محتوای کامل
    'title': str,                      # عنوان
    'meta_description': str,            # Meta Description
    'seo_score': float,                # SEO Score (0-100)
    'keyword_density': float,          # Keyword Density (%)
    'readability': float,              # Readability Score (0-100)
    'word_count': int,                 # تعداد کلمات
    'headings': List[str],             # لیست Headings
    'faq': List[Dict],                 # FAQ
    'recommendations': List[str],      # توصیه‌ها
    'keyword': str,
    'language': str
}
```

## 🎯 پارامترها

### generate_article()

- `keyword` (str): کلمه کلیدی اصلی
- `keyword_metrics` (Dict, optional): معیارهای کلمه کلیدی
  - `search_volume`: حجم جستجو
  - `difficulty`: سختی (0-100)
  - `competition`: سطح رقابت
  - `cpc`: هزینه هر کلیک
- `competitor_content` (List[Dict], optional): محتوای رقبا
- `target_length` (int): طول هدف (تعداد کلمات)
- `language` (str): زبان ('fa' یا 'en')
- `tone` (str): لحن ('professional', 'casual', 'friendly')
- `include_faq` (bool): شامل FAQ باشد

## 📈 SEO Score

SEO Score بر اساس فاکتورهای زیر محاسبه می‌شود:

- **Title** (10%): وجود عنوان
- **Meta Description** (10%): وجود و طول مناسب
- **H1** (10%): وجود H1
- **Headings** (15%): تعداد Headings
- **Keyword Density** (20%): تراکم کلمه کلیدی (1-2.5% ایده‌آل)
- **Content Length** (15%): طول محتوا
- **Keyword in Title** (10%): استفاده از کلمه کلیدی در عنوان
- **Keyword in Meta** (10%): استفاده از کلمه کلیدی در Meta Description

**تفسیر:**
- 80-100: عالی
- 60-80: خوب
- 40-60: متوسط
- 0-40: نیاز به بهبود

## 📝 Keyword Density

Keyword Density نشان می‌دهد که چند درصد از کلمات محتوا، کلمه کلیدی هستند.

**محدوده ایده‌آل:**
- 1.0% - 2.5%: ایده‌آل
- 0.5% - 1.0% یا 2.5% - 3.5%: قابل قبول
- کمتر از 0.5% یا بیشتر از 3.5%: نیاز به بهبود

## 📖 Readability

Readability Score نشان می‌دهد که محتوا چقدر خوانا است.

**تفسیر:**
- 80-100: بسیار خوانا
- 60-80: خوانا
- 40-60: متوسط
- 0-40: سخت

## 📝 مثال کامل

```python
import asyncio
from backend.core.content_generator import AIContentGenerator

async def main():
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        return
    
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65
    }
    
    result = await generator.generate_article(
        keyword="seo optimization",
        keyword_metrics=keyword_metrics,
        target_length=2000,
        language='en'
    )
    
    print(f"Title: {result['title']}")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Word Count: {result['word_count']}")
    
    # نمایش FAQ
    for faq in result['faq']:
        print(f"Q: {faq['question']}")
        print(f"A: {faq['answer']}")

asyncio.run(main())
```

## 🎯 کاربردها

### 1. تولید محتوای SEO
- تولید محتوای بهینه برای SEO
- استفاده طبیعی از کلمات کلیدی
- ساختار مناسب

### 2. رقابت با رقبا
- تحلیل محتوای رقبا
- تولید محتوای بهتر و کامل‌تر
- ارائه اطلاعات جدید

### 3. تولید سریع محتوا
- تولید خودکار محتوا
- صرفه‌جویی در زمان
- کیفیت بالا

## ⚠️ محدودیت‌ها

### هزینه
- OpenAI API هزینه‌بر است
- هر درخواست credit مصرف می‌کند
- از مدل‌های ارزان‌تر برای تست استفاده کنید

### کیفیت
- کیفیت به prompt وابسته است
- ممکن است نیاز به ویرایش داشته باشد
- همیشه محتوا را بررسی کنید

### Rate Limiting
- OpenAI Rate Limiting دارد
- بین درخواست‌ها delay اضافه کنید

## 🔧 تنظیمات

### تغییر مدل

```python
# در environment variables
OPENAI_MODEL=gpt-4-turbo-preview  # یا gpt-3.5-turbo
```

### تغییر Temperature

در کد می‌توانید temperature را تغییر دهید (پیش‌فرض: 0.7)

### تغییر Max Tokens

Max Tokens به صورت خودکار بر اساس target_length محاسبه می‌شود.

## 💡 بهترین روش‌ها

1. **استفاده از معیارها**: همیشه keyword_metrics را ارائه دهید
2. **تحلیل رقبا**: competitor_content را برای تولید محتوای بهتر استفاده کنید
3. **ویرایش**: همیشه محتوا را ویرایش و بررسی کنید
4. **SEO Score**: هدف SEO Score بالای 80 باشد

## 📚 منابع

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GPT-4 Guide](https://platform.openai.com/docs/guides/gpt)
- [SEO Content Writing](https://ahrefs.com/blog/seo-content-writing/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

