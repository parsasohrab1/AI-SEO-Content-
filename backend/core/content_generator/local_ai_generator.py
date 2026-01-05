"""
تولید محتوا با مدل‌های Open Source (Local)
استفاده از Llama 2, Mistral و سایر مدل‌های Open Source
"""

import logging
import os
from typing import Dict, Any, List, Optional
import asyncio
import re
from collections import Counter

logger = logging.getLogger(__name__)


class LocalAIContentGenerator:
    """
    کلاس تولید محتوا با مدل‌های Open Source
    
    ویژگی‌ها:
    - استفاده از Llama 2, Mistral و سایر مدل‌های Open Source
    - اجرای محلی (بدون نیاز به API)
    - کاهش هزینه
    - پشتیبانی از CPU و GPU
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.generator = None
        self.model_name = model_name or os.getenv(
            'LOCAL_AI_MODEL',
            'mistralai/Mistral-7B-Instruct-v0.2'
        )
        self.device = os.getenv('LOCAL_AI_DEVICE', 'auto')  # auto, cpu, cuda
        self.enabled = False
        
        # سعی می‌کنیم مدل را بارگذاری کنیم
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            import torch
            
            logger.info(f"Loading local AI model: {self.model_name}")
            
            # بررسی device
            if self.device == 'auto':
                self.device = 0 if torch.cuda.is_available() else -1
            elif self.device == 'cuda':
                self.device = 0 if torch.cuda.is_available() else -1
            else:
                self.device = -1  # CPU
            
            # بارگذاری مدل
            try:
                self.generator = pipeline(
                    "text-generation",
                    model=self.model_name,
                    device_map="auto" if self.device != -1 else None,
                    device=self.device,
                    torch_dtype=torch.float16 if self.device != -1 else torch.float32,
                    model_kwargs={
                        "load_in_8bit": os.getenv('LOCAL_AI_8BIT', 'false').lower() == 'true',
                        "load_in_4bit": os.getenv('LOCAL_AI_4BIT', 'false').lower() == 'true'
                    }
                )
                self.enabled = True
                logger.info(f"Local AI model loaded successfully on device: {self.device}")
            except Exception as e:
                logger.warning(f"Could not load model {self.model_name}: {str(e)}")
                logger.info("Trying with smaller model...")
                
                # Fallback به مدل کوچک‌تر
                try:
                    self.model_name = "gpt2"  # مدل کوچک برای تست
                    self.generator = pipeline(
                        "text-generation",
                        model=self.model_name,
                        device=self.device
                    )
                    self.enabled = True
                    logger.info(f"Fallback model {self.model_name} loaded")
                except Exception as e2:
                    logger.error(f"Could not load fallback model: {str(e2)}")
                    
        except ImportError:
            logger.warning("transformers or torch not installed. Install with: pip install transformers torch")
        except Exception as e:
            logger.error(f"Error initializing local AI generator: {str(e)}")
    
    async def generate_article(
        self,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]] = None,
        competitor_content: Optional[List[Dict]] = None,
        target_length: int = 1500,
        language: str = 'fa',
        tone: str = 'professional',
        include_faq: bool = True
    ) -> Dict[str, Any]:
        """
        تولید مقاله با مدل محلی
        
        Args:
            keyword: کلمه کلیدی اصلی
            keyword_metrics: معیارهای کلمه کلیدی
            competitor_content: محتوای رقبا
            target_length: طول هدف محتوا
            language: زبان محتوا
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
        if not self.enabled or not self.generator:
            logger.error("Local AI model not available")
            return self._empty_result(keyword)
        
        try:
            # ساخت prompt
            prompt = self._build_prompt(
                keyword=keyword,
                keyword_metrics=keyword_metrics,
                competitor_analysis=competitor_content,
                target_length=target_length,
                language=language,
                tone=tone,
                include_faq=include_faq
            )
            
            # تولید محتوا (اجرای در thread pool برای async)
            loop = asyncio.get_event_loop()
            generated_text = await loop.run_in_executor(
                None,
                self._generate_text,
                prompt,
                target_length
            )
            
            # پردازش محتوا
            processed_content = self._process_content(generated_text, keyword, language)
            
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
                'language': language,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            return self._empty_result(keyword)
    
    def _generate_text(self, prompt: str, target_length: int) -> str:
        """تولید متن با مدل محلی"""
        try:
            # تنظیمات generation
            max_new_tokens = int(target_length * 1.5)  # تقریباً 1.5 برابر target
            
            result = self.generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                return_full_text=False
            )
            
            # استخراج متن تولید شده
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                return generated_text
            elif isinstance(result, str):
                return result
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return ""
    
    def _build_prompt(
        self,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]],
        competitor_analysis: Optional[List[Dict]],
        target_length: int,
        language: str,
        tone: str,
        include_faq: bool
    ) -> str:
        """ساخت prompt برای مدل محلی"""
        
        # استفاده از prompt مشابه AIContentGenerator
        # اما با فرمت مناسب برای مدل‌های instruction-following
        
        if language == 'fa':
            system_prompt = f"""شما یک نویسنده متخصص SEO هستید. یک مقاله کامل و جامع درباره "{keyword}" بنویسید.

الزامات:
- طول: حدود {target_length} کلمه
- لحن: {tone}
- ساختار: H1, H2, H3
- بهینه برای SEO
- استفاده طبیعی از کلمه کلیدی "{keyword}"
"""
        else:
            system_prompt = f"""You are an expert SEO content writer. Write a comprehensive article about "{keyword}".

Requirements:
- Length: approximately {target_length} words
- Tone: {tone}
- Structure: H1, H2, H3
- SEO optimized
- Natural use of keyword "{keyword}"
"""
        
        # اضافه کردن اطلاعات کلمه کلیدی
        if keyword_metrics:
            if language == 'fa':
                system_prompt += f"\nاطلاعات کلمه کلیدی:\n"
                if keyword_metrics.get('search_volume'):
                    system_prompt += f"- حجم جستجو: {keyword_metrics['search_volume']:,}\n"
                if keyword_metrics.get('difficulty'):
                    system_prompt += f"- سختی: {keyword_metrics['difficulty']}/100\n"
            else:
                system_prompt += f"\nKeyword Information:\n"
                if keyword_metrics.get('search_volume'):
                    system_prompt += f"- Search Volume: {keyword_metrics['search_volume']:,}\n"
                if keyword_metrics.get('difficulty'):
                    system_prompt += f"- Difficulty: {keyword_metrics['difficulty']}/100\n"
        
        # اضافه کردن FAQ
        if include_faq:
            if language == 'fa':
                system_prompt += "\nشامل بخش FAQ با حداقل 5 سوال و پاسخ.\n"
            else:
                system_prompt += "\nInclude an FAQ section with at least 5 questions and answers.\n"
        
        # فرمت prompt برای مدل‌های instruction
        if 'mistral' in self.model_name.lower() or 'llama' in self.model_name.lower():
            # فرمت ChatML یا Instruction
            prompt = f"<s>[INST] {system_prompt}\n\nلطفاً مقاله را بنویسید: [/INST]"
        else:
            # فرمت ساده
            prompt = f"{system_prompt}\n\nArticle:\n"
        
        return prompt
    
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
        """محاسبه SEO Score (مشابه AIContentGenerator)"""
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
        
        keyword_count = sum(1 for word in words if keyword_lower in word)
        
        if len(words) == 0:
            return 0.0
        
        density = (keyword_count / len(words)) * 100
        return round(density, 2)
    
    def _calculate_readability(self, content: str, language: str) -> float:
        """محاسبه Readability Score"""
        sentences = re.split(r'[.!?]\s+', content)
        words = content.split()
        
        if len(sentences) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
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
        
        faq_section = re.search(
            r'(?:FAQ|سوالات متداول|Frequently Asked Questions).*?(?=\n##|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if faq_section:
            faq_text = faq_section.group(0)
            
            qa_pattern = r'###\s+(.+?)\n(.*?)(?=###|\Z)'
            matches = re.findall(qa_pattern, faq_text, re.DOTALL)
            
            for question, answer in matches:
                faq.append({
                    'question': question.strip(),
                    'answer': answer.strip()[:500]
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
            'recommendations': ['Local AI model not available'],
            'keyword': keyword,
            'language': 'fa',
            'model': self.model_name
        }

