# راهنمای پیاده‌سازی سریع - بهبودهای فوری

## 🚀 شروع سریع

این راهنما شامل کدهای آماده برای پیاده‌سازی سریع بهبودهای فوری است.

---

## 1. یکپارچه‌سازی OpenAI برای تولید محتوا

### 1.1 ایجاد فایل جدید: `backend/core/content_generation/ai_generator.py`

```python
"""
تولید محتوای هوشمند با OpenAI GPT-4
"""

import os
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """تولید محتوا با استفاده از OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv('AI_CONTENT_MODEL', 'gpt-4-turbo-preview')
    
    async def generate_article(
        self,
        keyword: str,
        keyword_metrics: Dict[str, Any] = None,
        competitor_content: List[Dict] = None,
        target_length: int = 1500,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        تولید مقاله با AI
        
        Args:
            keyword: کلمه کلیدی اصلی
            keyword_metrics: معیارهای کلمه کلیدی (search volume, difficulty, etc.)
            competitor_content: محتوای رقبا برای تحلیل
            target_length: طول هدف مقاله (تعداد کلمات)
            language: زبان محتوا ('fa' یا 'en')
        
        Returns:
            محتوای تولید شده با معیارهای SEO
        """
        try:
            # ساخت prompt پیشرفته
            prompt = self._build_prompt(
                keyword=keyword,
                keyword_metrics=keyword_metrics or {},
                competitor_content=competitor_content or [],
                target_length=target_length,
                language=language
            )
            
            # تولید محتوا با OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=target_length * 2,  # تقریبی برای کلمات
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            content = response.choices[0].message.content
            
            # محاسبه معیارهای SEO
            seo_metrics = self._calculate_seo_metrics(content, keyword, language)
            
            return {
                'content': content,
                'title': self._extract_title(content),
                'meta_description': self._generate_meta_description(content, keyword, language),
                'word_count': len(content.split()),
                'seo_score': seo_metrics['seo_score'],
                'keyword_density': seo_metrics['keyword_density'],
                'readability_score': seo_metrics['readability'],
                'headings': self._extract_headings(content),
                'language': language,
                'generated_by': 'openai_gpt4'
            }
            
        except Exception as e:
            logger.error(f"Error generating content with AI: {str(e)}")
            raise
    
    def _get_system_prompt(self, language: str) -> str:
        """پیام سیستم برای AI"""
        if language == 'fa':
            return """شما یک نویسنده متخصص SEO و تولید محتوا هستید. 
            محتوای شما باید:
            - بهینه شده برای موتورهای جستجو باشد
            - ارزشمند و مفید برای خواننده باشد
            - ساختار منظم با عنوان‌های مناسب داشته باشد
            - از کلمات کلیدی به صورت طبیعی استفاده کند
            - خوانا و جذاب باشد"""
        else:
            return """You are an expert SEO content writer.
            Your content must be:
            - SEO optimized
            - Valuable and useful for readers
            - Well-structured with appropriate headings
            - Use keywords naturally
            - Readable and engaging"""
    
    def _build_prompt(
        self,
        keyword: str,
        keyword_metrics: Dict[str, Any],
        competitor_content: List[Dict],
        target_length: int,
        language: str
    ) -> str:
        """ساخت prompt پیشرفته"""
        
        # خلاصه تحلیل رقبا
        competitor_summary = ""
        if competitor_content:
            competitor_summary = self._summarize_competitors(competitor_content, language)
        
        # اطلاعات کلمه کلیدی
        metrics_text = ""
        if keyword_metrics:
            metrics_text = f"""
            Keyword Metrics:
            - Search Volume: {keyword_metrics.get('search_volume', 'N/A')}
            - Difficulty: {keyword_metrics.get('difficulty', 'N/A')}
            - Competition: {keyword_metrics.get('competition', 'N/A')}
            """
        
        if language == 'fa':
            prompt = f"""
            یک مقاله جامع و بهینه شده برای SEO درباره "{keyword}" بنویسید.
            
            {metrics_text}
            
            {competitor_summary}
            
            الزامات:
            - طول مقاله: حدود {target_length} کلمه
            - استفاده طبیعی از کلمه کلیدی "{keyword}" (چگالی 1-2%)
            - ساختار منظم با عنوان‌های H2 و H3
            - مقدمه جذاب در 100 کلمه اول
            - محتوای ارزشمند و عمیق
            - نتیجه‌گیری با فراخوان به عمل
            - استفاده از کلمات کلیدی معنایی مرتبط
            
            مقاله را بنویسید:
            """
        else:
            prompt = f"""
            Write a comprehensive, SEO-optimized article about "{keyword}".
            
            {metrics_text}
            
            {competitor_summary}
            
            Requirements:
            - Article length: approximately {target_length} words
            - Natural use of keyword "{keyword}" (density 1-2%)
            - Well-structured with H2 and H3 headings
            - Engaging introduction in first 100 words
            - Valuable and in-depth content
            - Conclusion with call-to-action
            - Use related semantic keywords
            
            Write the article now:
            """
        
        return prompt
    
    def _summarize_competitors(self, competitor_content: List[Dict], language: str) -> str:
        """خلاصه کردن محتوای رقبا"""
        if not competitor_content:
            return ""
        
        summary_parts = []
        if language == 'fa':
            summary_parts.append("تحلیل محتوای رقبا:")
            summary_parts.append(f"- تعداد رقبا: {len(competitor_content)}")
            
            # استخراج موضوعات مشترک
            common_topics = set()
            for content in competitor_content[:3]:  # 3 رقیب اول
                if 'topics' in content:
                    common_topics.update(content['topics'])
            
            if common_topics:
                summary_parts.append(f"- موضوعات مشترک: {', '.join(list(common_topics)[:5])}")
        else:
            summary_parts.append("Competitor Content Analysis:")
            summary_parts.append(f"- Number of competitors: {len(competitor_content)}")
        
        return "\n".join(summary_parts)
    
    def _calculate_seo_metrics(
        self,
        content: str,
        keyword: str,
        language: str
    ) -> Dict[str, Any]:
        """محاسبه معیارهای SEO"""
        words = content.lower().split()
        keyword_lower = keyword.lower()
        
        # محاسبه Keyword Density
        keyword_count = sum(1 for word in words if keyword_lower in word.lower())
        total_words = len(words)
        keyword_density = (keyword_count / total_words * 100) if total_words > 0 else 0
        
        # محاسبه SEO Score (ساده)
        seo_score = 0
        
        # بررسی وجود کلمه کلیدی در 100 کلمه اول
        if keyword_lower in ' '.join(words[:100]).lower():
            seo_score += 20
        
        # بررسی Keyword Density
        if 1 <= keyword_density <= 2:
            seo_score += 20
        elif 0.5 <= keyword_density < 1 or 2 < keyword_density <= 3:
            seo_score += 10
        
        # بررسی طول محتوا
        if 1000 <= total_words <= 3000:
            seo_score += 20
        elif 500 <= total_words < 1000 or 3000 < total_words <= 5000:
            seo_score += 10
        
        # بررسی وجود عنوان‌ها
        if '##' in content or '<h2>' in content.lower():
            seo_score += 20
        
        # بررسی خوانایی (ساده)
        avg_sentence_length = total_words / max(content.count('.'), 1)
        if 15 <= avg_sentence_length <= 25:
            seo_score += 20
        
        return {
            'seo_score': min(seo_score, 100),
            'keyword_density': round(keyword_density, 2),
            'readability': self._simple_readability_score(content, language)
        }
    
    def _simple_readability_score(self, content: str, language: str) -> float:
        """محاسبه ساده خوانایی"""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # امتیاز ساده (هرچه جملات کوتاه‌تر، خوانایی بهتر)
        if avg_sentence_length <= 15:
            return 90
        elif avg_sentence_length <= 20:
            return 75
        elif avg_sentence_length <= 25:
            return 60
        else:
            return 45
    
    def _extract_title(self, content: str) -> str:
        """استخراج عنوان از محتوا"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line and len(line) < 100:
                return line
        return "مقاله SEO"
    
    def _generate_meta_description(
        self,
        content: str,
        keyword: str,
        language: str
    ) -> str:
        """تولید meta description"""
        # استفاده از 2-3 جمله اول
        sentences = content.split('.')[:3]
        description = '. '.join(sentences).strip()
        
        # محدود کردن به 160 کاراکتر
        if len(description) > 160:
            description = description[:157] + '...'
        
        return description
    
    def _extract_headings(self, content: str) -> List[Dict[str, str]]:
        """استخراج عنوان‌ها از محتوا"""
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                headings.append({
                    'level': 'h2',
                    'text': line[3:].strip()
                })
            elif line.startswith('### '):
                headings.append({
                    'level': 'h3',
                    'text': line[4:].strip()
                })
        
        return headings
```

