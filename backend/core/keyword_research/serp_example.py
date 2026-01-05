"""
مثال استفاده از SERP Feature Analyzer
"""

import asyncio
import logging
from .serp_feature_analyzer import SERPFeatureAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_analysis():
    """مثال: تحلیل ساده SERP Features"""
    
    analyzer = SERPFeatureAnalyzer()
    
    result = await analyzer.analyze_serp_features(
        keyword="seo optimization",
        language='en',
        location='us'
    )
    
    print(f"\n✅ تحلیل SERP Features برای '{result['keyword']}':\n")
    
    # Featured Snippet
    if result['featured_snippet']['present']:
        print("📌 Featured Snippet:")
        print(f"  نوع: {result['featured_snippet']['type']}")
        print(f"  محتوا: {result['featured_snippet']['content'][:200]}...")
        if result['featured_snippet']['source_url']:
            print(f"  منبع: {result['featured_snippet']['source_url']}")
    else:
        print("❌ Featured Snippet: موجود نیست")
    
    # People Also Ask
    if result['people_also_ask']:
        print(f"\n❓ People Also Ask ({len(result['people_also_ask'])} سوال):")
        for i, paa in enumerate(result['people_also_ask'][:5], 1):
            print(f"  {i}. {paa['question']}")
    else:
        print("\n❌ People Also Ask: موجود نیست")
    
    # Related Searches
    if result['related_searches']:
        print(f"\n🔍 Related Searches ({len(result['related_searches'])}):")
        for i, search in enumerate(result['related_searches'][:5], 1):
            print(f"  {i}. {search}")
    else:
        print("\n❌ Related Searches: موجود نیست")
    
    await analyzer.close()


async def example_all_features():
    """مثال: نمایش تمام ویژگی‌ها"""
    
    analyzer = SERPFeatureAnalyzer()
    
    result = await analyzer.analyze_serp_features(
        keyword="best seo tools",
        language='en'
    )
    
    print(f"\n✅ تحلیل کامل SERP Features:\n")
    
    summary = result['summary']
    print("📊 خلاصه:")
    print(f"  Featured Snippet: {'✅' if summary['featured_snippet_present'] else '❌'}")
    print(f"  People Also Ask: {summary['people_also_ask_count']} سوال")
    print(f"  Related Searches: {summary['related_searches_count']}")
    print(f"  Image Pack: {'✅' if summary['image_pack_present'] else '❌'} ({summary['image_count']} تصویر)")
    print(f"  Video Results: {summary['video_results_count']} ویدیو")
    print(f"  Local Pack: {'✅' if summary['local_pack_present'] else '❌'}")
    print(f"  Organic Results: {summary['organic_results_count']}")
    print(f"  Total Features: {summary['total_features']}")
    
    # Image Pack
    if result['image_pack']['present']:
        print(f"\n🖼️ Image Pack ({result['image_pack']['total_count']} تصویر):")
        for i, img in enumerate(result['image_pack']['images'][:5], 1):
            print(f"  {i}. {img.get('alt', 'No alt')}")
    
    # Video Results
    if result['video_results']:
        print(f"\n🎥 Video Results ({len(result['video_results'])}):")
        for i, video in enumerate(result['video_results'][:5], 1):
            print(f"  {i}. {video['title']}")
            print(f"     منبع: {video['source']}")
    
    # Local Pack
    if result['local_pack']['present']:
        print(f"\n📍 Local Pack ({len(result['local_pack']['businesses'])} کسب‌وکار):")
        for i, business in enumerate(result['local_pack']['businesses'], 1):
            print(f"  {i}. {business['name']}")
    
    await analyzer.close()


async def example_organic_results():
    """مثال: نمایش نتایج Organic"""
    
    analyzer = SERPFeatureAnalyzer()
    
    result = await analyzer.analyze_serp_features(
        keyword="seo",
        language='en'
    )
    
    print(f"\n✅ نتایج Organic برای '{result['keyword']}':\n")
    
    for i, organic in enumerate(result['organic_results'][:10], 1):
        print(f"{i}. {organic['title']}")
        print(f"   URL: {organic['url']}")
        if organic['snippet']:
            print(f"   Snippet: {organic['snippet'][:100]}...")
        print()
    
    await analyzer.close()


