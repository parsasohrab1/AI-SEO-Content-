"""
مثال استفاده از Semantic Keyword Analyzer
"""

import asyncio
import logging
from .semantic_analyzer import SemanticKeywordAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_find_semantic_keywords():
    """مثال: پیدا کردن کلمات کلیدی معنایی"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        print("Installing: pip install sentence-transformers")
        print("Model will be downloaded on first use.")
        return
    
    # پیدا کردن کلمات کلیدی معنایی
    semantic_keywords = await analyzer.find_semantic_keywords(
        main_keyword="seo optimization",
        threshold=0.6,
        top_n=20,
        language='en'
    )
    
    if semantic_keywords:
        print(f"\n✅ {len(semantic_keywords)} کلمه کلیدی معنایی پیدا شد:\n")
        
        # گروه‌بندی بر اساس نوع رابطه
        by_relation = {}
        for kw in semantic_keywords:
            relation = kw.get('semantic_relation', 'unknown')
            if relation not in by_relation:
                by_relation[relation] = []
            by_relation[relation].append(kw)
        
        for relation, kws in by_relation.items():
            print(f"\n📊 {relation} ({len(kws)} کلمه کلیدی):")
            for kw in kws[:5]:
                print(f"  • {kw['keyword']} (similarity: {kw['similarity']:.2f})")
    else:
        print("❌ هیچ کلمه کلیدی معنایی پیدا نشد")


async def example_lsi_keywords():
    """مثال: پیدا کردن کلمات کلیدی LSI"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        return
    
    main_keyword = "seo"
    context_keywords = [
        "search engine optimization",
        "keyword research",
        "on-page seo",
        "off-page seo",
        "link building",
        "content marketing",
        "technical seo"
    ]
    
    lsi_keywords = await analyzer.find_lsi_keywords(
        main_keyword=main_keyword,
        context_keywords=context_keywords,
        top_n=10
    )
    
    if lsi_keywords:
        print(f"\n✅ {len(lsi_keywords)} کلمه کلیدی LSI پیدا شد:\n")
        for kw in lsi_keywords:
            print(f"  • {kw['keyword']}")
            print(f"    LSI Score: {kw['lsi_score']:.2f}")
    else:
        print("❌ هیچ کلمه کلیدی LSI پیدا نشد")


async def example_cluster_keywords():
    """مثال: خوشه‌بندی کلمات کلیدی"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        return
    
    keywords = [
        "seo optimization",
        "keyword research",
        "link building",
        "content marketing",
        "social media marketing",
        "email marketing",
        "ppc advertising",
        "google ads",
        "facebook ads",
        "on-page seo",
        "off-page seo",
        "technical seo"
    ]
    
    clusters = await analyzer.cluster_semantic_keywords(
        keywords=keywords,
        n_clusters=3
    )
    
    if clusters:
        print(f"\n✅ کلمات کلیدی در {len(clusters)} خوشه:\n")
        for cluster_id, cluster_keywords in clusters.items():
            print(f"\n📦 خوشه {cluster_id + 1}:")
            for kw in cluster_keywords:
                print(f"  • {kw}")
    else:
        print("❌ خوشه‌بندی انجام نشد")


async def example_expand_keyword():
    """مثال: گسترش کلمه کلیدی"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        return
    
    keyword = "seo"
    
    # گسترش به صورت synonyms
    synonyms = await analyzer.expand_keyword_semantically(
        keyword=keyword,
        expansion_type='synonyms',
        language='en'
    )
    
    print(f"\n✅ Synonyms برای '{keyword}':")
    for syn in synonyms[:10]:
        print(f"  • {syn}")
    
    # گسترش به صورت related
    related = await analyzer.expand_keyword_semantically(
        keyword=keyword,
        expansion_type='related',
        language='en'
    )
    
    print(f"\n✅ Related keywords برای '{keyword}':")
    for rel in related[:10]:
        print(f"  • {rel}")


async def example_semantic_relationship():
    """مثال: بررسی رابطه معنایی"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        return
    
    keyword_pairs = [
        ("seo", "search engine optimization"),
        ("seo", "content marketing"),
        ("keyword research", "keyword analysis"),
        ("seo", "cooking recipe")
    ]
    
    print("\n🔍 بررسی روابط معنایی:\n")
    for kw1, kw2 in keyword_pairs:
        relationship = analyzer.get_semantic_relationship(kw1, kw2)
        
        print(f"{kw1} ↔ {kw2}")
        print(f"  Similarity: {relationship['similarity']:.2f}")
        print(f"  Relationship: {relationship['relationship']}")
        print(f"  Confidence: {relationship['confidence']:.2f}")
        print()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = SemanticKeywordAnalyzer()
    
    if not analyzer.model_loaded:
        print("⚠️ Semantic model not loaded.")
        print("\nبرای استفاده از Semantic Analysis:")
        print("1. pip install sentence-transformers")
        print("2. مدل به صورت خودکار دانلود می‌شود")
        return
    
    main_keyword = "seo"
    
    print(f"🔍 تحلیل معنایی برای '{main_keyword}'\n")
    
    # مرحله 1: پیدا کردن کلمات کلیدی معنایی
    print("📝 مرحله 1: پیدا کردن کلمات کلیدی معنایی...")
    semantic_keywords = await analyzer.find_semantic_keywords(
        main_keyword=main_keyword,
        threshold=0.6,
        top_n=20,
        language='en'
    )
    
    print(f"✅ {len(semantic_keywords)} کلمه کلیدی معنایی پیدا شد\n")
    
    # مرحله 2: خوشه‌بندی
    if semantic_keywords:
        print("📝 مرحله 2: خوشه‌بندی کلمات کلیدی...")
        keywords_list = [kw['keyword'] for kw in semantic_keywords]
        clusters = await analyzer.cluster_semantic_keywords(
            keywords=keywords_list,
            n_clusters=3
        )
        
        if clusters:
            print(f"✅ {len(clusters)} خوشه ایجاد شد\n")
            for cluster_id, cluster_keywords in clusters.items():
                print(f"خوشه {cluster_id + 1}: {', '.join(cluster_keywords[:5])}")
    
    # مرحله 3: گسترش کلمه کلیدی
    print(f"\n📝 مرحله 3: گسترش کلمه کلیدی '{main_keyword}'...")
    expanded = await analyzer.expand_keyword_semantically(
        keyword=main_keyword,
        expansion_type='related',
        language='en'
    )
    
    print(f"✅ {len(expanded)} کلمه کلیدی گسترش یافته:")
    for kw in expanded[:10]:
        print(f"  • {kw}")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Semantic Keyword Analyzer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_find_semantic_keywords())
    # asyncio.run(example_lsi_keywords())
    # asyncio.run(example_cluster_keywords())
    # asyncio.run(example_expand_keyword())
    # asyncio.run(example_semantic_relationship())
    asyncio.run(example_complete_workflow())

