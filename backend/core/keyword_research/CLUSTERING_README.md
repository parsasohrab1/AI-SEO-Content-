# راهنمای Keyword Clusterer

## 📋 معرفی

این ماژول خوشه‌بندی کلمات کلیدی را انجام می‌دهد. کلمات کلیدی مرتبط را در خوشه‌های موضوعی گروه‌بندی می‌کند و استراتژی محتوا برای هر خوشه پیشنهاد می‌دهد.

## ✨ Features

- ✅ خوشه‌بندی کلمات کلیدی بر اساس موضوع
- ✅ شناسایی کلمات کلیدی اصلی هر خوشه
- ✅ پیشنهاد استراتژی محتوا برای هر خوشه
- ✅ محاسبه معیارهای هر خوشه
- ✅ پشتیبانی از روش‌های مختلف (semantic, topic, hybrid)
- ✅ محاسبه خودکار تعداد خوشه‌ها
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 Usage

### مثال 1: خوشه‌بندی ساده

```python
from backend.core.keyword_research import KeywordClusterer

clusterer = KeywordClusterer()

keywords = [
    "seo optimization",
    "keyword research",
    "on-page seo",
    "link building",
    "content marketing"
]

result = await clusterer.cluster_keywords(
    keywords=keywords,
    n_clusters=3,
    method='hybrid',
    language='en'
)

# نمایش خوشه‌ها
for cluster_id, cluster_data in result['clusters'].items():
    print(f"خوشه {cluster_id}: {cluster_data['topic']}")
    print(f"  کلمات کلیدی: {cluster_data['keywords']}")
```

### مثال 2: خوشه‌بندی خودکار

```python
# تعداد خوشه‌ها به صورت خودکار محاسبه می‌شود
result = await clusterer.cluster_keywords(
    keywords=keywords,
    n_clusters=None,  # خودکار
    method='hybrid'
)
```

### مثال 3: دریافت استراتژی محتوا

```python
result = await clusterer.cluster_keywords(keywords=keywords)

# استراتژی محتوا برای هر خوشه
for cluster_id, strategy in result['content_strategy'].items():
    print(f"خوشه {cluster_id}:")
    print(f"  نوع: {strategy['type']}")
    print(f"  توصیحات: {strategy['description']}")
    print(f"  طول: {strategy['recommended_length']}")
    print(f"  فرکانس: {strategy['frequency']}")
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'clusters': {
        0: {
            'keywords': List[str],
            'topic': str,
            'main_keyword': str,
            'size': int,
            'metrics': {
                'average_length': float,
                'long_tail_count': int,
                'long_tail_ratio': float,
                'diversity': float,
                'total_keywords': int
            },
            'cluster_id': int
        },
        ...
    },
    'cluster_summary': {
        'total_clusters': int,
        'total_keywords': int,
        'average_keywords_per_cluster': float,
        'main_keywords': Dict[int, str]
    },
    'content_strategy': {
        0: {
            'type': str,  # Pillar, Cluster, Supporting
            'description': str,
            'recommended_length': str,
            'frequency': str,
            'recommendations': List[str],
            'keywords_count': int,
            'main_keyword': str
        },
        ...
    },
    'total_keywords': int,
    'total_clusters': int,
    'method_used': str
}
```

## 🎯 روش‌های خوشه‌بندی

### 1. Semantic (معنایی)
- استفاده از Word Embeddings
- نیاز به SemanticKeywordAnalyzer
- دقت بالا

```python
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='semantic'
)
```

### 2. Topic (موضوعی)
- گروه‌بندی بر اساس کلمات مشترک
- بدون نیاز به مدل
- سریع‌تر

```python
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='topic'
)
```

### 3. Hybrid (ترکیبی)
- ترکیب semantic و topic
- ابتدا semantic، سپس fallback به topic
- **پیشنهاد شده**

```python
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='hybrid'  # پیش‌فرض
)
```

## 📝 انواع استراتژی محتوا

### Pillar Content
- برای خوشه‌های بزرگ (≥10 کلمات کلیدی)
- مقاله جامع و کامل
- 3000+ کلمه
- 1 مقاله در ماه

### Cluster Content
- برای خوشه‌های متوسط (5-9 کلمات کلیدی)
- مقالات تخصصی
- 1500-2000 کلمه
- 2-3 مقاله در ماه

### Supporting Content
- برای خوشه‌های کوچک (<5 کلمات کلیدی)
- مقالات کوتاه
- 800-1200 کلمه
- 4-5 مقاله در ماه

