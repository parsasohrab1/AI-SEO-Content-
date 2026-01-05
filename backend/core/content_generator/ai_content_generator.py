"""
تولید محتوا با AI (OpenAI GPT-4)
تولید محتوای بهینه برای SEO با استفاده از AI
"""

import logging
import os
from typing import Dict, Any, List, Optional
import re
from collections import Counter

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """
    کلاس تولید محتوا با AI
    
    ویژگی‌ها:
    - استفاده از OpenAI GPT-4
    - تحلیل محتوای رقبا
    - تولید محتوای بهینه برای SEO
    - استفاده طبیعی از کلمات کلیدی
    """
    
    def __init__(self):
        self.client = None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.enabled = False
        
        # سعی می‌کنیم OpenAI client را بارگذاری کنیم
        try:
            from openai import AsyncOpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = AsyncOpenAI(api_key=api_key)
                self.enabled = True
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OPENAI_API_KEY not found in environment variables")
        except ImportError:
            logger.warning("openai package not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
    
    async def generate_article(
        self,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]] = None,
        competitor_content: Optional[List[Dict]] = None,
        target_length: int = 1500,
        language: str = 'fa',
        tone: str = 'professional',  # professional, casual, friendly
        include_faq: bool = True
    ) -> Dict[str, Any]:
        """
        تولید مقاله با AI
        
        Args:
            keyword: کلمه کلیدی اصلی
            keyword_metrics: معیارهای کلمه کلیدی (Search Volume, Difficulty, etc.)
            competitor_content: محتوای رقبا برای تحلیل
            target_length: طول هدف محتوا (تعداد کلمات)
            language: زبان محتوا ('fa' یا 'en')
            tone: لحن محتوا
            include_faq: شامل FAQ باشد
        
        Returns:
            {
                'content': str,
                'title': str,
                'meta_description': str,
                'seo_score': float,
                'keyword_density': float,
                'readability': float,
                'word_count': int,
                'headings': List[str],
                'faq': List[Dict],
                'recommendations': List[str]
            }
        """
        if not self.enabled or not self.client:
            logger.error("OpenAI client not available")
            return self._empty_result(keyword)
        
        try:
            # ساخت prompt پیشرفته
            prompt = self._build_advanced_prompt(
                keyword=keyword,
                keyword_metrics=keyword_metrics,
                competitor_analysis=competitor_content,
                target_length=target_length,
                language=language,
                tone=tone,
                include_faq=include_faq
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
                max_tokens=self._calculate_max_tokens(target_length, language)
            )
            
            content = response.choices[0].message.content
            
            # پردازش و تحلیل محتوا
            processed_content = self._process_content(content, keyword, language)
            
            # محاسبه معیارها
            seo_score = self._calculate_seo_score(processed_content, keyword, keyword_metrics)
            keyword_density = self._calculate_keyword_density(processed_content['content'], keyword)
            readability = self._calculate_readability(processed_content['content'], language)
            
            # استخراج FAQ
            faq = self._extract_faq(processed_content['content']) if include_faq else []
            
            # تولید توصیه‌ها
            recommendations = self._generate_recommendations(
                seo_score,
                keyword_density,
                readability,
                processed_content
            )
            
            return {
                'content': processed_content['content'],
                'title': processed_content.get('title', ''),
                'meta_description': processed_content.get('meta_description', ''),
                'seo_score': seo_score,
                'keyword_density': keyword_density,
                'readability': readability,
                'word_count': len(processed_content['content'].split()),
                'headings': processed_content.get('headings', []),
                'faq': faq,
                'recommendations': recommendations,
                'keyword': keyword,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            return self._empty_result(keyword)
    
    def _get_system_prompt(self, language: str) -> str:
        """دریافت System Prompt"""
        if language == 'fa':
            return """شما یک نویسنده متخصص SEO و تولید محتوا هستید. 
            شما محتوای با کیفیت، بهینه برای SEO و جذاب برای خوانندگان تولید می‌کنید.
            محتوای شما باید:
            - طبیعی و خوانا باشد
            - از کلمات کلیدی به صورت طبیعی استفاده کند
            - ساختار مناسبی داشته باشد (H1, H2, H3)
            - شامل اطلاعات مفید و ارزشمند باشد
            - بهینه برای موتورهای جستجو باشد"""
        else:
            return """You are an expert SEO content writer.
            You create high-quality, SEO-optimized, and engaging content.
            Your content should be:
            - Natural and readable
            - Use keywords naturally
            - Have proper structure (H1, H2, H3)
            - Include valuable and useful information
            - Optimized for search engines"""
    
    def _build_advanced_prompt(
        self,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]],
        competitor_analysis: Optional[List[Dict]],
        target_length: int,
        language: str,
        tone: str,
        include_faq: bool
    ) -> str:
        """ساخت prompt پیشرفته"""
        
        if language == 'fa':
            prompt = f"""یک مقاله کامل و جامع درباره "{keyword}" بنویسید.

الزامات:
- طول مقاله: حدود {target_length} کلمه
- لحن: {tone}
- ساختار: شامل H1, H2, H3
- بهینه برای SEO
- استفاده طبیعی از کلمه کلیدی "{keyword}"
"""
        else:
            prompt = f"""Write a comprehensive article about "{keyword}".

Requirements:
- Article length: approximately {target_length} words
- Tone: {tone}
- Structure: Include H1, H2, H3
- SEO optimized
- Natural use of keyword "{keyword}"
"""
        
        # اضافه کردن اطلاعات کلمه کلیدی
        if keyword_metrics:
            if language == 'fa':
                prompt += f"\nاطلاعات کلمه کلیدی:\n"
                if keyword_metrics.get('search_volume'):
                    prompt += f"- حجم جستجو: {keyword_metrics['search_volume']:,}\n"
                if keyword_metrics.get('difficulty'):
                    prompt += f"- سختی: {keyword_metrics['difficulty']}/100\n"
                if keyword_metrics.get('competition'):
                    prompt += f"- رقابت: {keyword_metrics['competition']}\n"
            else:
                prompt += f"\nKeyword Information:\n"
                if keyword_metrics.get('search_volume'):
                    prompt += f"- Search Volume: {keyword_metrics['search_volume']:,}\n"
                if keyword_metrics.get('difficulty'):
                    prompt += f"- Difficulty: {keyword_metrics['difficulty']}/100\n"
                if keyword_metrics.get('competition'):
                    prompt += f"- Competition: {keyword_metrics['competition']}\n"
        
        # اضافه کردن تحلیل رقبا
        if competitor_analysis:
            competitor_summary = self._summarize_competitors(competitor_analysis, language)
            if language == 'fa':
                prompt += f"\nتحلیل محتوای رقبا:\n{competitor_summary}\n"
                prompt += "محتوای شما باید:\n"
                prompt += "- کامل‌تر و جامع‌تر از رقبا باشد\n"
                prompt += "- اطلاعات جدید و ارزشمندتری ارائه دهد\n"
                prompt += "- ساختار بهتری داشته باشد\n"
                prompt += "- از کلمات کلیدی semantic استفاده کند\n"
            else:
                prompt += f"\nCompetitor Content Analysis:\n{competitor_summary}\n"
                prompt += "Your content should:\n"
                prompt += "- Be more comprehensive than competitors\n"
                prompt += "- Provide new and valuable information\n"
                prompt += "- Have better structure\n"
                prompt += "- Use semantic keywords\n"
        
        # اضافه کردن FAQ
        if include_faq:
            if language == 'fa':
                prompt += "\nشامل بخش FAQ (سوالات متداول) با حداقل 5 سوال و پاسخ.\n"
            else:
                prompt += "\nInclude an FAQ section with at least 5 questions and answers.\n"
        
        # اضافه کردن ساختار محتوا
        if language == 'fa':
            prompt += f"""
ساختار محتوا:
1. مقدمه جذاب با استفاده از کلمه کلیدی در 100 کلمه اول
2. زیرعنوان‌های ساختاریافته (H2, H3) با کلمات کلیدی semantic
3. بخش‌های محتوای مفصل و ارزشمند
4. نتیجه‌گیری با call-to-action

راهنمای SEO:
- استفاده طبیعی از کلمه کلیدی (تراکم: 1-2%)
- شامل کلمات کلیدی semantic
- فرصت‌های Internal Linking
- بهینه برای Featured Snippets
- شامل بخش FAQ در صورت لزوم

لطفاً مقاله را با فرمت زیر ارائه دهید:

# [عنوان اصلی - H1]

[توضیحات متا - 150-160 کاراکتر]

## [زیرعنوان 1 - H2]

[محتوا...]

## [زیرعنوان 2 - H2]

[محتوا...]

## سوالات متداول (FAQ)

### [سوال 1]
[پاسخ...]

### [سوال 2]
[پاسخ...]
"""
        else:
            prompt += f"""
Content Structure:
1. Engaging introduction with keyword in first 100 words
2. Well-structured headings (H2, H3) with semantic keywords
3. Detailed, valuable content sections
4. Conclusion with call-to-action

SEO Guidelines:
- Use keyword naturally (density: 1-2%)
- Include semantic keywords
- Use internal linking opportunities
- Optimize for featured snippets
- Include FAQ section if relevant

Please provide the article in the following format:

# [Main Title - H1]

[Meta Description - 150-160 characters]

## [Subheading 1 - H2]

[Content...]

## [Subheading 2 - H2]

[Content...]

## Frequently Asked Questions (FAQ)

### [Question 1]
[Answer...]

### [Question 2]
[Answer...]
"""
        
        return prompt
    
    def _summarize_competitors(
        self,
        competitor_analysis: List[Dict],
        language: str
    ) -> str:
        """
        خلاصه‌سازی محتوای رقبا
        
        Args:
            competitor_analysis: لیست محتوای رقبا
            language: زبان
        
        Returns:
            خلاصه محتوای رقبا
        """
        if not competitor_analysis:
            return ""
        
        summary_parts = []
        
        if language == 'fa':
            summary_parts.append(f"تعداد رقبا: {len(competitor_analysis)}")
            
            # محاسبه میانگین طول
            avg_length = sum(
                comp.get('word_count', 0) for comp in competitor_analysis
            ) / len(competitor_analysis) if competitor_analysis else 0
            
            summary_parts.append(f"میانگین طول محتوا: {int(avg_length)} کلمه")
            
            # استخراج موضوعات مشترک
            titles = [comp.get('title', '') for comp in competitor_analysis if comp.get('title')]
            if titles:
                summary_parts.append(f"عنوان‌های رقبا: {', '.join(titles[:3])}")
            
            # نکات کلیدی
            summary_parts.append("نکات کلیدی:")
            summary_parts.append("- رقبا روی چه موضوعاتی تمرکز دارند")
            summary_parts.append("- چه اطلاعاتی ارائه می‌دهند")
            summary_parts.append("- ساختار محتوای آن‌ها چگونه است")
        else:
            summary_parts.append(f"Number of competitors: {len(competitor_analysis)}")
            
            # محاسبه میانگین طول
            avg_length = sum(
                comp.get('word_count', 0) for comp in competitor_analysis
            ) / len(competitor_analysis) if competitor_analysis else 0
            
            summary_parts.append(f"Average content length: {int(avg_length)} words")
            
            # استخراج موضوعات مشترک
            titles = [comp.get('title', '') for comp in competitor_analysis if comp.get('title')]
            if titles:
                summary_parts.append(f"Competitor titles: {', '.join(titles[:3])}")
            
            # نکات کلیدی
            summary_parts.append("Key points:")
            summary_parts.append("- What topics competitors focus on")
            summary_parts.append("- What information they provide")
            summary_parts.append("- How their content is structured")
        
        return "\n".join(summary_parts)
    
    def _calculate_max_tokens(self, target_length: int, language: str) -> int:
        """محاسبه حداکثر tokens"""
        # تقریباً 1 token = 0.75 word برای انگلیسی
        # برای فارسی ممکن است بیشتر باشد
        if language == 'fa':
            return int(target_length * 2.5)  # فارسی بیشتر token نیاز دارد
        else:
            return int(target_length * 1.5)
    
    def _process_content(
        self,
        content: str,
        keyword: str,
        language: str
    ) -> Dict[str, Any]:
        """پردازش محتوا"""
        processed = {
            'content': content,
            'title': '',
            'meta_description': '',
            'headings': []
        }
        
        # استخراج عنوان (اولین H1)
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            processed['title'] = h1_match.group(1).strip()
        else:
            # اگر H1 نبود، از اولین خط استفاده می‌کنیم
            first_line = content.split('\n')[0].strip()
            processed['title'] = first_line[:100]
        
        # استخراج Meta Description
        # جستجوی در خطوط اولیه
        lines = content.split('\n')
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                processed['meta_description'] = line[:160]
                break
        
        # استخراج Headings
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        processed['headings'] = headings
        
        return processed
    
    def _calculate_seo_score(
        self,
        processed_content: Dict[str, Any],
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]]
    ) -> float:
        """محاسبه SEO Score"""
        score = 0.0
        
        content = processed_content.get('content', '')
        
        # فاکتور 1: وجود Title (10%)
        if processed_content.get('title'):
            score += 10
        
        # فاکتور 2: وجود Meta Description (10%)
        if processed_content.get('meta_description'):
            meta_desc = processed_content['meta_description']
            if 120 <= len(meta_desc) <= 160:
                score += 10
            elif 100 <= len(meta_desc) < 120 or 160 < len(meta_desc) <= 180:
                score += 7
            else:
                score += 5
        
        # فاکتور 3: وجود H1 (10%)
        if processed_content.get('title'):
            score += 10
        
        # فاکتور 4: تعداد Headings (15%)
        headings = processed_content.get('headings', [])
        if len(headings) >= 5:
            score += 15
        elif len(headings) >= 3:
            score += 10
        elif len(headings) >= 1:
            score += 5
        
        # فاکتور 5: Keyword Density (20%)
        keyword_density = self._calculate_keyword_density(content, keyword)
        if 1.0 <= keyword_density <= 2.5:
            score += 20
        elif 0.5 <= keyword_density < 1.0 or 2.5 < keyword_density <= 3.5:
            score += 15
        else:
            score += 10
        
        # فاکتور 6: طول محتوا (15%)
        word_count = len(content.split())
        if word_count >= 1500:
            score += 15
        elif word_count >= 1000:
            score += 12
        elif word_count >= 500:
            score += 8
        else:
            score += 5
        
        # فاکتور 7: استفاده از کلمه کلیدی در Title (10%)
        title = processed_content.get('title', '').lower()
        if keyword.lower() in title:
            score += 10
        
        # فاکتور 8: استفاده از کلمه کلیدی در Meta Description (10%)
        meta_desc = processed_content.get('meta_description', '').lower()
        if keyword.lower() in meta_desc:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """محاسبه Keyword Density"""
        words = content.lower().split()
        keyword_lower = keyword.lower()
        
        # شمارش تکرار کلمه کلیدی
        keyword_count = sum(1 for word in words if keyword_lower in word)
        
        if len(words) == 0:
            return 0.0
        
        density = (keyword_count / len(words)) * 100
        return round(density, 2)
    
    def _calculate_readability(self, content: str, language: str) -> float:
        """محاسبه Readability Score"""
        # یک محاسبه ساده Readability
        sentences = re.split(r'[.!?]\s+', content)
        words = content.split()
        
        if len(sentences) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Flesch Reading Ease (تقریبی)
        # Score بالاتر = خوانایی بهتر
        if avg_sentence_length <= 15:
            readability = 90
        elif avg_sentence_length <= 20:
            readability = 75
        elif avg_sentence_length <= 25:
            readability = 60
        else:
            readability = 45
        
        return round(readability, 1)
    
    def _extract_faq(self, content: str) -> List[Dict[str, Any]]:
        """استخراج FAQ از محتوا"""
        faq = []
        
        # جستجوی بخش FAQ
        faq_section = re.search(
            r'(?:FAQ|سوالات متداول|Frequently Asked Questions).*?(?=\n##|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if faq_section:
            faq_text = faq_section.group(0)
            
            # استخراج سوالات و پاسخ‌ها
            qa_pattern = r'###\s+(.+?)\n(.*?)(?=###|\Z)'
            matches = re.findall(qa_pattern, faq_text, re.DOTALL)
            
            for question, answer in matches:
                faq.append({
                    'question': question.strip(),
                    'answer': answer.strip()[:500]  # حداکثر 500 کاراکتر
                })
        
        return faq
    
    def _generate_recommendations(
        self,
        seo_score: float,
        keyword_density: float,
        readability: float,
        processed_content: Dict[str, Any]
    ) -> List[str]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        if seo_score < 70:
            recommendations.append("SEO Score پایین است. محتوا را بهبود دهید.")
        
        if keyword_density < 1.0:
            recommendations.append("Keyword Density پایین است. از کلمه کلیدی بیشتر استفاده کنید.")
        elif keyword_density > 3.5:
            recommendations.append("Keyword Density بالا است. از کلمه کلیدی کمتر استفاده کنید.")
        
        if readability < 60:
            recommendations.append("Readability پایین است. جملات را کوتاه‌تر کنید.")
        
        if not processed_content.get('meta_description'):
            recommendations.append("Meta Description اضافه کنید.")
        
        if len(processed_content.get('headings', [])) < 3:
            recommendations.append("Headings بیشتری اضافه کنید.")
        
        return recommendations
    
    def _empty_result(self, keyword: str) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'content': '',
            'title': '',
            'meta_description': '',
            'seo_score': 0.0,
            'keyword_density': 0.0,
            'readability': 0.0,
            'word_count': 0,
            'headings': [],
            'faq': [],
            'recommendations': ['OpenAI API not available'],
            'keyword': keyword,
            'language': 'fa'
        }

