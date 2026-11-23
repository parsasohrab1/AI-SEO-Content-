"""
تولید ویدیو بهینه برای SEO
استفاده از Lumen5، Synthesia یا MoviePy (Fallback)
"""

import logging
import os
import re
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoContentGenerator:
    """
    کلاس تولید ویدیو بهینه برای SEO
    
    ویژگی‌ها:
    - تبدیل متن به ویدیو
    - استفاده از Lumen5 یا Synthesia
    - زیرنویس خودکار
    - بهینه‌سازی برای YouTube SEO
    - Thumbnail Generator
    """
    
    def __init__(self):
        self.lumen5_client = None
        self.synthesia_client = None
        self.lumen5_enabled = False
        self.synthesia_enabled = False
        
        # سعی می‌کنیم Lumen5 client را بارگذاری کنیم
        try:
            lumen5_api_key = os.getenv('LUMEN5_API_KEY')
            if lumen5_api_key:
                # Lumen5 API integration
                self.lumen5_api_key = lumen5_api_key
                self.lumen5_enabled = True
                logger.info("Lumen5 client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize Lumen5 client: {str(e)}")
        
        # سعی می‌کنیم Synthesia client را بارگذاری کنیم
        try:
            synthesia_api_key = os.getenv('SYNTHESIA_API_KEY')
            if synthesia_api_key:
                # Synthesia API integration
                self.synthesia_api_key = synthesia_api_key
                self.synthesia_enabled = True
                logger.info("Synthesia client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize Synthesia client: {str(e)}")
    
    async def generate_video(
        self,
        article_content: str,
        keyword: str,
        duration: int = 60,
        model: str = 'lumen5',  # lumen5, synthesia, moviepy
        language: str = 'fa',
        include_subtitles: bool = True,
        style: str = 'professional'
    ) -> Dict[str, Any]:
        """
        تولید ویدیو از مقاله
        
        Args:
            article_content: محتوای مقاله
            keyword: کلمه کلیدی
            duration: مدت زمان ویدیو (ثانیه)
            model: مدل استفاده شده (lumen5, synthesia, moviepy)
            language: زبان
            include_subtitles: آیا زیرنویس اضافه شود
            style: استایل ویدیو
        
        Returns:
            {
                'video_url': str,
                'video_path': str,
                'thumbnail_url': str,
                'thumbnail_path': str,
                'subtitles_path': str,
                'title': str,
                'description': str,
                'tags': List[str],
                'duration': int,
                'format': str,
                'file_size': int,
                'youtube_optimized': bool,
                'model_used': str
            }
        """
        try:
            # استخراج اطلاعات از محتوا
            video_script = self._extract_video_script(article_content, duration)
            
            # تولید عنوان و توضیحات برای YouTube
            title = self._generate_youtube_title(keyword, language)
            description = self._generate_youtube_description(article_content, keyword, language)
            tags = self._generate_youtube_tags(keyword, article_content, language)
            
            # تولید ویدیو
            if model == 'lumen5' and self.lumen5_enabled:
                video_data = await self._generate_with_lumen5(video_script, style, duration)
                model_used = 'lumen5'
            elif model == 'synthesia' and self.synthesia_enabled:
                video_data = await self._generate_with_synthesia(video_script, style, duration, language)
                model_used = 'synthesia'
            else:
                # Fallback: استفاده از MoviePy
                video_data = await self._generate_with_moviepy(video_script, keyword, duration, language)
                model_used = 'moviepy'
            
            # تولید زیرنویس
            subtitles_path = None
            if include_subtitles:
                subtitles_path = await self._generate_subtitles(video_script, keyword, language)
            
            # تولید Thumbnail
            thumbnail_path = await self._generate_thumbnail(keyword, title, language)
            
            # ذخیره ویدیو
            video_path = await self._save_video(video_data, keyword)
            
            # بهینه‌سازی ویدیو
            optimized_path = await self._optimize_video(video_path, keyword)
            
            # محاسبه اطلاعات ویدیو
            video_info = await self._get_video_info(optimized_path)
            
            return {
                'video_url': f'/videos/{Path(optimized_path).name}',
                'video_path': optimized_path,
                'thumbnail_url': f'/thumbnails/{Path(thumbnail_path).name}',
                'thumbnail_path': thumbnail_path,
                'subtitles_path': subtitles_path,
                'title': title,
                'description': description,
                'tags': tags,
                'duration': video_info.get('duration', duration),
                'format': 'mp4',
                'file_size': video_info.get('file_size', 0),
                'youtube_optimized': True,
                'model_used': model_used,
                'keyword': keyword,
                'width': video_info.get('width', 1920),
                'height': video_info.get('height', 1080)
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return self._empty_video_result(keyword)
    
    def _extract_video_script(
        self,
        article_content: str,
        duration: int
    ) -> List[Dict[str, Any]]:
        """
        استخراج اسکریپت ویدیو از محتوا
        
        Returns:
            List of scenes: [{'text': str, 'duration': int, 'image': str}]
        """
        # تقسیم محتوا به بخش‌ها
        paragraphs = [p.strip() for p in article_content.split('\n\n') if p.strip()]
        
        # محاسبه مدت زمان هر بخش
        total_words = sum(len(p.split()) for p in paragraphs)
        words_per_second = 2.5  # سرعت خواندن متوسط
        total_estimated_duration = total_words / words_per_second
        
        # تنظیم تعداد بخش‌ها بر اساس duration
        if total_estimated_duration > duration:
            # کاهش تعداد بخش‌ها
            target_paragraphs = max(1, int(len(paragraphs) * duration / total_estimated_duration))
            paragraphs = paragraphs[:target_paragraphs]
        
        scenes = []
        duration_per_scene = duration / len(paragraphs) if paragraphs else duration
        
        for i, paragraph in enumerate(paragraphs):
            scene_duration = min(int(duration_per_scene), 10)  # حداکثر 10 ثانیه
            scenes.append({
                'text': paragraph[:200],  # محدود کردن طول
                'duration': scene_duration,
                'scene_number': i + 1
            })
        
        return scenes
    
    async def _generate_with_lumen5(
        self,
        video_script: List[Dict[str, Any]],
        style: str,
        duration: int
    ) -> bytes:
        """تولید ویدیو با Lumen5 API"""
        try:
            import httpx
            
            # ساخت درخواست به Lumen5 API
            # توجه: این یک مثال است، API واقعی Lumen5 ممکن است متفاوت باشد
            api_url = "https://api.lumen5.com/v2/videos"
            
            payload = {
                "script": [scene['text'] for scene in video_script],
                "style": style,
                "duration": duration
            }
            
            headers = {
                "Authorization": f"Bearer {self.lumen5_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # ایجاد ویدیو
                response = await client.post(api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                video_data = response.json()
                video_id = video_data.get('id')
                
                # انتظار برای آماده شدن ویدیو
                await asyncio.sleep(10)  # در واقع باید polling کنیم
                
                # دانلود ویدیو
                download_url = f"{api_url}/{video_id}/download"
                video_response = await client.get(download_url, headers=headers)
                video_response.raise_for_status()
                
                return video_response.content
                
        except Exception as e:
            logger.error(f"Error generating video with Lumen5: {str(e)}")
            raise
    
    async def _generate_with_synthesia(
        self,
        video_script: List[Dict[str, Any]],
        style: str,
        duration: int,
        language: str
    ) -> bytes:
        """تولید ویدیو با Synthesia API"""
        try:
            import httpx
            
            # ساخت درخواست به Synthesia API
            api_url = "https://api.synthesia.io/v2/videos"
            
            # ساخت اسکریپت برای Synthesia
            scenes = []
            for scene in video_script:
                scenes.append({
                    "type": "text",
                    "text": scene['text'],
                    "duration": scene['duration']
                })
            
            payload = {
                "title": "Generated Video",
                "scenes": scenes,
                "language": language,
                "style": style
            }
            
            headers = {
                "Authorization": f"Bearer {self.synthesia_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # ایجاد ویدیو
                response = await client.post(api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                video_data = response.json()
                video_id = video_data.get('id')
                
                # انتظار برای آماده شدن ویدیو
                await asyncio.sleep(10)  # در واقع باید polling کنیم
                
                # دانلود ویدیو
                download_url = f"{api_url}/{video_id}/download"
                video_response = await client.get(download_url, headers=headers)
                video_response.raise_for_status()
                
                return video_response.content
                
        except Exception as e:
            logger.error(f"Error generating video with Synthesia: {str(e)}")
            raise
    
    async def _generate_with_moviepy(
        self,
        video_script: List[Dict[str, Any]],
        keyword: str,
        duration: int,
        language: str
    ) -> str:
        """تولید ویدیو با MoviePy (Fallback)"""
        try:
            from moviepy.editor import (
                VideoFileClip, TextClip, CompositeVideoClip,
                ImageClip, concatenate_videoclips, ColorClip
            )
            from PIL import Image, ImageDraw, ImageFont
            
            # ایجاد پوشه موقت
            temp_dir = Path("backend/generated_content/temp_videos")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            clips = []
            
            for i, scene in enumerate(video_script):
                # ایجاد تصویر برای هر صحنه
                img = Image.new('RGB', (1920, 1080), color=(41, 128, 185))
                draw = ImageDraw.Draw(img)
                
                # اضافه کردن متن
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    font = ImageFont.load_default()
                
                # تقسیم متن به خطوط
                text = scene['text']
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] < 1800:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # رسم متن
                y_offset = 400
                for line in lines[:5]:  # حداکثر 5 خط
                    draw.text((60, y_offset), line, fill=(255, 255, 255), font=font)
                    y_offset += 80
                
                # Save the image
                img_path = temp_dir / f"scene_{i}.png"
                img.save(img_path)
                
                # ایجاد clip از تصویر
                img_clip = ImageClip(str(img_path)).set_duration(scene['duration'])
                clips.append(img_clip)
            
            # ترکیب کلیپ‌ها
            if clips:
                final_video = concatenate_videoclips(clips, method="compose")
            else:
                # ویدیو خالی
                final_video = ColorClip(size=(1920, 1080), color=(41, 128, 185), duration=duration)
            
            # ذخیره ویدیو
            output_path = temp_dir / f"video_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio=False
            )
            
            # پاک کردن کلیپ‌ها
            for clip in clips:
                clip.close()
            final_video.close()
            
            return str(output_path)
            
        except ImportError:
            logger.warning("MoviePy not available. Install with: pip install moviepy")
            raise
        except Exception as e:
            logger.error(f"Error generating video with MoviePy: {str(e)}")
            raise
    
    async def _generate_subtitles(
        self,
        video_script: List[Dict[str, Any]],
        keyword: str,
        language: str
    ) -> str:
        """تولید زیرنویس خودکار (SRT format)"""
        try:
            subtitles_dir = Path("backend/generated_content/subtitles")
            subtitles_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{keyword}_{datetime.now().strftime('%Y%m%d')}.srt"
            subtitles_path = subtitles_dir / filename
            
            current_time = 0
            
            with open(subtitles_path, 'w', encoding='utf-8') as f:
                for i, scene in enumerate(video_script):
                    start_time = self._format_srt_time(current_time)
                    end_time = self._format_srt_time(current_time + scene['duration'])
                    
                    f.write(f"{i + 1}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{scene['text']}\n\n")
                    
                    current_time += scene['duration']
            
            logger.info(f"Subtitles generated: {subtitles_path}")
            return str(subtitles_path)
            
        except Exception as e:
            logger.error(f"Error generating subtitles: {str(e)}")
            return ""
    
    def _format_srt_time(self, seconds: float) -> str:
        """فرمت زمان برای SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    async def _generate_thumbnail(
        self,
        keyword: str,
        title: str,
        language: str
    ) -> str:
        """تولید Thumbnail برای ویدیو"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # ایجاد تصویر thumbnail
            img = Image.new('RGB', (1280, 720), color=(41, 128, 185))
            draw = ImageDraw.Draw(img)
            
            # اضافه کردن عنوان
            try:
                font_large = ImageFont.truetype("arial.ttf", 80)
                font_small = ImageFont.truetype("arial.ttf", 50)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # رسم عنوان
            title_lines = self._wrap_text(title, 40)
            y_offset = 250
            for line in title_lines[:3]:  # حداکثر 3 خط
                bbox = draw.textbbox((0, 0), line, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = (1280 - text_width) // 2
                draw.text((x, y_offset), line, fill=(255, 255, 255), font=font_large)
                y_offset += 100
            
            # ذخیره thumbnail
            thumbnails_dir = Path("backend/generated_content/thumbnails")
            thumbnails_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{keyword}_{datetime.now().strftime('%Y%m%d')}.jpg"
            thumbnail_path = thumbnails_dir / filename
            img.save(thumbnail_path, 'JPEG', quality=95)
            
            logger.info(f"Thumbnail generated: {thumbnail_path}")
            return str(thumbnail_path)
            
        except ImportError:
            logger.warning("PIL not available for thumbnail generation")
            return ""
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return ""
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """تقسیم متن به خطوط"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _generate_youtube_title(
        self,
        keyword: str,
        language: str
    ) -> str:
        """تولید عنوان بهینه برای YouTube"""
        if language == 'fa':
            title = f"آموزش کامل {keyword} | راهنمای جامع"
        else:
            title = f"Complete Guide to {keyword} | Full Tutorial"
        
        # محدود کردن طول (حداکثر 100 کاراکتر)
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title
    
    def _generate_youtube_description(
        self,
        article_content: str,
        keyword: str,
        language: str
    ) -> str:
        """تولید توضیحات بهینه برای YouTube"""
        # استخراج خلاصه از محتوا
        first_paragraph = article_content.split('\n\n')[0] if '\n\n' in article_content else article_content[:300]
        
        if language == 'fa':
            description = f"""در این ویدیو به طور کامل درباره {keyword} صحبت می‌کنیم.

{first_paragraph}

📌 فهرست مطالب:
- معرفی {keyword}
- نکات مهم
- نتیجه‌گیری

🔔 برای دریافت ویدیوهای جدید، کانال را سابسکرایب کنید.

#سئو #آموزش #دیجیتال_مارکتینگ"""
        else:
            description = f"""In this video, we'll discuss {keyword} in detail.

{first_paragraph}

📌 Table of Contents:
- Introduction to {keyword}
- Key Points
- Conclusion

🔔 Subscribe to our channel for more videos.

#SEO #Tutorial #DigitalMarketing"""
        
        return description
    
    def _generate_youtube_tags(
        self,
        keyword: str,
        article_content: str,
        language: str
    ) -> List[str]:
        """تولید تگ‌های بهینه برای YouTube"""
        tags = [keyword]
        
        # استخراج کلمات کلیدی از محتوا
        words = re.findall(r'\b\w{4,}\b', article_content.lower())
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # اضافه کردن کلمات پرتکرار
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        for word, _ in sorted_words[:5]:
            if word not in tags:
                tags.append(word)
        
        # اضافه کردن تگ‌های عمومی
        if language == 'fa':
            tags.extend(['سئو', 'آموزش', 'دیجیتال_مارکتینگ'])
        else:
            tags.extend(['SEO', 'Tutorial', 'DigitalMarketing'])
        
        return tags[:15]  # حداکثر 15 تگ
    
    async def _save_video(
        self,
        video_data: Any,  # bytes or str (path)
        keyword: str
    ) -> str:
        """ذخیره ویدیو"""
        try:
            # اگر video_data یک path باشد (از MoviePy)
            if isinstance(video_data, str):
                # کپی فایل به پوشه videos
                import shutil
                videos_dir = Path("backend/generated_content/videos")
                videos_dir.mkdir(parents=True, exist_ok=True)
                
                source_path = Path(video_data)
                filename = self._generate_video_filename(keyword)
                dest_path = videos_dir / filename
                
                shutil.copy2(source_path, dest_path)
                logger.info(f"Video copied: {dest_path}")
                return str(dest_path)
            
            # اگر video_data bytes باشد
            import aiofiles
            
            videos_dir = Path("backend/generated_content/videos")
            videos_dir.mkdir(parents=True, exist_ok=True)
            
            filename = self._generate_video_filename(keyword)
            video_path = videos_dir / filename
            
            async with aiofiles.open(video_path, 'wb') as f:
                await f.write(video_data)
            
            logger.info(f"Video saved: {video_path}")
            return str(video_path)
            
        except ImportError:
            # Fallback: استفاده از open معمولی
            if isinstance(video_data, str):
                import shutil
                videos_dir = Path("backend/generated_content/videos")
                videos_dir.mkdir(parents=True, exist_ok=True)
                
                source_path = Path(video_data)
                filename = self._generate_video_filename(keyword)
                dest_path = videos_dir / filename
                
                shutil.copy2(source_path, dest_path)
                logger.info(f"Video copied: {dest_path}")
                return str(dest_path)
            
            videos_dir = Path("backend/generated_content/videos")
            videos_dir.mkdir(parents=True, exist_ok=True)
            
            filename = self._generate_video_filename(keyword)
            video_path = videos_dir / filename
            
            with open(video_path, 'wb') as f:
                f.write(video_data)
            
            logger.info(f"Video saved: {video_path}")
            return str(video_path)
            
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            raise
    
    def _generate_video_filename(self, keyword: str) -> str:
        """تولید نام فایل بهینه"""
        clean_keyword = re.sub(r'[^\w\s-]', '', keyword)
        clean_keyword = re.sub(r'\s+', '-', clean_keyword)
        clean_keyword = clean_keyword.lower()
        
        if len(clean_keyword) > 50:
            clean_keyword = clean_keyword[:50]
        
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{clean_keyword}-{timestamp}.mp4"
    
    async def _optimize_video(
        self,
        video_path: str,
        keyword: str
    ) -> str:
        """بهینه‌سازی ویدیو برای وب"""
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            
            # بهینه‌سازی: کاهش کیفیت برای حجم کمتر
            optimized_path = video_path.replace('.mp4', '_optimized.mp4')
            
            video.write_videofile(
                optimized_path,
                fps=24,
                bitrate="5000k",
                codec='libx264',
                preset='medium'
            )
            
            video.close()
            
            # حذف فایل اصلی
            if Path(video_path).exists() and video_path != optimized_path:
                Path(video_path).unlink()
            
            logger.info(f"Video optimized: {optimized_path}")
            return optimized_path
            
        except ImportError:
            logger.warning("MoviePy not available. Video not optimized.")
            return video_path
        except Exception as e:
            logger.error(f"Error optimizing video: {str(e)}")
            return video_path
    
    async def _get_video_info(
        self,
        video_path: str
    ) -> Dict[str, Any]:
        """دریافت اطلاعات ویدیو"""
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            file_size = Path(video_path).stat().st_size
            
            info = {
                'duration': int(video.duration),
                'width': video.w,
                'height': video.h,
                'fps': video.fps,
                'file_size': file_size
            }
            
            video.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {
                'duration': 60,
                'width': 1920,
                'height': 1080,
                'fps': 24,
                'file_size': 0
            }
    
    def _empty_video_result(self, keyword: str) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'video_url': '',
            'video_path': '',
            'thumbnail_url': '',
            'thumbnail_path': '',
            'subtitles_path': '',
            'title': f"Video about {keyword}",
            'description': '',
            'tags': [],
            'duration': 0,
            'format': 'mp4',
            'file_size': 0,
            'youtube_optimized': False,
            'model_used': 'none',
            'keyword': keyword,
            'error': 'Video generation failed'
        }

