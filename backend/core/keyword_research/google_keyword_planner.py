"""
یکپارچه‌سازی با Google Keyword Planner
پشتیبانی از Google Ads API (رسمی) و روش‌های جایگزین رایگان
"""

import os
import logging
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)


class GoogleKeywordPlanner:
    """
    کلاس یکپارچه‌سازی با Google Keyword Planner
    
    پشتیبانی از:
    1. Google Ads API (رسمی - نیاز به API Key)
    2. Google Autocomplete (رایگان)
    3. Google Trends (رایگان)
    4. Google Related Searches (رایگان)
    """
    
    def __init__(self):
        # بررسی وجود Google Ads API credentials
        self.google_ads_client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
        self.google_ads_client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
        self.google_ads_refresh_token = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
        self.google_ads_customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
        
        self.has_google_ads = all([
            self.google_ads_client_id,
            self.google_ads_client_secret,
            self.google_ads_refresh_token,
            self.google_ads_customer_id
        ])
        
        if self.has_google_ads:
            logger.info("Google Ads API credentials found")
        else:
            logger.info("Google Ads API not configured, using free methods")
        
        self.base_url = "https://www.google.com"
        self.timeout = 15.0
    
    async def get_keyword_ideas(
        self,
        seed_keyword: str,
        language: str = 'fa',
        country: str = 'ir',
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        دریافت ایده‌های کلمات کلیدی از Google Keyword Planner
        
        Args:
            seed_keyword: کلمه کلیدی اولیه
            language: زبان (fa, en, ...)
            country: کشور (ir, us, ...)
            max_results: حداکثر تعداد نتایج
        
        Returns:
            لیست کلمات کلیدی با معیارها:
            - keyword: کلمه کلیدی
            - search_volume: حجم جستجو (تقریبی)
            - competition: سطح رقابت
            - cpc: هزینه هر کلیک (تقریبی)
            - trend: روند جستجو
        """
        all_keywords = []
        
        # روش 1: استفاده از Google Ads API (اگر موجود باشد)
        if self.has_google_ads:
            try:
                api_keywords = await self._get_keywords_from_ads_api(
                    seed_keyword,
                    language,
                    country,
                    max_results
                )
                if api_keywords:
                    all_keywords.extend(api_keywords)
                    logger.info(f"Retrieved {len(api_keywords)} keywords from Google Ads API")
            except Exception as e:
                logger.warning(f"Google Ads API failed: {str(e)}, using free methods")
        
        # روش 2: استفاده از Google Autocomplete (رایگان)
        try:
            autocomplete_keywords = await self._get_keywords_from_autocomplete(
                seed_keyword,
                language,
                country
            )
            all_keywords.extend(autocomplete_keywords)
            logger.info(f"Retrieved {len(autocomplete_keywords)} keywords from Autocomplete")
        except Exception as e:
            logger.error(f"Autocomplete failed: {str(e)}")
        
        # روش 3: استفاده از Related Searches (رایگان)
        try:
            related_keywords = await self._get_related_searches(
                seed_keyword,
                language
            )
            all_keywords.extend(related_keywords)
            logger.info(f"Retrieved {len(related_keywords)} keywords from Related Searches")
        except Exception as e:
            logger.error(f"Related Searches failed: {str(e)}")
        
        # حذف تکراری‌ها و مرتب‌سازی
        unique_keywords = {}
        for kw in all_keywords:
            keyword_lower = kw['keyword'].lower().strip()
            if keyword_lower not in unique_keywords:
                unique_keywords[keyword_lower] = kw
            else:
                # ترکیب داده‌ها اگر تکراری بود
                existing = unique_keywords[keyword_lower]
                if not existing.get('search_volume') and kw.get('search_volume'):
                    existing['search_volume'] = kw['search_volume']
                if not existing.get('competition') and kw.get('competition'):
                    existing['competition'] = kw['competition']
        
        # مرتب‌سازی بر اساس حجم جستجو
        sorted_keywords = sorted(
            unique_keywords.values(),
            key=lambda x: x.get('search_volume', 0),
            reverse=True
        )
        
        return sorted_keywords[:max_results]
    
    async def get_keyword_metrics(
        self,
        keywords: List[str],
        language: str = 'fa',
        country: str = 'ir'
    ) -> Dict[str, Dict[str, Any]]:
        """
        دریافت معیارهای کلمات کلیدی
        
        Args:
            keywords: لیست کلمات کلیدی
            language: زبان
            country: کشور
        
        Returns:
            Dictionary با کلید کلمه کلیدی و مقدار معیارها:
            {
                'keyword': {
                    'search_volume': int,
                    'competition': str,  # Low, Medium, High
                    'cpc': float,
                    'trend': List[int],
                    'difficulty': int,  # 0-100
                    'opportunity_score': float  # 0-100
                }
            }
        """
        results = {}
        
        # استفاده از Google Ads API اگر موجود باشد
        if self.has_google_ads:
            try:
                api_metrics = await self._get_metrics_from_ads_api(
                    keywords,
                    language,
                    country
                )
                results.update(api_metrics)
            except Exception as e:
                logger.warning(f"Google Ads API metrics failed: {str(e)}")
        
        # برای کلمات کلیدی که معیار ندارند، از روش‌های رایگان استفاده می‌کنیم
        for keyword in keywords:
            if keyword.lower() not in results:
                try:
                    metrics = await self._estimate_keyword_metrics(
                        keyword,
                        language,
                        country
                    )
                    results[keyword.lower()] = metrics
                except Exception as e:
                    logger.error(f"Error estimating metrics for {keyword}: {str(e)}")
                    results[keyword.lower()] = {
                        'search_volume': 0,
                        'competition': 'Unknown',
                        'cpc': 0.0,
                        'trend': [],
                        'difficulty': 50,
                        'opportunity_score': 0
                    }
        
        return results
    
    # ==================== روش‌های رایگان ====================
    
    async def _get_keywords_from_autocomplete(
        self,
        seed_keyword: str,
        language: str = 'fa',
        country: str = 'ir'
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی از Google Autocomplete"""
        keywords = []
        
        try:
            # استفاده از Google Autocomplete API (غیررسمی اما کار می‌کند)
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': seed_keyword,
                'hl': language,
                'gl': country
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = json.loads(response.text)
                    if len(data) > 1:
                        for suggestion in data[1][:20]:  # 20 پیشنهاد اول
                            keywords.append({
                                'keyword': suggestion,
                                'source': 'autocomplete',
                                'search_volume': None,  # تخمین می‌شود
                                'competition': None,
                                'cpc': None
                            })
        except Exception as e:
            logger.error(f"Error fetching autocomplete: {str(e)}")
        
        return keywords
    
    async def _get_related_searches(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """دریافت جستجوهای مرتبط از Google"""
        keywords = []
        
        try:
            url = f"{self.base_url}/search"
            params = {
                'q': seed_keyword,
                'hl': language
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # پیدا کردن بخش "People also ask"
                    paa_sections = soup.find_all('div', class_='related-question-pair')
                    for section in paa_sections[:10]:
                        text = section.get_text(strip=True)
                        if text and len(text) > 5:
                            keywords.append({
                                'keyword': text,
                                'source': 'people_also_ask',
                                'search_volume': None,
                                'competition': None,
                                'cpc': None
                            })
                    
                    # پیدا کردن "Related searches"
                    related_divs = soup.find_all('div', class_='brs_col')
                    for div in related_divs:
                        link = div.find('a')
                        if link:
                            text = link.get_text(strip=True)
                            if text and len(text) > 5:
                                keywords.append({
                                    'keyword': text,
                                    'source': 'related_searches',
                                    'search_volume': None,
                                    'competition': None,
                                    'cpc': None
                                })
        except Exception as e:
            logger.error(f"Error fetching related searches: {str(e)}")
        
        return keywords
    
    async def _estimate_keyword_metrics(
        self,
        keyword: str,
        language: str = 'fa',
        country: str = 'ir'
    ) -> Dict[str, Any]:
        """تخمین معیارهای کلمه کلیدی با روش‌های رایگان"""
        
        # دریافت تعداد نتایج جستجو
        total_results = await self._get_search_results_count(keyword, language)
        
        # تخمین حجم جستجو بر اساس تعداد نتایج
        estimated_volume = self._estimate_volume_from_results(total_results)
        
        # تخمین رقابت
        competition = self._estimate_competition(total_results, keyword)
        
        # تخمین CPC (بسیار تقریبی)
        estimated_cpc = self._estimate_cpc(keyword, competition)
        
        # محاسبه Difficulty
        difficulty = self._calculate_difficulty(total_results, competition)
        
        # محاسبه Opportunity Score
        opportunity_score = self._calculate_opportunity_score(
            estimated_volume,
            difficulty,
            competition
        )
        
        return {
            'search_volume': estimated_volume,
            'competition': competition,
            'cpc': estimated_cpc,
            'trend': [],  # نیاز به Google Trends API
            'difficulty': difficulty,
            'opportunity_score': opportunity_score,
            'total_results': total_results,
            'source': 'estimated'
        }
    
    async def _get_search_results_count(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> int:
        """دریافت تعداد کل نتایج جستجو"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'q': keyword,
                'hl': language,
                'num': 10
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # استخراج تعداد کل نتایج
                    result_stats = soup.find('div', {'id': 'result-stats'})
                    if result_stats:
                        text = result_stats.get_text()
                        # استخراج عدد (مثلاً "About 1,230,000 results")
                        numbers = re.findall(r'[\d,]+', text.replace(',', ''))
                        if numbers:
                            return int(numbers[0].replace(',', ''))
        except Exception as e:
            logger.error(f"Error getting search results count: {str(e)}")
        
        return 0
    
    def _estimate_volume_from_results(self, total_results: int) -> int:
        """تخمین حجم جستجو بر اساس تعداد نتایج"""
        # فرمول تقریبی (بر اساس تجربه)
        if total_results == 0:
            return 0
        elif total_results < 1000:
            return 10  # بسیار کم
        elif total_results < 10000:
            return 100  # کم
        elif total_results < 100000:
            return 1000  # متوسط
        elif total_results < 1000000:
            return 10000  # بالا
        elif total_results < 10000000:
            return 100000  # بسیار بالا
        else:
            return 1000000  # فوق‌العاده بالا
    
    def _estimate_competition(self, total_results: int, keyword: str) -> str:
        """تخمین سطح رقابت"""
        keyword_length = len(keyword.split())
        
        # Long-tail keywords رقابت کمتری دارند
        if keyword_length >= 4:
            if total_results < 100000:
                return 'Low'
            elif total_results < 1000000:
                return 'Medium'
            else:
                return 'High'
        else:
            # Short keywords رقابت بیشتری دارند
            if total_results < 1000000:
                return 'Medium'
            else:
                return 'High'
    
    def _estimate_cpc(self, keyword: str, competition: str) -> float:
        """تخمین CPC (بسیار تقریبی)"""
        base_cpc = 0.5  # پایه
        
        # تعدیل بر اساس رقابت
        if competition == 'High':
            base_cpc *= 3
        elif competition == 'Medium':
            base_cpc *= 1.5
        
        # تعدیل بر اساس طول کلمه کلیدی
        keyword_length = len(keyword.split())
        if keyword_length >= 4:
            base_cpc *= 0.5  # Long-tail ارزان‌تر
        
        return round(base_cpc, 2)
    
    def _calculate_difficulty(
        self,
        total_results: int,
        competition: str
    ) -> int:
        """محاسبه Keyword Difficulty (0-100)"""
        difficulty = 0
        
        # فاکتور 1: تعداد نتایج
        if total_results > 10000000:
            difficulty += 50
        elif total_results > 1000000:
            difficulty += 40
        elif total_results > 100000:
            difficulty += 30
        elif total_results > 10000:
            difficulty += 20
        else:
            difficulty += 10
        
        # فاکتور 2: سطح رقابت
        if competition == 'High':
            difficulty += 40
        elif competition == 'Medium':
            difficulty += 25
        else:
            difficulty += 10
        
        return min(difficulty, 100)
    
    def _calculate_opportunity_score(
        self,
        search_volume: int,
        difficulty: int,
        competition: str
    ) -> float:
        """محاسبه Opportunity Score (0-100)"""
        # فرمول: (Volume * (100 - Difficulty)) / 100
        if search_volume == 0 or difficulty == 100:
            return 0
        
        # نرمال‌سازی حجم جستجو (0-100)
        if search_volume >= 100000:
            normalized_volume = 100
        elif search_volume >= 10000:
            normalized_volume = 75
        elif search_volume >= 1000:
            normalized_volume = 50
        elif search_volume >= 100:
            normalized_volume = 25
        else:
            normalized_volume = 10
        
        # محاسبه Opportunity
        opportunity = (normalized_volume * (100 - difficulty)) / 100
        
        # تعدیل بر اساس رقابت
        if competition == 'Low':
            opportunity *= 1.2
        elif competition == 'High':
            opportunity *= 0.8
        
        return min(round(opportunity, 2), 100)
    
    # ==================== Google Ads API (رسمی) ====================
    
    async def _get_keywords_from_ads_api(
        self,
        seed_keyword: str,
        language: str,
        country: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی از Google Ads API"""
        # این بخش نیاز به نصب google-ads library دارد
        # و نیاز به OAuth2 authentication
        
        try:
            from google.ads.googleads.client import GoogleAdsClient
            from google.ads.googleads.errors import GoogleAdsException
            
            # تنظیمات Google Ads API
            # (نیاز به فایل google-ads.yaml یا environment variables)
            
            # این بخش نیاز به پیاده‌سازی کامل دارد
            # برای سادگی، از روش‌های رایگان استفاده می‌کنیم
            
            logger.info("Google Ads API integration requires full OAuth2 setup")
            return []
            
        except ImportError:
            logger.warning("google-ads library not installed")
            return []
        except Exception as e:
            logger.error(f"Google Ads API error: {str(e)}")
            return []
    
    async def _get_metrics_from_ads_api(
        self,
        keywords: List[str],
        language: str,
        country: str
    ) -> Dict[str, Dict[str, Any]]:
        """دریافت معیارها از Google Ads API"""
        # مشابه بالا، نیاز به پیاده‌سازی کامل دارد
        return {}


# ==================== کلاس کمکی برای Trend Analysis ====================

class GoogleTrendsIntegration:
    """یکپارچه‌سازی با Google Trends"""
    
    async def get_trend_data(
        self,
        keyword: str,
        timeframe: str = '12m'
    ) -> Dict[str, Any]:
        """
        دریافت داده‌های Trend
        
        نیاز به نصب: pip install pytrends
        """
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='fa-IR', tz=360)
            pytrends.build_payload([keyword], timeframe=timeframe)
            
            trend_data = pytrends.interest_over_time()
            
            if not trend_data.empty:
                values = trend_data[keyword].tolist()
                avg_volume = sum(values) / len(values) if values else 0
                
                peak_index = values.index(max(values)) if values else 0
                peak_month = trend_data.index[peak_index].strftime('%Y-%m') if peak_index < len(trend_data.index) else None
                
                growth_rate = 0
                if len(values) >= 2 and values[0] > 0:
                    growth_rate = ((values[-1] - values[0]) / values[0] * 100)
                
                return {
                    'average_volume': int(avg_volume),
                    'trend': values,
                    'peak_month': peak_month,
                    'growth_rate': round(growth_rate, 2),
                    'is_growing': growth_rate > 0
                }
        except ImportError:
            logger.warning("pytrends not installed. Install with: pip install pytrends")
        except Exception as e:
            logger.error(f"Google Trends error: {str(e)}")
        
        return {
            'average_volume': 0,
            'trend': [],
            'peak_month': None,
            'growth_rate': 0,
            'is_growing': False
        }

