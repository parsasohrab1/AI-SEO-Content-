# راهنمای Semantic Keyword Analyzer

## 📋 معرفی

این ماژول تحلیل معنایی کلمات کلیدی را انجام می‌دهد. با استفاده از Word Embeddings و NLP، کلمات کلیدی معنایی مرتبط، هم‌معناها و کلمات کلیدی LSI را پیدا می‌کند.

## ✨ Features

- ✅ پیدا کردن کلمات کلیدی معنایی مرتبط
- ✅ شناسایی هم‌معناها (Synonyms)
- ✅ پیدا کردن کلمات کلیدی LSI (Latent Semantic Indexing)
- ✅ خوشه‌بندی کلمات کلیدی بر اساس معنا
- ✅ گسترش کلمات کلیدی به صورت معنایی
- ✅ بررسی رابطه معنایی بین کلمات کلیدی
- ✅ پشتیبانی از چند زبان (فارسی و انگلیسی)

## 🚀 نصب

### وابستگی‌های مورد نیاز

```bash
pip install sentence-transformers scikit-learn numpy
```

یا از requirements.txt:
```bash
pip install -r requirements.txt
```

**نکته:** مدل SentenceTransformer در اولین استفاده به صورت خودکار دانلود می‌شود (~420 MB).

## 📖 استفاده

### مثال 1: پیدا کردن کلمات کلیدی معنایی

```python
from backend.core.keyword_research import SemanticKeywordAnalyzer

analyzer = SemanticKeywordAnalyzer()

semantic_keywords = await analyzer.find_semantic_keywords(
    main_keyword="seo optimization",
    threshold=0.7,  # حداقل similarity
    top_n=20,
    language='en'
)

for kw in semantic_keywords:
    print(f"{kw['keyword']} - similarity: {kw['similarity']:.2f}")
```

### مثال 2: پیدا کردن کلمات کلیدی LSI

```python
main_keyword = "seo"
context_keywords = [
    "search engine optimization",
    "keyword research",
    "on-page seo",
    "link building"
]

lsi_keywords = await analyzer.find_lsi_keywords(
    main_keyword=main_keyword,
    context_keywords=context_keywords,
    top_n=10
)
```

### مثال 3: خوشه‌بندی کلمات کلیدی

```python
keywords = [
    "seo optimization",
    "keyword research",
    "link building",
    "content marketing",
    "social media marketing"
]

clusters = await analyzer.cluster_semantic_keywords(
    keywords=keywords,
    n_clusters=3
)

for cluster_id, cluster_keywords in clusters.items():
    print(f"خوشه {cluster_id}: {cluster_keywords}")
```

### مثال 4: گسترش کلمه کلیدی

```python
# گسترش به صورت synonyms
synonyms = await analyzer.expand_keyword_semantically(
    keyword="seo",
    expansion_type='synonyms',
    language='en'
)

# گسترش به صورت related
related = await analyzer.expand_keyword_semantically(
    keyword="seo",
    expansion_type='related',
    language='en'
)
```

### مثال 5: بررسی رابطه معنایی

```python
relationship = analyzer.get_semantic_relationship(
    keyword1="seo",
    keyword2="search engine optimization"
)

print(f"Similarity: {relationship['similarity']:.2f}")
print(f"Relationship: {relationship['relationship']}")
```

## 📊 ساختار داده‌های بازگشتی

### find_semantic_keywords()

```python
[
    {
        'keyword': str,
        'similarity': float,           # 0-1
        'semantic_relation': str,       # synonym, highly_related, related, lsi
        'source': 'semantic_analysis'
    },
    ...
]
```

### find_lsi_keywords()

```python
[
    {
        'keyword': str,
        'lsi_score': float,            # 0-1
        'context_similarity': float,    # 0-1
        'source': 'lsi_analysis'
    },
    ...
]
```

### cluster_semantic_keywords()

```python
{
    0: ['keyword1', 'keyword2', ...],
    1: ['keyword3', 'keyword4', ...],
    ...
}
```

### get_semantic_relationship()

```python
{
    'similarity': float,        # 0-1
    'relationship': str,        # synonym, highly_related, related, unrelated
    'confidence': float         # 0-1
}
```

## 🎯 انواع روابط معنایی

