"""
تحلیل فاصله محتوا (Content Gap Analysis)
شناسایی موضوعات، زوایا و انواع محتوای موجود در رقبا اما نه در سایت شما
"""

import logging
from typing import Dict, Any, List, Optional, Set
from collections import Counter
import re

logger = logging.getLogger(__name__)


class ContentGapAnalyzer:
    """
    کلاس تحلیل فاصله محتوا
    
    تحلیل:
    - موضوعاتی که رقبا پوشش داده‌اند اما شما نکرده‌اید
    - زوایای مختلف یک موضوع
    - عمق محتوا
    - انواع محتوا (مقاله، ویدیو، اینفوگرافیک)
    """
    
    def __init__(self):
        self.semantic_analyzer = None
        
        # سعی می‌کنیم Semantic Analyzer را بارگذاری کنیم
        try:
            from ..keyword_research.semantic_analyzer import SemanticKeywordAnalyzer
            self.semantic_analyzer = SemanticKeywordAnalyzer()
            if not self.semantic_analyzer.model_loaded:
                logger.warning("Semantic model not loaded. Content gap analysis will use fallback methods.")
        except Exception as e:
            logger.warning(f"Could not load SemanticKeywordAnalyzer: {str(e)}")
    
    async def analyze_content_gaps(
        self,
        site_content: Dict[str, Any],
        competitor_content: List[Dict[str, Any]],
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        تحلیل فاصله محتوا
        
        Args:
            site_content: محتوای سایت شما
                {
                    'articles': List[Dict],  # مقالات
                    'topics': List[str],      # موضوعات
                    'content_types': List[str]  # انواع محتوا
                }
            competitor_content: لیست محتوای رقبا
                [
                    {
                        'title': str,
                        'content': str,
                        'url': str,
                        'content_type': str,  # article, video, infographic
                        'topics': List[str],
                        'word_count': int
                    },
                    ...
                ]
            language: زبان
        
        Returns:
            {
                'topic_gaps': List[Dict],      # موضوعات موجود در رقبا اما نه در شما
                'angle_gaps': List[Dict],       # زوایای مختلف یک موضوع
                'depth_gaps': List[Dict],       # تفاوت عمق محتوا
                'content_type_gaps': List[Dict], # انواع محتوای موجود در رقبا
                'recommendations': List[str],   # پیشنهادات
                'summary': Dict
            }
        """
        try:
            # استخراج موضوعات
            your_topics = self._extract_topics(site_content, language)
            competitor_topics = self._extract_competitor_topics(competitor_content, language)
            
            # تحلیل فاصله موضوعات
            topic_gaps = self._analyze_topic_gaps(your_topics, competitor_topics, language)
            
            # تحلیل زوایا
            angle_gaps = self._analyze_angle_gaps(site_content, competitor_content, language)
            
            # تحلیل عمق
            depth_gaps = self._analyze_depth_gaps(site_content, competitor_content, language)
            
            # تحلیل انواع محتوا
            content_type_gaps = self._analyze_content_type_gaps(site_content, competitor_content)
            
            # تولید پیشنهادات
            recommendations = self._generate_recommendations(
                topic_gaps,
                angle_gaps,
                depth_gaps,
                content_type_gaps,
                language
            )
            
            # محاسبه خلاصه
            summary = self._calculate_summary(
                topic_gaps,
                angle_gaps,
                depth_gaps,
                content_type_gaps
            )
            
            return {
                'topic_gaps': topic_gaps,
                'angle_gaps': angle_gaps,
                'depth_gaps': depth_gaps,
                'content_type_gaps': content_type_gaps,
                'recommendations': recommendations,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content gaps: {str(e)}")
            return self._empty_gap_result()
    
    def _extract_topics(
        self,
        site_content: Dict[str, Any],
        language: str
    ) -> Set[str]:
        """استخراج موضوعات از محتوای سایت شما"""
        topics = set()
        
        # از مقالات
        articles = site_content.get('articles', [])
        for article in articles:
            article_topics = article.get('topics', [])
            topics.update(article_topics)
            
            # استخراج از عنوان
            title = article.get('title', '')
            if title:
                title_words = self._extract_keywords_from_text(title, language)
                topics.update(title_words)
        
        # از لیست موضوعات مستقیم
        direct_topics = site_content.get('topics', [])
        topics.update(direct_topics)
        
        return topics
    
    def _extract_competitor_topics(
        self,
        competitor_content: List[Dict[str, Any]],
        language: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """استخراج موضوعات از محتوای رقبا"""
        topic_map = {}
        
        for content_item in competitor_content:
            # استخراج از عنوان
            title = content_item.get('title', '')
            title_topics = self._extract_keywords_from_text(title, language)
            
            # استخراج از محتوا
            content_text = content_item.get('content', '')
            content_topics = self._extract_keywords_from_text(content_text[:1000], language)  # 1000 کاراکتر اول
            
            # ترکیب موضوعات
            all_topics = set(title_topics) | set(content_topics)
            
            # اضافه کردن موضوعات مستقیم
            direct_topics = content_item.get('topics', [])
            all_topics.update(direct_topics)
            
            # ذخیره در map
            for topic in all_topics:
                if topic not in topic_map:
                    topic_map[topic] = []
                topic_map[topic].append(content_item)
        
        return topic_map
    
    def _extract_keywords_from_text(
        self,
        text: str,
        language: str
    ) -> List[str]:
        """استخراج کلمات کلیدی از متن"""
        if not text:
            return []
        
        # تبدیل به lowercase
        text_lower = text.lower()
        
        # حذف علائم نگارشی
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        
        # تقسیم به کلمات
        words = text_clean.split()
        
        # فیلتر کردن stop words
        stop_words = {
            'fa': {'و', 'در', 'به', 'از', 'که', 'این', 'است', 'را', 'یک', 'آن', 'ها', 'می', 'شود', 'برای', 'با', 'تا'},
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        }
        
        stop_words_set = stop_words.get(language, stop_words['en'])
        filtered_words = [w for w in words if w not in stop_words_set and len(w) > 2]
        
        # شمارش و انتخاب کلمات پرتکرار
        word_freq = Counter(filtered_words)
        
        # انتخاب کلمات با تکرار >= 2
        keywords = [word for word, count in word_freq.items() if count >= 2]
        
        return keywords[:20]  # حداکثر 20 کلمه کلیدی
    
    def _analyze_topic_gaps(
        self,
        your_topics: Set[str],
        competitor_topics: Dict[str, List[Dict[str, Any]]],
        language: str
    ) -> List[Dict[str, Any]]:
        """تحلیل فاصله موضوعات"""
        gaps = []
        
        your_topics_lower = {t.lower() for t in your_topics}
        
        for topic, content_items in competitor_topics.items():
            topic_lower = topic.lower()
            
            # بررسی اینکه آیا این موضوع در محتوای شما وجود دارد
            if topic_lower not in your_topics_lower:
                # بررسی similarity با semantic analyzer
                similarity_score = 0.0
                if self.semantic_analyzer and self.semantic_analyzer.model_loaded:
                    # بررسی similarity با تمام موضوعات شما
                    for your_topic in your_topics:
                        try:
                            relationship = self.semantic_analyzer.get_semantic_relationship(
                                topic,
                                your_topic
                            )
                            similarity_score = max(similarity_score, relationship.get('similarity', 0.0))
                        except:
                            pass
                
                # اگر similarity کم باشد، یک gap است
                if similarity_score < 0.6:
                    # محاسبه اهمیت
                    importance = self._calculate_topic_importance(topic, content_items)
                    
                    gaps.append({
                        'topic': topic,
                        'importance': importance,
                        'competitor_count': len(content_items),
                        'content_items': content_items[:5],  # 5 مورد اول
                        'similarity_score': similarity_score,
                        'gap_type': 'topic'
                    })
        
        # مرتب‌سازی بر اساس اهمیت
        gaps.sort(key=lambda x: x['importance'], reverse=True)
        
        return gaps[:50]  # 50 gap برتر
    
    def _calculate_topic_importance(
        self,
        topic: str,
        content_items: List[Dict[str, Any]]
    ) -> float:
        """محاسبه اهمیت موضوع"""
        score = 0.0
        
        # فاکتور 1: تعداد محتوا (40%)
        count = len(content_items)
        if count >= 5:
            score += 40
        elif count >= 3:
            score += 30
        elif count >= 2:
            score += 20
        else:
            score += 10
        
        # فاکتور 2: میانگین طول محتوا (30%)
        avg_length = sum(
            item.get('word_count', 0) for item in content_items
        ) / len(content_items) if content_items else 0
        
        if avg_length >= 2000:
            score += 30
        elif avg_length >= 1500:
            score += 25
        elif avg_length >= 1000:
            score += 20
        else:
            score += 10
        
        # فاکتور 3: تنوع انواع محتوا (30%)
        content_types = set(item.get('content_type', 'article') for item in content_items)
        type_count = len(content_types)
        
        if type_count >= 3:
            score += 30
        elif type_count >= 2:
            score += 20
        else:
            score += 10
        
        return min(score, 100.0)
    
    def _analyze_angle_gaps(
        self,
        site_content: Dict[str, Any],
        competitor_content: List[Dict[str, Any]],
        language: str
    ) -> List[Dict[str, Any]]:
        """تحلیل فاصله زوایا"""
        gaps = []
        
        # استخراج زوایای رقبا
        competitor_angles = {}
        
        for content_item in competitor_content:
            title = content_item.get('title', '')
            content = content_item.get('content', '')
            
            # شناسایی زاویه از عنوان و محتوا
            angle = self._identify_content_angle(title, content, language)
            
            if angle:
                if angle not in competitor_angles:
                    competitor_angles[angle] = []
                competitor_angles[angle].append(content_item)
        
        # استخراج زوایای شما
        your_angles = set()
        articles = site_content.get('articles', [])
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            angle = self._identify_content_angle(title, content, language)
            if angle:
                your_angles.add(angle)
        
        # پیدا کردن زوایای موجود در رقبا اما نه در شما
        for angle, content_items in competitor_angles.items():
            if angle not in your_angles:
                gaps.append({
                    'angle': angle,
                    'importance': len(content_items),
                    'competitor_count': len(content_items),
                    'content_items': content_items[:3],
                    'gap_type': 'angle'
                })
        
        # مرتب‌سازی
        gaps.sort(key=lambda x: x['importance'], reverse=True)
        
        return gaps[:30]  # 30 gap برتر
    
    def _identify_content_angle(
        self,
        title: str,
        content: str,
        language: str
    ) -> Optional[str]:
        """شناسایی زاویه محتوا"""
        text = f"{title} {content[:200]}".lower()
        
        # الگوهای زاویه
        angle_patterns = {
            'fa': {
                'how_to': ['چگونه', 'راهنمای', 'آموزش', 'نحوه'],
                'what_is': ['چیست', 'چیست؟', 'معنی', 'تعریف'],
                'best': ['بهترین', 'برترین', 'عالی'],
                'comparison': ['مقایسه', 'تفاوت', 'مقایسه بین'],
                'review': ['نقد', 'بررسی', 'نقد و بررسی'],
                'guide': ['راهنمای', 'گام به گام', 'مراحل'],
                'tips': ['نکات', 'توصیه', 'راهکار'],
                'mistakes': ['اشتباهات', 'خطاها', 'مشکلات']
            },
            'en': {
                'how_to': ['how to', 'guide', 'tutorial', 'step by step'],
                'what_is': ['what is', 'definition', 'meaning'],
                'best': ['best', 'top', 'greatest'],
                'comparison': ['compare', 'vs', 'difference', 'versus'],
                'review': ['review', 'analysis'],
                'guide': ['guide', 'complete guide'],
                'tips': ['tips', 'tricks', 'advice'],
                'mistakes': ['mistakes', 'errors', 'common mistakes']
            }
        }
        
        patterns = angle_patterns.get(language, angle_patterns['en'])
        
        for angle_type, keywords in patterns.items():
            if any(keyword in text for keyword in keywords):
                return angle_type
        
        return None
    
    def _analyze_depth_gaps(
        self,
        site_content: Dict[str, Any],
        competitor_content: List[Dict[str, Any]],
        language: str
    ) -> List[Dict[str, Any]]:
        """تحلیل فاصله عمق محتوا"""
        gaps = []
        
        # محاسبه میانگین عمق محتوای شما
        your_articles = site_content.get('articles', [])
        your_avg_depth = self._calculate_average_depth(your_articles)
        
        # محاسبه عمق محتوای رقبا
        competitor_avg_depth = self._calculate_average_depth(competitor_content)
        
        # محاسبه تفاوت
        depth_difference = competitor_avg_depth - your_avg_depth
        
        if depth_difference > 0:
            # رقبا عمیق‌تر هستند
            gaps.append({
                'gap_type': 'depth',
                'your_average_depth': your_avg_depth,
                'competitor_average_depth': competitor_avg_depth,
                'difference': depth_difference,
                'recommendation': 'افزایش عمق محتوا' if language == 'fa' else 'Increase content depth'
            })
        
        # تحلیل عمق برای موضوعات مشترک
        common_topics = self._find_common_topics(site_content, competitor_content)
        
        for topic in common_topics[:10]:  # 10 موضوع اول
            your_depth = self._calculate_topic_depth(topic, your_articles)
            competitor_depth = self._calculate_topic_depth(topic, competitor_content)
            
            if competitor_depth > your_depth * 1.2:  # 20% عمیق‌تر
                gaps.append({
                    'gap_type': 'topic_depth',
                    'topic': topic,
                    'your_depth': your_depth,
                    'competitor_depth': competitor_depth,
                    'difference': competitor_depth - your_depth
                })
        
        return gaps
    
    def _calculate_average_depth(
        self,
        content_items: List[Dict[str, Any]]
    ) -> float:
        """محاسبه میانگین عمق محتوا"""
        if not content_items:
            return 0.0
        
        depths = []
        
        for item in content_items:
            # عمق بر اساس:
            # 1. طول محتوا (40%)
            word_count = item.get('word_count', 0)
            word_score = min(word_count / 2000, 1.0) * 40
            
            # 2. تعداد headings (30%)
            headings = item.get('headings', [])
            heading_score = min(len(headings) / 10, 1.0) * 30
            
            # 3. وجود FAQ (15%)
            has_faq = item.get('has_faq', False)
            faq_score = 15 if has_faq else 0
            
            # 4. وجود تصاویر/ویدیو (15%)
            has_media = item.get('has_images', False) or item.get('has_video', False)
            media_score = 15 if has_media else 0
            
            depth = word_score + heading_score + faq_score + media_score
            depths.append(depth)
        
        return sum(depths) / len(depths) if depths else 0.0
    
    def _calculate_topic_depth(
        self,
        topic: str,
        content_items: List[Dict[str, Any]]
    ) -> float:
        """محاسبه عمق برای یک موضوع خاص"""
        topic_items = [
            item for item in content_items
            if topic.lower() in item.get('title', '').lower() or
               topic.lower() in item.get('content', '').lower()[:500]
        ]
        
        return self._calculate_average_depth(topic_items)
    
    def _find_common_topics(
        self,
        site_content: Dict[str, Any],
        competitor_content: List[Dict[str, Any]]
    ) -> List[str]:
        """پیدا کردن موضوعات مشترک"""
        your_topics = self._extract_topics(site_content, 'en')
        competitor_topics = set(self._extract_competitor_topics(competitor_content, 'en').keys())
        
        common = your_topics & competitor_topics
        return list(common)
    
    def _analyze_content_type_gaps(
        self,
        site_content: Dict[str, Any],
        competitor_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """تحلیل فاصله انواع محتوا"""
        gaps = []
        
        # استخراج انواع محتوای شما
        your_content_types = set(site_content.get('content_types', []))
        
        # استخراج انواع محتوای رقبا
        competitor_content_types = set()
        for content_item in competitor_content:
            content_type = content_item.get('content_type', 'article')
            competitor_content_types.add(content_type)
        
        # پیدا کردن انواع محتوای موجود در رقبا اما نه در شما
        missing_types = competitor_content_types - your_content_types
        
        for content_type in missing_types:
            # شمارش تعداد این نوع محتوا در رقبا
            count = sum(
                1 for item in competitor_content
                if item.get('content_type') == content_type
            )
            
            gaps.append({
                'content_type': content_type,
                'competitor_count': count,
                'your_count': 0,
                'gap_type': 'content_type',
                'importance': count
            })
        
        # تحلیل تفاوت در تعداد
        for content_type in your_content_types & competitor_content_types:
            your_count = sum(
                1 for item in site_content.get('articles', [])
                if item.get('content_type') == content_type
            )
            competitor_count = sum(
                1 for item in competitor_content
                if item.get('content_type') == content_type
            )
            
            if competitor_count > your_count * 1.5:  # 50% بیشتر
                gaps.append({
                    'content_type': content_type,
                    'competitor_count': competitor_count,
                    'your_count': your_count,
                    'gap_type': 'content_type_quantity',
                    'importance': competitor_count - your_count
                })
        
        # مرتب‌سازی
        gaps.sort(key=lambda x: x['importance'], reverse=True)
        
        return gaps
    
    def _generate_recommendations(
        self,
        topic_gaps: List[Dict[str, Any]],
        angle_gaps: List[Dict[str, Any]],
        depth_gaps: List[Dict[str, Any]],
        content_type_gaps: List[Dict[str, Any]],
        language: str
    ) -> List[str]:
        """تولید پیشنهادات"""
        recommendations = []
        
        if language == 'fa':
            # پیشنهادات بر اساس topic gaps
            if topic_gaps:
                high_importance = [gap for gap in topic_gaps if gap.get('importance', 0) >= 70]
                if high_importance:
                    recommendations.append(
                        f"✅ {len(high_importance)} موضوع با اهمیت بالا شناسایی شد. "
                        f"پیشنهاد می‌شود محتوا برای این موضوعات تولید کنید."
                    )
                
                recommendations.append(
                    f"📝 {len(topic_gaps)} موضوع که رقبا پوشش داده‌اند اما شما نکرده‌اید. "
                    f"این فرصت‌ها را در اولویت قرار دهید."
                )
            
            # پیشنهادات بر اساس angle gaps
            if angle_gaps:
                recommendations.append(
                    f"🎯 {len(angle_gaps)} زاویه مختلف شناسایی شد. "
                    f"روی زوایای مختلف موضوعات تمرکز کنید."
                )
            
            # پیشنهادات بر اساس depth gaps
            if depth_gaps:
                depth_gap = next((g for g in depth_gaps if g.get('gap_type') == 'depth'), None)
                if depth_gap:
                    recommendations.append(
                        f"📊 عمق محتوای رقبا {depth_gap.get('difference', 0):.1f}% بیشتر است. "
                        f"محتوای خود را عمیق‌تر کنید."
                    )
            
            # پیشنهادات بر اساس content type gaps
            if content_type_gaps:
                missing_types = [g for g in content_type_gaps if g.get('your_count', 0) == 0]
                if missing_types:
                    types_str = ', '.join([g['content_type'] for g in missing_types[:3]])
                    recommendations.append(
                        f"🎨 انواع محتوای موجود در رقبا اما نه در شما: {types_str}. "
                        f"این انواع محتوا را اضافه کنید."
                    )
        else:
            # English recommendations
            if topic_gaps:
                recommendations.append(
                    f"✅ {len(topic_gaps)} topics identified that competitors cover but you don't. "
                    f"Prioritize creating content for these topics."
                )
            
            if angle_gaps:
                recommendations.append(
                    f"🎯 {len(angle_gaps)} different angles identified. "
                    f"Focus on different angles of topics."
                )
            
            if depth_gaps:
                depth_gap = next((g for g in depth_gaps if g.get('gap_type') == 'depth'), None)
                if depth_gap:
                    recommendations.append(
                        f"📊 Competitor content is {depth_gap.get('difference', 0):.1f}% deeper. "
                        f"Increase your content depth."
                    )
        
        return recommendations
    
    def _calculate_summary(
        self,
        topic_gaps: List[Dict[str, Any]],
        angle_gaps: List[Dict[str, Any]],
        depth_gaps: List[Dict[str, Any]],
        content_type_gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """محاسبه خلاصه"""
        high_importance_topics = [
            gap for gap in topic_gaps if gap.get('importance', 0) >= 70
        ]
        
        return {
            'total_topic_gaps': len(topic_gaps),
            'high_importance_topics': len(high_importance_topics),
            'total_angle_gaps': len(angle_gaps),
            'total_depth_gaps': len(depth_gaps),
            'total_content_type_gaps': len(content_type_gaps),
            'overall_gap_score': self._calculate_overall_gap_score(
                topic_gaps,
                angle_gaps,
                depth_gaps,
                content_type_gaps
            )
        }
    
    def _calculate_overall_gap_score(
        self,
        topic_gaps: List[Dict[str, Any]],
        angle_gaps: List[Dict[str, Any]],
        depth_gaps: List[Dict[str, Any]],
        content_type_gaps: List[Dict[str, Any]]
    ) -> float:
        """محاسبه Overall Gap Score"""
        score = 0.0
        
        # فاکتور 1: Topic Gaps (40%)
        if topic_gaps:
            avg_importance = sum(g.get('importance', 0) for g in topic_gaps) / len(topic_gaps)
            score += (avg_importance / 100) * 40
        else:
            score += 40  # اگر gap نباشد، امتیاز کامل
        
        # فاکتور 2: Angle Gaps (25%)
        if angle_gaps:
            score += min(len(angle_gaps) / 10, 1.0) * 25
        else:
            score += 25
        
        # فاکتور 3: Depth Gaps (20%)
        if depth_gaps:
            depth_gap = next((g for g in depth_gaps if g.get('gap_type') == 'depth'), None)
            if depth_gap:
                diff = depth_gap.get('difference', 0)
                score += max(0, 20 - (diff / 10))  # هر 10 واحد تفاوت = -1 امتیاز
            else:
                score += 20
        else:
            score += 20
        
        # فاکتور 4: Content Type Gaps (15%)
        if content_type_gaps:
            score += min(len(content_type_gaps) / 5, 1.0) * 15
        else:
            score += 15
        
        return min(score, 100.0)
    
    def _empty_gap_result(self) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'topic_gaps': [],
            'angle_gaps': [],
            'depth_gaps': [],
            'content_type_gaps': [],
            'recommendations': [],
            'summary': {
                'total_topic_gaps': 0,
                'high_importance_topics': 0,
                'total_angle_gaps': 0,
                'total_depth_gaps': 0,
                'total_content_type_gaps': 0,
                'overall_gap_score': 0.0
            }
        }

