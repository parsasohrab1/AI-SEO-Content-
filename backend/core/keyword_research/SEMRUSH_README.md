# راهنمای SEMrush Keyword Analyzer

## 📋 معرفی

این ماژول یکپارچه‌سازی کامل با SEMrush API برای تحلیل پیشرفته کلمات کلیدی است.

## ✨ Features

- ✅ دریافت اطلاعات جامع کلمات کلیدی (Keyword Overview)
- ✅ دریافت کلمات کلیدی مرتبط (Related Keywords)
- ✅ تحلیل فاصله کلمات کلیدی (Keyword Gap Analysis)
- ✅ محاسبه Keyword Difficulty دقیق
- ✅ محاسبه Opportunity Score
- ✅ تحلیل همزمان چند کلمه کلیدی (Bulk Analysis)
- ✅ پشتیبانی از دیتابیس‌های مختلف (US, UK, IR, etc.)

## 🚀 نصب

### 1. دریافت API Key

1. ثبت‌نام در [SEMrush](https://www.semrush.com)
2. رفتن به [SEMrush API](https://www.semrush.com/api/)
3. دریافت API Key

### 2. تنظیم Environment Variable

```bash
# در فایل .env
SEMRUSH_API_KEY=your_api_key_here
```

یا در Python:

```python
import os
os.environ['SEMRUSH_API_KEY'] = 'your_api_key_here'
```

## 📖 استفاده

### مثال 1: دریافت اطلاعات کلمه کلیدی

```python
from backend.core.keyword_research import SEMrushKeywordAnalyzer

analyzer = SEMrushKeywordAnalyzer()

overview = await analyzer.get_keyword_overview(
    keyword="seo optimization",
    database='us'  # یا 'ir' برای ایران
)

if overview:
    print(f"حجم جستجو: {overview['search_volume']:,}")
    print(f"سختی: {overview['difficulty']}/100")
    print(f"فرصت: {overview['opportunity_score']}/100")
```

### مثال 2: دریافت کلمات کلیدی مرتبط

```python
related = await analyzer.get_related_keywords(
    keyword="seo",
    database='us',
    limit=50
)

for kw in related:
    print(f"{kw['keyword']} - حجم: {kw['search_volume']:,}")
```

### مثال 3: تحلیل Keyword Gap

```python
gap_analysis = await analyzer.get_keyword_gap(
    site_url="https://yoursite.com",
    competitor_urls=[
        "https://competitor1.com",
        "https://competitor2.com"
    ],
    database='us',
    limit=100
)

# فرصت‌ها: کلمات کلیدی که رقبا دارند اما شما ندارید
opportunities = gap_analysis['opportunities']

# مزیت‌ها: کلمات کلیدی که شما دارید اما رقبا ندارند
advantages = gap_analysis['advantages']

# کلمات کلیدی مشترک
common = gap_analysis['common_keywords']
```

### مثال 4: تحلیل همزمان چند کلمه کلیدی

```python
keywords = ["seo", "keyword research", "on-page seo"]

results = await analyzer.get_bulk_keyword_overview(
    keywords=keywords,
    database='us',
    max_concurrent=5  # حداکثر 5 درخواست همزمان
)

for keyword, data in results.items():
    print(f"{keyword}: سختی {data['difficulty']}/100")
```

## 📊 ساختار داده‌های بازگشتی

### get_keyword_overview()

```python
{
    'keyword': str,                    # کلمه کلیدی
    'search_volume': int,              # حجم جستجو
    'cpc': float,                      # هزینه هر کلیک
    'competition': float,              # رقابت (0.00-1.00)
    'competition_level': str,          # Low, Medium, High
    'number_of_results': int,           # تعداد نتایج
    'trend': List[int],                # روند 12 ماهه
    'difficulty': int,                 # Keyword Difficulty (0-100)
    'difficulty_level': str,           # Easy, Medium, Hard
    'opportunity_score': float,        # Opportunity Score (0-100)
    'source': 'semrush'
}
```

### get_related_keywords()

```python
[
    {
        'keyword': str,
        'search_volume': int,
        'cpc': float,
        'competition': float,
        'difficulty': int,
        'opportunity_score': float,
        'source': 'semrush'
    },
    ...
]
```

### get_keyword_gap()

```python
{
    'your_keywords': List[Dict],        # کلمات کلیدی شما
    'competitor_keywords': {            # کلمات کلیدی رقبا
        'url1': List[Dict],
        'url2': List[Dict],
        ...
    },
    'opportunities': List[Dict],        # فرصت‌ها
    'advantages': List[Dict],           # مزیت‌ها
    'common_keywords': List[Dict],      # کلمات کلیدی مشترک
    'summary': {
        'your_total': int,
        'competitors_total': int,
        'opportunities_count': int,
        'advantages_count': int,
        'common_count': int
    }
}
```

## 🌍 دیتابیس‌های پشتیبانی شده

- `us` - United States
- `uk` - United Kingdom
- `ca` - Canada
- `au` - Australia
- `de` - Germany
- `fr` - France
- `ru` - Russia
- `es` - Spain
- `it` - Italy
- `br` - Brazil
- `jp` - Japan
- `in` - India
- و بیشتر...

## 🎯 Keyword Difficulty

Keyword Difficulty (KD) امتیازی از 0 تا 100 است که نشان می‌دهد چقدر سخت است برای یک کلمه کلیدی رتبه بگیرید.

- **0-30**: Easy (آسان)
- **30-70**: Medium (متوسط)
- **70-100**: Hard (سخت)

## 💡 Opportunity Score

Opportunity Score ترکیبی از:
- حجم جستجو (هرچه بیشتر بهتر)
- Keyword Difficulty (هرچه کمتر بهتر)
- سطح رقابت (هرچه کمتر بهتر)

فرمول: `(Normalized Volume × (100 - Difficulty)) / 100`

امتیاز بالاتر = فرصت بهتر

## ⚠️ محدودیت‌ها و نکات

### Rate Limiting
- SEMrush API محدودیت درخواست دارد
- از `max_concurrent` برای کنترل درخواست‌های همزمان استفاده کنید
- بین درخواست‌ها delay اضافه شده است

### هزینه
- SEMrush API نیاز به اشتراک پولی دارد
- هر درخواست API credit مصرف می‌کند
- از Bulk Analysis برای کاهش هزینه استفاده کنید

### Error Handling
- همیشه بررسی کنید که `enabled = True` باشد
- از try-except برای مدیریت خطاها استفاده کنید
- در صورت خطا، `None` یا لیست خالی برمی‌گرداند

## 🔧 تنظیمات پیشرفته

### تغییر Timeout

```python
analyzer = SEMrushKeywordAnalyzer()
analyzer.timeout = 60.0  # 60 ثانیه
```

### استفاده از Cache

```python
# پیشنهاد: استفاده از Redis برای cache
import redis
cache = redis.Redis()

async def get_cached_overview(keyword):
    cache_key = f"semrush:{keyword}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    overview = await analyzer.get_keyword_overview(keyword)
    if overview:
        cache.setex(cache_key, 3600, json.dumps(overview))  # 1 ساعت
    
    return overview
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import SEMrushKeywordAnalyzer

async def main():
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("SEMrush API Key تنظیم نشده است")
        return
    
    # 1. تحلیل کلمه کلیدی اصلی
    overview = await analyzer.get_keyword_overview("seo", database='us')
    
    if overview and overview['opportunity_score'] >= 50:
        print(f"✅ فرصت خوب: {overview['keyword']}")
        
        # 2. دریافت کلمات کلیدی مرتبط
        related = await analyzer.get_related_keywords("seo", limit=20)
        
        # 3. انتخاب کلمات کلیدی با فرصت بالا
        high_opportunity = [
            kw for kw in related
            if kw.get('opportunity_score', 0) >= 50
        ]
        
        print(f"\n🎯 {len(high_opportunity)} کلمه کلیدی با فرصت بالا:")
        for kw in high_opportunity[:10]:
            print(f"  - {kw['keyword']} (فرصت: {kw['opportunity_score']}/100)")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🐛 عیب‌یابی

### مشکل: API Key معتبر نیست
- بررسی کنید که API Key صحیح است
- بررسی کنید که API Key منقضی نشده است
- از [SEMrush API Dashboard](https://www.semrush.com/api/) بررسی کنید

### مشکل: Rate Limiting
- تعداد درخواست‌های همزمان را کاهش دهید
- بین درخواست‌ها delay اضافه کنید
- از cache استفاده کنید

### مشکل: نتایج خالی
- بررسی کنید که دیتابیس صحیح است
- بررسی کنید که کلمه کلیدی معتبر است
- بررسی کنید که API credit کافی دارید

## 📚 منابع

- [SEMrush API Documentation](https://www.semrush.com/api/)
- [SEMrush API Reference](https://www.semrush.com/api-docs/)
- [SEMrush Pricing](https://www.semrush.com/prices/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

