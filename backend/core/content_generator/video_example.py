"""
مثال استفاده از VideoContentGenerator
"""

import asyncio
import logging
from video_generator import VideoContentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """مثال استفاده"""
    
    generator = VideoContentGenerator()
    
    # مثال 1: تولید ویدیو ساده با MoviePy
    print("\n" + "="*50)
    print("مثال 1: تولید ویدیو ساده")
    print("="*50)
    
    article_content = """
    سئو سایت یکی از مهم‌ترین روش‌های بازاریابی دیجیتال است.
    با استفاده از تکنیک‌های سئو می‌توانید رتبه سایت خود را در موتورهای جستجو بهبود دهید.
    
    سئو شامل دو بخش اصلی است: سئو داخلی و سئو خارجی.
    سئو داخلی شامل بهینه‌سازی محتوا، ساختار سایت و تکنیک‌های فنی است.
    سئو خارجی شامل لینک‌سازی و فعالیت‌های خارج از سایت است.
    
    برای موفقیت در سئو، باید محتوای با کیفیت تولید کنید.
    محتوا باید مرتبط، مفید و به‌روز باشد.
    همچنین باید از کلمات کلیدی مناسب استفاده کنید.
    """
    
    result = await generator.generate_video(
        article_content=article_content,
        keyword="سئو سایت",
        duration=60,
        model="moviepy",
        language="fa",
        include_subtitles=True
    )
    
    print(f"✅ ویدیو تولید شد:")
    print(f"  - URL: {result['video_url']}")
    print(f"  - Path: {result['video_path']}")
    print(f"  - Thumbnail: {result['thumbnail_url']}")
    print(f"  - Subtitles: {result['subtitles_path']}")
    print(f"  - Title: {result['title']}")
    print(f"  - Duration: {result['duration']} seconds")
    print(f"  - Size: {result['width']}x{result['height']}")
    print(f"  - File Size: {result['file_size']} bytes")
    print(f"  - Model: {result['model_used']}")
    print(f"  - YouTube Optimized: {result['youtube_optimized']}")
    print(f"  - Tags: {', '.join(result['tags'][:5])}")
    
    # مثال 2: تولید ویدیو با Lumen5
    print("\n" + "="*50)
    print("مثال 2: تولید ویدیو با Lumen5")
    print("="*50)
    
    try:
        result = await generator.generate_video(
            article_content=article_content,
            keyword="بهینه‌سازی موتور جستجو",
            duration=90,
            model="lumen5",
            language="fa",
            style="modern"
        )
        
        print(f"✅ ویدیو تولید شد:")
        print(f"  - Model: {result['model_used']}")
        print(f"  - Title: {result['title']}")
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        print("   (نیاز به LUMEN5_API_KEY)")
    
    # مثال 3: تولید ویدیو با Synthesia
    print("\n" + "="*50)
    print("مثال 3: تولید ویدیو با Synthesia")
    print("="*50)
    
    try:
        result = await generator.generate_video(
            article_content=article_content,
            keyword="SEO optimization",
            duration=120,
            model="synthesia",
            language="en",
            style="professional"
        )
        
        print(f"✅ ویدیو تولید شد:")
        print(f"  - Model: {result['model_used']}")
        print(f"  - Title: {result['title']}")
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        print("   (نیاز به SYNTHESIA_API_KEY)")
    
    # مثال 4: تولید ویدیو انگلیسی
    print("\n" + "="*50)
    print("مثال 4: تولید ویدیو انگلیسی")
    print("="*50)
    
    english_content = """
    SEO optimization is crucial for improving website visibility in search engines.
    By using proper SEO techniques, you can rank higher in search results.
    
    SEO consists of two main parts: on-page SEO and off-page SEO.
    On-page SEO includes content optimization, site structure, and technical aspects.
    Off-page SEO includes link building and external activities.
    
    To succeed in SEO, you need to create high-quality content.
    Content should be relevant, useful, and up-to-date.
    You should also use appropriate keywords.
    """
    
    result = await generator.generate_video(
        article_content=english_content,
        keyword="SEO optimization",
        duration=60,
        model="moviepy",
        language="en",
        include_subtitles=True
    )
    
    print(f"✅ Video generated:")
    print(f"  - Title: {result['title']}")
    print(f"  - Description: {result['description'][:100]}...")
    print(f"  - Tags: {', '.join(result['tags'][:5])}")
    
    # مثال 5: تولید ویدیو بدون زیرنویس
    print("\n" + "="*50)
    print("مثال 5: تولید ویدیو بدون زیرنویس")
    print("="*50)
    
    result = await generator.generate_video(
        article_content=article_content,
        keyword="آموزش سئو",
        duration=45,
        model="moviepy",
        language="fa",
        include_subtitles=False
    )
    
    print(f"✅ ویدیو تولید شد:")
    print(f"  - Subtitles: {result['subtitles_path'] or 'None'}")


if __name__ == "__main__":
    asyncio.run(main())

