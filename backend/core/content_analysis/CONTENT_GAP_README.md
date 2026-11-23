# راهنمای Content Gap Analyzer

## 📋 معرفی

این ماژول تحلیل فاصله محتوا (Content Gap Analysis) را انجام می‌دهد. با مقایسه محتوای شما و رقبا، موضوعات، زوایا و انواع محتوای موجود در رقبا اما نه در شما را شناسایی می‌کند.

## ✨ Features

- ✅ شناسایی موضوعات موجود در رقبا اما نه در شما
- ✅ تحلیل زوایای مختلف یک موضوع
- ✅ تحلیل عمق محتوا
- ✅ تحلیل انواع محتوا (مقاله، ویدیو، اینفوگرافیک)
- ✅ محاسبه Overall Gap Score
- ✅ تولید پیشنهادات عملی
- ✅ پشتیبانی از Semantic Analysis

## 🚀 Usage

### مثال 1: تحلیل ساده

```python
from backend.core.content_analysis import ContentGapAnalyzer

analyzer = ContentGapAnalyzer()

site_content = {
    'articles': [
        {
            'title': 'SEO Guide',
            'content': 'Basic SEO tips...',
            'topics': ['seo'],
            'word_count': 1000
        }
    ],
    'topics': ['seo'],
    'content_types': ['article']
}

competitor_content = [
    {
        'title': 'Complete SEO Guide',
        'content': 'Comprehensive guide...',
        'topics': ['seo', 'advanced seo'],
        'word_count': 3000,
        'content_type': 'article'
    }
]

result = await analyzer.analyze_content_gaps(
    site_content=site_content,
    competitor_content=competitor_content,
    language='en'
)

# نمایش Topic Gaps
for gap in result['topic_gaps']:
    print(f"{gap['topic']} - Importance: {gap['importance']}")
```

### مثال 2: دریافت پیشنهادات

```python
result = await analyzer.analyze_content_gaps(
    site_content=site_content,
    competitor_content=competitor_content
)

# نمایش پیشنهادات
for rec in result['recommendations']:
    print(f"• {rec}")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'topic_gaps': [
        {
            'topic': str,
            'importance': float,  # 0-100
            'competitor_count': int,
            'content_items': List[Dict],
            'similarity_score': float,
            'gap_type': 'topic'
        },
        ...
    ],
    'angle_gaps': [
        {
            'angle': str,  # how_to, what_is, best, etc.
            'importance': int,
            'competitor_count': int,
            'content_items': List[Dict],
            'gap_type': 'angle'
        },
        ...
    ],
    'depth_gaps': [
        {
            'gap_type': 'depth' | 'topic_depth',
            'your_average_depth': float,
            'competitor_average_depth': float,
            'difference': float,
            'topic': str  # اگر topic_depth باشد
        },
        ...
    ],
    'content_type_gaps': [
        {
            'content_type': str,  # article, video, infographic
            'competitor_count': int,
            'your_count': int,
            'gap_type': 'content_type' | 'content_type_quantity',
            'importance': int
        },
        ...
    ],
    'recommendations': List[str],
    'summary': {
        'total_topic_gaps': int,
        'high_importance_topics': int,
        'total_angle_gaps': int,
        'total_depth_gaps': int,
        'total_content_type_gaps': int,
        'overall_gap_score': float  # 0-100
    }
}
```

## 🎯 انواع Gap

### 1. Topic Gaps (فاصله موضوعات)
موضوعاتی که رقبا پوشش داده‌اند اما شما نکرده‌اید.

**Importance محاسبه می‌شود بر اساس:**
- تعداد محتوا (40%)
- میانگین طول محتوا (30%)
- تنوع انواع محتوا (30%)

### 2. Angle Gaps (فاصله زوایا)
زوایای مختلف یک موضوع که رقبا پوشش داده‌اند.