---

## 2. یکپارچه‌سازی SEMrush API

### 2.1 ایجاد فایل: `backend/core/keyword_research/semrush_client.py`

```python
"""
یکپارچه‌سازی با SEMrush API برای تحقیق کلمات کلیدی
"""

import os
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SEMrushKeywordAnalyzer:
    """تحلیل کلمات کلیدی با SEMrush"""
    
    def __init__(self):
        self.api_key = os.getenv('SEMRUSH_API_KEY')
        if not self.api_key:
            logger.warning("SEMRUSH_API_KEY not found. SEMrush features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = "https://api.semrush.com/"
    
    async def get_keyword_overview(
        self,
        keyword: str,
        database: str = 'us'  # us, uk, ca, au, etc.
    ) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات جامع کلمه کلیدی
        
        Returns:
            {
                'keyword': str,
                'search_volume': int,
                'cpc': float,
                'competition': float,
                'competition_level': str,  # Low, Medium, High
                'trend': List[int],  # 12 ماه گذشته
                'difficulty': int  # 0-100
            }
        """
        if not self.enabled:
            return None
        
        try:
            params = {
                'key': self.api_key,
                'type': 'phrase_this',
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr,Td'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return self._parse_keyword_overview(response.text, keyword)
                else:
                    logger.error(f"SEMrush API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching keyword overview from SEMrush: {str(e)}")
            return None
    
    def _parse_keyword_overview(self, response_text: str, keyword: str) -> Dict[str, Any]:
        """پارس کردن پاسخ SEMrush"""
        lines = response_text.strip().split('\n')
        if not lines or len(lines) < 2:
            return None
        
        # فرمت: Phrase;Search Volume;CPC;Competition;Number of Results;Trend
        data = lines[1].split(';')
        
        if len(data) < 6:
            return None
        
        try:
            search_volume = int(data[1]) if data[1] else 0
            cpc = float(data[2]) if data[2] else 0.0
            competition = float(data[3]) if data[3] else 0.0
            
            # تعیین سطح رقابت
            if competition < 0.3:
                competition_level = 'Low'
            elif competition < 0.7:
                competition_level = 'Medium'
            else:
                competition_level = 'High'
            
            # Trend (12 ماه)
            trend_data = data[5].split(',') if len(data) > 5 else []
            trend = [int(x) for x in trend_data[:12]] if trend_data else []
            
            # محاسبه Keyword Difficulty (ساده)
            difficulty = self._calculate_difficulty(competition, search_volume)
            
            return {
                'keyword': keyword,
                'search_volume': search_volume,
                'cpc': cpc,
                'competition': competition,
                'competition_level': competition_level,
                'trend': trend,
                'difficulty': difficulty,
                'number_of_results': int(data[4]) if len(data) > 4 and data[4] else 0
            }
        except Exception as e:
            logger.error(f"Error parsing SEMrush response: {str(e)}")
            return None
    
    def _calculate_difficulty(self, competition: float, search_volume: int) -> int:
        """محاسبه Keyword Difficulty (0-100)"""
        # فرمول ساده: ترکیب Competition و Search Volume
        base_score = int(competition * 50)  # 0-50 از competition
        
        # تعدیل بر اساس Search Volume
        if search_volume > 10000:
            volume_score = 30
        elif search_volume > 1000:
            volume_score = 20
        elif search_volume > 100:
            volume_score = 10
        else:
            volume_score = 5
        
        difficulty = min(base_score + volume_score, 100)
        return difficulty
    
    async def get_related_keywords(
        self,
        keyword: str,
        database: str = 'us',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی مرتبط"""
        if not self.enabled:
            return []
        
        try:
            params = {
                'key': self.api_key,
                'type': 'phrase_related',
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return self._parse_related_keywords(response.text, limit)
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching related keywords: {str(e)}")
            return []
    
    def _parse_related_keywords(self, response_text: str, limit: int) -> List[Dict[str, Any]]:
        """پارس کردن کلمات کلیدی مرتبط"""
        keywords = []
        lines = response_text.strip().split('\n')
        
        for line in lines[1:limit+1]:  # خط اول header است
            data = line.split(';')
            if len(data) >= 4:
                try:
                    keywords.append({
                        'keyword': data[0],
                        'search_volume': int(data[1]) if data[1] else 0,
                        'cpc': float(data[2]) if data[2] else 0.0,
                        'competition': float(data[3]) if data[3] else 0.0
                    })
                except:
                    continue
        
        return keywords
```

