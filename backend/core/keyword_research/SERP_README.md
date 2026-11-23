# راهنمای SERP Feature Analyzer

## 📋 معرفی

این ماژول تحلیل ویژگی‌های SERP (Search Engine Results Page) را انجام می‌دهد. با استخراج Featured Snippets، People Also Ask، Related Searches و سایر ویژگی‌ها، به شما کمک می‌کند استراتژی SEO خود را بهبود دهید.

## ✨ Features

- ✅ استخراج Featured Snippets
- ✅ استخراج People Also Ask (PAA)
- ✅ استخراج Related Searches
- ✅ استخراج Image Pack
- ✅ استخراج Video Results
- ✅ استخراج Local Pack
- ✅ استخراج Organic Results
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 Usage

### مثال 1: تحلیل ساده

```python
from backend.core.keyword_research import SERPFeatureAnalyzer

analyzer = SERPFeatureAnalyzer()

result = await analyzer.analyze_serp_features(
    keyword="seo optimization",
    language='en',
    location='us'
)

# بررسی Featured Snippet
if result['featured_snippet']['present']:
    print(f"Featured Snippet: {result['featured_snippet']['content']}")

# نمایش People Also Ask
for paa in result['people_also_ask']:
    print(f"Q: {paa['question']}")
```

### مثال 2: تحلیل فارسی

```python
result = await analyzer.analyze_serp_features(
    keyword="سئو",
    language='fa',
    location='ir'
)
```

### مثال 3: دریافت خلاصه

```python
result = await analyzer.analyze_serp_features(keyword="seo")

summary = result['summary']
print(f"Featured Snippet: {summary['featured_snippet_present']}")
print(f"People Also Ask: {summary['people_also_ask_count']} سوال")
print(f"Related Searches: {summary['related_searches_count']}")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'keyword': str,
    'featured_snippet': {
        'present': bool,
        'type': str,  # paragraph, list, table
        'title': str,
        'content': str,
        'source_url': str,
        'source_title': str
    },
    'people_also_ask': [
        {
            'question': str,
            'expanded': bool
        },
        ...
    ],
    'related_searches': List[str],
    'image_pack': {
        'present': bool,
        'images': [
            {
                'url': str,
                'alt': str
            },
            ...
        ],
        'total_count': int
    },
    'video_results': [
        {
            'title': str,
            'url': str,
            'source': str  # youtube, other
        },
        ...
    ],
    'local_pack': {
        'present': bool,
        'businesses': [
            {
                'name': str,
                'address': str,
                'rating': float,
                'phone': str
            },
            ...
        ],
        'map_present': bool
    },
    'organic_results': [
        {
            'title': str,
            'url': str,
            'snippet': str,
            'position': int
        },
        ...
    ],
    'summary': {
        'featured_snippet_present': bool,
        'people_also_ask_count': int,
        'related_searches_count': int,
        'image_pack_present': bool,
        'image_count': int,
        'video_results_count': int,
        'local_pack_present': bool,
        'businesses_count': int,
        'organic_results_count': int,
        'total_features': int
    }
}
```

## 🎯 انواع ویژگی‌های SERP

### 1. Featured Snippet
پاسخ مستقیم Google که در بالای نتایج نمایش داده می‌شود.

**انواع:**
- `paragraph`: متن ساده
- `list`: لیست (numbered یا bulleted)
- `table`: جدول

**استراتژی:**
- محتوای کوتاه و مستقیم (40-60 کلمه)
- پاسخ مستقیم به سوال
- استفاده از لیست یا جدول برای ساختار بهتر

### 2. People Also Ask (PAA)
سوالات مرتبط که کاربران می‌پرسند.

**استراتژی:**
- تولید محتوا برای پاسخ به این سوالات
- استفاده از FAQ Schema
- ساختار H2/H3 برای هر سوال

### 3. Related Searches
جستجوهای مرتبط در پایین صفحه.

**استراتژی:**
- استفاده از این کلمات کلیدی در محتوا
- تولید محتوای مرتبط
- Internal Linking

### 4. Image Pack
بسته تصاویر مرتبط.

**استراتژی:**
- بهینه‌سازی تصاویر
- استفاده از Alt Text مناسب
- استفاده از Schema.org/ImageObject

