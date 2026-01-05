"""
مثال استفاده از AI Content Generator
"""

import asyncio
import logging
from .ai_content_generator import AIContentGenerator

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_generation():
    """مثال: تولید ساده محتوا"""
    
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        print("Set OPENAI_API_KEY environment variable")
        return
    
    result = await generator.generate_article(
        keyword="seo optimization",
        target_length=1500,
        language='en'
    )
    
    print(f"\n✅ محتوا تولید شد:\n")
    print(f"عنوان: {result['title']}")
    print(f"تعداد کلمات: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Keyword Density: {result['keyword_density']}%")
    print(f"Readability: {result['readability']}/100")
    
    print(f"\nمحتوا:\n{result['content'][:500]}...")


async def example_with_metrics():
    """مثال: تولید با معیارهای کلمه کلیدی"""
    
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        return
    
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65,
        'competition': 'high',
        'cpc': 2.5
    }
    
    result = await generator.generate_article(
        keyword="seo optimization",
        keyword_metrics=keyword_metrics,
        target_length=2000,
        language='en'
    )
    
    print(f"\n✅ محتوا با معیارها تولید شد:\n")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Keyword Density: {result['keyword_density']}%")
    
    # نمایش Headings
    if result['headings']:
        print(f"\n📋 Headings ({len(result['headings'])}):")
        for heading in result['headings'][:5]:
            print(f"  • {heading}")


async def example_with_competitors():
    """مثال: تولید با تحلیل رقبا"""
    
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        return
    
    competitor_content = [
        {
            'title': 'SEO Optimization Guide',
            'content': 'Basic SEO optimization tips...',
            'word_count': 1200
        },
        {
            'title': 'How to Optimize SEO',
            'content': 'Advanced SEO techniques...',
            'word_count': 1500
        }
    ]
    
    result = await generator.generate_article(
        keyword="seo optimization",
        competitor_content=competitor_content,
        target_length=2000,
        language='en'
    )
    
    print(f"\n✅ محتوا با تحلیل رقبا تولید شد:\n")
    print(f"تعداد کلمات: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}/100")
    
    # نمایش FAQ
    if result['faq']:
        print(f"\n❓ FAQ ({len(result['faq'])}):")
        for i, faq in enumerate(result['faq'][:3], 1):
            print(f"{i}. {faq['question']}")
            print(f"   {faq['answer'][:100]}...")


async def example_persian_content():
    """مثال: تولید محتوای فارسی"""
    
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        return
    
    result = await generator.generate_article(
        keyword="بهینه‌سازی سئو",
        target_length=1500,
        language='fa',
        tone='professional'
    )
    
    print(f"\n✅ محتوای فارسی تولید شد:\n")
    print(f"عنوان: {result['title']}")
    print(f"Meta Description: {result['meta_description']}")
    print(f"تعداد کلمات: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}/100")
    
    # نمایش محتوا
    print(f"\nمحتوا:\n{result['content'][:500]}...")


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    generator = AIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ OpenAI API not configured")
        print("\nبرای استفاده:")
        print("1. pip install openai")
        print("2. Set OPENAI_API_KEY environment variable")
        return
    
    keyword = "seo optimization"
    
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65,
        'competition': 'high'
    }
    
    competitor_content = [
        {
            'title': 'SEO Optimization Guide',
            'content': 'Basic tips for SEO...',
            'word_count': 1200
        }
    ]
    
    print(f"🔍 تولید محتوا برای '{keyword}'\n")
    
    result = await generator.generate_article(
        keyword=keyword,
        keyword_metrics=keyword_metrics,
        competitor_content=competitor_content,
        target_length=2000,
        language='en',
        tone='professional',
        include_faq=True
    )
    
    print("=" * 60)
    print("📊 نتایج")
    print("=" * 60)
    
    print(f"\n📝 عنوان:")
    print(f"  {result['title']}")
    
    print(f"\n📄 Meta Description:")
    print(f"  {result['meta_description']}")
    
    print(f"\n📊 معیارها:")
    print(f"  SEO Score: {result['seo_score']}/100")
    print(f"  Keyword Density: {result['keyword_density']}%")
    print(f"  Readability: {result['readability']}/100")
    print(f"  Word Count: {result['word_count']}")
    
    print(f"\n📋 Headings ({len(result['headings'])}):")
    for i, heading in enumerate(result['headings'][:5], 1):
        print(f"  {i}. {heading}")
    
    if result['faq']:
        print(f"\n❓ FAQ ({len(result['faq'])}):")
        for i, faq in enumerate(result['faq'][:3], 1):
            print(f"  {i}. {faq['question']}")
            print(f"     {faq['answer'][:100]}...")
    
    if result['recommendations']:
        print(f"\n💡 توصیه‌ها:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📄 محتوا (500 کاراکتر اول):")
    print(f"  {result['content'][:500]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از AI Content Generator")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_generation())
    # asyncio.run(example_with_metrics())
    # asyncio.run(example_with_competitors())
    # asyncio.run(example_persian_content())
    asyncio.run(example_complete_workflow())

