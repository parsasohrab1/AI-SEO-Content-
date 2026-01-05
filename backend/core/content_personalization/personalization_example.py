"""
مثال استفاده از ContentPersonalizer
"""

import asyncio
import logging
from content_personalizer import ContentPersonalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """مثال استفاده"""
    
    personalizer = ContentPersonalizer()
    
    base_content = """
    سئو سایت یکی از مهم‌ترین روش‌های بازاریابی دیجیتال است.
    با استفاده از تکنیک‌های سئو می‌توانید رتبه سایت خود را در موتورهای جستجو بهبود دهید.
    
    سئو شامل دو بخش اصلی است: سئو داخلی و سئو خارجی.
    سئو داخلی شامل بهینه‌سازی محتوا، ساختار سایت و تکنیک‌های فنی است.
    سئو خارجی شامل لینک‌سازی و فعالیت‌های خارج از سایت است.
    
    برای موفقیت در سئو، باید محتوای با کیفیت تولید کنید.
    محتوا باید مرتبط، مفید و به‌روز باشد.
    """
    
    # مثال 1: شخصی‌سازی برای B2B
    print("\n" + "="*50)
    print("مثال 1: شخصی‌سازی برای B2B")
    print("="*50)
    
    target_audience = {
        'type': 'B2B',
        'expertise_level': 'intermediate',
        'industry': 'ecommerce',
        'role': 'Marketing Manager'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=base_content,
        target_audience=target_audience,
        user_intent='commercial',
        language='fa'
    )
    
    print(f"✅ محتوای شخصی‌سازی شده:\n{personalized[:500]}...")
    
    # مثال 2: شخصی‌سازی برای B2C
    print("\n" + "="*50)
    print("مثال 2: شخصی‌سازی برای B2C")
    print("="*50)
    
    target_audience = {
        'type': 'B2C',
        'expertise_level': 'beginner',
        'role': 'Individual User'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=base_content,
        target_audience=target_audience,
        user_intent='informational',
        language='fa'
    )
    
    print(f"✅ محتوای شخصی‌سازی شده:\n{personalized[:500]}...")
    
    # مثال 3: شخصی‌سازی برای Technical
    print("\n" + "="*50)
    print("مثال 3: شخصی‌سازی برای Technical")
    print("="*50)
    
    target_audience = {
        'type': 'Technical',
        'expertise_level': 'advanced',
        'role': 'Developer'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=base_content,
        target_audience=target_audience,
        user_intent='informational',
        language='fa'
    )
    
    print(f"✅ محتوای شخصی‌سازی شده:\n{personalized[:500]}...")
    
    # مثال 4: شخصی‌سازی برای Beginner
    print("\n" + "="*50)
    print("مثال 4: شخصی‌سازی برای Beginner")
    print("="*50)
    
    target_audience = {
        'type': 'General',
        'expertise_level': 'beginner',
        'role': 'New User'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=base_content,
        target_audience=target_audience,
        user_intent='informational',
        language='fa'
    )
    
    print(f"✅ محتوای شخصی‌سازی شده:\n{personalized[:500]}...")
    
    # مثال 5: شخصی‌سازی برای Transactional Intent
    print("\n" + "="*50)
    print("مثال 5: شخصی‌سازی برای Transactional Intent")
    print("="*50)
    
    target_audience = {
        'type': 'B2B',
        'expertise_level': 'intermediate',
        'industry': 'healthcare'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=base_content,
        target_audience=target_audience,
        user_intent='transactional',
        language='fa'
    )
    
    print(f"✅ محتوای شخصی‌سازی شده:\n{personalized[:500]}...")
    
    # مثال 6: شخصی‌سازی انگلیسی
    print("\n" + "="*50)
    print("مثال 6: شخصی‌سازی انگلیسی")
    print("="*50)
    
    english_content = """
    SEO is one of the most important digital marketing methods.
    By using SEO techniques, you can improve your website's ranking in search engines.
    
    SEO consists of two main parts: on-page SEO and off-page SEO.
    On-page SEO includes content optimization, site structure, and technical aspects.
    Off-page SEO includes link building and external activities.
    """
    
    target_audience = {
        'type': 'B2C',
        'expertise_level': 'beginner',
        'role': 'Small Business Owner'
    }
    
    personalized = await personalizer.personalize_content(
        base_content=english_content,
        target_audience=target_audience,
        user_intent='commercial',
        language='en'
    )
    
    print(f"✅ Personalized content:\n{personalized[:500]}...")


if __name__ == "__main__":
    asyncio.run(main())