### Synonym (هم‌معنا)
- Similarity: ≥ 0.9
- کلمات کلیدی که معنی یکسانی دارند
- مثال: "seo" و "search engine optimization"

### Highly Related (بسیار مرتبط)
- Similarity: 0.75 - 0.9
- کلمات کلیدی که بسیار مرتبط هستند
- مثال: "seo" و "keyword research"

### Related (مرتبط)
- Similarity: 0.6 - 0.75
- کلمات کلیدی که مرتبط هستند
- مثال: "seo" و "content marketing"

### LSI (Latent Semantic Indexing)
- Similarity: 0.5 - 0.6
- کلمات کلیدی که در همان زمینه استفاده می‌شوند
- مثال: "seo" و "website traffic"

## 🔧 تنظیمات

### تغییر مدل

```python
# در environment variables
SEMANTIC_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2

# یا مدل‌های دیگر:
# - paraphrase-MiniLM-L6-v2 (انگلیسی، سریع‌تر)
# - distiluse-base-multilingual-cased (چندزبانه)
```

### Threshold

```python
# threshold بالاتر = نتایج دقیق‌تر اما کمتر
semantic_keywords = await analyzer.find_semantic_keywords(
    main_keyword="seo",
    threshold=0.8  # فقط کلمات کلیدی با similarity ≥ 0.8
)
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.keyword_research import SemanticKeywordAnalyzer

async def main():
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ مدل بارگذاری نشده است")
        return
    
    # 1. پیدا کردن کلمات کلیدی معنایی
    semantic_keywords = await analyzer.find_semantic_keywords(
        main_keyword="seo",
        threshold=0.6,
        top_n=20
    )
    
    # 2. خوشه‌بندی
    keywords_list = [kw['keyword'] for kw in semantic_keywords]
    clusters = await analyzer.cluster_semantic_keywords(
        keywords=keywords_list,
        n_clusters=3
    )
    
    # 3. نمایش نتایج
    print(f"✅ {len(semantic_keywords)} کلمه کلیدی معنایی")
    print(f"✅ {len(clusters)} خوشه ایجاد شد")

asyncio.run(main())
```

## 🎯 کاربردها

### 1. بهبود محتوا
- استفاده از کلمات کلیدی معنایی در محتوا
- بهبود Relevance برای موتورهای جستجو

### 2. Keyword Research
- پیدا کردن کلمات کلیدی مرتبط
- گسترش لیست کلمات کلیدی

### 3. Content Optimization
- استفاده از LSI keywords در محتوا
- بهبود Semantic SEO

### 4. Keyword Clustering
- سازماندهی کلمات کلیدی
- استراتژی محتوا بر اساس خوشه‌ها

## ⚠️ محدودیت‌ها

### نیاز به مدل
- نیاز به دانلود مدل (اولین بار ~420 MB)
- نیاز به RAM کافی برای اجرای مدل

### دقت
- نتایج بر اساس مدل هستند
- ممکن است برای زبان‌های خاص دقت کمتری داشته باشد

### Performance
- محاسبه embeddings ممکن است زمان‌بر باشد
- برای لیست‌های بزرگ، از batch processing استفاده کنید

## 🔧 بهینه‌سازی

### استفاده از Cache

```python
# Cache کردن embeddings
import redis
cache = redis.Redis()

async def get_cached_embedding(keyword):
    cache_key = f"embedding:{keyword}"
    cached = cache.get(cache_key)
    if cached:
        return pickle.loads(cached)
    
    embedding = analyzer.model.encode([keyword])[0]
    cache.setex(cache_key, 86400, pickle.dumps(embedding))  # 24 ساعت
    return embedding
```

### Batch Processing

```python
# پردازش دسته‌ای برای بهبود عملکرد
keywords = ["seo", "keyword research", "link building"]
embeddings = analyzer.model.encode(keywords, batch_size=32)
```

## 📚 منابع

- [Sentence Transformers](https://www.sbert.net/)
- [Word Embeddings](https://en.wikipedia.org/wiki/Word_embedding)
- [LSI Keywords](https://www.searchenginejournal.com/lsi-keywords/)
- [Semantic SEO](https://ahrefs.com/blog/semantic-seo/)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

