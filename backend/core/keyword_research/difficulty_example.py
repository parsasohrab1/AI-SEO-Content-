"""
مثال استفاده از Keyword Difficulty Calculator
"""

import asyncio
import logging
from .keyword_difficulty import KeywordDifficultyCalculator

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_difficulty():
    """مثال: محاسبه ساده Keyword Difficulty"""
    
    calculator = KeywordDifficultyCalculator()
    
    # محاسبه Difficulty
    result = await calculator.calculate_difficulty(
        keyword="seo optimization",
        language='en',
        use_apis=False  # استفاده از روش‌های رایگان
    )
    
    print("\n✅ نتایج محاسبه Keyword Difficulty:\n")
    print(f"کلمه کلیدی: {result['keyword']}")
    print(f"Difficulty Score: {result['difficulty_score']}/100")
    print(f"Difficulty Level: {result['difficulty_level']}")
    print(f"Estimated Effort: {result['estimated_effort']}")
    print(f"تعداد نتایج جستجو: {result['total_results']:,}")
    print(f"تعداد رقبا تحلیل شده: {result['analyzed_competitors']}")
    
    # نمایش فاکتورها
    if result.get('factors'):
        print("\n📊 فاکتورهای تاثیرگذار:\n")
        factors = result['factors']
        print(f"Domain Authority Impact: {factors.get('domain_authority_impact', 0):.2f}")
        print(f"Backlinks Impact: {factors.get('backlinks_impact', 0):.2f}")
        print(f"Content Quality Impact: {factors.get('content_quality_impact', 0):.2f}")
        print(f"Brand Strength Impact: {factors.get('brand_strength_impact', 0):.2f}")
        print(f"Domain Age Impact: {factors.get('domain_age_impact', 0):.2f}")
        print(f"Search Results Impact: {factors.get('search_results_impact', 0):.2f}")
        print(f"Keyword Length Impact: {factors.get('keyword_length_impact', 0):.2f}")
    
    # نمایش تحلیل رقبا
    if result.get('competitor_analysis'):
        comp_analysis = result['competitor_analysis']
        print("\n🏆 تحلیل رقبا:\n")
        print(f"میانگین Domain Authority: {comp_analysis.get('average_domain_authority', 0):.2f}")
        print(f"میانگین Backlinks: {comp_analysis.get('average_backlinks', 0):,.0f}")
        print(f"میانگین Content Quality: {comp_analysis.get('average_content_quality', 0):.2f}")
        print(f"تعداد برندهای قوی: {comp_analysis.get('strong_brand_count', 0)}")
        print(f"میانگین سن دامنه: {comp_analysis.get('average_domain_age', 0):.2f} سال")
    
    # نمایش توصیه‌ها
    if result.get('recommendations'):
        print("\n💡 توصیه‌ها:\n")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec}")
    
    await calculator.close()


async def example_comparison():
    """مثال: مقایسه Difficulty چند کلمه کلیدی"""
    
    calculator = KeywordDifficultyCalculator()
    
    keywords = [
        "seo",
        "seo optimization",
        "how to optimize seo for beginners",
        "best seo tools 2024"
    ]
    
    print("\n🔍 مقایسه Difficulty کلمات کلیدی:\n")
    
    results = []
    for keyword in keywords:
        result = await calculator.calculate_difficulty(
            keyword=keyword,
            language='en',
            use_apis=False
        )
        results.append(result)
    
    # مرتب‌سازی بر اساس Difficulty Score
    results.sort(key=lambda x: x['difficulty_score'])
    
    print("کلمات کلیدی از آسان به سخت:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['keyword']}")
        print(f"   Difficulty: {result['difficulty_score']}/100 ({result['difficulty_level']})")
        print(f"   Effort: {result['estimated_effort']}")
        print()
    
    await calculator.close()