**انواع زوایا:**
- `how_to`: چگونه
- `what_is`: چیست
- `best`: بهترین
- `comparison`: مقایسه
- `review`: نقد و بررسی
- `guide`: راهنمای کامل
- `tips`: نکات و توصیه‌ها
- `mistakes`: اشتباهات رایج

### 3. Depth Gaps (فاصله عمق)
تفاوت عمق محتوا بین شما و رقبا.

**عمق محاسبه می‌شود بر اساس:**
- طول محتوا (40%)
- تعداد Headings (30%)
- وجود FAQ (15%)
- وجود تصاویر/ویدیو (15%)

### 4. Content Type Gaps (فاصله انواع محتوا)
انواع محتوای موجود در رقبا اما نه در شما.

**انواع محتوا:**
- `article`: مقاله
- `video`: ویدیو
- `infographic`: اینفوگرافیک
- `podcast`: پادکست
- `ebook`: کتاب الکترونیکی

## 📝 مثال کامل

```python
import asyncio
from backend.core.content_analysis import ContentGapAnalyzer

async def main():
    analyzer = ContentGapAnalyzer()
    
    site_content = {
        'articles': [
            {
                'title': 'SEO Basics',
                'topics': ['seo'],
                'word_count': 1000
            }
        ],
        'topics': ['seo'],
        'content_types': ['article']
    }
    
    competitor_content = [
        {
            'title': 'Complete SEO Guide',
            'topics': ['seo', 'advanced seo'],
            'word_count': 3000,
            'content_type': 'article'
        },
        {
            'title': 'SEO Video Tutorial',
            'topics': ['seo'],
            'content_type': 'video'
        }
    ]
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content
    )
    
    # Display the summary
    summary = result['summary']
    print(f"Topic Gaps: {summary['total_topic_gaps']}")
    print(f"Overall Gap Score: {summary['overall_gap_score']}/100")
    
    # نمایش Topic Gaps
    for gap in result['topic_gaps'][:10]:
        print(f"{gap['topic']} - {gap['importance']:.1f}/100")

asyncio.run(main())
```

## 🎯 کاربردها

### 1. Content Strategy
- شناسایی موضوعات برای تولید محتوا
- اولویت‌بندی موضوعات
- برنامه‌ریزی محتوا

### 2. Competitive Analysis
- درک استراتژی محتوای رقبا
- شناسایی فرصت‌ها
- Benchmarking

### 3. Content Optimization
- بهبود عمق محتوا
- اضافه کردن انواع محتوا
- پوشش زوایای مختلف

## ⚠️ محدودیت‌ها

### Semantic Analysis
- نیاز به مدل Semantic (اختیاری)
- در صورت عدم وجود، از روش‌های fallback استفاده می‌شود

### دقت
- دقت به کیفیت داده‌های ورودی وابسته است
- استخراج موضوعات ممکن است کامل نباشد

## 💡 بهترین روش‌ها

1. **داده‌های کامل**: محتوای کامل رقبا را ارائه دهید
2. **موضوعات دقیق**: موضوعات را به درستی استخراج کنید
3. **اولویت‌بندی**: روی Topic Gaps با Importance بالا تمرکز کنید
4. **مانیتورینگ**: به صورت دوره‌ای تحلیل کنید

## 📊 Overall Gap Score

Overall Gap Score نشان می‌دهد که چقدر محتوای شما از رقبا فاصله دارد.

**محاسبه بر اساس:**
- Topic Gaps (40%)
- Angle Gaps (25%)
- Depth Gaps (20%)
- Content Type Gaps (15%)

**تفسیر:**
- 80-100: عالی (فاصله کم)
- 60-80: خوب
- 40-60: متوسط
- 0-40: نیاز به بهبود (فاصله زیاد)

## 📚 منابع

- [Content Gap Analysis](https://ahrefs.com/blog/content-gap-analysis/)
- [Competitive Content Analysis](https://www.semrush.com/blog/competitive-content-analysis/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

