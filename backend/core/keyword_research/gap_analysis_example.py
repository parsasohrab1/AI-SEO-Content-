"""
مثال استفاده از Keyword Gap Analyzer
"""

import asyncio
import logging
from .keyword_gap_analyzer import KeywordGapAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_gap_analysis():
    """مثال: تحلیل فاصله کلمات کلیدی ساده"""
    
    analyzer = KeywordGapAnalyzer()
    
    site_url = "https://yoursite.com"
    competitor_urls = [
        "https://competitor1.com",
        "https://competitor2.com"
    ]
    
    result = await analyzer.analyze_gap(
        site_url=site_url,
        competitor_urls=competitor_urls,
        use_apis=True,
        limit_per_site=50,
        language='en'
    )
    
    print(f"\n✅ نتایج تحلیل فاصله کلمات کلیدی:\n")
    
    # Display the summary
    summary = result.get('summary', {})
    print("📊 خلاصه:")
    print(f"  کلمات کلیدی شما: {summary.get('your_total_keywords', 0)}")
    print(f"  کلمات کلیدی رقبا: {summary.get('competitors_total_keywords', 0)}")
    print(f"  فرصت‌ها: {summary.get('opportunities_count', 0)}")
    print(f"  مزیت‌ها: {summary.get('advantages_count', 0)}")
    print(f"  رقابت: {summary.get('competition_count', 0)}")
    
    # نمایش فرصت‌ها
    opportunities = result.get('opportunities', [])
    if opportunities:
        print(f"\n🎯 10 فرصت برتر:")
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{i}. {opp['keyword']}")
            print(f"   Opportunity Score: {opp.get('opportunity_score', 0):.1f}/100")
            print(f"   Search Volume: {opp.get('search_volume', 0):,}")
            print(f"   رقبا: {len(opp.get('competitors', []))}")
    
    # نمایش مزیت‌ها
    advantages = result.get('advantages', [])
    if advantages:
        print(f"\n💪 10 مزیت برتر:")
        for i, adv in enumerate(advantages[:10], 1):
            print(f"{i}. {adv['keyword']}")
            print(f"   Advantage Score: {adv.get('advantage_score', 0):.1f}/100")
            print(f"   Search Volume: {adv.get('search_volume', 0):,}")


