"""
تحلیل معنایی کلمات کلیدی
استفاده از NLP و Word Embeddings برای پیدا کردن کلمات کلیدی معنایی مرتبط
"""

import logging
import os
from typing import Dict, Any, List, Optional
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class SemanticKeywordAnalyzer:
    """
    کلاس تحلیل معنایی کلمات کلیدی
    
    استفاده از Word Embeddings و NLP برای پیدا کردن:
    - کلمات کلیدی معنایی مرتبط
    - کلمات کلیدی LSI (Latent Semantic Indexing)
    - کلمات کلیدی هم‌معنا
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        
        # سعی می‌کنیم مدل را بارگذاری کنیم
        try:
            from sentence_transformers import SentenceTransformer
            
            # استفاده از مدل چندزبانه
            model_name = os.getenv(
                'SEMANTIC_MODEL_NAME',
                'paraphrase-multilingual-MiniLM-L12-v2'
            )
            
            logger.info(f"Loading semantic model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.model_loaded = True
            logger.info("Semantic model loaded successfully")
            
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Error loading semantic model: {str(e)}")
            self.model_loaded = False
    
    async def find_semantic_keywords(
        self,
        main_keyword: str,
        candidate_keywords: Optional[List[str]] = None,
        threshold: float = 0.7,
        top_n: int = 20,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """
        پیدا کردن کلمات کلیدی معنایی مرتبط
        
        Args:
            main_keyword: کلمه کلیدی اصلی
            candidate_keywords: لیست کاندیداها (اگر None باشد، از روش‌های دیگر استفاده می‌شود)
            threshold: حداقل similarity (0-1)
            top_n: حداکثر تعداد نتایج
            language: زبان
        
        Returns:
            لیست کلمات کلیدی معنایی مرتبط:
            {
                'keyword': str,
                'similarity': float,  # 0-1
                'semantic_relation': str,  # synonym, related, lsi
                'source': str
            }
        """
        if not self.model_loaded:
            logger.warning("Semantic model not loaded. Using fallback method.")
            return self._fallback_semantic_keywords(main_keyword, language, top_n)
        
        try:
            # اگر candidate_keywords موجود نباشد، از روش‌های دیگر استفاده می‌کنیم
            if not candidate_keywords:
                candidate_keywords = await self._generate_candidates(
                    main_keyword,
                    language
                )
            
            if not candidate_keywords:
                return []
            
            # محاسبه embeddings
            main_embedding = self.model.encode([main_keyword], convert_to_numpy=True)
            candidate_embeddings = self.model.encode(
                candidate_keywords,
                convert_to_numpy=True
            )
            
            # محاسبه similarity (cosine similarity)
            similarities = self._calculate_cosine_similarity(
                main_embedding[0],
                candidate_embeddings
            )
            
            # فیلتر و مرتب‌سازی
            results = []
            for i, (keyword, similarity) in enumerate(zip(candidate_keywords, similarities)):
                if similarity >= threshold:
                    results.append({
                        'keyword': keyword,
                        'similarity': float(similarity),
                        'semantic_relation': self._classify_relation(similarity),
                        'source': 'semantic_analysis'
                    })
            
            # مرتب‌سازی بر اساس similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results[:top_n]
            
        except Exception as e:
            logger.error(f"Error finding semantic keywords: {str(e)}")
            return self._fallback_semantic_keywords(main_keyword, language, top_n)
    
    def _calculate_cosine_similarity(
        self,
        main_embedding: np.ndarray,
        candidate_embeddings: np.ndarray
    ) -> np.ndarray:
        """محاسبه Cosine Similarity"""
        # نرمال‌سازی
        main_norm = main_embedding / np.linalg.norm(main_embedding)
        candidate_norms = candidate_embeddings / np.linalg.norm(
            candidate_embeddings,
            axis=1,
            keepdims=True
        )
        
        # محاسبه dot product
        similarities = np.dot(candidate_norms, main_norm)
        
        return similarities
    
    def _classify_relation(self, similarity: float) -> str:
        """طبقه‌بندی نوع رابطه معنایی"""
        if similarity >= 0.9:
            return 'synonym'  # هم‌معنا
        elif similarity >= 0.75:
            return 'highly_related'  # بسیار مرتبط
        elif similarity >= 0.6:
            return 'related'  # مرتبط
        else:
            return 'lsi'  # LSI (Latent Semantic Indexing)
    
    async def _generate_candidates(
        self,
        main_keyword: str,
        language: str = 'fa'
    ) -> List[str]:
        """تولید کاندیداهای کلمات کلیدی"""
        candidates = []
        
        # استفاده از Long-tail Extractor برای تولید کاندیداها
        try:
            from .long_tail_extractor import LongTailKeywordExtractor
            extractor = LongTailKeywordExtractor()
            
            long_tail_keywords = await extractor.extract_long_tail_keywords(
                seed_keywords=[main_keyword],
                min_length=2,  # شامل کلمات کوتاه‌تر هم
                max_results=50,
                language=language
            )
            
            candidates.extend([kw['keyword'] for kw in long_tail_keywords])
            await extractor.close()
        except Exception as e:
            logger.warning(f"Could not use LongTailExtractor: {str(e)}")
        
        # استفاده از Google Keyword Planner
        try:
            from .google_keyword_planner import GoogleKeywordPlanner
            planner = GoogleKeywordPlanner()
            
            related = await planner.get_keyword_ideas(
                seed_keyword=main_keyword,
                language=language,
                max_results=30
            )
            
            candidates.extend([kw['keyword'] for kw in related])
        except Exception as e:
            logger.warning(f"Could not use GoogleKeywordPlanner: {str(e)}")
        
        # حذف تکراری‌ها
        candidates = list(set(candidates))
        
        return candidates
    
    def _fallback_semantic_keywords(
        self,
        main_keyword: str,
        language: str,
        top_n: int
    ) -> List[Dict[str, Any]]:
        """روش جایگزین در صورت عدم وجود مدل"""
        # استفاده از دیکشنری ساده برای کلمات کلیدی رایج
        semantic_dict = {
            'fa': {
                'سئو': ['بهینه‌سازی موتور جستجو', 'SEO', 'سئو سایت', 'بهینه‌سازی سایت', 'رتبه‌بندی گوگل'],
                'بهینه‌سازی': ['سئو', 'SEO', 'بهینه', 'بهبود', 'توسعه'],
                'محتوا': ['مطلب', 'مقاله', 'نوشته', 'متن', 'کنتنت'],
                'کلمه کلیدی': ['کیورد', 'keyword', 'کلیدواژه', 'واژه کلیدی']
            },
            'en': {
                'seo': ['search engine optimization', 'SEO', 'website optimization', 'ranking', 'organic search'],
                'optimization': ['SEO', 'improvement', 'enhancement', 'optimization', 'development'],
                'content': ['article', 'post', 'text', 'material', 'content'],
                'keyword': ['key phrase', 'search term', 'query', 'keyword']
            }
        }
        
        keywords_dict = semantic_dict.get(language, semantic_dict['en'])
        
        # جستجوی کلمات مرتبط
        related = []
        for key, values in keywords_dict.items():
            if key.lower() in main_keyword.lower() or main_keyword.lower() in key.lower():
                for value in values:
                    if value.lower() != main_keyword.lower():
                        related.append({
                            'keyword': value,
                            'similarity': 0.7,  # تخمینی
                            'semantic_relation': 'related',
                            'source': 'fallback_dictionary'
                        })
        
        return related[:top_n]
    
    async def find_lsi_keywords(
        self,
        main_keyword: str,
        context_keywords: List[str],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        پیدا کردن کلمات کلیدی LSI (Latent Semantic Indexing)
        
        LSI keywords کلمات کلیدی هستند که در همان زمینه استفاده می‌شوند
        اما لزوماً هم‌معنا نیستند.
        
        Args:
            main_keyword: کلمه کلیدی اصلی
            context_keywords: کلمات کلیدی زمینه (از محتوای موجود)
            top_n: حداکثر تعداد نتایج
        """
        if not self.model_loaded:
            return []
        
        try:
            # محاسبه embedding برای main keyword
            main_embedding = self.model.encode([main_keyword], convert_to_numpy=True)[0]
            
            # محاسبه embedding برای context keywords
            context_embeddings = self.model.encode(
                context_keywords,
                convert_to_numpy=True
            )
            
            # محاسبه centroid از context keywords
            context_centroid = np.mean(context_embeddings, axis=0)
            
            # محاسبه similarity بین main keyword و context centroid
            main_norm = main_embedding / np.linalg.norm(main_embedding)
            centroid_norm = context_centroid / np.linalg.norm(context_centroid)
            similarity = np.dot(main_norm, centroid_norm)
            
            # پیدا کردن کلمات کلیدی که به centroid نزدیک‌تر هستند
            results = []
            for keyword, embedding in zip(context_keywords, context_embeddings):
                keyword_norm = embedding / np.linalg.norm(embedding)
                keyword_similarity = np.dot(keyword_norm, centroid_norm)
                
                if keyword_similarity >= 0.5:  # threshold برای LSI
                    results.append({
                        'keyword': keyword,
                        'lsi_score': float(keyword_similarity),
                        'context_similarity': float(similarity),
                        'source': 'lsi_analysis'
                    })
            
            # مرتب‌سازی بر اساس LSI score
            results.sort(key=lambda x: x['lsi_score'], reverse=True)
            
            return results[:top_n]
            
        except Exception as e:
            logger.error(f"Error finding LSI keywords: {str(e)}")
            return []
    
    async def cluster_semantic_keywords(
        self,
        keywords: List[str],
        n_clusters: int = 5
    ) -> Dict[str, List[str]]:
        """
        خوشه‌بندی کلمات کلیدی بر اساس معنا
        
        Args:
            keywords: لیست کلمات کلیدی
            n_clusters: تعداد خوشه‌ها
        
        Returns:
            Dictionary با کلید شماره خوشه و مقدار لیست کلمات کلیدی
        """
        if not self.model_loaded or len(keywords) < n_clusters:
            return {}
        
        try:
            from sklearn.cluster import KMeans
            
            # محاسبه embeddings
            embeddings = self.model.encode(keywords, convert_to_numpy=True)
            
            # خوشه‌بندی با KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(embeddings)
            
            # گروه‌بندی کلمات کلیدی
            clustered = {}
            for i, keyword in enumerate(keywords):
                cluster_id = int(clusters[i])
                if cluster_id not in clustered:
                    clustered[cluster_id] = []
                clustered[cluster_id].append(keyword)
            
            return clustered
            
        except ImportError:
            logger.warning("scikit-learn not installed. Install with: pip install scikit-learn")
            return {}
        except Exception as e:
            logger.error(f"Error clustering keywords: {str(e)}")
            return {}
    
    async def expand_keyword_semantically(
        self,
        keyword: str,
        expansion_type: str = 'synonyms',  # synonyms, related, lsi
        language: str = 'fa'
    ) -> List[str]:
        """
        گسترش کلمه کلیدی به صورت معنایی
        
        Args:
            keyword: کلمه کلیدی
            expansion_type: نوع گسترش
            language: زبان
        
        Returns:
            لیست کلمات کلیدی گسترش یافته
        """
        if not self.model_loaded:
            return []
        
        try:
            # تولید کاندیداها
            candidates = await self._generate_candidates(keyword, language)
            
            if not candidates:
                return []
            
            # پیدا کردن کلمات کلیدی معنایی
            semantic_keywords = await self.find_semantic_keywords(
                main_keyword=keyword,
                candidate_keywords=candidates,
                threshold=0.6 if expansion_type == 'synonyms' else 0.5,
                language=language
            )
            
            # فیلتر بر اساس نوع
            if expansion_type == 'synonyms':
                filtered = [
                    kw['keyword'] for kw in semantic_keywords
                    if kw['semantic_relation'] == 'synonym'
                ]
            elif expansion_type == 'related':
                filtered = [
                    kw['keyword'] for kw in semantic_keywords
                    if kw['semantic_relation'] in ['synonym', 'highly_related', 'related']
                ]
            else:  # lsi
                filtered = [
                    kw['keyword'] for kw in semantic_keywords
                    if kw['semantic_relation'] == 'lsi'
                ]
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error expanding keyword: {str(e)}")
            return []
    
    def get_semantic_relationship(
        self,
        keyword1: str,
        keyword2: str
    ) -> Dict[str, Any]:
        """
        بررسی رابطه معنایی بین دو کلمه کلیدی
        
        Returns:
            {
                'similarity': float,
                'relationship': str,  # synonym, related, unrelated
                'confidence': float
            }
        """
        if not self.model_loaded:
            return {
                'similarity': 0.0,
                'relationship': 'unknown',
                'confidence': 0.0
            }
        
        try:
            # محاسبه embeddings
            embeddings = self.model.encode(
                [keyword1, keyword2],
                convert_to_numpy=True
            )
            
            # محاسبه similarity
            similarity = self._calculate_cosine_similarity(
                embeddings[0],
                embeddings[1:2]
            )[0]
            
            # تعیین نوع رابطه
            if similarity >= 0.9:
                relationship = 'synonym'
                confidence = 1.0
            elif similarity >= 0.7:
                relationship = 'highly_related'
                confidence = 0.8
            elif similarity >= 0.5:
                relationship = 'related'
                confidence = 0.6
            else:
                relationship = 'unrelated'
                confidence = 1.0 - similarity
            
            return {
                'similarity': float(similarity),
                'relationship': relationship,
                'confidence': float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error getting semantic relationship: {str(e)}")
            return {
                'similarity': 0.0,
                'relationship': 'unknown',
                'confidence': 0.0
            }

