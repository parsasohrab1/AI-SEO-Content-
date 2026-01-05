"""
شخصی‌سازی محتوا بر اساس مخاطب، Intent و سطح تخصص
"""

import logging
import os
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class ContentPersonalizer:
    """
    کلاس شخصی‌سازی محتوا
    
    ویژگی‌ها:
    - شخصی‌سازی بر اساس مخاطب هدف (B2B, B2C, Technical, General)
    - شخصی‌سازی بر اساس Intent (Informational, Commercial, Transactional)
    - تنظیم سطح تخصص
    - پشتیبانی از زبان‌های مختلف
    """
    
    def __init__(self):
        self.openai_client = None
        
        # سعی می‌کنیم OpenAI client را بارگذاری کنیم
        try:
            from openai import AsyncOpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized for content personalization")
        except ImportError:
            logger.warning("openai package not installed")
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI client: {str(e)}")
    
    async def personalize_content(
        self,
        base_content: str,
        target_audience: Dict[str, Any],
        user_intent: str,
        language: str = 'fa'
    ) -> str:
        """
        شخصی‌سازی محتوا بر اساس مخاطب، Intent و سطح تخصص
        
        Args:
            base_content: محتوای پایه
            target_audience: اطلاعات مخاطب هدف
                {
                    'type': 'B2B' | 'B2C' | 'Technical' | 'General',
                    'expertise_level': 'beginner' | 'intermediate' | 'advanced',
                    'industry': str (اختیاری),
                    'role': str (اختیاری)
                }
            user_intent: نوع Intent
                'informational' | 'commercial' | 'transactional'
            language: زبان محتوا
        
        Returns:
            محتوای شخصی‌سازی شده
        """
        try:
            # اگر OpenAI در دسترس است، از آن استفاده می‌کنیم
            if self.openai_client:
                return await self._personalize_with_ai(
                    base_content, target_audience, user_intent, language
                )
            else:
                # Fallback: استفاده از rule-based personalization
                return self._personalize_with_rules(
                    base_content, target_audience, user_intent, language
                )
                
        except Exception as e:
            logger.error(f"Error personalizing content: {str(e)}")
            # در صورت خطا، محتوای اصلی را برمی‌گردانیم
            return base_content
    
    async def _personalize_with_ai(
        self,
        base_content: str,
        target_audience: Dict[str, Any],
        user_intent: str,
        language: str
    ) -> str:
        """شخصی‌سازی با استفاده از OpenAI"""
        try:
            prompt = self._build_personalization_prompt(
                base_content, target_audience, user_intent, language
            )
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
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
                max_tokens=4000
            )
            
            personalized_content = response.choices[0].message.content
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error in AI personalization: {str(e)}")
            # Fallback به rule-based
            return self._personalize_with_rules(
                base_content, target_audience, user_intent, language
            )
    
    def _personalize_with_rules(
        self,
        base_content: str,
        target_audience: Dict[str, Any],
        user_intent: str,
        language: str
    ) -> str:
        """شخصی‌سازی با استفاده از قوانین"""
        content = base_content
        
        # شخصی‌سازی بر اساس نوع مخاطب
        audience_type = target_audience.get('type', 'General')
        content = self._adjust_for_audience_type(content, audience_type, language)
        
        # شخصی‌سازی بر اساس سطح تخصص
        expertise_level = target_audience.get('expertise_level', 'intermediate')
        content = self._adjust_for_expertise(content, expertise_level, language)
        
        # شخصی‌سازی بر اساس Intent
        content = self._adjust_for_intent(content, user_intent, language)
        
        # شخصی‌سازی بر اساس صنعت (اگر مشخص باشد)
        industry = target_audience.get('industry')
        if industry:
            content = self._adjust_for_industry(content, industry, language)
        
        return content
    
    def _adjust_for_audience_type(
        self,
        content: str,
        audience_type: str,
        language: str
    ) -> str:
        """تنظیم محتوا بر اساس نوع مخاطب"""
        
        if audience_type == 'B2B':
            # B2B: حرفه‌ای‌تر، متمرکز بر ROI و مزایای کسب‌وکار
            if language == 'fa':
                # اضافه کردن عبارات B2B
                content = self._add_b2b_elements(content, language)
            else:
                content = self._add_b2b_elements(content, language)
        
        elif audience_type == 'B2C':
            # B2C: ساده‌تر، متمرکز بر مزایای شخصی
            if language == 'fa':
                content = self._add_b2c_elements(content, language)
            else:
                content = self._add_b2c_elements(content, language)
        
        elif audience_type == 'Technical':
            # Technical: جزئیات فنی بیشتر
            if language == 'fa':
                content = self._add_technical_elements(content, language)
            else:
                content = self._add_technical_elements(content, language)
        
        # General: بدون تغییر خاص
        
        return content
    
    def _adjust_for_expertise(
        self,
        content: str,
        expertise_level: str,
        language: str
    ) -> str:
        """تنظیم محتوا بر اساس سطح تخصص"""
        
        if expertise_level == 'beginner':
            # Beginner: توضیحات بیشتر، مثال‌های ساده
            if language == 'fa':
                # اضافه کردن توضیحات مقدماتی
                intro = "در این بخش، ما به طور ساده توضیح می‌دهیم که:\n\n"
                content = intro + content
                # اضافه کردن مثال‌های ساده
                content = self._add_beginner_examples(content, language)
            else:
                intro = "In this section, we'll explain simply:\n\n"
                content = intro + content
                content = self._add_beginner_examples(content, language)
        
        elif expertise_level == 'advanced':
            # Advanced: جزئیات فنی بیشتر، فرض بر دانش قبلی
            if language == 'fa':
                # حذف توضیحات مقدماتی
                content = self._remove_basic_explanations(content, language)
                # اضافه کردن جزئیات فنی
                content = self._add_advanced_details(content, language)
            else:
                content = self._remove_basic_explanations(content, language)
                content = self._add_advanced_details(content, language)
        
        # Intermediate: بدون تغییر خاص
        
        return content
    
    def _adjust_for_intent(
        self,
        content: str,
        user_intent: str,
        language: str
    ) -> str:
        """تنظیم محتوا بر اساس Intent"""
        
        if user_intent == 'informational':
            # Informational: تمرکز بر آموزش و اطلاعات
            if language == 'fa':
                # اضافه کردن بخش‌های آموزشی
                content = self._add_informational_elements(content, language)
            else:
                content = self._add_informational_elements(content, language)
        
        elif user_intent == 'commercial':
            # Commercial: تمرکز بر مقایسه و مزایا
            if language == 'fa':
                # اضافه کردن بخش مقایسه
                content = self._add_commercial_elements(content, language)
            else:
                content = self._add_commercial_elements(content, language)
        
        elif user_intent == 'transactional':
            # Transactional: تمرکز بر CTA و اقدام
            if language == 'fa':
                # اضافه کردن CTA
                content = self._add_transactional_elements(content, language)
            else:
                content = self._add_transactional_elements(content, language)
        
        return content
    
    def _adjust_for_industry(
        self,
        content: str,
        industry: str,
        language: str
    ) -> str:
        """تنظیم محتوا بر اساس صنعت"""
        # اضافه کردن مثال‌های مرتبط با صنعت
        if language == 'fa':
            industry_examples = {
                'ecommerce': 'مثال: در فروشگاه‌های آنلاین، این تکنیک می‌تواند...',
                'healthcare': 'مثال: در صنعت سلامت، این روش می‌تواند...',
                'education': 'مثال: در آموزش آنلاین، این راهکار می‌تواند...'
            }
        else:
            industry_examples = {
                'ecommerce': 'Example: In online stores, this technique can...',
                'healthcare': 'Example: In healthcare, this method can...',
                'education': 'Example: In online education, this solution can...'
            }
        
        example = industry_examples.get(industry.lower(), '')
        if example:
            content += f"\n\n{example}"
        
        return content
    
    def _add_b2b_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر B2B"""
        if language == 'fa':
            b2b_intro = "از دیدگاه کسب‌وکار، این راهکار می‌تواند:\n"
            b2b_points = [
                "- ROI را بهبود بخشد",
                "- کارایی تیم را افزایش دهد",
                "- هزینه‌های عملیاتی را کاهش دهد"
            ]
        else:
            b2b_intro = "From a business perspective, this solution can:\n"
            b2b_points = [
                "- Improve ROI",
                "- Increase team efficiency",
                "- Reduce operational costs"
            ]
        
        # اضافه کردن در ابتدای محتوا
        b2b_section = b2b_intro + "\n".join(b2b_points) + "\n\n"
        return b2b_section + content
    
    def _add_b2c_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر B2C"""
        if language == 'fa':
            b2c_intro = "این راهکار برای شما چه مزایایی دارد:\n"
            b2c_points = [
                "- صرفه‌جویی در زمان",
                "- بهبود تجربه کاربری",
                "- دسترسی آسان‌تر"
            ]
        else:
            b2c_intro = "What benefits does this solution offer you:\n"
            b2c_points = [
                "- Save time",
                "- Improve user experience",
                "- Easier access"
            ]
        
        b2c_section = b2c_intro + "\n".join(b2c_points) + "\n\n"
        return b2c_section + content
    
    def _add_technical_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر فنی"""
        if language == 'fa':
            tech_intro = "جزئیات فنی:\n"
            tech_points = [
                "- معماری سیستم",
                "- پیاده‌سازی",
                "- بهینه‌سازی عملکرد"
            ]
        else:
            tech_intro = "Technical details:\n"
            tech_points = [
                "- System architecture",
                "- Implementation",
                "- Performance optimization"
            ]
        
        tech_section = tech_intro + "\n".join(tech_points) + "\n\n"
        return tech_section + content
    
    def _add_beginner_examples(self, content: str, language: str) -> str:
        """اضافه کردن مثال‌های مقدماتی"""
        if language == 'fa':
            example = "\n\nمثال ساده: فرض کنید می‌خواهید یک وب‌سایت راه‌اندازی کنید..."
        else:
            example = "\n\nSimple example: Let's say you want to launch a website..."
        
        return content + example
    
    def _remove_basic_explanations(self, content: str, language: str) -> str:
        """حذف توضیحات مقدماتی"""
        # حذف جملات ساده‌کننده
        if language == 'fa':
            patterns = [
                r'به طور ساده[^.]*\.',
                r'به زبان ساده[^.]*\.',
                r'در واقع[^.]*\.'
            ]
        else:
            patterns = [
                r'Simply put[^.]*\.',
                r'In simple terms[^.]*\.',
                r'Basically[^.]*\.'
            ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content
    
    def _add_advanced_details(self, content: str, language: str) -> str:
        """اضافه کردن جزئیات پیشرفته"""
        if language == 'fa':
            advanced_section = "\n\nجزئیات پیشرفته:\n"
            advanced_points = [
                "- پیاده‌سازی پیشرفته",
                "- بهینه‌سازی الگوریتم",
                "- مقیاس‌پذیری"
            ]
        else:
            advanced_section = "\n\nAdvanced details:\n"
            advanced_points = [
                "- Advanced implementation",
                "- Algorithm optimization",
                "- Scalability"
            ]
        
        return content + advanced_section + "\n".join(advanced_points)
    
    def _add_informational_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر اطلاعاتی"""
        if language == 'fa':
            info_section = "\n\nاطلاعات بیشتر:\n"
            info_points = [
                "- راهنمای کامل",
                "- نکات مهم",
                "- منابع بیشتر"
            ]
        else:
            info_section = "\n\nMore information:\n"
            info_points = [
                "- Complete guide",
                "- Important tips",
                "- Additional resources"
            ]
        
        return content + info_section + "\n".join(info_points)
    
    def _add_commercial_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر تجاری"""
        if language == 'fa':
            commercial_section = "\n\nمقایسه و مزایا:\n"
            commercial_points = [
                "- مقایسه با راهکارهای دیگر",
                "- مزایای منحصر به فرد",
                "- قیمت‌گذاری"
            ]
        else:
            commercial_section = "\n\nComparison and benefits:\n"
            commercial_points = [
                "- Comparison with other solutions",
                "- Unique advantages",
                "- Pricing"
            ]
        
        return content + commercial_section + "\n".join(commercial_points)
    
    def _add_transactional_elements(self, content: str, language: str) -> str:
        """اضافه کردن عناصر تراکنشی"""
        if language == 'fa':
            cta = "\n\nآماده شروع هستید؟ همین حالا اقدام کنید و از مزایای این راهکار بهره‌مند شوید."
        else:
            cta = "\n\nReady to get started? Take action now and benefit from this solution."
        
        return content + cta
    
    def _build_personalization_prompt(
        self,
        base_content: str,
        target_audience: Dict[str, Any],
        user_intent: str,
        language: str
    ) -> str:
        """ساخت prompt برای شخصی‌سازی با AI"""
        
        audience_type = target_audience.get('type', 'General')
        expertise_level = target_audience.get('expertise_level', 'intermediate')
        industry = target_audience.get('industry', '')
        role = target_audience.get('role', '')
        
        if language == 'fa':
            prompt = f"""شخصی‌سازی محتوای زیر بر اساس مشخصات زیر:

