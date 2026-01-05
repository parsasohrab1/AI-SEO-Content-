"""
مثال استفاده از Local AI Content Generator
"""

import asyncio
import logging
from .local_ai_generator import LocalAIContentGenerator

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_generation():
    """مثال: تولید ساده محتوا"""
    
    generator = LocalAIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ Local AI model not loaded")
        print("Installing: pip install transformers torch")
        print("Model will be downloaded on first use")
        return
    
    print(f"✅ Model loaded: {generator.model_name}")
    print(f"   Device: {generator.device}\n")
    
    result = await generator.generate_article(
        keyword="seo optimization",
        target_length=1000,  # کوتاه‌تر برای تست
        language='en'
    )
    
    print(f"\n✅ محتوا تولید شد:\n")
    print(f"عنوان: {result['title']}")
    print(f"تعداد کلمات: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Keyword Density: {result['keyword_density']}%")
    print(f"Readability: {result['readability']}/100")
    print(f"Model: {result['model']}")
    
    print(f"\nمحتوا (500 کاراکتر اول):\n{result['content'][:500]}...")


async def example_with_custom_model():
    """مثال: استفاده از مدل خاص"""
    
    # استفاده از مدل کوچک‌تر برای تست
    generator = LocalAIContentGenerator(model_name="gpt2")
    
    if not generator.enabled:
        print("⚠️ Model not loaded")
        return
    
    result = await generator.generate_article(
        keyword="seo",
        target_length=500,
        language='en'
    )
    
    print(f"\n✅ محتوا با مدل {result['model']} تولید شد")
    print(f"تعداد کلمات: {result['word_count']}")


async def example_persian_content():
    """مثال: تولید محتوای فارسی"""
    
    generator = LocalAIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ Local AI model not loaded")
        return
    
    result = await generator.generate_article(
        keyword="بهینه‌سازی سئو",
        target_length=1000,
        language='fa',
        tone='professional'
    )
    
    print(f"\n✅ محتوای فارسی تولید شد:\n")
    print(f"عنوان: {result['title']}")
    print(f"Meta Description: {result['meta_description']}")
    print(f"تعداد کلمات: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}/100")


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    generator = LocalAIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ Local AI model not loaded")
        print("\nبرای استفاده:")
        print("1. pip install transformers torch")
        print("2. مدل به صورت خودکار دانلود می‌شود")
        print("3. برای GPU: pip install torch --index-url https://download.pytorch.org/whl/cu118")
        return
    
    keyword = "seo optimization"
    
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65
    }
    
    print(f"🔍 تولید محتوا با Local AI برای '{keyword}'\n")
    print(f"Model: {generator.model_name}")
    print(f"Device: {generator.device}\n")
    
    result = await generator.generate_article(
        keyword=keyword,
        keyword_metrics=keyword_metrics,
        target_length=1500,
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
    print(f"  Model: {result['model']}")
    
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
    print("مثال استفاده از Local AI Content Generator")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_generation())
    # asyncio.run(example_with_custom_model())
    # asyncio.run(example_persian_content())
    asyncio.run(example_complete_workflow())

