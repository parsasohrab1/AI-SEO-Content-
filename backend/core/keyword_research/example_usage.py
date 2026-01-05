"""
مثال استفاده از Google Keyword Planner
"""

import asyncio
import logging
from .google_keyword_planner import GoogleKeywordPlanner

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_get_keyword_ideas():
    """مثال: دریافت ایده‌های کلمات کلیدی"""
    
    planner = GoogleKeywordPlanner()
    
    # دریافت ایده‌های کلمات کلیدی
    keywords = await planner.get_keyword_ideas(
        seed_keyword="بهینه‌سازی سئو",
        language='fa',
        country='ir',
        max_results=20
    )
    
    print(f"\n✅ دریافت {len(keywords)} کلمه کلیدی:\n")
    for i, kw in enumerate(keywords[:10], 1):
        print(f"{i}. {kw['keyword']}")
        print(f"   منبع: {kw.get('source', 'unknown')}")
        if kw.get('search_volume'):
            print(f"   حجم جستجو: {kw['search_volume']}")
        print()


async def example_get_keyword_metrics():
    """مثال: دریافت معیارهای کلمات کلیدی"""
    
    planner = GoogleKeywordPlanner()
    
    keywords_to_analyze = [
        "بهینه‌سازی سئو",
        "آموزش سئو",
        "سئو سایت"
    ]
    
    metrics = await planner.get_keyword_metrics(
        keywords=keywords_to_analyze,
        language='fa',
        country='ir'
    )
    
    print("\n✅ معیارهای کلمات کلیدی:\n")
    for keyword, data in metrics.items():
        print(f"کلمه کلیدی: {keyword}")
        print(f"  حجم جستجو: {data.get('search_volume', 'N/A')}")
        print(f"  رقابت: {data.get('competition', 'N/A')}")
        print(f"  سختی: {data.get('difficulty', 'N/A')}/100")
        print(f"  امتیاز فرصت: {data.get('opportunity_score', 'N/A')}/100")
        print(f"  CPC (تخمینی): ${data.get('cpc', 'N/A')}")
        print()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    planner = GoogleKeywordPlanner()
    
    # مرحله 1: دریافت ایده‌های کلمات کلیدی
    print("🔍 در حال دریافت ایده‌های کلمات کلیدی...")
    keyword_ideas = await planner.get_keyword_ideas(
        seed_keyword="سئو",
        language='fa',
        max_results=30
    )
    
    # مرحله 2: دریافت معیارهای کلمات کلیدی برتر
    top_keywords = [kw['keyword'] for kw in keyword_ideas[:10]]
    print(f"\n📊 در حال تحلیل {len(top_keywords)} کلمه کلیدی برتر...")
    
    metrics = await planner.get_keyword_metrics(
        keywords=top_keywords,
        language='fa'
    )
    
    # مرحله 3: مرتب‌سازی بر اساس Opportunity Score
    sorted_keywords = sorted(
        metrics.items(),
        key=lambda x: x[1].get('opportunity_score', 0),
        reverse=True
    )
    
    print("\n🎯 کلمات کلیدی برتر بر اساس Opportunity Score:\n")
    for i, (keyword, data) in enumerate(sorted_keywords[:5], 1):
        print(f"{i}. {keyword}")
        print(f"   حجم جستجو: {data.get('search_volume', 'N/A')}")
        print(f"   سختی: {data.get('difficulty', 'N/A')}/100")
        print(f"   امتیاز فرصت: {data.get('opportunity_score', 'N/A')}/100")
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Google Keyword Planner")
    print("=" * 60)
    
    # اجرای مثال‌ها
    asyncio.run(example_get_keyword_ideas())
    asyncio.run(example_get_keyword_metrics())
    asyncio.run(example_complete_workflow())