## 🎯 کاربردها

### 1. Content Strategy
- سازماندهی کلمات کلیدی برای استراتژی محتوا
- تعیین اولویت‌های تولید محتوا
- پوشش کامل موضوعات

### 2. Topic Clusters
- ایجاد Topic Clusters (Pillar + Cluster Content)
- ساختار محتوای منسجم
- بهبود Internal Linking

### 3. Keyword Organization
- سازماندهی کلمات کلیدی
- شناسایی موضوعات اصلی
- اولویت‌بندی کلمات کلیدی

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import KeywordClusterer

async def main():
    clusterer = KeywordClusterer()
    
    keywords = [
        "seo optimization",
        "keyword research",
        "on-page seo",
        "link building",
        "content marketing",
        "social media marketing"
    ]
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        method='hybrid',
        language='en'
    )
    
    # نمایش خوشه‌ها
    for cluster_id, cluster_data in result['clusters'].items():
        print(f"\nخوشه {cluster_id + 1}:")
        print(f"  موضوع: {cluster_data['topic']}")
        print(f"  کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"  کلمات کلیدی: {cluster_data['keywords']}")
        
        # استراتژی محتوا
        strategy = result['content_strategy'][cluster_id]
        print(f"\n  استراتژی:")
        print(f"    نوع: {strategy['type']}")
        print(f"    طول: {strategy['recommended_length']}")

asyncio.run(main())
```

## 🔧 تنظیمات

### تعیین تعداد خوشه‌ها

```python
# خودکار (پیشنهاد شده)
result = await clusterer.cluster_keywords(
    keywords=keywords,
    n_clusters=None
)

# دستی
result = await clusterer.cluster_keywords(
    keywords=keywords,
    n_clusters=5
)
```

### انتخاب روش

```python
# Semantic (نیاز به مدل)
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='semantic'
)

# Topic (بدون نیاز به مدل)
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='topic'
)

# Hybrid (بهترین)
result = await clusterer.cluster_keywords(
    keywords=keywords,
    method='hybrid'
)
```

## 📊 معیارهای خوشه

هر خوشه شامل معیارهای زیر است:

- **average_length**: میانگین طول کلمات کلیدی
- **long_tail_count**: تعداد Long-tail keywords
- **long_tail_ratio**: نسبت Long-tail keywords
- **diversity**: تنوع کلمات کلیدی
- **total_keywords**: تعداد کل کلمات کلیدی

## 🎯 Pillar & Cluster Strategy

این ماژول از استراتژی **Pillar & Cluster** استفاده می‌کند:

1. **Pillar Content**: مقاله جامع درباره موضوع اصلی
2. **Cluster Content**: مقالات تخصصی برای هر کلمه کلیدی
3. **Supporting Content**: مقالات کوتاه و سریع

این استراتژی به بهبود Internal Linking و Authority کمک می‌کند.

## ⚠️ محدودیت‌ها

### تعداد کلمات کلیدی
- حداقل 2 کلمه کلیدی برای خوشه‌بندی
- برای 1 کلمه کلیدی، یک خوشه واحد ایجاد می‌شود

### دقت
- روش Topic ممکن است دقت کمتری داشته باشد
- روش Semantic دقیق‌تر است اما نیاز به مدل دارد

## 🔍 مثال‌های واقعی

### ورودی:
```python
keywords = [
    "seo",
    "keyword research",
    "on-page seo",
    "link building",
    "content marketing"
]
```

### خروجی:
```python
{
    'clusters': {
        0: {
            'topic': 'seo',
            'main_keyword': 'seo',
            'keywords': ['seo', 'on-page seo', 'keyword research'],
            'size': 3
        },
        1: {
            'topic': 'marketing',
            'main_keyword': 'content marketing',
            'keywords': ['content marketing', 'link building'],
            'size': 2
        }
    },
    'content_strategy': {
        0: {
            'type': 'Supporting Content',
            'recommended_length': '800-1200 words'
        },
        1: {
            'type': 'Supporting Content',
            'recommended_length': '800-1200 words'
        }
    }
}
```

## 📚 منابع

- [Topic Clusters](https://www.hubspot.com/topic-clusters)
- [Pillar Content Strategy](https://ahrefs.com/blog/pillar-content/)
- [Keyword Clustering](https://www.semrush.com/blog/keyword-clustering/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

