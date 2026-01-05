"""
تولید تصاویر بهینه برای SEO
استفاده از DALL-E 3 یا Stable Diffusion
"""

import logging
import os
import re
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageContentGenerator:
    """
    کلاس تولید تصاویر بهینه برای SEO
    
    ویژگی‌ها:
    - استفاده از DALL-E 3 یا Stable Diffusion
    - تولید Alt text خودکار
    - نام فایل بهینه
    - ابعاد مناسب
    - فرمت WebP
    """
    
    def __init__(self):
        self.openai_client = None
        self.stable_diffusion_client = None
        self.dalle_enabled = False
        self.stable_diffusion_enabled = False
        
        # سعی می‌کنیم OpenAI client را بارگذاری کنیم
        try:
            from openai import AsyncOpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                self.dalle_enabled = True
                logger.info("OpenAI DALL-E client initialized")
        except ImportError:
            logger.warning("openai package not installed")
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI client: {str(e)}")
        
        # سعی می‌کنیم Stable Diffusion client را بارگذاری کنیم
        try:
            # استفاده از Hugging Face یا Replicate API
            replicate_api_token = os.getenv('REPLICATE_API_TOKEN')
            if replicate_api_token:
                import replicate
                self.stable_diffusion_client = replicate
                self.stable_diffusion_enabled = True
                logger.info("Stable Diffusion client initialized")
        except ImportError:
            logger.warning("replicate package not installed. Install with: pip install replicate")
        except Exception as e:
            logger.warning(f"Could not initialize Stable Diffusion client: {str(e)}")
    
    async def generate_seo_image(
        self,
        keyword: str,
        article_content: Optional[str] = None,
        style: str = 'professional',
        size: str = '1024x1024',  # 1024x1024, 1792x1024, 1024x1792
        model: str = 'dalle',  # dalle, stable_diffusion
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        تولید تصویر بهینه شده برای SEO
        
        Args:
            keyword: کلمه کلیدی
            article_content: محتوای مقاله (اختیاری)
            style: استایل تصویر (professional, artistic, modern, etc.)
            size: ابعاد تصویر
            model: مدل استفاده شده (dalle, stable_diffusion)
            language: زبان
        
        Returns:
            {
                'image_url': str,
                'image_path': str,
                'alt_text': str,
                'filename': str,
                'width': int,
                'height': int,
                'format': str,
                'file_size': int,
                'seo_optimized': bool,
                'model_used': str
            }
        """
        try:
            # ساخت prompt برای تصویر
            prompt = self._build_image_prompt(keyword, article_content, style, language)
            
            # تولید تصویر
            if model == 'dalle' and self.dalle_enabled:
                image_data = await self._generate_with_dalle(prompt, size)
                model_used = 'dalle-3'
            elif model == 'stable_diffusion' and self.stable_diffusion_enabled:
                image_data = await self._generate_with_stable_diffusion(prompt, size)
                model_used = 'stable-diffusion'
            else:
                # Fallback: استفاده از مدل موجود
                if self.dalle_enabled:
                    image_data = await self._generate_with_dalle(prompt, size)
                    model_used = 'dalle-3'
                elif self.stable_diffusion_enabled:
                    image_data = await self._generate_with_stable_diffusion(prompt, size)
                    model_used = 'stable-diffusion'
                else:
                    logger.error("No image generation model available")
                    return self._empty_image_result(keyword)
            
            # تولید Alt text
            alt_text = self._generate_alt_text(keyword, article_content, language)
            
            # تولید نام فایل بهینه
            filename = self._generate_optimized_filename(keyword, language)
            
            # ذخیره تصویر
            image_path = await self._save_image(image_data, filename)
            
            # بهینه‌سازی تصویر (تبدیل به WebP)
            optimized_path = await self._optimize_image(image_path, filename)
            
            # محاسبه ابعاد و حجم فایل
            image_info = await self._get_image_info(optimized_path)
            
            return {
                'image_url': f'/images/{Path(optimized_path).name}',
                'image_path': optimized_path,
                'alt_text': alt_text,
                'filename': filename,
                'width': image_info.get('width', 1024),
                'height': image_info.get('height', 1024),
                'format': 'webp',
                'file_size': image_info.get('file_size', 0),
                'seo_optimized': True,
                'model_used': model_used,
                'keyword': keyword
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO image: {str(e)}")
            return self._empty_image_result(keyword)
    
    def _build_image_prompt(
        self,
        keyword: str,
        article_content: Optional[str],
        style: str,
        language: str
    ) -> str:
        """ساخت prompt برای تولید تصویر"""
        
        # استخراج موضوع از محتوا
        topic = keyword
        if article_content:
            # استخراج موضوع اصلی از محتوا
            first_paragraph = article_content.split('\n\n')[0] if '\n\n' in article_content else article_content[:200]
            # ساده‌سازی: استفاده از keyword
            topic = keyword
        
        # ساخت prompt بر اساس style
        style_descriptions = {
            'professional': 'professional, clean, modern',
            'artistic': 'artistic, creative, visually appealing',
            'modern': 'modern, sleek, contemporary',
            'minimalist': 'minimalist, simple, clean',
            'illustrated': 'illustrated, hand-drawn style',
            'photorealistic': 'photorealistic, high quality'
        }
        
        style_desc = style_descriptions.get(style, 'professional, clean')
        
        if language == 'fa':
            prompt = f"تصویر حرفه‌ای و جذاب درباره {topic}. استایل: {style_desc}. تصویر باید واضح، با کیفیت و مناسب برای استفاده در وب باشد."
        else:
            prompt = f"Professional and engaging image about {topic}. Style: {style_desc}. The image should be clear, high quality, and suitable for web use."
        
        return prompt
    
    async def _generate_with_dalle(
        self,
        prompt: str,
        size: str
    ) -> bytes:
        """تولید تصویر با DALL-E 3"""
        try:
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            # دانلود تصویر
            image_url = response.data[0].url
            import httpx
            async with httpx.AsyncClient() as client:
                image_response = await client.get(image_url)
                return image_response.content
                
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {str(e)}")
            raise
    
    async def _generate_with_stable_diffusion(
        self,
        prompt: str,
        size: str
    ) -> bytes:
        """تولید تصویر با Stable Diffusion"""
        try:
            # استفاده از Replicate API (sync است، پس در thread اجرا می‌کنیم)
            def run_replicate():
                return self.stable_diffusion_client.run(
                    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                    input={
                        "prompt": prompt,
                        "image_dimensions": size
                    }
                )
            
            # اجرای sync در thread
            output = await asyncio.to_thread(run_replicate)
            
            # دانلود تصویر
            if output:
                image_url = output[0] if isinstance(output, list) else output
                import httpx
                async with httpx.AsyncClient() as client:
                    image_response = await client.get(image_url)
                    return image_response.content
            
            raise Exception("No image generated")
            
        except Exception as e:
            logger.error(f"Error generating image with Stable Diffusion: {str(e)}")
            raise
    
    def _generate_alt_text(
        self,
        keyword: str,
        article_content: Optional[str],
        language: str
    ) -> str:
        """تولید Alt text خودکار"""
        
        if language == 'fa':
            # استخراج اطلاعات از محتوا
            if article_content:
                # استخراج موضوع اصلی
                first_sentence = article_content.split('.')[0] if '.' in article_content else article_content[:100]
                alt_text = f"تصویر {keyword} - {first_sentence[:50]}"
            else:
                alt_text = f"تصویر {keyword}"
        else:
            if article_content:
                first_sentence = article_content.split('.')[0] if '.' in article_content else article_content[:100]
                alt_text = f"Image of {keyword} - {first_sentence[:50]}"
            else:
                alt_text = f"Image of {keyword}"
        
        # محدود کردن طول Alt text (حداکثر 125 کاراکتر)
        if len(alt_text) > 125:
            alt_text = alt_text[:122] + "..."
        
        return alt_text
    
    def _generate_optimized_filename(
        self,
        keyword: str,
        language: str
    ) -> str:
        """تولید نام فایل بهینه"""
        
        # پاک کردن کاراکترهای غیرمجاز
        clean_keyword = re.sub(r'[^\w\s-]', '', keyword)
        clean_keyword = re.sub(r'\s+', '-', clean_keyword)
        clean_keyword = clean_keyword.lower()
        
        # محدود کردن طول
        if len(clean_keyword) > 50:
            clean_keyword = clean_keyword[:50]
        
        # اضافه کردن timestamp برای یکتایی
        timestamp = datetime.now().strftime("%Y%m%d")
        
        filename = f"{clean_keyword}-{timestamp}.webp"
        
        return filename
    
    async def _save_image(
        self,
        image_data: bytes,
        filename: str
    ) -> str:
        """ذخیره تصویر"""
        try:
            import aiofiles
            
            # ایجاد پوشه images
            images_dir = Path("backend/generated_content/images")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # ذخیره تصویر
            image_path = images_dir / filename
            async with aiofiles.open(image_path, 'wb') as f:
                await f.write(image_data)
            
            logger.info(f"Image saved: {image_path}")
            return str(image_path)
            
        except ImportError:
            # Fallback: استفاده از open معمولی
            images_dir = Path("backend/generated_content/images")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            image_path = images_dir / filename
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Image saved: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise
    
    async def _optimize_image(
        self,
        image_path: str,
        filename: str
    ) -> str:
        """بهینه‌سازی تصویر (تبدیل به WebP)"""
        try:
            from PIL import Image
            
            # باز کردن تصویر
            image = Image.open(image_path)
            
            # تبدیل به RGB اگر RGBA باشد
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # تغییر نام فایل به .webp
            webp_filename = filename.replace('.jpg', '.webp').replace('.png', '.webp')
            if not webp_filename.endswith('.webp'):
                webp_filename += '.webp'
            
            webp_path = Path(image_path).parent / webp_filename
            
            # ذخیره به فرمت WebP با کیفیت بهینه
            image.save(webp_path, 'WEBP', quality=85, optimize=True)
            
            # حذف فایل اصلی
            if Path(image_path).exists() and image_path != str(webp_path):
                Path(image_path).unlink()
            
            logger.info(f"Image optimized and saved as WebP: {webp_path}")
            return str(webp_path)
            
        except ImportError:
            logger.warning("PIL not available. Image not optimized to WebP.")
            return image_path
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            return image_path
    
    async def _get_image_info(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """دریافت اطلاعات تصویر"""
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            file_size = Path(image_path).stat().st_size
            
            return {
                'width': image.width,
                'height': image.height,
                'file_size': file_size,
                'format': image.format
            }
            
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {
                'width': 1024,
                'height': 1024,
                'file_size': 0,
                'format': 'webp'
            }
    
    def _empty_image_result(self, keyword: str) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'image_url': '',
            'image_path': '',
            'alt_text': f"Image of {keyword}",
            'filename': '',
            'width': 0,
            'height': 0,
            'format': 'webp',
            'file_size': 0,
            'seo_optimized': False,
            'model_used': 'none',
            'keyword': keyword,
            'error': 'Image generation failed'
        }

