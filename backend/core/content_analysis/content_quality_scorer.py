"""
امتیازدهی کیفیت محتوا
محاسبه معیارهای مختلف کیفیت محتوا برای SEO
"""

import logging
import re
from typing import Dict, Any, Optional, List, Set
from collections import Counter
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentQualityScorer:
    """
    کلاس امتیازدهی کیفیت محتوا
    
    معیارها:
    - SEO Score
    - Readability Score
    - Keyword Optimization Score
    - Content Depth Score
    - Uniqueness Score
    - Engagement Potential Score
    """
    
    def __init__(self):
        self.semantic_analyzer = None
        
        # سعی می‌کنیم Semantic Analyzer را بارگذاری کنیم
        try:
            from ..keyword_research.semantic_analyzer import SemanticKeywordAnalyzer
            self.semantic_analyzer = SemanticKeywordAnalyzer()
            if not self.semantic_analyzer.model_loaded:
                logger.warning("Semantic model not loaded. Uniqueness scoring will use fallback methods.")
        except Exception as e:
            logger.warning(f"Could not load SemanticKeywordAnalyzer: {str(e)}")
    
    def score_content(
        self,
        content: str,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        meta_description: Optional[str] = None,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        امتیازدهی کیفیت محتوا
        
        Args:
            content: محتوای متنی
            keyword: کلمه کلیدی اصلی
            keyword_metrics: معیارهای کلمه کلیدی
            title: عنوان (اختیاری)
            meta_description: Meta Description (اختیاری)
            language: زبان
        
        Returns:
            {
                'overall_score': float,
                'seo_score': float,
                'readability_score': float,
                'keyword_optimization': float,
                'content_depth': float,
                'uniqueness': float,
                'engagement_potential': float,
                'recommendations': List[str],
                'breakdown': Dict
            }
        """
        try:
            # استخراج اطلاعات از محتوا
            content_info = self._extract_content_info(content, title, meta_description)
            
            # محاسبه معیارها
            seo_score = self._calculate_seo_score(content_info, keyword, keyword_metrics)
            readability_score = self._calculate_readability_score(content, language)
            keyword_optimization = self._calculate_keyword_optimization(
                content_info,
                content,
                keyword,
                keyword_metrics
            )
            content_depth = self._calculate_content_depth(content_info, content)
            uniqueness = self._calculate_uniqueness(content, keyword, language)
            engagement_potential = self._calculate_engagement_potential(content_info, content)
            
            # محاسبه Overall Score
            overall_score = self._calculate_overall_score(
                seo_score,
                readability_score,
                keyword_optimization,
                content_depth,
                uniqueness,
                engagement_potential
            )
            
            # تولید توصیه‌ها
            recommendations = self._generate_recommendations(
                overall_score,
                seo_score,
                readability_score,
                keyword_optimization,
                content_depth,
                uniqueness,
                engagement_potential,
                content_info,
                keyword,
                language
            )
            
            return {
                'overall_score': round(overall_score, 1),
                'seo_score': round(seo_score, 1),
                'readability_score': round(readability_score, 1),
                'keyword_optimization': round(keyword_optimization, 1),
                'content_depth': round(content_depth, 1),
                'uniqueness': round(uniqueness, 1),
                'engagement_potential': round(engagement_potential, 1),
                'recommendations': recommendations,
                'breakdown': {
                    'word_count': content_info.get('word_count', 0),
                    'heading_count': content_info.get('heading_count', 0),
                    'paragraph_count': content_info.get('paragraph_count', 0),
                    'image_count': content_info.get('image_count', 0),
                    'link_count': content_info.get('link_count', 0),
                    'has_title': content_info.get('has_title', False),
                    'has_meta_description': content_info.get('has_meta_description', False),
                    'has_h1': content_info.get('has_h1', False),
                    'has_faq': content_info.get('has_faq', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error scoring content: {str(e)}")
            return self._empty_score_result()
    
    def _extract_content_info(
        self,
        content: str,
        title: Optional[str],
        meta_description: Optional[str]
    ) -> Dict[str, Any]:
        """استخراج اطلاعات از محتوا"""
        info = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'heading_count': 0,
            'h1_count': 0,
            'h2_count': 0,
            'h3_count': 0,
            'paragraph_count': len(re.split(r'\n\s*\n', content)),
            'image_count': 0,
            'link_count': 0,
            'has_title': title is not None and len(title) > 0,
            'has_meta_description': meta_description is not None and len(meta_description) > 0,
            'has_h1': False,
            'has_faq': False,
            'title': title or '',
            'meta_description': meta_description or ''
        }
        
        # استخراج Headings
        h1_matches = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        h2_matches = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        h3_matches = re.findall(r'^###\s+(.+)$', content, re.MULTILINE)
        
        info['h1_count'] = len(h1_matches)
        info['h2_count'] = len(h2_matches)
        info['h3_count'] = len(h3_matches)
        info['heading_count'] = info['h1_count'] + info['h2_count'] + info['h3_count']
        info['has_h1'] = info['h1_count'] > 0
        
        # استخراج تصاویر
        image_matches = re.findall(r'!\[.*?\]\(.*?\)', content)
        info['image_count'] = len(image_matches)
        
        # استخراج لینک‌ها
        link_matches = re.findall(r'\[.*?\]\(.*?\)', content)
        info['link_count'] = len(link_matches)
        
        # بررسی وجود FAQ
        faq_patterns = [
            r'FAQ|سوالات متداول|Frequently Asked Questions',
            r'###\s+.*\?',
            r'Q:\s*|سوال:'
        ]
        for pattern in faq_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                info['has_faq'] = True
                break
        
        return info
    
    def _calculate_seo_score(
        self,
        content_info: Dict[str, Any],
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]]
    ) -> float:
        """محاسبه SEO Score"""
        score = 0.0
        
        # فاکتور 1: Title (15%)
        if content_info.get('has_title'):
            title = content_info.get('title', '')
            if 30 <= len(title) <= 60:
                score += 15
            elif 20 <= len(title) < 30 or 60 < len(title) <= 70:
                score += 12
            else:
                score += 8
            
            # استفاده از کلمه کلیدی در Title
            if keyword.lower() in title.lower():
                score += 5  # Bonus
        else:
            score += 0
        
        # فاکتور 2: Meta Description (10%)
        if content_info.get('has_meta_description'):
            meta_desc = content_info.get('meta_description', '')
            if 120 <= len(meta_desc) <= 160:
                score += 10
            elif 100 <= len(meta_desc) < 120 or 160 < len(meta_desc) <= 180:
                score += 7
            else:
                score += 5
            
            # استفاده از کلمه کلیدی در Meta Description
            if keyword.lower() in meta_desc.lower():
                score += 3  # Bonus
        else:
            score += 0
        
        # فاکتور 3: H1 (10%)
        if content_info.get('has_h1'):
            score += 10
        else:
            score += 0
        
        # فاکتور 4: Headings Structure (15%)
        heading_count = content_info.get('heading_count', 0)
        if heading_count >= 5:
            score += 15
        elif heading_count >= 3:
            score += 12
        elif heading_count >= 1:
            score += 8
        else:
            score += 3
        
        # فاکتور 5: Content Length (15%)
        word_count = content_info.get('word_count', 0)
        if word_count >= 2000:
            score += 15
        elif word_count >= 1500:
            score += 12
        elif word_count >= 1000:
            score += 10
        elif word_count >= 500:
            score += 7
        else:
            score += 3
        
        # فاکتور 6: Images (10%)
        image_count = content_info.get('image_count', 0)
        if image_count >= 3:
            score += 10
        elif image_count >= 2:
            score += 7
        elif image_count >= 1:
            score += 5
        else:
            score += 2
        
        # فاکتور 7: Internal Links (10%)
        link_count = content_info.get('link_count', 0)
        if link_count >= 5:
            score += 10
        elif link_count >= 3:
            score += 7
        elif link_count >= 1:
            score += 5
        else:
            score += 2
        
        # فاکتور 8: FAQ (10%)
        if content_info.get('has_faq'):
            score += 10
        else:
            score += 0
        
        # فاکتور 9: Keyword in First Paragraph (5%)
        first_paragraph = content.split('\n\n')[0] if content else ''
        if keyword.lower() in first_paragraph.lower():
            score += 5
        
        return min(score, 100.0)
    
    def _calculate_readability_score(
        self,
        content: str,
        language: str
    ) -> float:
        """محاسبه Readability Score"""
        if not content:
            return 0.0
        
        sentences = re.split(r'[.!?]\s+', content)
        words = content.split()
        
        if len(sentences) == 0:
            return 0.0
        
        # میانگین طول جمله
        avg_sentence_length = len(words) / len(sentences)
        
        # میانگین طول کلمه
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # محاسبه Readability (Flesch Reading Ease تقریبی)
        if language == 'fa':
            # برای فارسی، محاسبه ساده‌تر
            if avg_sentence_length <= 15:
                readability = 90
            elif avg_sentence_length <= 20:
                readability = 80
            elif avg_sentence_length <= 25:
                readability = 70
            elif avg_sentence_length <= 30:
                readability = 60
            else:
                readability = 50
        else:
            # Flesch Reading Ease (تقریبی)
            asl = avg_sentence_length
            asw = avg_word_length
            
            # فرمول ساده شده
            readability = 206.835 - (1.015 * asl) - (84.6 * (asw / 100))
            readability = max(0, min(100, readability))
        
        return round(readability, 1)
    
    def _calculate_keyword_optimization(
        self,
        content_info: Dict[str, Any],
        content: str,
        keyword: str,
        keyword_metrics: Optional[Dict[str, Any]]
    ) -> float:
        """محاسبه Keyword Optimization Score"""
        score = 0.0
        
        if not content:
            word_count = content_info.get('word_count', 0)
            if word_count == 0:
                return 0.0
        else:
            word_count = len(content.split())
        
        # فاکتور 1: Keyword Density (40%)
        keyword_lower = keyword.lower()
        words = content.lower().split() if content else []
        keyword_count = sum(1 for word in words if keyword_lower in word)
        
        if word_count > 0:
            density = (keyword_count / word_count) * 100
            
            if 1.0 <= density <= 2.5:
                score += 40  # ایده‌آل
            elif 0.5 <= density < 1.0 or 2.5 < density <= 3.5:
                score += 30  # قابل قبول
            elif 0.2 <= density < 0.5 or 3.5 < density <= 4.5:
                score += 20  # نیاز به بهبود
            else:
                score += 10  # ضعیف
        
        # فاکتور 2: Keyword in Title (20%)
        title = content_info.get('title', '')
        if keyword_lower in title.lower():
            score += 20
        else:
            score += 0
        
        # فاکتور 3: Keyword in Meta Description (15%)
        meta_desc = content_info.get('meta_description', '')
        if keyword_lower in meta_desc.lower():
            score += 15
        else:
            score += 0
        
        # فاکتور 4: Keyword in H1 (15%)
        if content_info.get('has_h1'):
            # فرض می‌کنیم H1 شامل keyword است اگر title شامل آن باشد
            if keyword_lower in title.lower():
                score += 15
        else:
            score += 0
        
        # فاکتور 5: Keyword in First Paragraph (10%)
        if content:
            first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content.split('\n')[0]
            if keyword_lower in first_paragraph.lower():
                score += 10
        
        return min(score, 100.0)
    
    def _calculate_content_depth(
        self,
        content_info: Dict[str, Any],
        content: str
    ) -> float:
        """محاسبه Content Depth Score"""
        score = 0.0
        
        # فاکتور 1: Word Count (30%)
        word_count = content_info.get('word_count', 0)
        if word_count >= 2000:
            score += 30
        elif word_count >= 1500:
            score += 25
        elif word_count >= 1000:
            score += 20
        elif word_count >= 500:
            score += 15
        else:
            score += 10
        
        # فاکتور 2: Heading Structure (25%)
        heading_count = content_info.get('heading_count', 0)
        if heading_count >= 8:
            score += 25
        elif heading_count >= 5:
            score += 20
        elif heading_count >= 3:
            score += 15
        elif heading_count >= 1:
            score += 10
        else:
            score += 5
        
        # فاکتور 3: Paragraphs (15%)
        paragraph_count = content_info.get('paragraph_count', 0)
        if paragraph_count >= 10:
            score += 15
        elif paragraph_count >= 7:
            score += 12
        elif paragraph_count >= 5:
            score += 10
        elif paragraph_count >= 3:
            score += 7
        else:
            score += 5
        
        # فاکتور 4: Images (15%)
        image_count = content_info.get('image_count', 0)
        if image_count >= 5:
            score += 15
        elif image_count >= 3:
            score += 12
        elif image_count >= 2:
            score += 10
        elif image_count >= 1:
            score += 7
        else:
            score += 3
        
        # فاکتور 5: Links (10%)
        link_count = content_info.get('link_count', 0)
        if link_count >= 5:
            score += 10
        elif link_count >= 3:
            score += 8
        elif link_count >= 1:
            score += 5
        else:
            score += 2
        
        # فاکتور 6: FAQ (5%)
        if content_info.get('has_faq'):
            score += 5
        
        return min(score, 100.0)
    
    def _calculate_uniqueness(
        self,
        content: str,
        keyword: str,
        language: str
    ) -> float:
        """محاسبه Uniqueness Score"""
        if not content:
            return 0.0
        
        score = 100.0  # شروع از 100
        
        # فاکتور 1: طول محتوا (هرچه طولانی‌تر، منحصر به فردتر)
        word_count = len(content.split())
        if word_count < 500:
            score -= 20  # محتوای کوتاه معمولاً کمتر منحصر به فرد است
        elif word_count >= 2000:
            score += 10  # محتوای طولانی معمولاً منحصر به فردتر است
        
        # فاکتور 2: تنوع کلمات
        words = content.lower().split()
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words) if words else 0
        
        if diversity_ratio >= 0.7:
            score += 10  # تنوع بالا
        elif diversity_ratio >= 0.5:
            score += 5
        elif diversity_ratio < 0.3:
            score -= 15  # تکرار زیاد
        
        # فاکتور 3: استفاده از Semantic Analysis (اگر موجود باشد)
        if self.semantic_analyzer and self.semantic_analyzer.model_loaded:
            # این یک تخمین است - در حالت واقعی باید با محتوای دیگر مقایسه شود
            # برای حال حاضر، بر اساس ساختار محتوا قضاوت می‌کنیم
            pass
        
        # فاکتور 4: وجود عناصر منحصر به فرد
        if re.search(r'FAQ|سوالات متداول', content, re.IGNORECASE):
            score += 5
        
        # شمارش تصاویر و لینک‌ها از محتوا
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        if image_count > 0:
            score += 5
        
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
        if link_count > 3:
            score += 5
        
        return max(0, min(100, score))
    
    def _calculate_engagement_potential(
        self,
        content_info: Dict[str, Any],
        content: str
    ) -> float:
        """محاسبه Engagement Potential Score"""
        score = 0.0
        
        # فاکتور 1: وجود سوالات (20%)
        question_count = len(re.findall(r'\?', content))
        if question_count >= 5:
            score += 20
        elif question_count >= 3:
            score += 15
        elif question_count >= 1:
            score += 10
        
        # فاکتور 2: وجود Call-to-Action (20%)
        cta_patterns = [
            r'خرید|buy|order|register|sign up|ثبت نام',
            r'دانلود|download|get started|شروع کنید',
            r'تماس|contact|call|راهنمایی'
        ]
        for pattern in cta_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 7
                break
        
        # فاکتور 3: وجود لیست‌ها (15%)
        list_patterns = [
            r'^\s*[-*•]\s+',  # Bullet lists
            r'^\s*\d+\.\s+',  # Numbered lists
            r'<ul>|<ol>'  # HTML lists
        ]
        list_count = sum(1 for pattern in list_patterns if re.search(pattern, content, re.MULTILINE))
        if list_count >= 2:
            score += 15
        elif list_count >= 1:
            score += 10
        
        # فاکتور 4: وجود تصاویر (15%)
        image_count = content_info.get('image_count', 0)
        if image_count >= 3:
            score += 15
        elif image_count >= 2:
            score += 12
        elif image_count >= 1:
            score += 8
        
        # فاکتور 5: وجود لینک‌ها (15%)
        link_count = content_info.get('link_count', 0)
        if link_count >= 5:
            score += 15
        elif link_count >= 3:
            score += 12
        elif link_count >= 1:
            score += 8
        
        # فاکتور 6: وجود FAQ (15%)
        if content_info.get('has_faq'):
            score += 15
        
        return min(score, 100.0)
    
    def _calculate_overall_score(
        self,
        seo_score: float,
        readability_score: float,
        keyword_optimization: float,
        content_depth: float,
        uniqueness: float,
        engagement_potential: float
    ) -> float:
        """محاسبه Overall Score"""
        # وزن‌دهی معیارها
        weights = {
            'seo_score': 0.25,
            'readability_score': 0.15,
            'keyword_optimization': 0.20,
            'content_depth': 0.20,
            'uniqueness': 0.10,
            'engagement_potential': 0.10
        }
        
        overall = (
            seo_score * weights['seo_score'] +
            readability_score * weights['readability_score'] +
            keyword_optimization * weights['keyword_optimization'] +
            content_depth * weights['content_depth'] +
            uniqueness * weights['uniqueness'] +
            engagement_potential * weights['engagement_potential']
        )
        
        return overall
    
    def _generate_recommendations(
        self,
        overall_score: float,
        seo_score: float,
        readability_score: float,
        keyword_optimization: float,
        content_depth: float,
        uniqueness: float,
        engagement_potential: float,
        content_info: Dict[str, Any],
        keyword: str,
        language: str
    ) -> List[str]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        if language == 'fa':
            # توصیه‌های کلی
            if overall_score < 70:
                recommendations.append("امتیاز کلی محتوا پایین است. محتوا را بهبود دهید.")
            
            # توصیه‌های SEO
            if seo_score < 70:
                recommendations.append("SEO Score پایین است. تگ‌های SEO را بهبود دهید.")
            
            if not content_info.get('has_title'):
                recommendations.append("عنوان (Title) اضافه کنید.")
            
            if not content_info.get('has_meta_description'):
                recommendations.append("Meta Description اضافه کنید.")
            
            if not content_info.get('has_h1'):
                recommendations.append("H1 اضافه کنید.")
            
            # توصیه‌های Readability
            if readability_score < 60:
                recommendations.append("Readability پایین است. جملات را کوتاه‌تر کنید.")
            
            # توصیه‌های Keyword Optimization
            if keyword_optimization < 70:
                recommendations.append("Keyword Optimization پایین است. از کلمه کلیدی بیشتر استفاده کنید.")
            
            # توصیه‌های Content Depth
            if content_depth < 70:
                word_count = content_info.get('word_count', 0)
                if word_count < 1000:
                    recommendations.append(f"محتوای شما {word_count} کلمه است. حداقل 1000 کلمه توصیه می‌شود.")
                
                heading_count = content_info.get('heading_count', 0)
                if heading_count < 3:
                    recommendations.append("Headings بیشتری اضافه کنید (حداقل 3).")
            
            # توصیه‌های Engagement
            if engagement_potential < 60:
                if content_info.get('image_count', 0) == 0:
                    recommendations.append("تصاویر اضافه کنید.")
                
                if not content_info.get('has_faq'):
                    recommendations.append("بخش FAQ اضافه کنید.")
        else:
            # English recommendations
            if overall_score < 70:
                recommendations.append("Overall content score is low. Improve the content.")
            
            if seo_score < 70:
                recommendations.append("SEO Score is low. Improve SEO tags.")
            
            if not content_info.get('has_title'):
                recommendations.append("Add a title.")
            
            if not content_info.get('has_meta_description'):
                recommendations.append("Add meta description.")
            
            if readability_score < 60:
                recommendations.append("Readability is low. Use shorter sentences.")
            
            if keyword_optimization < 70:
                recommendations.append("Keyword optimization is low. Use keyword more naturally.")
        
        return recommendations
    
    def _empty_score_result(self) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'overall_score': 0.0,
            'seo_score': 0.0,
            'readability_score': 0.0,
            'keyword_optimization': 0.0,
            'content_depth': 0.0,
            'uniqueness': 0.0,
            'engagement_potential': 0.0,
            'recommendations': ['Content not available'],
            'breakdown': {}
        }

