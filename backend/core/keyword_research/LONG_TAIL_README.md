# راهنمای Long-tail Keyword Extractor

## 📋 معرفی

این ماژول استخراج کلمات کلیدی Long-tail را انجام می‌دهد. Long-tail keywords کلمات کلیدی طولانی‌تر و خاص‌تر هستند که معمولاً رقابت کمتری دارند و نرخ تبدیل بالاتری دارند.

## ✨ ویژگی‌ها

- ✅ استخراج از Google Autocomplete
- ✅ استخراج از People Also Ask (PAA)
- ✅ استخراج از Related Searches
- ✅ ترکیب با Modifiers
- ✅ تولید Keywords سوالی
- ✅ استخراج بر اساس Intent
- ✅ دریافت معیارها (اختیاری)
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 استفاده

### مثال 1: استخراج ساده

```python
from backend.core.keyword_research import LongTailKeywordExtractor

extractor = LongTailKeywordExtractor()

keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["seo"],
    min_length=3,  # حداقل 3 کلمه
    max_results=50,
    language='en'
)

for kw in keywords:
    print(f"{kw['keyword']} - منبع: {kw['source']}")
```

### مثال 2: استخراج با معیارها

```python
# دریافت معیارها از APIهای خارجی
keywords = await extractor.extract_with_metrics(
    seed_keywords=["seo"],
    min_length=3,
    max_results=30,
    language='en',
    get_metrics=True  # دریافت Search Volume, Difficulty, etc.
)

# مرتب‌سازی بر اساس Opportunity Score
sorted_keywords = sorted(
    keywords,
    key=lambda x: x.get('opportunity_score', 0),
    reverse=True
)
```

### مثال 3: استخراج بر اساس Intent

```python
# استخراج Keywords با Intent مشخص
informational = await extractor.extract_by_intent(
    seed_keyword="seo",
    intent='informational',  # یا 'commercial', 'transactional'
    language='en'
)
```

### مثال 4: استخراج فارسی

```python
keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["سئو"],
    min_length=3,
    max_results=30,
    language='fa'
)
```

## 📊 ساختار داده‌های بازگشتی

```python
[
    {
        'keyword': str,                    # کلمه کلیدی Long-tail
        'source': str,                     # autocomplete, paa, related_searches, combination, question
        'seed_keyword': str,               # کلمه کلیدی اولیه
        'word_count': int,                 # تعداد کلمات
        'estimated_difficulty': str,        # low, medium, high
        'search_volume': int,              # (اگر get_metrics=True)
        'competition': str,                 # (اگر get_metrics=True)
        'difficulty': int,                 # (اگر get_metrics=True)
        'opportunity_score': float         # (اگر get_metrics=True)
    },
    ...
]
```

## 🎯 منابع استخراج

### 1. Google Autocomplete
- پیشنهادات خودکار Google
- معمولاً 10 پیشنهاد اول
- منبع: `autocomplete`

### 2. People Also Ask (PAA)
- سوالات مرتبط که کاربران می‌پرسند
- معمولاً 10-20 سوال
- منبع: `people_also_ask`

### 3. Related Searches
- جستجوهای مرتبط در پایین صفحه نتایج
- معمولاً 8-10 جستجو
- منبع: `related_searches`

### 4. Combination (ترکیب)
- ترکیب کلمه کلیدی با Modifiers
- مثال: "بهترین seo", "راهنمای seo"
- منبع: `combination`

### 5. Question-based
- تولید Keywords سوالی
- مثال: "چگونه seo", "seo چیست"
- منبع: `question`

## 🎯 Intent-based Keywords

### Informational Intent
**هدف:** جستجوی اطلاعات

**Modifiers فارسی:**
- چیست، چگونه، راهنمای، آموزش، تفاوت

**Modifiers انگلیسی:**
- what is, how to, guide, tutorial, difference

**مثال:**
- "چگونه سئو را بهبود دهیم"
- "what is seo optimization"

### Commercial Intent
**هدف:** جستجوی تجاری (قبل از خرید)

**Modifiers فارسی:**
- بهترین، مقایسه، نقد و بررسی، مزایا و معایب

**Modifiers انگلیسی:**
- best, compare, review, pros and cons

**مثال:**
- "بهترین ابزار سئو"
- "best seo tools comparison"

### Transactional Intent
**هدف:** جستجوی خرید

**Modifiers فارسی:**
- خرید، قیمت، فروش، تخفیف، ارزان

**Modifiers انگلیسی:**
- buy, price, sell, discount, cheap

**مثال:**
- "خرید ابزار سئو"
- "buy seo tool"

## 📈 مزایای Long-tail Keywords

