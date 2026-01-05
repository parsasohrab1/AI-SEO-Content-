# راهنمای Keyword Difficulty Calculator

## 📋 معرفی

این ماژول محاسبه پیشرفته Keyword Difficulty را انجام می‌دهد. Keyword Difficulty نشان می‌دهد که چقدر سخت است برای یک کلمه کلیدی در نتایج جستجو رتبه بگیرید.

## ✨ ویژگی‌ها

- ✅ محاسبه Difficulty Score (0-100)
- ✅ تحلیل Domain Authority رقبا
- ✅ تحلیل تعداد Backlinks صفحات رتبه‌دار
- ✅ ارزیابی کیفیت محتوای رقبا
- ✅ تحلیل سن دامنه
- ✅ شناسایی قدرت برند
- ✅ تولید توصیه‌های عملی
- ✅ پشتیبانی از APIهای خارجی (SEMrush, Ahrefs)
- ✅ روش‌های رایگان (بدون نیاز به API)

## 🚀 استفاده

### مثال 1: محاسبه ساده

```python
from backend.core.keyword_research import KeywordDifficultyCalculator

calculator = KeywordDifficultyCalculator()

result = await calculator.calculate_difficulty(
    keyword="seo optimization",
    language='en',
    use_apis=False  # استفاده از روش‌های رایگان
)

print(f"Difficulty: {result['difficulty_score']}/100")
print(f"Level: {result['difficulty_level']}")  # easy, medium, hard
print(f"Effort: {result['estimated_effort']}")  # low, medium, high
```

### مثال 2: استفاده با APIهای خارجی

```python
# استفاده از SEMrush و Ahrefs اگر موجود باشند
result = await calculator.calculate_difficulty(
    keyword="seo",
    language='en',
    use_apis=True  # استفاده از APIها
)
```

### مثال 3: مقایسه چند کلمه کلیدی

```python
keywords = ["seo", "seo optimization", "how to do seo"]

results = []
for keyword in keywords:
    result = await calculator.calculate_difficulty(keyword)
    results.append(result)

# مرتب‌سازی بر اساس Difficulty
results.sort(key=lambda x: x['difficulty_score'])

for result in results:
    print(f"{result['keyword']}: {result['difficulty_score']}/100")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'difficulty_score': int,           # 0-100
    'difficulty_level': str,           # 'easy', 'medium', 'hard'
    'estimated_effort': str,           # 'low', 'medium', 'high'
    'competitor_analysis': {
        'competitors': List[Dict],      # جزئیات هر رقیب
        'average_domain_authority': float,
        'average_backlinks': float,
        'average_content_quality': float,
        'strong_brand_count': int,
        'average_domain_age': float,
        'total_competitors_analyzed': int
    },
    'factors': {
        'domain_authority_impact': float,    # 0-1
        'backlinks_impact': float,            # 0-1
        'content_quality_impact': float,      # 0-1
        'brand_strength_impact': float,       # 0-1
        'domain_age_impact': float,           # 0-1
        'search_results_impact': float,       # 0-1
        'keyword_length_impact': float        # 0-1
    },
    'recommendations': List[str],      # توصیه‌های عملی
    'keyword': str,
    'total_results': int,
    'analyzed_competitors': int
}
```

## 🎯 فاکتورهای تاثیرگذار

### 1. Domain Authority (25%)
- هرچه Domain Authority رقبا بالاتر باشد، Difficulty بیشتر است
- برندهای قوی (Wikipedia, YouTube, etc.) Difficulty را افزایش می‌دهند

### 2. Backlinks (20%)
- تعداد Backlinks صفحات رتبه‌دار
- هرچه Backlinks بیشتر، رقابت سخت‌تر

### 3. Content Quality (15%)
- کیفیت محتوای رقبا
- بررسی H1, Meta Description, Alt Text, etc.

### 4. Brand Strength (15%)
- حضور برندهای قوی در نتایج
- برندهای معروف رقابت را سخت‌تر می‌کنند

