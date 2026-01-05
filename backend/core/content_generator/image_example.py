"""
مثال استفاده از ImageContentGenerator
"""

import asyncio
import logging
from image_generator import ImageContentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """مثال استفاده"""
    
    generator = ImageContentGenerator()
    
    # مثال 1: تولید تصویر ساده
    print("\n" + "="*50)
    print("مثال 1: تولید تصویر ساده")
    print("="*50)
    
    result = await generator.generate_seo_image(
        keyword="سئو سایت",
        style="professional",
        language="fa"
    )
    
    print(f"✅ تصویر تولید شد:")
    print(f"  - URL: {result['image_url']}")
    print(f"  - Path: {result['image_path']}")
    print(f"  - Alt Text: {result['alt_text']}")
    print(f"  - Filename: {result['filename']}")
    print(f"  - Size: {result['width']}x{result['height']}")
    print(f"  - Format: {result['format']}")
    print(f"  - File Size: {result['file_size']} bytes")
    print(f"  - Model: {result['model_used']}")
    print(f"  - SEO Optimized: {result['seo_optimized']}")
    
    # مثال 2: تولید تصویر با محتوا
    print("\n" + "="*50)
    print("مثال 2: تولید تصویر با محتوا")
    print("="*50)
    
    article_content = """
    سئو سایت یکی از مهم‌ترین روش‌های بازاریابی دیجیتال است.
    با استفاده از تکنیک‌های سئو می‌توانید رتبه سایت خود را در موتورهای جستجو بهبود دهید.
    """
    
    result = await generator.generate_seo_image(
        keyword="بهینه‌سازی موتور جستجو",
        article_content=article_content,
        style="modern",
        language="fa"
    )
    
    print(f"✅ تصویر تولید شد:")
    print(f"  - Alt Text: {result['alt_text']}")
    print(f"  - Filename: {result['filename']}")
    
    # مثال 3: تولید تصویر با استایل مختلف
    print("\n" + "="*50)
    print("مثال 3: تولید تصویر با استایل هنری")
    print("="*50)
    
    result = await generator.generate_seo_image(
        keyword="طراحی وب",
        style="artistic",
        size="1792x1024",
        language="fa"
    )
    
    print(f"✅ تصویر تولید شد:")
    print(f"  - Size: {result['width']}x{result['height']}")
    print(f"  - Model: {result['model_used']}")
    
    # مثال 4: تولید تصویر انگلیسی
    print("\n" + "="*50)
    print("مثال 4: تولید تصویر انگلیسی")
    print("="*50)
    
    result = await generator.generate_seo_image(
        keyword="SEO optimization",
        article_content="SEO optimization is crucial for improving website visibility in search engines.",
        style="professional",
        language="en"
    )
    
    print(f"✅ Image generated:")
    print(f"  - Alt Text: {result['alt_text']}")
    print(f"  - Filename: {result['filename']}")
    
    # مثال 5: استفاده از Stable Diffusion
    print("\n" + "="*50)
    print("مثال 5: استفاده از Stable Diffusion")
    print("="*50)
    
    result = await generator.generate_seo_image(
        keyword="محتوای دیجیتال",
        style="illustrated",
        model="stable_diffusion",
        language="fa"
    )
    
    print(f"✅ تصویر تولید شد:")
    print(f"  - Model: {result['model_used']}")
    print(f"  - SEO Optimized: {result['seo_optimized']}")


if __name__ == "__main__":
    asyncio.run(main())

