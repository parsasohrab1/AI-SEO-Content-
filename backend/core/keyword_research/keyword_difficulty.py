"""
محاسبه Keyword Difficulty پیشرفته
تحلیل سختی کلمات کلیدی بر اساس فاکتورهای مختلف
"""

import logging
import httpx
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
import asyncio

logger = logging.getLogger(__name__)


class KeywordDifficultyCalculator:
    """
    کلاس محاسبه Keyword Difficulty
    
    محاسبه سختی کلمه کلیدی بر اساس:
    - Domain Authority رقبا
    - تعداد Backlinks صفحات رتبه‌دار
    - کیفیت محتوای رقبا
    - سن دامنه
    - قدرت برند
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # برندهای قوی (معمولاً رقابت بیشتری دارند)
        self.strong_brands = {
            'wikipedia.org', 'youtube.com', 'amazon.com', 'facebook.com',
            'twitter.com', 'linkedin.com', 'reddit.com', 'pinterest.com',
            'instagram.com', 'quora.com', 'medium.com', 'wordpress.com',
            'blogger.com', 'tumblr.com', 'github.com', 'stackoverflow.com'
        }
    
    async def calculate_difficulty(
        self,
        keyword: str,
        language: str = 'fa',
        use_apis: bool = True
    ) -> Dict[str, Any]:
        """
        محاسبه سختی کلمه کلیدی
        
        Args:
            keyword: کلمه کلیدی مورد نظر
            language: زبان
            use_apis: استفاده از APIهای خارجی (SEMrush, Ahrefs) اگر موجود باشند
        
        Returns:
            {
                'difficulty_score': int,  # 0-100
                'difficulty_level': str,  # 'easy', 'medium', 'hard'
                'estimated_effort': str,  # 'low', 'medium', 'high'
                'competitor_analysis': Dict,
                'factors': Dict,  # فاکتورهای تاثیرگذار
                'recommendations': List[str]
            }
        """
        try:
            # دریافت نتایج جستجو
            search_results = await self._get_search_results(keyword, language)
            
            if not search_results or not search_results.get('top_domains'):
                return self._default_difficulty(keyword, "No search results found")
            
            top_domains = search_results['top_domains']
            total_results = search_results.get('total_results', 0)
            
            # تحلیل رقبا
            competitor_analysis = await self._analyze_competitors(
                top_domains,
                keyword,
                use_apis
            )
            
            # محاسبه فاکتورها
            factors = self._calculate_factors(
                competitor_analysis,
                total_results,
                keyword
            )
            
            # محاسبه Difficulty Score
            difficulty_score = self._calculate_difficulty_score(factors)
            
            # تعیین سطح
            difficulty_level = self._get_difficulty_level(difficulty_score)
            estimated_effort = self._get_estimated_effort(difficulty_score)
            
            # تولید توصیه‌ها
            recommendations = self._generate_recommendations(
                difficulty_score,
                factors,
                competitor_analysis
            )
            
            return {
                'difficulty_score': difficulty_score,
                'difficulty_level': difficulty_level,
                'estimated_effort': estimated_effort,
                'competitor_analysis': competitor_analysis,
                'factors': factors,
                'recommendations': recommendations,
                'keyword': keyword,
                'total_results': total_results,
                'analyzed_competitors': len(top_domains)
            }
            
        except Exception as e:
            logger.error(f"Error calculating keyword difficulty: {str(e)}")
            return self._default_difficulty(keyword, str(e))
    
    async def _get_search_results(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """دریافت نتایج جستجو از Google"""
        try:
            url = "https://www.google.com/search"
            params = {
                'q': keyword,
                'hl': language,
                'num': 10
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # استخراج تعداد کل نتایج
                result_stats = soup.find('div', {'id': 'result-stats'})
                total_results = 0
                if result_stats:
                    text = result_stats.get_text()
                    numbers = re.findall(r'[\d,]+', text.replace(',', ''))
                    if numbers:
                        total_results = int(numbers[0].replace(',', ''))
                
                # استخراج دامنه‌های رتبه‌دار (10 نتیجه اول)
                top_domains = []
                search_results = soup.find_all('div', class_='g')[:10]
                
                for result in search_results:
                    link = result.find('a', href=True)
                    if link:
                        href = link['href']
                        if 'http' in href:
                            try:
                                domain = urlparse(href).netloc
                                if domain and domain not in top_domains:
                                    top_domains.append(domain)
                            except:
                                continue
                
                return {
                    'total_results': total_results,
                    'top_domains': top_domains
                }
        except Exception as e:
            logger.error(f"Error getting search results: {str(e)}")
        
        return {}
    
    async def _analyze_competitors(
        self,
        domains: List[str],
        keyword: str,
        use_apis: bool
    ) -> Dict[str, Any]:
        """تحلیل رقبا"""
        competitor_data = []
        
        for domain in domains[:10]:  # تحلیل 10 رقیب اول
            try:
                competitor_info = await self._analyze_single_competitor(
                    domain,
                    keyword,
                    use_apis
                )
                if competitor_info:
                    competitor_data.append(competitor_info)
            except Exception as e:
                logger.warning(f"Error analyzing competitor {domain}: {str(e)}")
                continue
        
        # محاسبه میانگین‌ها
        if competitor_data:
            avg_domain_authority = sum(
                c.get('domain_authority', 0) for c in competitor_data
            ) / len(competitor_data)
            
            avg_backlinks = sum(
                c.get('backlinks', 0) for c in competitor_data
            ) / len(competitor_data)
            
            avg_content_quality = sum(
                c.get('content_quality_score', 0) for c in competitor_data
            ) / len(competitor_data)
            
            strong_brand_count = sum(
                1 for c in competitor_data if c.get('is_strong_brand', False)
            )
            
            avg_domain_age = sum(
                c.get('domain_age_years', 0) for c in competitor_data
            ) / len(competitor_data)
        else:
            avg_domain_authority = 50
            avg_backlinks = 1000
            avg_content_quality = 50
            strong_brand_count = 0
            avg_domain_age = 5
        
        return {
            'competitors': competitor_data,
            'average_domain_authority': round(avg_domain_authority, 2),
            'average_backlinks': round(avg_backlinks, 0),
            'average_content_quality': round(avg_content_quality, 2),
            'strong_brand_count': strong_brand_count,
            'average_domain_age': round(avg_domain_age, 2),
            'total_competitors_analyzed': len(competitor_data)
        }
    
    async def _analyze_single_competitor(
        self,
        domain: str,
        keyword: str,
        use_apis: bool
    ) -> Optional[Dict[str, Any]]:
        """تحلیل یک رقیب"""
        competitor_info = {
            'domain': domain,
            'domain_authority': 0,
            'backlinks': 0,
            'content_quality_score': 0,
            'is_strong_brand': domain.lower() in self.strong_brands,
            'domain_age_years': 0
        }
        
        # استفاده از APIهای خارجی اگر موجود باشند
        if use_apis:
            # سعی می‌کنیم از SEMrush استفاده کنیم
            try:
                from .semrush_client import SEMrushKeywordAnalyzer
                semrush = SEMrushKeywordAnalyzer()
                if semrush.enabled:
                    # دریافت Domain Authority از SEMrush
                    # (این نیاز به endpoint خاص دارد که در اینجا ساده شده)
                    pass
            except:
                pass
            
            # سعی می‌کنیم از Ahrefs استفاده کنیم
            try:
                from .ahrefs_client import AhrefsKeywordAnalyzer
                ahrefs = AhrefsKeywordAnalyzer()
                if ahrefs.enabled:
                    # دریافت Domain Rating از Ahrefs
                    # (این نیاز به endpoint خاص دارد)
                    pass
            except:
                pass
        
        # روش‌های رایگان: تخمین بر اساس فاکتورهای قابل دسترسی
        competitor_info['domain_authority'] = self._estimate_domain_authority(domain)
        competitor_info['backlinks'] = self._estimate_backlinks(domain)
        competitor_info['content_quality_score'] = await self._estimate_content_quality(
            domain,
            keyword
        )
        competitor_info['domain_age_years'] = await self._estimate_domain_age(domain)
        
        return competitor_info
    
    def _estimate_domain_authority(self, domain: str) -> int:
        """تخمین Domain Authority"""
        # برندهای قوی
        if domain.lower() in self.strong_brands:
            return 90
        
        # دامنه‌های .edu, .gov معمولاً Authority بالایی دارند
        if domain.endswith('.edu') or domain.endswith('.gov'):
            return 85
        
        # دامنه‌های .org معمولاً Authority متوسط-بالا دارند
        if domain.endswith('.org'):
            return 60
        
        # تخمین بر اساس طول دامنه (دامنه‌های کوتاه‌تر معمولاً بهتر هستند)
        domain_length = len(domain.replace('.', ''))
        if domain_length < 10:
            return 70
        elif domain_length < 15:
            return 55
        else:
            return 45
    
    def _estimate_backlinks(self, domain: str) -> int:
        """تخمین تعداد Backlinks"""
        # برندهای قوی
        if domain.lower() in self.strong_brands:
            return 1000000
        
        # دامنه‌های .edu, .gov
        if domain.endswith('.edu') or domain.endswith('.gov'):
            return 500000
        
        # تخمین بر اساس نوع دامنه
        if domain.endswith('.org'):
            return 100000
        
        # تخمین پایه
        return 10000
    
    async def _estimate_content_quality(
        self,
        domain: str,
        keyword: str
    ) -> int:
        """تخمین کیفیت محتوا"""
        try:
            # سعی می‌کنیم صفحه اصلی را بررسی کنیم
            url = f"https://{domain}"
            response = await self.client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # بررسی وجود H1
                h1_count = len(soup.find_all('h1'))
                
                # بررسی وجود Meta Description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                has_meta_desc = meta_desc is not None
                
                # بررسی طول محتوا
                text_content = soup.get_text()
                word_count = len(text_content.split())
                
                # محاسبه امتیاز
                score = 0
                
                if h1_count > 0:
                    score += 20
                if has_meta_desc:
                    score += 20
                if word_count > 500:
                    score += 30
                elif word_count > 200:
                    score += 20
                else:
                    score += 10
                
                # بررسی وجود تصاویر با Alt
                images = soup.find_all('img')
                images_with_alt = sum(1 for img in images if img.get('alt'))
                if images:
                    alt_ratio = images_with_alt / len(images)
                    score += int(alt_ratio * 30)
                
                return min(score, 100)
        except:
            pass
        
        # Fallback: تخمین بر اساس نوع دامنه
        if domain.lower() in self.strong_brands:
            return 80
        elif domain.endswith('.edu') or domain.endswith('.gov'):
            return 75
        else:
            return 50
    
    async def _estimate_domain_age(self, domain: str) -> int:
        """تخمین سن دامنه (به سال)"""
        # این یک تخمین ساده است
        # در حالت واقعی می‌توان از WHOIS API استفاده کرد
        
        # برندهای قوی معمولاً قدیمی‌تر هستند
        if domain.lower() in self.strong_brands:
            return 15
        
        # دامنه‌های .edu, .gov معمولاً قدیمی‌تر هستند
        if domain.endswith('.edu') or domain.endswith('.gov'):
            return 10
        
        # تخمین پایه
        return 5
    
    def _calculate_factors(
        self,
        competitor_analysis: Dict[str, Any],
        total_results: int,
        keyword: str
    ) -> Dict[str, Any]:
        """محاسبه فاکتورهای تاثیرگذار"""
        
        avg_da = competitor_analysis.get('average_domain_authority', 50)
        avg_backlinks = competitor_analysis.get('average_backlinks', 1000)
        avg_content_quality = competitor_analysis.get('average_content_quality', 50)
        strong_brand_count = competitor_analysis.get('strong_brand_count', 0)
        avg_domain_age = competitor_analysis.get('average_domain_age', 5)
        keyword_length = len(keyword.split())
        
        return {
            'domain_authority_impact': self._normalize_factor(avg_da, 0, 100),
            'backlinks_impact': self._normalize_factor(avg_backlinks, 0, 100000, reverse=True),
            'content_quality_impact': self._normalize_factor(avg_content_quality, 0, 100),
            'brand_strength_impact': min(strong_brand_count / 10, 1.0),
            'domain_age_impact': self._normalize_factor(avg_domain_age, 0, 20),
            'search_results_impact': self._normalize_factor(total_results, 0, 10000000),
            'keyword_length_impact': 1.0 - (min(keyword_length, 5) / 5) * 0.3  # Long-tail آسان‌تر
        }
    
    def _normalize_factor(
        self,
        value: float,
        min_val: float,
        max_val: float,
        reverse: bool = False
    ) -> float:
        """نرمال‌سازی فاکتور به بازه 0-1"""
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0, min(1, normalized))
        
        if reverse:
            return 1 - normalized
        return normalized
    
    def _calculate_difficulty_score(self, factors: Dict[str, Any]) -> int:
        """محاسبه نهایی Difficulty Score"""
        
        # وزن‌دهی فاکتورها
        weights = {
            'domain_authority_impact': 0.25,
            'backlinks_impact': 0.20,
            'content_quality_impact': 0.15,
            'brand_strength_impact': 0.15,
            'domain_age_impact': 0.10,
            'search_results_impact': 0.10,
            'keyword_length_impact': 0.05
        }
        
        # محاسبه امتیاز وزنی
        weighted_score = sum(
            factors.get(factor, 0) * weight
            for factor, weight in weights.items()
        )
        
        # تبدیل به بازه 0-100
        difficulty_score = int(weighted_score * 100)
        
        return max(0, min(100, difficulty_score))
    
    def _get_difficulty_level(self, score: int) -> str:
        """تعیین سطح سختی"""
        if score < 30:
            return 'easy'
        elif score < 70:
            return 'medium'
        else:
            return 'hard'
    
    def _get_estimated_effort(self, score: int) -> str:
        """تخمین تلاش مورد نیاز"""
        if score < 30:
            return 'low'
        elif score < 70:
            return 'medium'
        else:
            return 'high'
    
    def _generate_recommendations(
        self,
        difficulty_score: int,
        factors: Dict[str, Any],
        competitor_analysis: Dict[str, Any]
    ) -> List[str]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        if difficulty_score >= 70:
            recommendations.append("این کلمه کلیدی رقابت بسیار بالایی دارد. پیشنهاد می‌شود:")
            recommendations.append("- روی کلمات کلیدی Long-tail تمرکز کنید")
            recommendations.append("- محتوای بسیار با کیفیت و جامع تولید کنید")
            recommendations.append("- استراتژی Link Building قوی پیاده‌سازی کنید")
            recommendations.append("- صبر و پشتکار داشته باشید (6-12 ماه)")
        elif difficulty_score >= 40:
            recommendations.append("این کلمه کلیدی رقابت متوسطی دارد. پیشنهاد می‌شود:")
            recommendations.append("- محتوای بهینه و ارزشمند تولید کنید")
            recommendations.append("- Internal Linking را بهبود دهید")
            recommendations.append("- Social Signals را افزایش دهید")
            recommendations.append("- انتظار نتایج در 3-6 ماه")
        else:
            recommendations.append("این کلمه کلیدی فرصت خوبی دارد. پیشنهاد می‌شود:")
            recommendations.append("- محتوای هدفمند و مرتبط تولید کنید")
            recommendations.append("- Technical SEO را بهینه کنید")
            recommendations.append("- Local SEO را در نظر بگیرید")
            recommendations.append("- انتظار نتایج در 1-3 ماه")
        
        # توصیه‌های خاص بر اساس فاکتورها
        if factors.get('brand_strength_impact', 0) > 0.5:
            recommendations.append("⚠️ توجه: رقبای قوی با برندهای معروف در نتایج حضور دارند")
        
        if factors.get('domain_authority_impact', 0) > 0.7:
            recommendations.append("💡 پیشنهاد: روی Domain Authority خود کار کنید")
        
        if factors.get('backlinks_impact', 0) > 0.7:
            recommendations.append("🔗 پیشنهاد: استراتژی Link Building را تقویت کنید")
        
        return recommendations
    
    def _default_difficulty(
        self,
        keyword: str,
        error_message: str
    ) -> Dict[str, Any]:
        """برگرداندن Difficulty پیش‌فرض در صورت خطا"""
        return {
            'difficulty_score': 50,
            'difficulty_level': 'medium',
            'estimated_effort': 'medium',
            'competitor_analysis': {},
            'factors': {},
            'recommendations': [
                f"خطا در محاسبه: {error_message}",
                "لطفاً دوباره تلاش کنید یا از APIهای خارجی استفاده کنید"
            ],
            'keyword': keyword,
            'total_results': 0,
            'analyzed_competitors': 0,
            'error': error_message
        }
    
    async def close(self):
        """بستن client"""
        await self.client.aclose()

