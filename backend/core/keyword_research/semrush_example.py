"""
مثال استفاده از SEMrush Keyword Analyzer
"""

import asyncio
import logging
import os
from .semrush_client import SEMrushKeywordAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_keyword_overview():
    """مثال: دریافت اطلاعات جامع یک کلمه کلیدی"""
    
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ SEMrush API Key تنظیم نشده است.")
        print("لطفاً SEMRUSH_API_KEY را در environment variables تنظیم کنید.")
        return
    
    # دریافت اطلاعات کلمه کلیدی
    overview = await analyzer.get_keyword_overview(
        keyword="seo optimization",
        database='us'  # یا 'ir' برای ایران
    )
    
    if overview:
        print("\n✅ اطلاعات کلمه کلیدی:\n")
        print(f"کلمه کلیدی: {overview['keyword']}")
        print(f"حجم جستجو: {overview['search_volume']:,}")
        print(f"CPC: ${overview['cpc']}")
        print(f"رقابت: {overview['competition']} ({overview['competition_level']})")
        print(f"سختی: {overview['difficulty']}/100 ({overview['difficulty_level']})")
        print(f"امتیاز فرصت: {overview['opportunity_score']}/100")
        print(f"تعداد نتایج: {overview['number_of_results']:,}")
        if overview['trend']:
            print(f"روند (12 ماه): {overview['trend']}")
    else:
        print("❌ خطا در دریافت اطلاعات")


async def example_related_keywords():
    """مثال: دریافت کلمات کلیدی مرتبط"""
    
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ SEMrush API Key تنظیم نشده است.")
        return
    
    # دریافت کلمات کلیدی مرتبط
    related = await analyzer.get_related_keywords(
        keyword="seo",
        database='us',
        limit=20
    )
    
    if related:
        print(f"\n✅ {len(related)} کلمه کلیدی مرتبط:\n")
        for i, kw in enumerate(related[:10], 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   حجم: {kw['search_volume']:,} | "
                  f"سختی: {kw['difficulty']}/100 | "
                  f"فرصت: {kw['opportunity_score']}/100")
    else:
        print("❌ خطا در دریافت کلمات کلیدی مرتبط")


async def example_keyword_gap():
    """مثال: تحلیل فاصله کلمات کلیدی"""
    
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ SEMrush API Key تنظیم نشده است.")
        return
    
    # تحلیل Gap
    gap_analysis = await analyzer.get_keyword_gap(
        site_url="https://example.com",
        competitor_urls=[
            "https://competitor1.com",
            "https://competitor2.com"
        ],
        database='us',
        limit=50
    )
    
    summary = gap_analysis['summary']
    
    print("\n✅ تحلیل فاصله کلمات کلیدی:\n")
    print(f"کلمات کلیدی شما: {summary['your_total']}")
    print(f"کلمات کلیدی رقبا: {summary['competitors_total']}")
    print(f"فرصت‌ها: {summary['opportunities_count']}")
    print(f"مزیت‌ها: {summary['advantages_count']}")
    print(f"مشترک: {summary['common_count']}")
    
    # نمایش فرصت‌های برتر
    if gap_analysis['opportunities']:
        print("\n🎯 10 فرصت برتر:\n")
        for i, opp in enumerate(gap_analysis['opportunities'][:10], 1):
            print(f"{i}. {opp['keyword']}")
            print(f"   حجم: {opp.get('search_volume', 0):,} | "
                  f"سختی: {opp.get('difficulty', 0)}/100")
    
    # نمایش مزیت‌های برتر
    if gap_analysis['advantages']:
        print("\n💪 10 مزیت برتر:\n")
        for i, adv in enumerate(gap_analysis['advantages'][:10], 1):
            print(f"{i}. {adv['keyword']}")
            print(f"   حجم: {adv.get('search_volume', 0):,}")


async def example_bulk_analysis():
    """مثال: تحلیل چند کلمه کلیدی به صورت همزمان"""
    
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ SEMrush API Key تنظیم نشده است.")
        return
    
    keywords = [
        "seo",
        "search engine optimization",
        "keyword research",
        "on-page seo",
        "off-page seo"
    ]
    
    print(f"\n🔍 در حال تحلیل {len(keywords)} کلمه کلیدی...\n")
    
    results = await analyzer.get_bulk_keyword_overview(
        keywords=keywords,
        database='us',
        max_concurrent=3  # حداکثر 3 درخواست همزمان
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
        print(f"   سختی: {data['difficulty']}/100")
        print(f"   فرصت: {data['opportunity_score']}/100")
        print()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = SEMrushKeywordAnalyzer()
    
    if not analyzer.enabled:
        print("⚠️ SEMrush API Key تنظیم نشده است.")
        print("\nبرای استفاده از SEMrush:")
        print("1. ثبت‌نام در https://www.semrush.com")
        print("2. دریافت API Key از https://www.semrush.com/api/")
        print("3. تنظیم SEMRUSH_API_KEY در environment variables")
        return
    
    seed_keyword = "seo"
    
    # مرحله 1: دریافت اطلاعات کلمه کلیدی اصلی
    print(f"🔍 مرحله 1: تحلیل کلمه کلیدی '{seed_keyword}'...")
    overview = await analyzer.get_keyword_overview(seed_keyword, database='us')
    
    if overview:
        print(f"✅ حجم جستجو: {overview['search_volume']:,}")
        print(f"✅ سختی: {overview['difficulty']}/100")
        print(f"✅ فرصت: {overview['opportunity_score']}/100")
    
    # مرحله 2: دریافت کلمات کلیدی مرتبط
    print(f"\n🔍 مرحله 2: دریافت کلمات کلیدی مرتبط...")
    related = await analyzer.get_related_keywords(seed_keyword, limit=30)
    
    if related:
        # مرحله 3: انتخاب کلمات کلیدی با Opportunity Score بالا
        high_opportunity = [
            kw for kw in related
            if kw.get('opportunity_score', 0) >= 50
        ]
        
        print(f"\n✅ {len(high_opportunity)} کلمه کلیدی با فرصت بالا:\n")
        for i, kw in enumerate(high_opportunity[:10], 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   حجم: {kw['search_volume']:,} | "
                  f"سختی: {kw['difficulty']}/100 | "
                  f"فرصت: {kw['opportunity_score']}/100")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از SEMrush Keyword Analyzer")
    print("=" * 60)
    
    # بررسی وجود API Key
    if not os.getenv('SEMRUSH_API_KEY'):
        print("\n⚠️ هشدار: SEMRUSH_API_KEY تنظیم نشده است.")
        print("مثال‌ها اجرا می‌شوند اما نتایج واقعی برنمی‌گردانند.\n")
    
    # اجرای مثال‌ها
    # asyncio.run(example_keyword_overview())
    # asyncio.run(example_related_keywords())
    # asyncio.run(example_keyword_gap())
    # asyncio.run(example_bulk_analysis())
    asyncio.run(example_complete_workflow())

