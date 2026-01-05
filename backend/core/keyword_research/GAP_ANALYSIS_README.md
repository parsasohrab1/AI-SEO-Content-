# راهنمای Keyword Gap Analyzer

## 📋 معرفی

این ماژول تحلیل فاصله کلمات کلیدی (Keyword Gap Analysis) را انجام می‌دهد. با مقایسه کلمات کلیدی شما و رقبا، فرصت‌ها و مزیت‌ها را شناسایی می‌کند.

## ✨ ویژگی‌ها

- ✅ شناسایی فرصت‌ها (کلمات کلیدی رقبا که شما ندارید)
- ✅ شناسایی مزیت‌ها (کلمات کلیدی شما که رقبا ندارند)
- ✅ تحلیل رقابت (کلمات کلیدی مشترک)
- ✅ محاسبه Opportunity Score
- ✅ محاسبه Advantage Score
- ✅ پیشنهادات عملی
- ✅ پشتیبانی از SEMrush و Ahrefs API
- ✅ روش‌های رایگان (بدون نیاز به API)

## 🚀 استفاده

### مثال 1: تحلیل ساده

```python
from backend.core.keyword_research import KeywordGapAnalyzer

analyzer = KeywordGapAnalyzer()

result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=[
        "https://competitor1.com",
        "https://competitor2.com"
    ],
    use_apis=True,
    limit_per_site=100,
    language='en'
)

# نمایش فرصت‌ها
for opp in result['opportunities'][:10]:
    print(f"{opp['keyword']} - Score: {opp['opportunity_score']}")
```

### مثال 2: تحلیل با روش رایگان

```python
# بدون نیاز به API
result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=["https://competitor1.com"],
    use_apis=False,  # استفاده از روش‌های رایگان
    language='fa'
)
```

### مثال 3: دریافت پیشنهادات

```python
result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=["https://competitor1.com"]
)

# نمایش پیشنهادات
for rec in result['recommendations']:
    print(f"• {rec}")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'opportunities': [
        {
            'keyword': str,
            'opportunity_score': float,  # 0-100
            'search_volume': int,
            'position': int,
            'cpc': float,
            'traffic': int,
            'competitors': List[str],
            'competitor_count': int
        },
        ...
    ],
    'advantages': [
        {
            'keyword': str,
            'advantage_score': float,  # 0-100
            'search_volume': int,
            'position': int,
            'cpc': float,
            'traffic': int
        },
        ...
    ],
    'competition': [
        {
            'keyword': str,
            'your_position': int,
            'competitor_positions': List[int],
            'search_volume': int,
            'competition_level': str  # winning, losing, tied
        },
        ...
    ],
    'recommendations': List[str],
    'summary': {
        'your_total_keywords': int,
        'competitors_total_keywords': int,
        'opportunities_count': int,
        'high_opportunities': int,
        'medium_opportunities': int,
        'advantages_count': int,
        'high_advantages': int,
        'competition_count': int,
        'winning_keywords': int,
        'losing_keywords': int,
        'coverage_ratio': float
    },
    'competitor_analysis': {
        'your_keywords_count': int,
        'competitors_analyzed': int,
        'total_competitor_keywords': int
    }
}
```

## 🎯 انواع نتایج

### 1. Opportunities (فرصت‌ها)
کلمات کلیدی که رقبا دارند اما شما ندارید.

**Opportunity Score محاسبه می‌شود بر اساس:**
- Search Volume (40%)
- تعداد رقبا (30%)
- Position رقبا (20%)
- CPC (10%)

**تفسیر Score:**
- 70-100: فرصت عالی
- 40-70: فرصت خوب
- 0-40: فرصت متوسط

### 2. Advantages (مزیت‌ها)
کلمات کلیدی که شما دارید اما رقبا ندارند.

**Advantage Score محاسبه می‌شود بر اساس:**
- Search Volume (50%)
- Position شما (30%)
- Traffic (20%)

**تفسیر Score:**
- 70-100: مزیت عالی
- 40-70: مزیت خوب
- 0-40: مزیت متوسط

### 3. Competition (رقابت)
کلمات کلیدی مشترک بین شما و رقبا.