async def example_with_recommendations():
    """مثال: تحلیل با پیشنهادات"""
    
    analyzer = KeywordGapAnalyzer()
    
    result = await analyzer.analyze_gap(
        site_url="https://yoursite.com",
        competitor_urls=["https://competitor1.com"],
        language='fa'
    )
    
    print(f"\n✅ تحلیل فاصله کلمات کلیدی:\n")
    
    # نمایش پیشنهادات
    recommendations = result.get('recommendations', [])
    if recommendations:
        print("💡 پیشنهادات:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    # نمایش فرصت‌های با اولویت بالا
    opportunities = result.get('opportunities', [])
    high_opportunities = [
        opp for opp in opportunities
        if opp.get('opportunity_score', 0) >= 70
    ]
    
    if high_opportunities:
        print(f"\n🔥 {len(high_opportunities)} فرصت با اولویت بالا:")
        for opp in high_opportunities[:5]:
            print(f"  • {opp['keyword']} (Score: {opp.get('opportunity_score', 0):.1f})")


async def example_competition_analysis():
    """مثال: تحلیل رقابت"""
    
    analyzer = KeywordGapAnalyzer()
    
    result = await analyzer.analyze_gap(
        site_url="https://yoursite.com",
        competitor_urls=["https://competitor1.com", "https://competitor2.com"],
        language='en'
    )
    
    print(f"\n✅ تحلیل رقابت:\n")
    
    # نمایش کلمات کلیدی مشترک
    competition = result.get('competition', [])
    
    # گروه‌بندی بر اساس سطح رقابت
    winning = [comp for comp in competition if comp.get('competition_level') == 'winning']
    losing = [comp for comp in competition if comp.get('competition_level') == 'losing']
    tied = [comp for comp in competition if comp.get('competition_level') == 'tied']
    
    print(f"🎯 برنده ({len(winning)}):")
    for comp in winning[:5]:
        print(f"  • {comp['keyword']} (Position: {comp.get('your_position', 'N/A')})")
    
    print(f"\n⚠️ در حال باخت ({len(losing)}):")
    for comp in losing[:5]:
        print(f"  • {comp['keyword']} (Your Position: {comp.get('your_position', 'N/A')})")
    
    print(f"\n🤝 مساوی ({len(tied)}):")
    for comp in tied[:5]:
        print(f"  • {comp['keyword']}")


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = KeywordGapAnalyzer()
    
    site_url = "https://yoursite.com"
    competitor_urls = [
        "https://competitor1.com",
        "https://competitor2.com"
    ]
    
    print(f"🔍 تحلیل فاصله کلمات کلیدی...\n")
    print(f"سایت شما: {site_url}")
    print(f"رقبا: {', '.join(competitor_urls)}\n")
    
    result = await analyzer.analyze_gap(
        site_url=site_url,
        competitor_urls=competitor_urls,
        use_apis=True,
        limit_per_site=100,
        language='en'
    )
    
    print("=" * 60)
    print("📊 نتایج تحلیل")
    print("=" * 60)
    
    # خلاصه
    summary = result.get('summary', {})
    print(f"\n📈 خلاصه:")
    print(f"  کلمات کلیدی شما: {summary.get('your_total_keywords', 0)}")
    print(f"  کلمات کلیدی رقبا: {summary.get('competitors_total_keywords', 0)}")
    print(f"  Coverage Ratio: {summary.get('coverage_ratio', 0):.1f}%")
    
    print(f"\n  فرصت‌ها:")
    print(f"    کل: {summary.get('opportunities_count', 0)}")
    print(f"    با اولویت بالا: {summary.get('high_opportunities', 0)}")
    print(f"    با اولویت متوسط: {summary.get('medium_opportunities', 0)}")
    
    print(f"\n  مزیت‌ها:")
    print(f"    کل: {summary.get('advantages_count', 0)}")
    print(f"    با اولویت بالا: {summary.get('high_advantages', 0)}")
    
    print(f"\n  رقابت:")
    print(f"    کل: {summary.get('competition_count', 0)}")
    print(f"    برنده: {summary.get('winning_keywords', 0)}")
    print(f"    در حال باخت: {summary.get('losing_keywords', 0)}")
    
    # فرصت‌ها
    opportunities = result.get('opportunities', [])
    if opportunities:
        print("\n" + "=" * 60)
        print("🎯 فرصت‌ها (کلمات کلیدی رقبا که شما ندارید)")
        print("=" * 60)
        print(f"\n{len(opportunities)} فرصت شناسایی شد\n")
        
        high_opp = [opp for opp in opportunities if opp.get('opportunity_score', 0) >= 70]
        if high_opp:
            print("🔥 فرصت‌های با اولویت بالا:\n")
            for i, opp in enumerate(high_opp[:10], 1):
                print(f"{i}. {opp['keyword']}")
                print(f"   Score: {opp.get('opportunity_score', 0):.1f}/100")
                print(f"   Search Volume: {opp.get('search_volume', 0):,}")
                print(f"   رقبا: {len(opp.get('competitors', []))}")
                print()
    
    # مزیت‌ها
    advantages = result.get('advantages', [])
    if advantages:
        print("=" * 60)
        print("💪 مزیت‌ها (کلمات کلیدی شما که رقبا ندارند)")
        print("=" * 60)
        print(f"\n{len(advantages)} مزیت شناسایی شد\n")
        
        high_adv = [adv for adv in advantages if adv.get('advantage_score', 0) >= 70]
        if high_adv:
            print("⭐ مزیت‌های با اولویت بالا:\n")
            for i, adv in enumerate(high_adv[:10], 1):
                print(f"{i}. {adv['keyword']}")
                print(f"   Score: {adv.get('advantage_score', 0):.1f}/100")
                print(f"   Search Volume: {adv.get('search_volume', 0):,}")
                print()
    
    # پیشنهادات
    recommendations = result.get('recommendations', [])
    if recommendations:
        print("=" * 60)
        print("💡 پیشنهادات")
        print("=" * 60)
        print()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Keyword Gap Analyzer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_gap_analysis())
    # asyncio.run(example_with_recommendations())
    # asyncio.run(example_competition_analysis())
    asyncio.run(example_complete_workflow())