مخاطب هدف: {audience_type}
سطح تخصص: {expertise_level}
Intent: {user_intent}
"""
            if industry:
                prompt += f"صنعت: {industry}\n"
            if role:
                prompt += f"نقش: {role}\n"
            
            prompt += f"""
محتوای پایه:
{base_content}

لطفاً محتوا را شخصی‌سازی کنید تا:
1. مناسب مخاطب {audience_type} باشد
2. سطح تخصص {expertise_level} را در نظر بگیرد
3. Intent {user_intent} را برآورده کند
4. زبان و لحن مناسب را استفاده کند
"""
        else:
            prompt = f"""Personalize the following content based on these specifications:

Target Audience: {audience_type}
Expertise Level: {expertise_level}
Intent: {user_intent}
"""
            if industry:
                prompt += f"Industry: {industry}\n"
            if role:
                prompt += f"Role: {role}\n"
            
            prompt += f"""
Base Content:
{base_content}

Please personalize the content to:
1. Be appropriate for {audience_type} audience
2. Consider {expertise_level} expertise level
3. Fulfill {user_intent} intent
4. Use appropriate language and tone
"""
        
        return prompt
    
    def _get_system_prompt(self, language: str) -> str:
        """دریافت system prompt"""
        if language == 'fa':
            return """شما یک متخصص تولید محتوا هستید که در شخصی‌سازی محتوا تخصص دارید.
شما باید محتوا را بر اساس مخاطب، سطح تخصص و Intent شخصی‌سازی کنید.
محتوای شخصی‌سازی شده باید طبیعی، جذاب و موثر باشد."""
        else:
            return """You are a content creation expert specializing in content personalization.
You should personalize content based on audience, expertise level, and intent.
The personalized content should be natural, engaging, and effective."""