async def example_with_apis():
    """مثال: استفاده با APIهای خارجی"""
    
    calculator = KeywordDifficultyCalculator()
    
    # استفاده از APIهای خارجی (SEMrush, Ahrefs) اگر موجود باشند
    result = await calculator.calculate_difficulty(
        keyword="seo optimization",
        language='en',
        use_apis=True  # استفاده از APIها
    )
    
    print("\n✅ نتایج با استفاده از APIهای خارجی:\n")
    print(f"Difficulty Score: {result['difficulty_score']}/100")
    print(f"Difficulty Level: {result['difficulty_level']}")
    
    # نمایش جزئیات رقبا
    if result.get('competitor_analysis', {}).get('competitors'):
        print("\n🏆 جزئیات رقبا:\n")
        for i, comp in enumerate(result['competitor_analysis']['competitors'][:5], 1):
            print(f"{i}. {comp['domain']}")
            print(f"   DA: {comp.get('domain_authority', 0)}")
            print(f"   Backlinks: {comp.get('backlinks', 0):,}")
            print(f"   Content Quality: {comp.get('content_quality_score', 0)}")
            print(f"   Strong Brand: {comp.get('is_strong_brand', False)}")
            print()
    
    await calculator.close()


async def example_persian_keyword():
    """مثال: محاسبه Difficulty برای کلمه کلیدی فارسی"""
    
    calculator = KeywordDifficultyCalculator()
    
    result = await calculator.calculate_difficulty(
        keyword="بهینه‌سازی سئو",
        language='fa',
        use_apis=False
    )
    
    print("\n✅ نتایج برای کلمه کلیدی فارسی:\n")
    print(f"کلمه کلیدی: {result['keyword']}")
    print(f"امتیاز سختی: {result['difficulty_score']}/100")
    print(f"سطح سختی: {result['difficulty_level']}")
    print(f"تلاش تخمینی: {result['estimated_effort']}")
    
    if result.get('recommendations'):
        print("\n💡 توصیه‌ها:\n")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    
    await calculator.close()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    calculator = KeywordDifficultyCalculator()
    
    seed_keyword = "seo"
    
    print(f"🔍 تحلیل Keyword Difficulty برای '{seed_keyword}'\n")
    
    # محاسبه Difficulty
    result = await calculator.calculate_difficulty(
        keyword=seed_keyword,
        language='en',
        use_apis=True
    )
    
    # نمایش نتایج
    print("=" * 60)
    print("📊 نتایج تحلیل")
    print("=" * 60)
    print(f"\nکلمه کلیدی: {result['keyword']}")
    print(f"Difficulty Score: {result['difficulty_score']}/100")
    print(f"Level: {result['difficulty_level'].upper()}")
    print(f"Effort: {result['estimated_effort'].upper()}")
    
    # نمایش خلاصه رقبا
    comp_analysis = result.get('competitor_analysis', {})
    if comp_analysis:
        print(f"\n🏆 خلاصه رقبا:")
        print(f"  • تعداد رقبا: {comp_analysis.get('total_competitors_analyzed', 0)}")
        print(f"  • میانگین DA: {comp_analysis.get('average_domain_authority', 0):.1f}")
        print(f"  • برندهای قوی: {comp_analysis.get('strong_brand_count', 0)}")
    
    # نمایش توصیه‌ها
    if result.get('recommendations'):
        print(f"\n💡 توصیه‌های کلیدی:")
        for rec in result['recommendations'][:5]:
            print(f"  • {rec}")
    
    # تصمیم‌گیری
    print("\n" + "=" * 60)
    print("🎯 تصمیم‌گیری")
    print("=" * 60)
    
    if result['difficulty_score'] < 30:
        print("\n✅ این کلمه کلیدی فرصت خوبی دارد!")
        print("   پیشنهاد: شروع فوری با استراتژی مناسب")
    elif result['difficulty_score'] < 70:
        print("\n⚠️ این کلمه کلیدی رقابت متوسطی دارد")
        print("   پیشنهاد: استراتژی قوی و صبر 3-6 ماهه")
    else:
        print("\n❌ این کلمه کلیدی رقابت بسیار بالایی دارد")
        print("   پیشنهاد: تمرکز روی Long-tail keywords")
    
    await calculator.close()


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Keyword Difficulty Calculator")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_difficulty())
    # asyncio.run(example_comparison())
    # asyncio.run(example_with_apis())
    # asyncio.run(example_persian_keyword())
    asyncio.run(example_complete_workflow())

