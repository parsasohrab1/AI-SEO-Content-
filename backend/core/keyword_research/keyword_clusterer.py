"""
خوشه‌بندی کلمات کلیدی
گروه‌بندی کلمات کلیدی مرتبط و پیشنهاد استراتژی محتوا
"""

import logging
from typing import Dict, Any, List, Optional
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


class KeywordClusterer:
    """
    کلاس خوشه‌بندی کلمات کلیدی
    
    ویژگی‌ها:
    - گروه‌بندی بر اساس موضوع
    - شناسایی کلمات کلیدی اصلی هر خوشه
    - پیشنهاد استراتژی محتوا برای هر خوشه
    - تحلیل معیارهای هر خوشه
    """
    
    def __init__(self):
        self.semantic_analyzer = None
        
        # سعی می‌کنیم Semantic Analyzer را بارگذاری کنیم
        try:
            from .semantic_analyzer import SemanticKeywordAnalyzer
            self.semantic_analyzer = SemanticKeywordAnalyzer()
            if not self.semantic_analyzer.model_loaded:
                logger.warning("Semantic model not loaded. Clustering will use fallback methods.")
        except Exception as e:
            logger.warning(f"Could not load SemanticKeywordAnalyzer: {str(e)}")
    
    async def cluster_keywords(
        self,
        keywords: List[str],
        n_clusters: Optional[int] = None,
        method: str = 'semantic',  # 'semantic', 'topic', 'hybrid'
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        خوشه‌بندی کلمات کلیدی مرتبط
        
        Args:
            keywords: لیست کلمات کلیدی
            n_clusters: تعداد خوشه‌ها (اگر None باشد، خودکار محاسبه می‌شود)
            method: روش خوشه‌بندی
            language: زبان
        
        Returns:
            {
                'clusters': Dict[int, Dict],  # خوشه‌ها با جزئیات
                'cluster_summary': Dict,      # خلاصه خوشه‌ها
                'content_strategy': Dict,     # استراتژی محتوا برای هر خوشه
                'total_keywords': int,
                'total_clusters': int
            }
        """
        if not keywords:
            return self._empty_clustering_result()
        
        # حذف تکراری‌ها
        unique_keywords = list(dict.fromkeys(keywords))
        
        if len(unique_keywords) < 2:
            return self._single_keyword_result(unique_keywords[0] if unique_keywords else "")
        
        # تعیین تعداد خوشه‌ها
        if n_clusters is None:
            n_clusters = self._calculate_optimal_clusters(unique_keywords)
        
        # خوشه‌بندی بر اساس روش انتخاب شده
        if method == 'semantic' and self.semantic_analyzer and self.semantic_analyzer.model_loaded:
            clusters = await self._cluster_semantic(unique_keywords, n_clusters)
        elif method == 'topic':
            clusters = await self._cluster_by_topic(unique_keywords, n_clusters, language)
        else:  # hybrid
            clusters = await self._cluster_hybrid(unique_keywords, n_clusters, language)
        
        # تحلیل خوشه‌ها
        analyzed_clusters = await self._analyze_clusters(clusters, language)
        
        # شناسایی کلمات کلیدی اصلی
        main_keywords = self._identify_main_keywords(analyzed_clusters)
        
        # پیشنهاد استراتژی محتوا
        content_strategy = self._generate_content_strategy(analyzed_clusters, language)
        
        return {
            'clusters': analyzed_clusters,
            'cluster_summary': {
                'total_clusters': len(analyzed_clusters),
                'total_keywords': len(unique_keywords),
                'average_keywords_per_cluster': len(unique_keywords) / len(analyzed_clusters) if analyzed_clusters else 0,
                'main_keywords': main_keywords
            },
            'content_strategy': content_strategy,
            'total_keywords': len(unique_keywords),
            'total_clusters': len(analyzed_clusters),
            'method_used': method
        }
    
    async def _cluster_semantic(
        self,
        keywords: List[str],
        n_clusters: int
    ) -> Dict[int, List[str]]:
        """خوشه‌بندی بر اساس معنا"""
        try:
            clusters = await self.semantic_analyzer.cluster_semantic_keywords(
                keywords=keywords,
                n_clusters=n_clusters
            )
            return clusters
        except Exception as e:
            logger.error(f"Error in semantic clustering: {str(e)}")
            return await self._cluster_by_topic(keywords, n_clusters, 'en')
    
    async def _cluster_by_topic(
        self,
        keywords: List[str],
        n_clusters: int,
        language: str
    ) -> Dict[int, List[str]]:
        """خوشه‌بندی بر اساس موضوع (روش جایگزین)"""
        # استخراج کلمات کلیدی مشترک
        clusters = {}
        
        # شناسایی موضوعات بر اساس کلمات مشترک
        topic_keywords = self._identify_topic_keywords(keywords, language)
        
        # گروه‌بندی بر اساس موضوعات
        for i, (topic, topic_keywords_list) in enumerate(topic_keywords.items()):
            if i < n_clusters:
                clusters[i] = []
                for keyword in keywords:
                    # بررسی اینکه آیا keyword به این topic مرتبط است
                    if any(tk in keyword.lower() for tk in topic_keywords_list):
                        clusters[i].append(keyword)
        
        # توزیع کلمات کلیدی باقی‌مانده
        assigned_keywords = set()
        for cluster_keywords in clusters.values():
            assigned_keywords.update(cluster_keywords)
        
        remaining_keywords = [kw for kw in keywords if kw not in assigned_keywords]
        
        # توزیع یکنواخت کلمات کلیدی باقی‌مانده
        for i, keyword in enumerate(remaining_keywords):
            cluster_id = i % len(clusters)
            clusters[cluster_id].append(keyword)
        
        return clusters
    
    def _identify_topic_keywords(
        self,
        keywords: List[str],
        language: str
    ) -> Dict[str, List[str]]:
        """شناسایی کلمات کلیدی موضوعات"""
        # استخراج کلمات مشترک
        all_words = []
        for keyword in keywords:
            words = keyword.lower().split()
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # فیلتر کردن stop words
        stop_words = {
            'fa': {'و', 'در', 'به', 'از', 'که', 'این', 'است', 'را', 'یک', 'آن', 'ها', 'می', 'شود'},
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        }
        
        stop_words_set = stop_words.get(language, stop_words['en'])
        filtered_words = {
            word: count for word, count in word_freq.items()
            if word not in stop_words_set and len(word) > 2
        }
        
        # شناسایی موضوعات بر اساس کلمات پرتکرار
        topics = {}
        top_words = dict(Counter(filtered_words).most_common(10))
        
        for i, (word, count) in enumerate(top_words.items()):
            if i < 5:  # 5 موضوع اول
                topics[word] = [word]
        
        return topics
    
    async def _cluster_hybrid(
        self,
        keywords: List[str],
        n_clusters: int,
        language: str
    ) -> Dict[int, List[str]]:
        """خوشه‌بندی ترکیبی (معنایی + موضوعی)"""
        # ابتدا خوشه‌بندی معنایی
        if self.semantic_analyzer and self.semantic_analyzer.model_loaded:
            try:
                semantic_clusters = await self._cluster_semantic(keywords, n_clusters)
                # اگر خوشه‌بندی معنایی موفق بود، از آن استفاده می‌کنیم
                if semantic_clusters:
                    return semantic_clusters
            except:
                pass
        
        # Fallback به خوشه‌بندی موضوعی
        return await self._cluster_by_topic(keywords, n_clusters, language)
    
    def _calculate_optimal_clusters(self, keywords: List[str]) -> int:
        """محاسبه تعداد بهینه خوشه‌ها"""
        n = len(keywords)
        
        # قانون کلی: تعداد خوشه‌ها بین 2 تا sqrt(n)
        optimal = max(2, min(int(np.sqrt(n)), n // 3))
        
        return optimal
    
    async def _analyze_clusters(
        self,
        clusters: Dict[int, List[str]],
        language: str
    ) -> Dict[int, Dict[str, Any]]:
        """تحلیل خوشه‌ها"""
        analyzed = {}
        
        for cluster_id, cluster_keywords in clusters.items():
            if not cluster_keywords:
                continue
            
            # شناسایی موضوع خوشه
            topic = self._identify_cluster_topic(cluster_keywords, language)
            
            # محاسبه معیارها
            metrics = self._calculate_cluster_metrics(cluster_keywords)
            
            # شناسایی کلمات کلیدی اصلی
            main_keyword = self._find_main_keyword(cluster_keywords)
            
            analyzed[cluster_id] = {
                'keywords': cluster_keywords,
                'topic': topic,
                'main_keyword': main_keyword,
                'size': len(cluster_keywords),
                'metrics': metrics,
                'cluster_id': cluster_id
            }
        
        return analyzed
    
    def _identify_cluster_topic(
        self,
        keywords: List[str],
        language: str
    ) -> str:
        """شناسایی موضوع خوشه"""
        # استخراج کلمات مشترک
        all_words = []
        for keyword in keywords:
            words = keyword.lower().split()
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # فیلتر کردن stop words
        stop_words = {
            'fa': {'و', 'در', 'به', 'از', 'که', 'این', 'است', 'را'},
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        }
        
        stop_words_set = stop_words.get(language, stop_words['en'])
        filtered_words = {
            word: count for word, count in word_freq.items()
            if word not in stop_words_set and len(word) > 2
        }
        
        if filtered_words:
            # کلمه پرتکرارترین به عنوان موضوع
            topic = max(filtered_words, key=filtered_words.get)
            return topic
        
        # Fallback: استفاده از اولین کلمه کلیدی
        return keywords[0].split()[0] if keywords else "unknown"
    
    def _calculate_cluster_metrics(
        self,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """محاسبه معیارهای خوشه"""
        # میانگین طول کلمات کلیدی
        avg_length = sum(len(kw.split()) for kw in keywords) / len(keywords) if keywords else 0
        
        # تعداد Long-tail keywords
        long_tail_count = sum(1 for kw in keywords if len(kw.split()) >= 4)
        
        # تنوع کلمات کلیدی
        all_words = set()
        for keyword in keywords:
            all_words.update(keyword.lower().split())
        diversity = len(all_words) / sum(len(kw.split()) for kw in keywords) if keywords else 0
        
        return {
            'average_length': round(avg_length, 2),
            'long_tail_count': long_tail_count,
            'long_tail_ratio': round(long_tail_count / len(keywords), 2) if keywords else 0,
            'diversity': round(diversity, 2),
            'total_keywords': len(keywords)
        }
    
    def _find_main_keyword(
        self,
        keywords: List[str]
    ) -> str:
        """پیدا کردن کلمه کلیدی اصلی خوشه"""
        if not keywords:
            return ""
        
        # کلمه کلیدی کوتاه‌تر معمولاً اصلی‌تر است
        # اما باید پرتکرارترین کلمه را در نظر بگیریم
        
        # استخراج کلمات مشترک
        all_words = []
        for keyword in keywords:
            words = keyword.lower().split()
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # پیدا کردن کلمه کلیدی که شامل پرتکرارترین کلمه است
        if word_freq:
            most_common_word = word_freq.most_common(1)[0][0]
            
            # پیدا کردن کوتاه‌ترین کلمه کلیدی که شامل این کلمه است
            candidates = [kw for kw in keywords if most_common_word in kw.lower()]
            if candidates:
                return min(candidates, key=len)
        
        # Fallback: کوتاه‌ترین کلمه کلیدی
        return min(keywords, key=len)
    
    def _identify_main_keywords(
        self,
        analyzed_clusters: Dict[int, Dict[str, Any]]
    ) -> Dict[int, str]:
        """شناسایی کلمات کلیدی اصلی هر خوشه"""
        main_keywords = {}
        
        for cluster_id, cluster_data in analyzed_clusters.items():
            main_keyword = cluster_data.get('main_keyword', '')
            if main_keyword:
                main_keywords[cluster_id] = main_keyword
        
        return main_keywords
    
    def _generate_content_strategy(
        self,
        analyzed_clusters: Dict[int, Dict[str, Any]],
        language: str
    ) -> Dict[int, Dict[str, Any]]:
        """پیشنهاد استراتژی محتوا برای هر خوشه"""
        strategies = {}
        
        strategy_templates = {
            'fa': {
                'pillar': {
                    'type': 'Pillar Content',
                    'description': 'یک مقاله جامع و کامل درباره موضوع اصلی',
                    'recommended_length': '3000+ کلمه',
                    'frequency': '1 مقاله در ماه'
                },
                'cluster': {
                    'type': 'Cluster Content',
                    'description': 'مقالات تخصصی برای هر کلمه کلیدی',
                    'recommended_length': '1500-2000 کلمه',
                    'frequency': '2-3 مقاله در ماه'
                },
                'supporting': {
                    'type': 'Supporting Content',
                    'description': 'مقالات کوتاه و سریع',
                    'recommended_length': '800-1200 کلمه',
                    'frequency': '4-5 مقاله در ماه'
                }
            },
            'en': {
                'pillar': {
                    'type': 'Pillar Content',
                    'description': 'Comprehensive article about the main topic',
                    'recommended_length': '3000+ words',
                    'frequency': '1 article per month'
                },
                'cluster': {
                    'type': 'Cluster Content',
                    'description': 'Specialized articles for each keyword',
                    'recommended_length': '1500-2000 words',
                    'frequency': '2-3 articles per month'
                },
                'supporting': {
                    'type': 'Supporting Content',
                    'description': 'Short and quick articles',
                    'recommended_length': '800-1200 words',
                    'frequency': '4-5 articles per month'
                }
            }
        }
        
        templates = strategy_templates.get(language, strategy_templates['en'])
        
        for cluster_id, cluster_data in analyzed_clusters.items():
            size = cluster_data.get('size', 0)
            metrics = cluster_data.get('metrics', {})
            
            # تعیین نوع استراتژی بر اساس اندازه خوشه
            if size >= 10:
                strategy_type = 'pillar'
            elif size >= 5:
                strategy_type = 'cluster'
            else:
                strategy_type = 'supporting'
            
            strategy = templates[strategy_type].copy()
            
            # اضافه کردن توصیه‌های خاص
            recommendations = []
            
            if metrics.get('long_tail_ratio', 0) > 0.5:
                recommendations.append(
                    'این خوشه شامل کلمات کلیدی Long-tail زیادی است. فرصت خوبی برای تولید محتوا با رقابت کمتر.'
                if language == 'fa' else
                'This cluster has many long-tail keywords. Good opportunity for content with less competition.'
                )
            
            if size >= 10:
                recommendations.append(
                    'این خوشه بزرگ است. پیشنهاد می‌شود یک Pillar Content جامع ایجاد کنید.'
                if language == 'fa' else
                'This is a large cluster. Consider creating a comprehensive Pillar Content.'
                )
            
            strategy['recommendations'] = recommendations
            strategy['keywords_count'] = size
            strategy['main_keyword'] = cluster_data.get('main_keyword', '')
            
            strategies[cluster_id] = strategy
        
        return strategies
    
    def _empty_clustering_result(self) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'clusters': {},
            'cluster_summary': {
                'total_clusters': 0,
                'total_keywords': 0,
                'average_keywords_per_cluster': 0,
                'main_keywords': {}
            },
            'content_strategy': {},
            'total_keywords': 0,
            'total_clusters': 0,
            'method_used': 'none'
        }
    
    def _single_keyword_result(self, keyword: str) -> Dict[str, Any]:
        """نتیجه برای یک کلمه کلیدی"""
        return {
            'clusters': {
                0: {
                    'keywords': [keyword],
                    'topic': keyword.split()[0] if keyword else 'unknown',
                    'main_keyword': keyword,
                    'size': 1,
                    'metrics': {
                        'average_length': len(keyword.split()),
                        'long_tail_count': 1 if len(keyword.split()) >= 4 else 0,
                        'long_tail_ratio': 1.0 if len(keyword.split()) >= 4 else 0.0,
                        'diversity': 1.0,
                        'total_keywords': 1
                    },
                    'cluster_id': 0
                }
            },
            'cluster_summary': {
                'total_clusters': 1,
                'total_keywords': 1,
                'average_keywords_per_cluster': 1.0,
                'main_keywords': {0: keyword}
            },
            'content_strategy': {
                0: {
                    'type': 'Single Keyword',
                    'description': 'Content for single keyword',
                    'recommended_length': '1500-2000 words',
                    'frequency': '1 article',
                    'keywords_count': 1,
                    'main_keyword': keyword
                }
            },
            'total_keywords': 1,
            'total_clusters': 1,
            'method_used': 'single'
        }

