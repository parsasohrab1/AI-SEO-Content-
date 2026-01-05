# راهنمای Ahrefs Keyword Analyzer

## 📋 معرفی

این ماژول یکپارچه‌سازی کامل با Ahrefs API برای تحلیل پیشرفته کلمات کلیدی و رتبه‌بندی است.

## ✨ ویژگی‌ها

- ✅ دریافت معیارهای دقیق کلمات کلیدی (Keyword Metrics)
- ✅ دریافت کلمات کلیدی رتبه‌دار (Ranking Keywords)
- ✅ دریافت ایده‌های کلمات کلیدی (Keyword Ideas)
- ✅ تحلیل کلمات کلیدی رقبا (Competitor Analysis)
- ✅ Keyword Difficulty دقیق (0-100)
- ✅ Click Potential (0-100)
- ✅ Parent Topic شناسایی
- ✅ SERP Features تحلیل
- ✅ تحلیل همزمان چند کلمه کلیدی (Bulk Analysis)

## 🚀 نصب

### 1. دریافت API Credentials

1. ثبت‌نام در [Ahrefs](https://ahrefs.com)
2. رفتن به [Ahrefs API](https://ahrefs.com/api)
3. دریافت API Token و API ID

### 2. تنظیم Environment Variables

```bash
# در فایل .env
AHREFS_API_TOKEN=your_api_token_here
AHREFS_API_ID=your_api_id_here
```

یا در Python:

```python
import os
os.environ['AHREFS_API_TOKEN'] = 'your_api_token'
os.environ['AHREFS_API_ID'] = 'your_api_id'
```

## 📖 استفاده

### مثال 1: دریافت معیارهای کلمه کلیدی

```python
from backend.core.keyword_research import AhrefsKeywordAnalyzer

analyzer = AhrefsKeywordAnalyzer()

metrics = await analyzer.get_keyword_metrics(
    keyword="seo optimization",
    country='us'
)

if metrics:
    print(f"حجم جستجو: {metrics['search_volume']:,}")
    print(f"Keyword Difficulty: {metrics['keyword_difficulty']}/100")
    print(f"Click Potential: {metrics['click_potential']}/100")
    print(f"Parent Topic: {metrics['parent_topic']}")
```

### مثال 2: دریافت کلمات کلیدی رتبه‌دار

```python
ranking_keywords = await analyzer.get_ranking_keywords(
    url="https://yoursite.com",
    country='us',
    limit=100,
    mode='domain'  # یا 'url' برای یک صفحه خاص
)

for kw in ranking_keywords:
    print(f"{kw['keyword']} - رتبه: {kw['position']} - حجم: {kw['search_volume']:,}")
```

### مثال 3: دریافت ایده‌های کلمات کلیدی

```python
ideas = await analyzer.get_keyword_ideas(
    seed_keyword="seo",
    country='us',
    limit=50
)

# مرتب‌سازی بر اساس Opportunity Score
sorted_ideas = sorted(
    ideas,
    key=lambda x: x.get('opportunity_score', 0),
    reverse=True
)

for idea in sorted_ideas[:10]:
    print(f"{idea['keyword']} - فرصت: {idea['opportunity_score']}/100")
```

### مثال 4: تحلیل کلمات کلیدی رقیب

```python
analysis = await analyzer.get_competitor_keywords(
    competitor_url="https://competitor.com",
    your_url="https://yoursite.com",
    country='us',
    limit=100
)

# فرصت‌ها: کلمات کلیدی رقیب که شما ندارید
opportunities = analysis['opportunities']

print(f"تعداد فرصت‌ها: {len(opportunities)}")
for opp in opportunities[:10]:
    print(f"- {opp['keyword']} (حجم: {opp['search_volume']:,})")
```

### مثال 5: تحلیل همزمان چند کلمه کلیدی

```python
keywords = ["seo", "keyword research", "on-page seo"]

results = await analyzer.get_bulk_keyword_metrics(
    keywords=keywords,
    country='us',
    max_concurrent=5
)

for keyword, data in results.items():
    print(f"{keyword}:")
    print(f"  Difficulty: {data['keyword_difficulty']}/100")
    print(f"  Click Potential: {data['click_potential']}/100")
    print(f"  Opportunity: {data['opportunity_score']}/100")
```

## 📊 ساختار داده‌های بازگشتی

### get_keyword_metrics()

```python
{
    'keyword': str,                    # کلمه کلیدی
    'search_volume': int,              # حجم جستجو
    'keyword_difficulty': int,         # Keyword Difficulty (0-100)
    'difficulty_level': str,           # Easy, Medium, Hard
    'cpc': float,                      # هزینه هر کلیک
    'click_potential': int,            # Click Potential (0-100)
    'parent_topic': str,               # Parent Topic
    'serp_features': List[str],        # SERP Features
    'trend': Dict[str, int],           # روند ماهانه
    'opportunity_score': float,        # Opportunity Score (0-100)
    'source': 'ahrefs'
}
```

### get_ranking_keywords()

```python
[
    {
        'keyword': str,
        'position': int,                # رتبه در SERP
        'search_volume': int,
        'cpc': float,
        'url': str,                    # URL صفحه
        'traffic': int,                # ترافیک تخمینی
        'source': 'ahrefs'
    },
    ...
]
```

### get_keyword_ideas()

```python
[
    {
        'keyword': str,
        'search_volume': int,
        'keyword_difficulty': int,
        'cpc': float,
        'click_potential': int,
        'opportunity_score': float,
        'source': 'ahrefs'
    },
    ...
]
```

### get_competitor_keywords()

```python
{
    'competitor_keywords': List[Dict],  # کلمات کلیدی رقیب
    'your_keywords': List[Dict],        # کلمات کلیدی شما
    'opportunities': List[Dict],        # فرصت‌ها
    'summary': {
        'competitor_total': int,
        'your_total': int,
        'opportunities_count': int
    }
}
```

## 🌍 کشورهای پشتیبانی شده

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

## 💡 Click Potential

Click Potential نشان می‌دهد که چقدر احتمال دارد کاربران روی نتایج جستجو کلیک کنند.

- **0-30**: Low (پایین)
- **30-70**: Medium (متوسط)
- **70-100**: High (بالا)

## 🎯 Opportunity Score

Opportunity Score ترکیبی از:
- حجم جستجو (هرچه بیشتر بهتر)
- Keyword Difficulty (هرچه کمتر بهتر)
- Click Potential (هرچه بیشتر بهتر)

فرمول: `(Normalized Volume × (100 - Difficulty)) / 100 × Click Adjustment`

امتیاز بالاتر = فرصت بهتر

## 🔐 Authentication

Ahrefs API v2 از HMAC-SHA256 برای authentication استفاده می‌کند:

1. تولید timestamp
2. ساخت string برای signature
3. تولید HMAC-SHA256 signature با API Token
4. ارسال signature همراه با درخواست

این فرآیند به صورت خودکار در کلاس انجام می‌شود.

## ⚠️ محدودیت‌ها و نکات

### Rate Limiting
- Ahrefs API محدودیت درخواست دارد
- از `max_concurrent` برای کنترل درخواست‌های همزمان استفاده کنید
- بین درخواست‌ها delay اضافه شده است

### هزینه
- Ahrefs API نیاز به اشتراک پولی دارد
- هر درخواست API credit مصرف می‌کند
- از Bulk Analysis برای کاهش هزینه استفاده کنید

### Error Handling
- همیشه بررسی کنید که `enabled = True` باشد
- از try-except برای مدیریت خطاها استفاده کنید
- در صورت خطا، `None` یا لیست خالی برمی‌گرداند

### Authentication Errors
- اگر خطای 401 دریافت کردید، API credentials را بررسی کنید
- مطمئن شوید که API Token و API ID صحیح هستند
- بررسی کنید که API Token منقضی نشده است

## 🔧 تنظیمات پیشرفته

### تغییر Timeout

```python
analyzer = AhrefsKeywordAnalyzer()
analyzer.timeout = 60.0  # 60 ثانیه
```

### استفاده از Cache

```python
# پیشنهاد: استفاده از Redis برای cache
import redis
cache = redis.Redis()

async def get_cached_metrics(keyword):
    cache_key = f"ahrefs:metrics:{keyword}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    metrics = await analyzer.get_keyword_metrics(keyword)
    if metrics:
        cache.setex(cache_key, 3600, json.dumps(metrics))  # 1 ساعت
    
    return metrics
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import AhrefsKeywordAnalyzer

async def main():
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("Ahrefs API credentials تنظیم نشده است")
        return
    
    # 1. تحلیل کلمه کلیدی اصلی
    metrics = await analyzer.get_keyword_metrics("seo", country='us')
    
    if metrics and metrics['opportunity_score'] >= 50:
        print(f"✅ فرصت خوب: {metrics['keyword']}")
        print(f"   Click Potential: {metrics['click_potential']}/100")
        
        # 2. دریافت ایده‌های کلمات کلیدی
        ideas = await analyzer.get_keyword_ideas("seo", limit=30)
        
        # 3. انتخاب کلمات کلیدی با Click Potential بالا
        high_click_potential = [
            kw for kw in ideas
            if kw.get('click_potential', 0) >= 70
        ]
        
        print(f"\n🎯 {len(high_click_potential)} کلمه کلیدی با Click Potential بالا:")
        for kw in high_click_potential[:10]:
            print(f"  - {kw['keyword']} (Click: {kw['click_potential']}/100)")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🐛 عیب‌یابی

### مشکل: API credentials معتبر نیست
- بررسی کنید که API Token و API ID صحیح هستند
- بررسی کنید که API credentials منقضی نشده‌اند
- از [Ahrefs API Dashboard](https://ahrefs.com/api) بررسی کنید

### مشکل: Rate Limiting
- تعداد درخواست‌های همزمان را کاهش دهید
- بین درخواست‌ها delay اضافه کنید
- از cache استفاده کنید

### مشکل: نتایج خالی
- بررسی کنید که کشور صحیح است
- بررسی کنید که کلمه کلیدی معتبر است
- بررسی کنید که API credit کافی دارید

### مشکل: Authentication Error (401)
- بررسی کنید که API Token و API ID صحیح هستند
- بررسی کنید که signature به درستی تولید می‌شود
- بررسی کنید که timestamp معتبر است

## 📊 مقایسه با سایر APIها

| ویژگی | Google Keyword Planner | SEMrush | Ahrefs |
|-------|----------------------|---------|--------|
| Keyword Difficulty | ❌ | ✅ | ✅ |
| Click Potential | ❌ | ❌ | ✅ |
| Parent Topic | ❌ | ❌ | ✅ |
| Ranking Keywords | ❌ | ✅ | ✅ |
| Keyword Gap | ❌ | ✅ | ✅ |
| نیاز به API Key | اختیاری | ✅ | ✅ |
| هزینه | رایگان | پولی | پولی |

## 📚 منابع

- [Ahrefs API Documentation](https://ahrefs.com/api/documentation)
- [Ahrefs API Reference](https://ahrefs.com/api/documentation)
- [Ahrefs Pricing](https://ahrefs.com/pricing)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

