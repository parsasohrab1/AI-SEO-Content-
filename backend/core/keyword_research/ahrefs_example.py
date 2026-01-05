"""
مثال استفاده از Ahrefs Keyword Analyzer
"""

import asyncio
import logging
import os
from .ahrefs_client import AhrefsKeywordAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_keyword_metrics():
    """مثال: دریافت معیارهای کلمه کلیدی"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        print("لطفاً AHREFS_API_TOKEN و AHREFS_API_ID را در environment variables تنظیم کنید.")
        return
    
    # دریافت معیارهای کلمه کلیدی
    metrics = await analyzer.get_keyword_metrics(
        keyword="seo optimization",
        country='us'
    )
    
    if metrics:
        print("\n✅ معیارهای کلمه کلیدی:\n")
        print(f"کلمه کلیدی: {metrics['keyword']}")
        print(f"حجم جستجو: {metrics['search_volume']:,}")
        print(f"Keyword Difficulty: {metrics['keyword_difficulty']}/100 ({metrics['difficulty_level']})")
        print(f"CPC: ${metrics['cpc']}")
        print(f"Click Potential: {metrics['click_potential']}/100")
        print(f"Parent Topic: {metrics.get('parent_topic', 'N/A')}")
        print(f"Opportunity Score: {metrics['opportunity_score']}/100")
        if metrics.get('serp_features'):
            print(f"SERP Features: {', '.join(metrics['serp_features'])}")
    else:
        print("❌ خطا در دریافت معیارها")


async def example_ranking_keywords():
    """مثال: دریافت کلمات کلیدی رتبه‌دار"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        return
    
    # دریافت کلمات کلیدی که سایت برای آن‌ها رتبه دارد
    ranking_keywords = await analyzer.get_ranking_keywords(
        url="https://example.com",
        country='us',
        limit=50,
        mode='domain'  # یا 'url' برای یک صفحه خاص
    )
    
    if ranking_keywords:
        print(f"\n✅ {len(ranking_keywords)} کلمه کلیدی رتبه‌دار:\n")
        for i, kw in enumerate(ranking_keywords[:10], 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   رتبه: {kw['position']} | "
                  f"حجم: {kw['search_volume']:,} | "
                  f"ترافیک: {kw.get('traffic', 0):,}")
            print(f"   URL: {kw.get('url', 'N/A')}")
    else:
        print("❌ خطا در دریافت کلمات کلیدی رتبه‌دار")


async def example_keyword_ideas():
    """مثال: دریافت ایده‌های کلمات کلیدی"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        return
    
    # دریافت ایده‌های کلمات کلیدی
    ideas = await analyzer.get_keyword_ideas(
        seed_keyword="seo",
        country='us',
        limit=30
    )
    
    if ideas:
        print(f"\n✅ {len(ideas)} ایده کلمه کلیدی:\n")
        for i, kw in enumerate(ideas[:10], 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   حجم: {kw['search_volume']:,} | "
                  f"سختی: {kw['keyword_difficulty']}/100 | "
                  f"فرصت: {kw['opportunity_score']}/100")
    else:
        print("❌ خطا در دریافت ایده‌های کلمات کلیدی")


async def example_competitor_analysis():
    """مثال: تحلیل کلمات کلیدی رقیب"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        return
    
    # تحلیل کلمات کلیدی رقیب
    analysis = await analyzer.get_competitor_keywords(
        competitor_url="https://competitor.com",
        your_url="https://yoursite.com",
        country='us',
        limit=100
    )
    
    summary = analysis['summary']
    
    print("\n✅ تحلیل کلمات کلیدی رقیب:\n")
    print(f"کلمات کلیدی رقیب: {summary['competitor_total']}")
    print(f"کلمات کلیدی شما: {summary['your_total']}")
    print(f"فرصت‌ها: {summary['opportunities_count']}")
    
    # نمایش فرصت‌های برتر
    if analysis['opportunities']:
        print("\n🎯 10 فرصت برتر:\n")
        for i, opp in enumerate(analysis['opportunities'][:10], 1):
            print(f"{i}. {opp['keyword']}")
            print(f"   رتبه رقیب: {opp.get('position', 'N/A')}")
            print(f"   حجم: {opp.get('search_volume', 0):,}")
            print(f"   ترافیک: {opp.get('traffic', 0):,}")