async def example_persian_keyword():
    """مثال: تحلیل کلمه کلیدی فارسی"""
    
    analyzer = SERPFeatureAnalyzer()
    
    result = await analyzer.analyze_serp_features(
        keyword="سئو",
        language='fa',
        location='ir'
    )
    
    print(f"\n✅ تحلیل SERP Features برای '{result['keyword']}':\n")
    
    summary = result['summary']
    print("📊 خلاصه:")
    print(f"  Featured Snippet: {'✅' if summary['featured_snippet_present'] else '❌'}")
    print(f"  People Also Ask: {summary['people_also_ask_count']} سوال")
    print(f"  Related Searches: {summary['related_searches_count']}")
    print(f"  Image Pack: {'✅' if summary['image_pack_present'] else '❌'}")
    print(f"  Video Results: {summary['video_results_count']}")
    print(f"  Local Pack: {'✅' if summary['local_pack_present'] else '❌'}")
    
    # نمایش People Also Ask
    if result['people_also_ask']:
        print(f"\n❓ People Also Ask:")
        for paa in result['people_also_ask'][:5]:
            print(f"  • {paa['question']}")
    
    await analyzer.close()


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = SERPFeatureAnalyzer()
    
    keyword = "seo optimization"
    
    print(f"🔍 تحلیل SERP Features برای '{keyword}'\n")
    
    result = await analyzer.analyze_serp_features(
        keyword=keyword,
        language='en',
        location='us'
    )
    
    print("=" * 60)
    print("📊 نتایج تحلیل")
    print("=" * 60)
    
    summary = result['summary']
    
    # Featured Snippet
    print(f"\n📌 Featured Snippet:")
    if result['featured_snippet']['present']:
        print(f"  ✅ موجود است")
        print(f"  نوع: {result['featured_snippet']['type']}")
        print(f"  محتوا: {result['featured_snippet']['content'][:300]}...")
        if result['featured_snippet']['source_url']:
            print(f"  منبع: {result['featured_snippet']['source_url']}")
    else:
        print(f"  ❌ موجود نیست")
    
    # People Also Ask
    print(f"\n❓ People Also Ask:")
    print(f"  تعداد: {summary['people_also_ask_count']}")
    if result['people_also_ask']:
        for i, paa in enumerate(result['people_also_ask'][:5], 1):
            print(f"  {i}. {paa['question']}")
    
    # Related Searches
    print(f"\n🔍 Related Searches:")
    print(f"  تعداد: {summary['related_searches_count']}")
    if result['related_searches']:
        for i, search in enumerate(result['related_searches'][:5], 1):
            print(f"  {i}. {search}")
    
    # Image Pack
    print(f"\n🖼️ Image Pack:")
    if result['image_pack']['present']:
        print(f"  ✅ موجود است ({summary['image_count']} تصویر)")
        for i, img in enumerate(result['image_pack']['images'][:3], 1):
            print(f"  {i}. Alt: {img.get('alt', 'N/A')}")
    else:
        print(f"  ❌ موجود نیست")
    
    # Video Results
    print(f"\n🎥 Video Results:")
    print(f"  تعداد: {summary['video_results_count']}")
    if result['video_results']:
        for i, video in enumerate(result['video_results'][:3], 1):
            print(f"  {i}. {video['title']} ({video['source']})")
    
    # Local Pack
    print(f"\n📍 Local Pack:")
    if result['local_pack']['present']:
        print(f"  ✅ موجود است ({summary['businesses_count']} کسب‌وکار)")
        for i, business in enumerate(result['local_pack']['businesses'], 1):
            print(f"  {i}. {business['name']}")
    else:
        print(f"  ❌ موجود نیست")
    
    # Organic Results
    print(f"\n🔗 Organic Results:")
    print(f"  تعداد: {summary['organic_results_count']}")
    for i, organic in enumerate(result['organic_results'][:5], 1):
        print(f"  {i}. {organic['title']}")
        print(f"     {organic['url']}")
    
    # خلاصه نهایی
    print("\n" + "=" * 60)
    print("📈 خلاصه نهایی")
    print("=" * 60)
    print(f"  Total Features: {summary['total_features']}/6")
    print(f"  Featured Snippet: {'✅' if summary['featured_snippet_present'] else '❌'}")
    print(f"  People Also Ask: {summary['people_also_ask_count']} سوال")
    print(f"  Related Searches: {summary['related_searches_count']}")
    print(f"  Image Pack: {'✅' if summary['image_pack_present'] else '❌'}")
    print(f"  Video Results: {summary['video_results_count']}")
    print(f"  Local Pack: {'✅' if summary['local_pack_present'] else '❌'}")
    
    await analyzer.close()


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از SERP Feature Analyzer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_analysis())
    # asyncio.run(example_all_features())
    # asyncio.run(example_organic_results())
    # asyncio.run(example_persian_keyword())
    asyncio.run(example_complete_workflow())