---

## 3. به‌روزرسانی ContentGenerator موجود

### 3.1 اضافه کردن استفاده از AI Generator

در فایل `backend/core/content_generator.py`:

```python
# در ابتدای فایل
from .content_generation.ai_generator import AIContentGenerator

class ContentGenerator:
    def __init__(self):
        # اضافه کردن AI Generator
        try:
            self.ai_generator = AIContentGenerator()
            self.ai_enabled = True
        except Exception as e:
            logger.warning(f"AI Generator not available: {str(e)}")
            self.ai_generator = None
            self.ai_enabled = False
    
    async def _generate_text_content_for_keyword(
        self,
        keyword: str,
        site_url: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """تولید محتوای متنی برای یک کلمه کلیدی خاص"""
        
        # استفاده از AI Generator اگر موجود باشد
        if self.ai_enabled and self.ai_generator:
            try:
                # دریافت معیارهای کلمه کلیدی (اگر SEMrush موجود باشد)
                keyword_metrics = await self._get_keyword_metrics(keyword)
                
                # تولید با AI
                ai_content = await self.ai_generator.generate_article(
                    keyword=keyword,
                    keyword_metrics=keyword_metrics,
                    target_length=1500,
                    language=language
                )
                
                return [{
                    'id': f"content_{hash(keyword)}_{datetime.now().timestamp()}",
                    'title': ai_content['title'],
                    'content': ai_content['content'],
                    'type': 'article',
                    'word_count': ai_content['word_count'],
                    'keywords': [keyword],
                    'status': 'generated',
                    'created_at': datetime.now().isoformat(),
                    'seo_score': ai_content['seo_score'],
                    'description': ai_content['meta_description'],
                    'headings': ai_content['headings'],
                    'generated_by': 'ai'
                }]
            except Exception as e:
                logger.error(f"Error generating with AI, falling back to template: {str(e)}")
        
        # Fallback به روش قبلی (template-based)
        return await self._generate_template_content(keyword, site_url, language)
    
    async def _get_keyword_metrics(self, keyword: str) -> Dict[str, Any]:
        """دریافت معیارهای کلمه کلیدی"""
        try:
            from .keyword_research.semrush_client import SEMrushKeywordAnalyzer
            semrush = SEMrushKeywordAnalyzer()
            if semrush.enabled:
                return await semrush.get_keyword_overview(keyword)
        except:
            pass
        return {}
```