async def example_bulk_analysis():
    """مثال: تحلیل همزمان چند کلمه کلیدی"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        return
    
    keywords = [
        "seo",
        "search engine optimization",
        "keyword research",
        "on-page seo",
        "off-page seo"
    ]
    
    print(f"\n🔍 در حال تحلیل {len(keywords)} کلمه کلیدی...\n")
    
    results = await analyzer.get_bulk_keyword_metrics(
        keywords=keywords,
        country='us',
        max_concurrent=3
    )
    
    print(f"✅ تحلیل {len(results)} کلمه کلیدی تکمیل شد:\n")
    
    # مرتب‌سازی بر اساس Opportunity Score
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].get('opportunity_score', 0),
        reverse=True
    )
    
    for keyword, data in sorted_results:
        print(f"📊 {keyword}")
        print(f"   حجم: {data['search_volume']:,}")
        print(f"   سختی: {data['keyword_difficulty']}/100")
        print(f"   Click Potential: {data['click_potential']}/100")
        print(f"   فرصت: {data['opportunity_score']}/100")
        print()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = AhrefsKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ Ahrefs API Key تنظیم نشده است.")
        print("\nبرای استفاده از Ahrefs:")
        print("1. ثبت‌نام در https://ahrefs.com")
        print("2. دریافت API Token از https://ahrefs.com/api")
        print("3. تنظیم AHREFS_API_TOKEN و AHREFS_API_ID در environment variables")
        return
    
    # مرحله 1: دریافت معیارهای کلمه کلیدی اصلی
    seed_keyword = "seo"
    print(f"🔍 مرحله 1: تحلیل کلمه کلیدی '{seed_keyword}'...")
    metrics = await analyzer.get_keyword_metrics(seed_keyword, country='us')
    
    if metrics:
        print(f"✅ حجم جستجو: {metrics['search_volume']:,}")
        print(f"✅ Keyword Difficulty: {metrics['keyword_difficulty']}/100")
        print(f"✅ Click Potential: {metrics['click_potential']}/100")
        print(f"✅ Opportunity Score: {metrics['opportunity_score']}/100")
    
    # مرحله 2: دریافت ایده‌های کلمات کلیدی
    print(f"\n🔍 مرحله 2: دریافت ایده‌های کلمات کلیدی...")
    ideas = await analyzer.get_keyword_ideas(seed_keyword, limit=30)
    
    if ideas:
        # مرحله 3: انتخاب کلمات کلیدی با Opportunity Score بالا
        high_opportunity = [
            kw for kw in ideas
            if kw.get('opportunity_score', 0) >= 50
        ]
        
        print(f"\n✅ {len(high_opportunity)} کلمه کلیدی با فرصت بالا:\n")
        for i, kw in enumerate(high_opportunity[:10], 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   حجم: {kw['search_volume']:,} | "
                  f"سختی: {kw['keyword_difficulty']}/100 | "
                  f"Click Potential: {kw['click_potential']}/100 | "
                  f"فرصت: {kw['opportunity_score']}/100")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Ahrefs Keyword Analyzer")
    print("=" * 60)
    
    # بررسی وجود API Keys
    if not os.getenv('AHREFS_API_TOKEN') or not os.getenv('AHREFS_API_ID'):
        print("\n⚠️ هشدار: AHREFS_API_TOKEN یا AHREFS_API_ID تنظیم نشده است.")
        print("مثال‌ها اجرا می‌شوند اما نتایج واقعی برنمی‌گردانند.\n")
    
    # اجرای مثال‌ها
    # asyncio.run(example_keyword_metrics())
    # asyncio.run(example_ranking_keywords())
    # asyncio.run(example_keyword_ideas())
    # asyncio.run(example_competitor_analysis())
    # asyncio.run(example_bulk_analysis())
    asyncio.run(example_complete_workflow())

