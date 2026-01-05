"""
مثال استفاده از Keyword Clusterer
"""

import asyncio
import logging
from .keyword_clusterer import KeywordClusterer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_clustering():
    """مثال: خوشه‌بندی ساده"""
    
    clusterer = KeywordClusterer()
    
    keywords = [
        "seo optimization",
        "keyword research",
        "on-page seo",
        "off-page seo",
        "technical seo",
        "link building",
        "content marketing",
        "social media marketing",
        "email marketing",
        "ppc advertising",
        "google ads",
        "facebook ads"
    ]
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        n_clusters=3,
        method='hybrid',
        language='en'
    )
    
    print(f"\n✅ خوشه‌بندی {result['total_keywords']} کلمه کلیدی در {result['total_clusters']} خوشه:\n")
    
    # نمایش خوشه‌ها
    for cluster_id, cluster_data in result['clusters'].items():
        print(f"📦 خوشه {cluster_id + 1}: {cluster_data['topic']}")
        print(f"   کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"   تعداد کلمات کلیدی: {cluster_data['size']}")
        print(f"   کلمات کلیدی: {', '.join(cluster_data['keywords'][:5])}")
        if len(cluster_data['keywords']) > 5:
            print(f"   ... و {len(cluster_data['keywords']) - 5} کلمه کلیدی دیگر")
        print()


async def example_with_strategy():
    """مثال: خوشه‌بندی با استراتژی محتوا"""
    
    clusterer = KeywordClusterer()
    
    keywords = [
        "سئو",
        "بهینه‌سازی سئو",
        "آموزش سئو",
        "راهنمای سئو",
        "ابزار سئو",
        "تحلیل سئو",
        "مشاوره سئو",
        "خدمات سئو",
        "قیمت سئو",
        "خرید سئو"
    ]
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        method='hybrid',
        language='fa'
    )
    
    print(f"\n✅ خوشه‌بندی و استراتژی محتوا:\n")
    
    # نمایش خوشه‌ها با استراتژی
    for cluster_id, cluster_data in result['clusters'].items():
        strategy = result['content_strategy'].get(cluster_id, {})
        
        print(f"📦 خوشه {cluster_id + 1}: {cluster_data['topic']}")
        print(f"   کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"   تعداد: {cluster_data['size']} کلمه کلیدی")
        
        if strategy:
            print(f"\n   📝 استراتژی محتوا:")
            print(f"   نوع: {strategy.get('type', 'N/A')}")
            print(f"   توضیحات: {strategy.get('description', 'N/A')}")
            print(f"   طول پیشنهادی: {strategy.get('recommended_length', 'N/A')}")
            print(f"   فرکانس: {strategy.get('frequency', 'N/A')}")
            
            if strategy.get('recommendations'):
                print(f"\n   💡 توصیه‌ها:")
                for rec in strategy['recommendations']:
                    print(f"   • {rec}")
        print()


async def example_auto_clusters():
    """مثال: خوشه‌بندی خودکار (بدون تعیین تعداد)"""
    
    clusterer = KeywordClusterer()
    
    keywords = [
        "seo",
        "keyword research",
        "on-page seo",
        "link building",
        "content marketing",
        "social media",
        "email marketing",
        "ppc",
        "google ads",
        "facebook ads",
        "instagram ads",
        "twitter ads",
        "youtube seo",
        "local seo",
        "ecommerce seo"
    ]
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        n_clusters=None,  # خودکار محاسبه می‌شود
        method='hybrid',
        language='en'
    )
    
    print(f"\n✅ خوشه‌بندی خودکار:")
    print(f"   تعداد خوشه‌ها: {result['total_clusters']}")
    print(f"   میانگین کلمات کلیدی در هر خوشه: {result['cluster_summary']['average_keywords_per_cluster']:.1f}")
    
    print(f"\n📊 خلاصه خوشه‌ها:\n")
    for cluster_id, cluster_data in result['clusters'].items():
        print(f"خوشه {cluster_id + 1}:")
        print(f"  موضوع: {cluster_data['topic']}")
        print(f"  کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"  تعداد: {cluster_data['size']} کلمه کلیدی")
        print()


async def example_persian_clustering():
    """مثال: خوشه‌بندی کلمات کلیدی فارسی"""
    
    clusterer = KeywordClusterer()
    
    keywords = [
        "سئو",
        "بهینه‌سازی سئو",
        "آموزش سئو",
        "راهنمای سئو",
        "ابزار سئو",
        "تحلیل سئو",
        "مشاوره سئو",
        "خدمات سئو",
        "قیمت سئو",
        "خرید سئو",
        "کلمه کلیدی",
        "تحقیق کلمه کلیدی",
        "تحلیل کلمه کلیدی",
        "بهینه‌سازی کلمه کلیدی",
        "رتبه‌بندی کلمه کلیدی"
    ]
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        n_clusters=3,
        method='hybrid',
        language='fa'
    )
    
    print(f"\n✅ خوشه‌بندی کلمات کلیدی فارسی:\n")
    
    for cluster_id, cluster_data in result['clusters'].items():
        print(f"📦 خوشه {cluster_id + 1}: {cluster_data['topic']}")
        print(f"   کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"   کلمات کلیدی ({cluster_data['size']}):")
        for kw in cluster_data['keywords']:
            print(f"     • {kw}")
        print()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    clusterer = KeywordClusterer()
    
    keywords = [
        "seo optimization",
        "keyword research",
        "on-page seo",
        "off-page seo",
        "technical seo",
        "link building",
        "content marketing",
        "social media marketing",
        "email marketing",
        "ppc advertising",
        "google ads",
        "facebook ads",
        "instagram marketing",
        "youtube seo",
        "local seo"
    ]
    
    print(f"🔍 خوشه‌بندی {len(keywords)} کلمه کلیدی...\n")
    
    result = await clusterer.cluster_keywords(
        keywords=keywords,
        n_clusters=None,  # خودکار
        method='hybrid',
        language='en'
    )
    
    print("=" * 60)
    print("📊 نتایج خوشه‌بندی")
    print("=" * 60)
    print(f"\nتعداد خوشه‌ها: {result['total_clusters']}")
    print(f"تعداد کل کلمات کلیدی: {result['total_keywords']}")
    print(f"میانگین در هر خوشه: {result['cluster_summary']['average_keywords_per_cluster']:.1f}")
    
    # نمایش خوشه‌ها
    print("\n" + "=" * 60)
    print("📦 خوشه‌ها")
    print("=" * 60)
    
    for cluster_id, cluster_data in result['clusters'].items():
        print(f"\nخوشه {cluster_id + 1}: {cluster_data['topic']}")
        print(f"  کلمه کلیدی اصلی: {cluster_data['main_keyword']}")
        print(f"  تعداد: {cluster_data['size']} کلمه کلیدی")
        print(f"  کلمات کلیدی:")
        for kw in cluster_data['keywords']:
            print(f"    • {kw}")
        
        # نمایش معیارها
        metrics = cluster_data.get('metrics', {})
        print(f"\n  📊 معیارها:")
        print(f"    میانگین طول: {metrics.get('average_length', 0)}")
        print(f"    Long-tail: {metrics.get('long_tail_count', 0)} ({metrics.get('long_tail_ratio', 0)*100:.0f}%)")
        print(f"    تنوع: {metrics.get('diversity', 0):.2f}")
    
    # نمایش استراتژی محتوا
    print("\n" + "=" * 60)
    print("📝 استراتژی محتوا")
    print("=" * 60)
    
    for cluster_id, strategy in result['content_strategy'].items():
        print(f"\nخوشه {cluster_id + 1}:")
        print(f"  نوع: {strategy.get('type', 'N/A')}")
        print(f"  توضیحات: {strategy.get('description', 'N/A')}")
        print(f"  طول: {strategy.get('recommended_length', 'N/A')}")
        print(f"  فرکانس: {strategy.get('frequency', 'N/A')}")
        
        if strategy.get('recommendations'):
            print(f"  توصیه‌ها:")
            for rec in strategy['recommendations']:
                print(f"    • {rec}")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Keyword Clusterer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_clustering())
    # asyncio.run(example_with_strategy())
    # asyncio.run(example_auto_clusters())
    # asyncio.run(example_persian_clustering())
    asyncio.run(example_complete_workflow())