### 1. رقابت کمتر
- Long-tail keywords معمولاً رقابت کمتری دارند
- رتبه‌گیری آسان‌تر است

### 2. نرخ تبدیل بالاتر
- کاربران با Long-tail keywords هدفمندتر هستند
- احتمال تبدیل بیشتر است

### 3. هدف‌گیری دقیق‌تر
- Long-tail keywords دقیق‌تر هستند
- ترافیک با کیفیت‌تر

### 4. فرصت‌های بیشتر
- هزاران Long-tail keyword برای هر کلمه کلیدی اصلی
- فرصت‌های نامحدود

## 🔧 تنظیمات

### min_length
حداقل تعداد کلمات برای Long-tail keyword:

```python
keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["seo"],
    min_length=4  # حداقل 4 کلمه
)
```

### max_results
حداکثر تعداد نتایج:

```python
keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["seo"],
    max_results=100  # حداکثر 100 کلمه کلیدی
)
```

### use_all_methods
استفاده از تمام روش‌ها یا فقط ترکیب:

```python
# استفاده از تمام روش‌ها (پیش‌فرض)
keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["seo"],
    use_all_methods=True
)

# فقط ترکیب با Modifiers (سریع‌تر)
keywords = await extractor.extract_long_tail_keywords(
    seed_keywords=["seo"],
    use_all_methods=False
)
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import LongTailKeywordExtractor

async def main():
    extractor = LongTailKeywordExtractor()
    
    # استخراج Long-tail keywords
    keywords = await extractor.extract_long_tail_keywords(
        seed_keywords=["seo", "keyword research"],
        min_length=3,
        max_results=50,
        language='en'
    )
    
    # فیلتر کردن بر اساس Difficulty
    low_difficulty = [
        kw for kw in keywords
        if kw.get('estimated_difficulty') == 'low'
    ]
    
    print(f"✅ {len(low_difficulty)} کلمه کلیدی با Difficulty پایین:\n")
    for kw in low_difficulty[:10]:
        print(f"  • {kw['keyword']}")
    
    # استخراج بر اساس Intent
    for intent in ['informational', 'commercial', 'transactional']:
        intent_keywords = await extractor.extract_by_intent(
            seed_keyword="seo",
            intent=intent,
            language='en'
        )
        print(f"\n{intent}: {len(intent_keywords)} کلمه کلیدی")
    
    await extractor.close()

asyncio.run(main())
```

## ⚠️ محدودیت‌ها

### Rate Limiting
- Google ممکن است درخواست‌های زیاد را محدود کند
- بین درخواست‌ها delay اضافه کنید

### نتایج متغیر
- نتایج Google Autocomplete و Related Searches ممکن است تغییر کنند
- نتایج ممکن است بر اساس موقعیت جغرافیایی متفاوت باشند

### زبان
- برخی روش‌ها برای زبان‌های خاص بهتر کار می‌کنند
- فارسی و انگلیسی به خوبی پشتیبانی می‌شوند

## 🎯 بهترین روش‌ها

1. **استفاده ترکیبی**: از تمام روش‌ها استفاده کنید
2. **فیلتر کردن**: بر اساس Difficulty و Intent فیلتر کنید
3. **تحلیل معیارها**: از `get_metrics=True` برای دریافت معیارها استفاده کنید
4. **گروه‌بندی**: کلمات کلیدی را بر اساس Intent گروه‌بندی کنید

## 📊 آمار

- **Google Autocomplete**: معمولاً 10-20 کلمه کلیدی
- **People Also Ask**: معمولاً 10-20 سوال
- **Related Searches**: معمولاً 8-10 جستجو
- **Combination**: 10-15 کلمه کلیدی (بسته به تعداد Modifiers)
- **Question-based**: 10 کلمه کلیدی

**جمع کل**: معمولاً 50-100+ کلمه کلیدی Long-tail برای هر seed keyword

## 🔍 مثال‌های واقعی

### Seed Keyword: "seo"

**Long-tail Keywords:**
- "how to improve seo for beginners"
- "best seo tools 2024"
- "seo optimization guide"
- "what is seo and why is it important"
- "compare seo tools"

### Seed Keyword: "سئو"

**Long-tail Keywords:**
- "چگونه سئو سایت را بهبود دهیم"
- "بهترین ابزار سئو 1404"
- "راهنمای بهینه‌سازی سئو"
- "سئو چیست و چرا مهم است"
- "مقایسه ابزارهای سئو"

## 📚 منابع

- [Long-tail Keywords Guide](https://ahrefs.com/blog/long-tail-keywords/)
- [Google Autocomplete](https://support.google.com/websearch/answer/106230)
- [People Also Ask](https://www.searchenginejournal.com/people-also-ask/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