### 5. Domain Age (10%)
- سن دامنه رقبا
- دامنه‌های قدیمی‌تر معمولاً Authority بالاتری دارند

### 6. Search Results (10%)
- تعداد کل نتایج جستجو
- هرچه نتایج بیشتر، رقابت بیشتر

### 7. Keyword Length (5%)
- طول کلمه کلیدی
- Long-tail keywords معمولاً آسان‌تر هستند

## 📈 تفسیر نتایج

### Difficulty Score: 0-30 (Easy)
- ✅ فرصت عالی
- ✅ رقابت کم
- ✅ نتایج در 1-3 ماه
- ✅ تلاش: Low

**توصیه‌ها:**
- محتوای هدفمند تولید کنید
- Technical SEO را بهینه کنید
- Local SEO را در نظر بگیرید

### Difficulty Score: 30-70 (Medium)
- ⚠️ رقابت متوسط
- ⚠️ نتایج در 3-6 ماه
- ⚠️ تلاش: Medium

**توصیه‌ها:**
- محتوای بهینه و ارزشمند تولید کنید
- Internal Linking را بهبود دهید
- Social Signals را افزایش دهید

### Difficulty Score: 70-100 (Hard)
- ❌ رقابت بسیار بالا
- ❌ نتایج در 6-12 ماه
- ❌ تلاش: High

**توصیه‌ها:**
- روی Long-tail keywords تمرکز کنید
- محتوای بسیار با کیفیت و جامع تولید کنید
- استراتژی Link Building قوی پیاده‌سازی کنید
- صبر و پشتکار داشته باشید

## 🔧 تنظیمات

### استفاده از APIهای خارجی

```python
# اگر SEMrush یا Ahrefs API موجود باشد، از آن‌ها استفاده می‌شود
result = await calculator.calculate_difficulty(
    keyword="seo",
    use_apis=True  # استفاده از APIها
)
```

### روش‌های رایگان

```python
# بدون نیاز به API Key
result = await calculator.calculate_difficulty(
    keyword="seo",
    use_apis=False  # فقط روش‌های رایگان
)
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import KeywordDifficultyCalculator

async def analyze_keyword(keyword: str):
    calculator = KeywordDifficultyCalculator()
    
    result = await calculator.calculate_difficulty(
        keyword=keyword,
        language='en',
        use_apis=True
    )
    
    print(f"\n📊 تحلیل: {keyword}")
    print(f"Difficulty: {result['difficulty_score']}/100")
    print(f"Level: {result['difficulty_level']}")
    print(f"Effort: {result['estimated_effort']}")
    
    # نمایش توصیه‌ها
    print("\n💡 توصیه‌ها:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
    
    await calculator.close()
    
    return result

# استفاده
result = asyncio.run(analyze_keyword("seo optimization"))
```

## ⚠️ محدودیت‌ها

### روش‌های رایگان
- تخمین‌ها ممکن است دقیق نباشند
- Domain Authority و Backlinks تخمینی هستند
- کیفیت محتوا بر اساس فاکتورهای محدود ارزیابی می‌شود

### استفاده از APIها
- نیاز به API Key دارد
- ممکن است هزینه‌بر باشد
- Rate Limiting ممکن است اعمال شود

## 🎯 بهترین روش‌ها

1. **استفاده ترکیبی**: از APIها برای دقت بیشتر و روش‌های رایگان برای سرعت
2. **مقایسه**: چند کلمه کلیدی را با هم مقایسه کنید
3. **Long-tail**: برای کلمات کلیدی سخت، روی Long-tail تمرکز کنید
4. **مانیتورینگ**: Difficulty را به صورت دوره‌ای بررسی کنید

## 📚 منابع

- [Moz Keyword Difficulty](https://moz.com/learn/seo/keyword-difficulty)
- [Ahrefs Keyword Difficulty](https://ahrefs.com/blog/keyword-difficulty/)
- [SEMrush Keyword Difficulty](https://www.semrush.com/kb/986-keyword-difficulty)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