**Competition Level:**
- `winning`: شما رتبه بهتری دارید
- `losing`: رقبا رتبه بهتری دارند
- `tied`: رتبه مساوی
- `you_only`: فقط شما رتبه دارید
- `competitor_only`: فقط رقیب رتبه دارد

## 🔧 تنظیمات

### استفاده از APIها

```python
# استفاده از SEMrush و Ahrefs (اگر موجود باشند)
result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=["https://competitor1.com"],
    use_apis=True
)
```

### روش‌های رایگان

```python
# بدون نیاز به API Key
result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=["https://competitor1.com"],
    use_apis=False
)
```

### محدود کردن تعداد

```python
# محدود کردن تعداد کلمات کلیدی برای هر سایت
result = await analyzer.analyze_gap(
    site_url="https://yoursite.com",
    competitor_urls=["https://competitor1.com"],
    limit_per_site=50  # حداکثر 50 کلمه کلیدی برای هر سایت
)
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import KeywordGapAnalyzer

async def main():
    analyzer = KeywordGapAnalyzer()
    
    result = await analyzer.analyze_gap(
        site_url="https://yoursite.com",
        competitor_urls=[
            "https://competitor1.com",
            "https://competitor2.com"
        ],
        use_apis=True,
        language='en'
    )
    
    # نمایش خلاصه
    summary = result['summary']
    print(f"فرصت‌ها: {summary['opportunities_count']}")
    print(f"مزیت‌ها: {summary['advantages_count']}")
    print(f"رقابت: {summary['competition_count']}")
    
    # نمایش فرصت‌های برتر
    high_opp = [
        opp for opp in result['opportunities']
        if opp.get('opportunity_score', 0) >= 70
    ]
    
    print(f"\n{len(high_opp)} فرصت با اولویت بالا:")
    for opp in high_opp[:10]:
        print(f"  • {opp['keyword']} (Score: {opp['opportunity_score']:.1f})")
    
    # نمایش پیشنهادات
    print("\nپیشنهادات:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

asyncio.run(main())
```

## 🎯 کاربردها

### 1. Content Strategy
- شناسایی فرصت‌های تولید محتوا
- اولویت‌بندی کلمات کلیدی
- برنامه‌ریزی محتوا

### 2. SEO Optimization
- بهبود رتبه برای کلمات کلیدی در حال باخت
- حفظ رتبه برای کلمات کلیدی برنده
- سرمایه‌گذاری روی مزیت‌ها

### 3. Competitive Intelligence
- درک استراتژی رقبا
- شناسایی نقاط قوت و ضعف
- Benchmarking

## ⚠️ محدودیت‌ها

### APIها
- نیاز به API Key برای SEMrush/Ahrefs
- Rate Limiting ممکن است اعمال شود
- هزینه‌بر بودن

### روش‌های رایگان
- دقت کمتر
- داده‌های محدود
- نیاز به Crawling

## 🔍 مثال‌های واقعی

### ورودی:
```python
site_url = "https://yoursite.com"
competitor_urls = ["https://competitor1.com"]
```

### خروجی:
```python
{
    'opportunities': [
        {
            'keyword': 'seo tools',
            'opportunity_score': 85.0,
            'search_volume': 12000,
            'competitor_count': 2
        },
        ...
    ],
    'advantages': [
        {
            'keyword': 'keyword research guide',
            'advantage_score': 75.0,
            'search_volume': 5000
        },
        ...
    ],
    'competition': [
        {
            'keyword': 'seo optimization',
            'your_position': 5,
            'competition_level': 'winning'
        },
        ...
    ]
}
```

## 💡 بهترین روش‌ها

1. **استفاده از APIها**: برای دقت بیشتر از SEMrush/Ahrefs استفاده کنید
2. **تحلیل چند رقیب**: حداقل 2-3 رقیب را تحلیل کنید
3. **اولویت‌بندی**: روی فرصت‌های با Score بالا تمرکز کنید
4. **مانیتورینگ**: به صورت دوره‌ای تحلیل کنید

## 📚 منابع

- [Keyword Gap Analysis](https://ahrefs.com/blog/keyword-gap-analysis/)
- [Competitor Analysis](https://www.semrush.com/blog/competitor-analysis/)
- [SEO Competitive Analysis](https://moz.com/learn/seo/competitive-analysis)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