---

## 4. اضافه کردن به requirements.txt

```txt
# AI Content Generation
openai==1.3.5  # موجود است

# Keyword Research
httpx==0.25.1  # موجود است
```

---

## 5. تنظیم Environment Variables

In the `.env` file:

```env
# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# SEMrush API (اختیاری)
SEMRUSH_API_KEY=your-semrush-api-key-here

# Configuration
AI_CONTENT_MODEL=gpt-4-turbo-preview
```

---

## 6. تست سریع

### تست AI Content Generator:

```python
import asyncio
from backend.core.content_generation.ai_generator import AIContentGenerator

async def test_ai_generator():
    generator = AIContentGenerator()
    
    result = await generator.generate_article(
        keyword="بهینه‌سازی سئو",
        target_length=1000,
        language='fa'
    )
    
    print(f"Title: {result['title']}")
    print(f"Word Count: {result['word_count']}")
    print(f"SEO Score: {result['seo_score']}")
    print(f"Content Preview: {result['content'][:200]}...")

# اجرا
asyncio.run(test_ai_generator())
```

---

## 📝 نکات مهم

1. **API Keys**: مطمئن شوید که API keys را در `.env` تنظیم کرده‌اید
2. **هزینه‌ها**: OpenAI GPT-4 هزینه‌بر است، برای تست از GPT-3.5-turbo استفاده کنید
3. **Rate Limits**: به محدودیت‌های API توجه کنید
4. **Error Handling**: همیشه fallback به روش قبلی داشته باشید

---

**آماده برای پیاده‌سازی!** 🚀

