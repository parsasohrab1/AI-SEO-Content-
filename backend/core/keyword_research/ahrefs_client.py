"""
یکپارچه‌سازی با Ahrefs API
تحلیل پیشرفته کلمات کلیدی و رتبه‌بندی با Ahrefs
"""

import os
import logging
import httpx
import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, quote
import json

logger = logging.getLogger(__name__)


class AhrefsKeywordAnalyzer:
    """
    کلاس تحلیل کلمات کلیدی با Ahrefs API
    
    نیاز به API Token از Ahrefs دارد
    دریافت API Token: https://ahrefs.com/api
    """
    
    def __init__(self):
        self.api_token = os.getenv('AHREFS_API_TOKEN')
        self.api_id = os.getenv('AHREFS_API_ID')
        self.base_url = "https://apiv2.ahrefs.com"
        self.timeout = 30.0
        
        if not self.api_token or not self.api_id:
            logger.warning("AHREFS_API_TOKEN or AHREFS_API_ID not found. Ahrefs features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Ahrefs API initialized")
    
    def _generate_signature(self, method: str, endpoint: str, timestamp: str) -> str:
        """
        تولید signature برای Ahrefs API v2
        
        Ahrefs API v2 از HMAC-SHA256 برای authentication استفاده می‌کند
        """
        if not self.api_token:
            return ""
        
        # ساخت string برای signature
        string_to_sign = f"{method}\n{endpoint}\n{timestamp}\n"
        
        # تولید HMAC-SHA256 signature
        signature = hmac.new(
            self.api_token.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def get_keyword_metrics(
        self,
        keyword: str,
        country: str = 'us',
        output: str = 'json'
    ) -> Optional[Dict[str, Any]]:
        """
        دریافت معیارهای Ahrefs برای یک کلمه کلیدی
        
        Args:
            keyword: کلمه کلیدی مورد نظر
            country: کشور (us, uk, ca, au, de, fr, ru, es, it, br, jp, in, etc.)
            output: فرمت خروجی (json, csv)
        
        Returns:
            {
                'keyword': str,
                'search_volume': int,
                'keyword_difficulty': int,  # 0-100
                'cpc': float,
                'click_potential': int,  # 0-100
                'parent_topic': str,
                'serp_features': List[str],
                'trend': Dict[str, int],  # روند ماهانه
                'source': 'ahrefs'
            }
        """
        if not self.enabled:
            logger.warning("Ahrefs API not enabled. Please set AHREFS_API_TOKEN and AHREFS_API_ID.")
            return None
        
        try:
            endpoint = "/keywords-explorer/keywords"
            timestamp = str(int(time.time()))
            
            # تولید signature
            signature = self._generate_signature("GET", endpoint, timestamp)
            
            params = {
                'token': self.api_id,
                'timestamp': timestamp,
                'signature': signature,
                'target': keyword,
                'country': country,
                'output': output
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=self.timeout,
                    headers={
                        'Accept': 'application/json'
                    }
                )
                
                if response.status_code == 200:
                    return self._parse_keyword_metrics(response.json(), keyword)
                elif response.status_code == 401:
                    logger.error("Ahrefs API authentication failed. Check your API credentials.")
                    return None
                elif response.status_code == 429:
                    logger.error("Ahrefs API rate limit exceeded. Please wait and try again.")
                    return None
                else:
                    logger.error(f"Ahrefs API HTTP error: {response.status_code}")
                    logger.debug(f"Response: {response.text[:200]}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Ahrefs API request timeout")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ahrefs API response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching keyword metrics from Ahrefs: {str(e)}")
            return None
    
    def _parse_keyword_metrics(
        self,
        response_data: Dict[str, Any],
        keyword: str
    ) -> Dict[str, Any]:
        """پارس کردن پاسخ Ahrefs API"""
        try:
            # ساختار پاسخ Ahrefs API ممکن است متفاوت باشد
            # این یک ساختار نمونه است
            metrics = response_data.get('metrics', {})
            
            search_volume = metrics.get('search_volume', 0)
            keyword_difficulty = metrics.get('keyword_difficulty', 0)
            cpc = metrics.get('cpc', 0.0)
            click_potential = metrics.get('click_potential', 0)
            parent_topic = metrics.get('parent_topic', '')
            
            # SERP Features
            serp_features = metrics.get('serp_features', [])
            
            # Trend (اگر موجود باشد)
            trend = metrics.get('trend', {})
            
            # محاسبه Opportunity Score
            opportunity_score = self._calculate_opportunity_score(
                search_volume,
                keyword_difficulty,
                click_potential
            )
            
            return {
                'keyword': keyword,
                'search_volume': search_volume,
                'keyword_difficulty': keyword_difficulty,
                'difficulty_level': self._get_difficulty_level(keyword_difficulty),
                'cpc': round(cpc, 2),
                'click_potential': click_potential,
                'parent_topic': parent_topic,
                'serp_features': serp_features,
                'trend': trend,
                'opportunity_score': opportunity_score,
                'source': 'ahrefs'
            }
        except Exception as e:
            logger.error(f"Error parsing Ahrefs metrics: {str(e)}")
            return None
    
    def _get_difficulty_level(self, difficulty: int) -> str:
        """تعیین سطح سختی"""
        if difficulty < 30:
            return 'Easy'
        elif difficulty < 70:
            return 'Medium'
        else:
            return 'Hard'
    
    def _calculate_opportunity_score(
        self,
        search_volume: int,
        difficulty: int,
        click_potential: int
    ) -> float:
        """محاسبه Opportunity Score"""
        if search_volume == 0 or difficulty == 100:
            return 0
        
        # نرمال‌سازی حجم جستجو
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
        
        # محاسبه Opportunity با در نظر گیری Click Potential
        base_opportunity = (normalized_volume * (100 - difficulty)) / 100
        
        # تعدیل بر اساس Click Potential
        click_adjustment = click_potential / 100
        opportunity = base_opportunity * (0.7 + 0.3 * click_adjustment)
        
        return min(round(opportunity, 2), 100)
    
    async def get_ranking_keywords(
        self,
        url: str,
        country: str = 'us',
        limit: int = 100,
        mode: str = 'domain'  # 'domain' یا 'url'
    ) -> List[Dict[str, Any]]:
        """
        دریافت کلمات کلیدی که سایت برای آن‌ها رتبه دارد
        
        Args:
            url: آدرس سایت یا URL صفحه
            country: کشور
            limit: حداکثر تعداد نتایج
            mode: 'domain' برای کل دامنه یا 'url' برای یک صفحه خاص
        
        Returns:
            لیست کلمات کلیدی با معیارها:
            {
                'keyword': str,
                'position': int,  # رتبه در SERP
                'search_volume': int,
                'cpc': float,
                'url': str,  # URL صفحه
                'traffic': int,  # ترافیک تخمینی
                'source': 'ahrefs'
            }
        """
        if not self.enabled:
            logger.warning("Ahrefs API not enabled")
            return []
        
        try:
            # استخراج دامنه
            parsed_url = urlparse(url)
            target = parsed_url.netloc.replace('www.', '') if mode == 'domain' else url
            
            endpoint = "/site-explorer/backlinks"
            timestamp = str(int(time.time()))
            
            # تولید signature
            signature = self._generate_signature("GET", endpoint, timestamp)
            
            params = {
                'token': self.api_id,
                'timestamp': timestamp,
                'signature': signature,
                'target': target,
                'mode': mode,
                'country': country,
                'output': 'json',
                'limit': limit
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_ranking_keywords(response.json(), limit)
                else:
                    logger.error(f"Ahrefs API HTTP error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching ranking keywords: {str(e)}")
            return []
    
    def _parse_ranking_keywords(
        self,
        response_data: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """پارس کردن کلمات کلیدی رتبه‌دار"""
        keywords = []
        
        try:
            # ساختار پاسخ Ahrefs API
            organic_keywords = response_data.get('organic_keywords', [])
            
            for item in organic_keywords[:limit]:
                try:
                    keyword_data = {
                        'keyword': item.get('keyword', ''),
                        'position': item.get('position', 0),
                        'search_volume': item.get('search_volume', 0),
                        'cpc': item.get('cpc', 0.0),
                        'url': item.get('url', ''),
                        'traffic': item.get('traffic', 0),
                        'source': 'ahrefs'
                    }
                    
                    keywords.append(keyword_data)
                except Exception as e:
                    logger.warning(f"Error parsing keyword item: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing ranking keywords: {str(e)}")
        
        return keywords
    
    async def get_keyword_ideas(
        self,
        seed_keyword: str,
        country: str = 'us',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        دریافت ایده‌های کلمات کلیدی مرتبط
        
        Args:
            seed_keyword: کلمه کلیدی اولیه
            country: کشور
            limit: حداکثر تعداد نتایج
        
        Returns:
            لیست کلمات کلیدی مرتبط
        """
        if not self.enabled:
            logger.warning("Ahrefs API not enabled")
            return []
        
        try:
            endpoint = "/keywords-explorer/keywords-ideas"
            timestamp = str(int(time.time()))
            
            signature = self._generate_signature("GET", endpoint, timestamp)
            
            params = {
                'token': self.api_id,
                'timestamp': timestamp,
                'signature': signature,
                'keyword': seed_keyword,
                'country': country,
                'output': 'json',
                'limit': limit
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_keyword_ideas(response.json(), limit)
                else:
                    logger.error(f"Ahrefs API HTTP error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching keyword ideas: {str(e)}")
            return []
    
    def _parse_keyword_ideas(
        self,
        response_data: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """پارس کردن ایده‌های کلمات کلیدی"""
        keywords = []
        
        try:
            ideas = response_data.get('keywords', [])
            
            for item in ideas[:limit]:
                try:
                    keyword_data = {
                        'keyword': item.get('keyword', ''),
                        'search_volume': item.get('search_volume', 0),
                        'keyword_difficulty': item.get('keyword_difficulty', 0),
                        'cpc': item.get('cpc', 0.0),
                        'click_potential': item.get('click_potential', 0),
                        'source': 'ahrefs'
                    }
                    
                    # محاسبه Opportunity Score
                    keyword_data['opportunity_score'] = self._calculate_opportunity_score(
                        keyword_data['search_volume'],
                        keyword_data['keyword_difficulty'],
                        keyword_data['click_potential']
                    )
                    
                    keywords.append(keyword_data)
                except Exception as e:
                    logger.warning(f"Error parsing keyword idea: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing keyword ideas: {str(e)}")
        
        return keywords
    
    async def get_competitor_keywords(
        self,
        competitor_url: str,
        your_url: str,
        country: str = 'us',
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        دریافت کلمات کلیدی رقیب که شما ندارید
        
        Args:
            competitor_url: آدرس سایت رقیب
            your_url: آدرس سایت شما
            country: کشور
            limit: حداکثر تعداد نتایج
        
        Returns:
            {
                'competitor_keywords': List[Dict],
                'your_keywords': List[Dict],
                'opportunities': List[Dict],  # کلمات کلیدی رقیب که شما ندارید
                'summary': Dict
            }
        """
        if not self.enabled:
            logger.warning("Ahrefs API not enabled")
            return {
                'competitor_keywords': [],
                'your_keywords': [],
                'opportunities': [],
                'summary': {}
            }
        
        try:
            # دریافت کلمات کلیدی رقیب
            competitor_keywords = await self.get_ranking_keywords(
                competitor_url,
                country=country,
                limit=limit
            )
            
            # دریافت کلمات کلیدی شما
            your_keywords = await self.get_ranking_keywords(
                your_url,
                country=country,
                limit=limit
            )
            
            # ایجاد set از کلمات کلیدی
            competitor_keyword_set = {kw['keyword'].lower() for kw in competitor_keywords}
            your_keyword_set = {kw['keyword'].lower() for kw in your_keywords}
            
            # فرصت‌ها: کلمات کلیدی رقیب که شما ندارید
            opportunities_keywords = competitor_keyword_set - your_keyword_set
            
            opportunities = [
                kw for kw in competitor_keywords
                if kw['keyword'].lower() in opportunities_keywords
            ]
            
            # مرتب‌سازی بر اساس Search Volume
            opportunities.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
            
            return {
                'competitor_keywords': competitor_keywords,
                'your_keywords': your_keywords,
                'opportunities': opportunities[:50],  # 50 فرصت برتر
                'summary': {
                    'competitor_total': len(competitor_keywords),
                    'your_total': len(your_keywords),
                    'opportunities_count': len(opportunities)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in competitor keywords analysis: {str(e)}")
            return {
                'competitor_keywords': [],
                'your_keywords': [],
                'opportunities': [],
                'summary': {}
            }
    
    async def get_bulk_keyword_metrics(
        self,
        keywords: List[str],
        country: str = 'us',
        max_concurrent: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        دریافت معیارهای چند کلمه کلیدی به صورت همزمان
        
        Args:
            keywords: لیست کلمات کلیدی
            country: کشور
            max_concurrent: حداکثر درخواست همزمان
        
        Returns:
            Dictionary با کلید کلمه کلیدی و مقدار معیارها
        """
        import asyncio
        
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(keyword: str):
            async with semaphore:
                metrics = await self.get_keyword_metrics(keyword, country)
                if metrics:
                    results[keyword.lower()] = metrics
                # تاخیر برای جلوگیری از Rate Limiting
                await asyncio.sleep(0.5)
        
        tasks = [fetch_with_semaphore(kw) for kw in keywords]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results

