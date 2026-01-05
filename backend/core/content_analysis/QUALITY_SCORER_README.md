# راهنمای Content Quality Scorer

## 📋 معرفی

این ماژول امتیازدهی کیفیت محتوا را انجام می‌دهد. با محاسبه 6 معیار مختلف، کیفیت کلی محتوا را ارزیابی می‌کند و توصیه‌های بهبود ارائه می‌دهد.

## ✨ ویژگی‌ها

- ✅ محاسبه SEO Score (0-100)
- ✅ محاسبه Readability Score (0-100)
- ✅ محاسبه Keyword Optimization Score (0-100)
- ✅ محاسبه Content Depth Score (0-100)
- ✅ محاسبه Uniqueness Score (0-100)
- ✅ محاسبه Engagement Potential Score (0-100)
- ✅ محاسبه Overall Score
- ✅ تولید توصیه‌های بهبود
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 استفاده

### مثال 1: امتیازدهی ساده

```python
from backend.core.content_analysis import ContentQualityScorer

scorer = ContentQualityScorer()

result = scorer.score_content(
    content="Your content here...",
    keyword="seo optimization",
    title="SEO Guide",
    meta_description="Complete SEO guide",
    language='en'
)

print(f"Overall Score: {result['overall_score']}/100")
print(f"SEO Score: {result['seo_score']}/100")
```

### مثال 2: امتیازدهی با معیارهای کلمه کلیدی

```python
keyword_metrics = {
    'search_volume': 12000,
    'difficulty': 65,
    'competition': 'high'
}

result = scorer.score_content(
    content="Your content...",
    keyword="seo",
    keyword_metrics=keyword_metrics,
    language='en'
)
```

### مثال 3: دریافت توصیه‌ها

```python
result = scorer.score_content(
    content="Your content...",
    keyword="seo"
)

for rec in result['recommendations']:
    print(f"• {rec}")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'overall_score': float,           # 0-100
    'seo_score': float,               # 0-100
    'readability_score': float,        # 0-100
    'keyword_optimization': float,     # 0-100
    'content_depth': float,            # 0-100
    'uniqueness': float,               # 0-100
    'engagement_potential': float,     # 0-100
    'recommendations': List[str],
    'breakdown': {
        'word_count': int,
        'heading_count': int,
        'paragraph_count': int,
        'image_count': int,
        'link_count': int,
        'has_title': bool,
        'has_meta_description': bool,
        'has_h1': bool,
        'has_faq': bool
    }
}
```

## 🎯 معیارهای امتیازدهی

### 1. SEO Score (25%)
امتیازدهی بر اساس:
- Title (15%)
- Meta Description (10%)
- H1 (10%)
- Headings Structure (15%)
- Content Length (15%)
- Images (10%)
- Internal Links (10%)
- FAQ (10%)
- Keyword in First Paragraph (5%)

### 2. Readability Score (15%)
امتیازدهی بر اساس:
- میانگین طول جمله
- میانگین طول کلمه
- Flesch Reading Ease (برای انگلیسی)

**تفسیر:**
- 80-100: بسیار خوانا
- 60-80: خوانا
- 40-60: متوسط
- 0-40: سخت

### 3. Keyword Optimization (20%)
امتیازدهی بر اساس:
- Keyword Density (40%) - ایده‌آل: 1-2.5%
- Keyword in Title (20%)
- Keyword in Meta Description (15%)
- Keyword in H1 (15%)
- Keyword in First Paragraph (10%)

### 4. Content Depth (20%)
امتیازدهی بر اساس:
- Word Count (30%)
- Heading Structure (25%)
- Paragraphs (15%)
- Images (15%)
- Links (10%)
- FAQ (5%)

### 5. Uniqueness (10%)
امتیازدهی بر اساس:
- طول محتوا
- تنوع کلمات
- وجود عناصر منحصر به فرد

### 6. Engagement Potential (10%)
امتیازدهی بر اساس:
- وجود سوالات (20%)
- Call-to-Action (20%)
- لیست‌ها (15%)
- تصاویر (15%)
- لینک‌ها (15%)
- FAQ (15%)

## 📝 مثال کامل

```python
from backend.core.content_analysis import ContentQualityScorer

scorer = ContentQualityScorer()

content = """
# SEO Optimization Guide

This is a comprehensive guide to SEO optimization...

## What is SEO?

SEO stands for Search Engine Optimization...

## FAQ

### What is SEO?
SEO is the process...
"""

result = scorer.score_content(
    content=content,
    keyword="seo optimization",
    title="SEO Optimization Guide",
    meta_description="Complete guide to SEO optimization",
    language='en'
)

print(f"Overall Score: {result['overall_score']}/100")
print(f"SEO Score: {result['seo_score']}/100")
print(f"Readability: {result['readability_score']}/100")
```

## 🎯 Overall Score

Overall Score میانگین وزنی تمام معیارها است:

- SEO Score: 25%
- Readability Score: 15%
- Keyword Optimization: 20%
- Content Depth: 20%
- Uniqueness: 10%
- Engagement Potential: 10%

**تفسیر:**
- 80-100: عالی
- 60-80: خوب
- 40-60: متوسط
- 0-40: نیاز به بهبود

## 💡 توصیه‌ها

سیستم به صورت خودکار توصیه‌های بهبود را تولید می‌کند:

- اگر SEO Score پایین باشد: "SEO Score پایین است. تگ‌های SEO را بهبود دهید."
- اگر Title نباشد: "عنوان (Title) اضافه کنید."
- اگر Readability پایین باشد: "Readability پایین است. جملات را کوتاه‌تر کنید."
- و غیره...

## 📊 Breakdown

Breakdown شامل اطلاعات جزئی محتوا است:

- `word_count`: تعداد کلمات
- `heading_count`: تعداد Headings
- `paragraph_count`: تعداد پاراگراف‌ها
- `image_count`: تعداد تصاویر
- `link_count`: تعداد لینک‌ها
- `has_title`: وجود Title
- `has_meta_description`: وجود Meta Description
- `has_h1`: وجود H1
- `has_faq`: وجود FAQ

## 🎯 کاربردها

### 1. ارزیابی کیفیت محتوا
- بررسی کیفیت محتوای تولید شده
- شناسایی نقاط ضعف
- اولویت‌بندی بهبودها

### 2. بهینه‌سازی محتوا
- بهبود SEO Score
- بهبود Readability
- بهبود Keyword Optimization

### 3. Benchmarking
- مقایسه محتوای مختلف
- ردیابی پیشرفت
- هدف‌گذاری

## ⚠️ محدودیت‌ها

### دقت
- امتیازدهی بر اساس الگوریتم‌های ساده است
- ممکن است نیاز به تنظیم داشته باشد

### Uniqueness
- برای دقت بیشتر نیاز به Semantic Analysis دارد
- در صورت عدم وجود، از روش‌های fallback استفاده می‌شود

## 💡 بهترین روش‌ها

1. **هدف Overall Score ≥ 80**: برای محتوای با کیفیت
2. **بررسی Breakdown**: برای درک جزئیات
3. **پیگیری توصیه‌ها**: برای بهبود محتوا
4. **مقایسه**: محتوای مختلف را با هم مقایسه کنید

## 📚 منابع

- [Content Quality Guidelines](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [SEO Best Practices](https://ahrefs.com/blog/seo-best-practices/)
- [Readability Tests](https://en.wikipedia.org/wiki/Readability)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

