"""
ماژول تولید محتوای خودکار
"""

import logging
import os
from typing import Dict, Any, List
from datetime import datetime
import random
from pathlib import Path

logger = logging.getLogger(__name__)


class ContentGenerator:
    """کلاس تولید محتوا"""
    
    async def generate_all(
        self,
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any],
        content_types: List[str]
    ) -> Dict[str, Any]:
        """
        تولید تمام انواع محتوا
        
        Args:
            site_analysis: نتایج تحلیل سایت
            seo_analysis: نتایج تحلیل سئو
            content_types: انواع محتوای مورد نیاز
            
        Returns:
            محتوای تولید شده
        """
        logger.info(f"Generating content types: {content_types}")
        
        # استخراج URL - از site_analysis یا از خود site_analysis
        site_url = site_analysis.get('url', '') if isinstance(site_analysis, dict) else ''
        if not site_url and isinstance(site_analysis, dict):
            site_url = site_analysis.get('site_url', '')
        if not site_url:
            site_url = 'https://example.com'  # Fallback
        
        content_items = []
        total_words = 0
        
        # استخراج کلمات کلیدی از تحلیل سئو
        keywords = []
        if seo_analysis and isinstance(seo_analysis, dict):
            keywords = seo_analysis.get('content', {}).get('keywords', []) if isinstance(seo_analysis.get('content'), dict) else []
        
        if not keywords:
            # کلمات کلیدی پیش‌فرض بر اساس URL
            keywords = self._extract_keywords_from_url(site_url)
        
        # تولید محتوای متنی
        if 'text' in content_types or 'article' in content_types:
            text_content = await self._generate_text_content(site_url, keywords, site_analysis, seo_analysis)
            content_items.extend(text_content)
            total_words += sum(item.get('word_count', 0) for item in text_content)
        
        # تولید محتوای تصویری (metadata)
        if 'image' in content_types:
            image_content = await self._generate_image_content(site_url, keywords)
            content_items.extend(image_content)
        
        # تولید محتوای ویدیویی (metadata)
        if 'video' in content_types:
            video_content = await self._generate_video_content(site_url, keywords)
            content_items.extend(video_content)
        
        return {
            'content_items': content_items,
            'total_items': len(content_items),
            'total_words': total_words,
            'content_types': content_types,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_text_content(
        self,
        site_url: str,
        keywords: List[str],
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """تولید محتوای متنی"""
        items = []
        
        # تولید 3-5 مقاله نمونه
        num_articles = random.randint(3, 5)
        
        for i in range(num_articles):
            # انتخاب کلمات کلیدی برای این مقاله
            article_keywords = random.sample(keywords, min(3, len(keywords))) if keywords else ['سئو', 'بهینه‌سازی', 'محتوای دیجیتال']
            
            # تولید عنوان
            title = f"راهنمای جامع {article_keywords[0] if article_keywords else 'سئو'} - {site_url.split('//')[-1].split('/')[0]}"
            
            # تولید محتوا
            content = self._generate_article_content(title, article_keywords, site_analysis)
            word_count = len(content.split())
            
            # ایجاد فایل Word برای متن
            file_path = await self._save_text_file(
                f'content_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                title,
                content
            )
            
            items.append({
                'id': f'content_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                'type': 'text',
                'title': title,
                'content': content,
                'word_count': word_count,
                'keywords': article_keywords,
                'status': 'generated',
                'seo_score': random.randint(70, 95),
                'created_at': datetime.now().isoformat(),
                'file_path': file_path,
                'file_type': 'docx'
            })
        
        return items
    
    async def _generate_image_content(self, site_url: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """تولید metadata محتوای تصویری"""
        items = []
        
        num_images = random.randint(2, 4)
        for i in range(num_images):
            keyword = keywords[i % len(keywords)] if keywords else 'سئو'
            
            # ایجاد فایل تصویری JPG
            file_path = await self._save_image_file(
                f'image_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                keyword
            )
            
            items.append({
                'id': f'image_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                'type': 'image',
                'title': f'تصویر {keyword}',
                'description': f'تصویر بهینه شده برای {keyword}',
                'keywords': [keyword],
                'status': 'generated',
                'created_at': datetime.now().isoformat(),
                'file_path': file_path,
                'file_type': 'jpg'
            })
        
        return items
    
    async def _generate_video_content(self, site_url: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """تولید metadata محتوای ویدیویی"""
        items = []
        
        num_videos = random.randint(1, 2)
        for i in range(num_videos):
            keyword = keywords[i % len(keywords)] if keywords else 'سئو'
            
            # ایجاد فایل ویدیویی MP4
            file_path = await self._save_video_file(
                f'video_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                keyword
            )
            
            items.append({
                'id': f'video_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                'type': 'video',
                'title': f'ویدیو آموزشی {keyword}',
                'description': f'ویدیو آموزشی درباره {keyword}',
                'keywords': [keyword],
                'status': 'generated',
                'duration': f'{random.randint(3, 10)} دقیقه',
                'created_at': datetime.now().isoformat(),
                'file_path': file_path,
                'file_type': 'mp4'
            })
        
        return items
    
    def _extract_keywords_from_url(self, url: str) -> List[str]:
        """استخراج کلمات کلیدی از URL"""
        # حذف پروتکل و مسیر
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        # تقسیم بر اساس نقطه و خط تیره
        parts = domain.replace('.', ' ').replace('-', ' ').split()
        # فیلتر کردن قسمت‌های کوتاه
        keywords = [p for p in parts if len(p) > 3]
        return keywords[:5] if keywords else ['سئو', 'بهینه‌سازی', 'محتوای دیجیتال']
    
    def _generate_article_content(self, title: str, keywords: List[str], site_analysis: Dict[str, Any]) -> str:
        """تولید محتوای مقاله"""
        cms_type = site_analysis.get('cms_type', 'custom')
        
        content = f"""
{title}

مقدمه:
این مقاله به بررسی {keywords[0] if keywords else 'سئو'} می‌پردازد و راهکارهای عملی برای بهبود عملکرد سایت ارائه می‌دهد.

بخش اول: اهمیت {keywords[0] if keywords else 'سئو'}
{keywords[0] if keywords else 'سئو'} یکی از مهم‌ترین عوامل موفقیت در دنیای دیجیتال است. با بهینه‌سازی صحیح می‌توانید رتبه سایت خود را در موتورهای جستجو بهبود دهید.

بخش دوم: راهکارهای عملی
برای بهبود {keywords[0] if keywords else 'سئو'}، باید به موارد زیر توجه کنید:

1. بهینه‌سازی محتوا
2. بهبود سرعت بارگذاری
3. استفاده از کلمات کلیدی مناسب
4. ساختار مناسب صفحات

بخش سوم: نتیجه‌گیری
با رعایت اصول {keywords[0] if keywords else 'سئو'} و بهینه‌سازی مداوم، می‌توانید به نتایج مطلوب برسید.

نکات مهم:
- همیشه محتوای با کیفیت تولید کنید
- از کلمات کلیدی به صورت طبیعی استفاده کنید
- سرعت سایت را بهینه نگه دارید
- تجربه کاربری را بهبود دهید

"""
        return content.strip()

