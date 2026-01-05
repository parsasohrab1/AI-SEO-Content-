"""
مثال استفاده از Long-tail Keyword Extractor
"""

import asyncio
import logging
from .long_tail_extractor import LongTailKeywordExtractor

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_extraction():
    """مثال: استخراج ساده Long-tail Keywords"""
    
    extractor = LongTailKeywordExtractor()
    
    # استخراج Long-tail keywords
    keywords = await extractor.extract_long_tail_keywords(
        seed_keywords=["seo"],
        min_length=3,  # حداقل 3 کلمه
        max_results=30,
        language='en'
    )
    
    print(f"\n✅ دریافت {len(keywords)} کلمه کلیدی Long-tail:\n")
    
    # گروه‌بندی بر اساس منبع
    by_source = {}
    for kw in keywords:
        source = kw.get('source', 'unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(kw)
    
    for source, kws in by_source.items():
        print(f"\n📊 {source} ({len(kws)} کلمه کلیدی):")
        for kw in kws[:5]:
            print(f"  • {kw['keyword']} ({kw['word_count']} کلمه)")
    
    await extractor.close()


async def example_persian_keywords():
    """مثال: استخراج Long-tail Keywords فارسی"""
    
    extractor = LongTailKeywordExtractor()
    
    keywords = await extractor.extract_long_tail_keywords(
        seed_keywords=["سئو"],
        min_length=3,
        max_results=30,
        language='fa'
    )
    
    print(f"\n✅ دریافت {len(keywords)} کلمه کلیدی Long-tail فارسی:\n")
    
    for i, kw in enumerate(keywords[:15], 1):
        print(f"{i}. {kw['keyword']}")
        print(f"   منبع: {kw['source']} | "
              f"تعداد کلمات: {kw['word_count']} | "
              f"سختی: {kw.get('estimated_difficulty', 'unknown')}")
    
    await extractor.close()


async def example_with_metrics():
    """مثال: استخراج با معیارها"""
    
    extractor = LongTailKeywordExtractor()
    
    # استخراج با دریافت معیارها از API
    keywords = await extractor.extract_with_metrics(
        seed_keywords=["seo"],
        min_length=3,
        max_results=20,
        language='en',
        get_metrics=True  # دریافت معیارها
    )
    
    print(f"\n✅ دریافت {len(keywords)} کلمه کلیدی با معیارها:\n")
    
    # مرتب‌سازی بر اساس Opportunity Score (اگر موجود باشد)
    keywords_with_metrics = [
        kw for kw in keywords if kw.get('opportunity_score')
    ]
    keywords_with_metrics.sort(
        key=lambda x: x.get('opportunity_score', 0),
        reverse=True
    )
    
    for kw in keywords_with_metrics[:10]:
        print(f"📊 {kw['keyword']}")
        if kw.get('search_volume'):
            print(f"   حجم جستجو: {kw['search_volume']:,}")
        if kw.get('difficulty'):
            print(f"   سختی: {kw['difficulty']}/100")
        if kw.get('opportunity_score'):
            print(f"   فرصت: {kw['opportunity_score']}/100")
        print()
    
    await extractor.close()


async def example_by_intent():
    """مثال: استخراج بر اساس Intent"""
    
    extractor = LongTailKeywordExtractor()
    
    seed_keyword = "seo"
    
    # استخراج بر اساس Intentهای مختلف
    intents = ['informational', 'commercial', 'transactional']
    
    print(f"\n🔍 استخراج Long-tail Keywords بر اساس Intent برای '{seed_keyword}':\n")
    
    for intent in intents:
        keywords = await extractor.extract_by_intent(
            seed_keyword=seed_keyword,
            intent=intent,
            language='en'
        )
        
        print(f"\n📌 {intent.upper()} Intent ({len(keywords)} کلمه کلیدی):")
        for kw in keywords[:5]:
            print(f"  • {kw['keyword']}")
    
    await extractor.close()


async def example_multiple_seeds():
    """مثال: استخراج از چند کلمه کلیدی اولیه"""
    
    extractor = LongTailKeywordExtractor()
    
    seed_keywords = ["seo", "keyword research", "on-page seo"]
    
    keywords = await extractor.extract_long_tail_keywords(
        seed_keywords=seed_keywords,
        min_length=3,
        max_results=50,
        language='en'
    )
    
    print(f"\n✅ دریافت {len(keywords)} کلمه کلیدی Long-tail از {len(seed_keywords)} کلمه کلیدی اولیه:\n")
    
    # گروه‌بندی بر اساس seed keyword
    by_seed = {}
    for kw in keywords:
        seed = kw.get('seed_keyword', 'unknown')
        if seed not in by_seed:
            by_seed[seed] = []
        by_seed[seed].append(kw)
    
    for seed, kws in by_seed.items():
        print(f"\n🌱 از '{seed}':")
        for kw in kws[:5]:
            print(f"  • {kw['keyword']} ({kw['word_count']} کلمه)")
    
    await extractor.close()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    extractor = LongTailKeywordExtractor()
    
    seed_keyword = "seo"
    
    print(f"🔍 استخراج Long-tail Keywords برای '{seed_keyword}'\n")
    
    # مرحله 1: استخراج Long-tail keywords
    print("📝 مرحله 1: استخراج Long-tail Keywords...")
    long_tail_keywords = await extractor.extract_long_tail_keywords(
        seed_keywords=[seed_keyword],
        min_length=3,
        max_results=50,
        language='en'
    )
    
    print(f"✅ {len(long_tail_keywords)} کلمه کلیدی Long-tail استخراج شد\n")
    
    # مرحله 2: فیلتر کردن بر اساس Difficulty
    print("📊 مرحله 2: فیلتر کردن بر اساس Difficulty...")
    low_difficulty = [
        kw for kw in long_tail_keywords
        if kw.get('estimated_difficulty') == 'low'
    ]
    
    print(f"✅ {len(low_difficulty)} کلمه کلیدی با Difficulty پایین\n")
    
    # مرحله 3: نمایش کلمات کلیدی برتر
    print("🎯 10 کلمه کلیدی Long-tail برتر:\n")
    for i, kw in enumerate(low_difficulty[:10], 1):
        print(f"{i}. {kw['keyword']}")
        print(f"   منبع: {kw['source']} | "
              f"کلمات: {kw['word_count']} | "
              f"سختی: {kw.get('estimated_difficulty', 'unknown')}")
    
    # مرحله 4: استخراج بر اساس Intent
    print("\n📌 استخراج بر اساس Intent:\n")
    for intent in ['informational', 'commercial', 'transactional']:
        intent_keywords = await extractor.extract_by_intent(
            seed_keyword=seed_keyword,
            intent=intent,
            language='en'
        )
        print(f"{intent}: {len(intent_keywords)} کلمه کلیدی")
    
    await extractor.close()


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Long-tail Keyword Extractor")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_extraction())
    # asyncio.run(example_persian_keywords())
    # asyncio.run(example_with_metrics())
    # asyncio.run(example_by_intent())
    # asyncio.run(example_multiple_seeds())
    asyncio.run(example_complete_workflow())