### 5. Video Results
نتایج ویدیویی.

**استراتژی:**
- تولید ویدیو برای کلمات کلیدی
- بهینه‌سازی YouTube SEO
- استفاده از Video Schema

### 6. Local Pack
نتایج محلی (برای جستجوهای محلی).

**استراتژی:**
- بهینه‌سازی Google My Business
- استفاده از Local Schema
- دریافت Reviews

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import SERPFeatureAnalyzer

async def main():
    analyzer = SERPFeatureAnalyzer()
    
    result = await analyzer.analyze_serp_features(
        keyword="seo optimization",
        language='en'
    )
    
    # Featured Snippet
    if result['featured_snippet']['present']:
        print("✅ Featured Snippet موجود است")
        print(f"نوع: {result['featured_snippet']['type']}")
        print(f"محتوا: {result['featured_snippet']['content'][:200]}")
    
    # People Also Ask
    if result['people_also_ask']:
        print(f"\n❓ {len(result['people_also_ask'])} سوال در People Also Ask:")
        for paa in result['people_also_ask'][:5]:
            print(f"  • {paa['question']}")
    
    # Related Searches
    if result['related_searches']:
        print(f"\n🔍 {len(result['related_searches'])} Related Search:")
        for search in result['related_searches'][:5]:
            print(f"  • {search}")
    
    # خلاصه
    summary = result['summary']
    print(f"\n📊 خلاصه:")
    print(f"  Total Features: {summary['total_features']}/6")
    
    await analyzer.close()

asyncio.run(main())
```

## 🎯 کاربردها

### 1. Content Strategy
- شناسایی نوع محتوای مورد نیاز
- تولید محتوا برای Featured Snippet
- پاسخ به سوالات People Also Ask

### 2. SEO Optimization
- بهینه‌سازی برای Featured Snippet
- استفاده از Related Searches
- بهینه‌سازی تصاویر برای Image Pack

### 3. Competitive Analysis
- تحلیل ویژگی‌های SERP رقبا
- شناسایی فرصت‌ها
- Benchmarking

## ⚠️ محدودیت‌ها

### Rate Limiting
- Google ممکن است درخواست‌های زیاد را محدود کند
- بین درخواست‌ها delay اضافه کنید

### نتایج متغیر
- نتایج SERP ممکن است تغییر کنند
- نتایج ممکن است بر اساس موقعیت جغرافیایی متفاوت باشند

### ساختار HTML
- Google ساختار HTML را تغییر می‌دهد
- ممکن است نیاز به به‌روزرسانی کد باشد

## 🔧 تنظیمات

### تغییر موقعیت جغرافیایی

```python
result = await analyzer.analyze_serp_features(
    keyword="seo",
    language='en',
    location='us'  # یا 'uk', 'ca', 'ir', etc.
)
```

### تغییر زبان

```python
result = await analyzer.analyze_serp_features(
    keyword="سئو",
    language='fa',  # فارسی
    location='ir'
)
```

## 💡 بهترین روش‌ها

1. **تحلیل دوره‌ای**: SERP Features تغییر می‌کنند
2. **مقایسه**: چند کلمه کلیدی را با هم مقایسه کنید
3. **اولویت‌بندی**: روی Featured Snippet و People Also Ask تمرکز کنید
4. **مانیتورینگ**: تغییرات را ردیابی کنید

## 📊 مثال‌های واقعی

### ورودی:
```python
keyword = "seo optimization"
```

### خروجی:
```python
{
    'featured_snippet': {
        'present': True,
        'type': 'paragraph',
        'content': 'SEO optimization is the process...'
    },
    'people_also_ask': [
        {'question': 'What is SEO optimization?'},
        {'question': 'How to optimize SEO?'}
    ],
    'related_searches': [
        'seo optimization tools',
        'seo optimization guide'
    ],
    'image_pack': {
        'present': True,
        'total_count': 20
    },
    'video_results': [
        {'title': 'SEO Optimization Tutorial', 'source': 'youtube'}
    ]
}
```

## 📚 منابع

- [SERP Features Guide](https://moz.com/learn/seo/serp-features)
- [Featured Snippets](https://ahrefs.com/blog/featured-snippets/)
- [People Also Ask](https://www.searchenginejournal.com/people-also-ask/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

