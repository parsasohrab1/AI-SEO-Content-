"""
یکپارچه‌سازی با SEMrush API
تحلیل پیشرفته کلمات کلیدی با SEMrush
"""

import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import asyncio

logger = logging.getLogger(__name__)


class SEMrushKeywordAnalyzer:
    """
    کلاس تحلیل کلمات کلیدی با SEMrush API
    
    نیاز به API Key از SEMrush دارد
    دریافت API Key: https://www.semrush.com/api/
    """
    
    def __init__(self):
        self.api_key = os.getenv('SEMRUSH_API_KEY')
        self.base_url = "https://api.semrush.com/"
        self.timeout = 30.0
        
        if not self.api_key:
            logger.warning("SEMRUSH_API_KEY not found. SEMrush features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("SEMrush API initialized")
    
    async def get_keyword_overview(
        self,
        keyword: str,
        database: str = 'us',
        export_columns: str = 'Ph,Nq,Cp,Co,Nr,Td'
    ) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات جامع کلمه کلیدی
        
        Args:
            keyword: کلمه کلیدی مورد نظر
            database: دیتابیس (us, uk, ca, au, de, fr, ru, es, it, br, jp, in, etc.)
            export_columns: ستون‌های مورد نیاز
                - Ph: Phrase (کلمه کلیدی)
                - Nq: Search Volume (حجم جستجو)
                - Cp: CPC (هزینه هر کلیک)
                - Co: Competition (رقابت)
                - Nr: Number of Results (تعداد نتایج)
                - Td: Trend (روند)
                - Kd: Keyword Difficulty (سختی کلمه کلیدی)
        
        Returns:
            {
                'keyword': str,
                'search_volume': int,
                'cpc': float,
                'competition': float,  # 0.00-1.00
                'competition_level': str,  # Low, Medium, High
                'number_of_results': int,
                'trend': List[int],  # 12 ماه گذشته
                'difficulty': int,  # 0-100 (Keyword Difficulty)
                'difficulty_level': str  # Easy, Medium, Hard
            }
        """
        if not self.enabled:
            logger.warning("SEMrush API not enabled. Please set SEMRUSH_API_KEY.")
            return None
        
        try:
            params = {
                'key': self.api_key,
                'type': 'phrase_this',
                'phrase': keyword,
                'database': database,
                'export_columns': export_columns
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_keyword_overview(response.text, keyword)
                elif response.status_code == 200 and 'ERROR' in response.text:
                    error_msg = response.text.split('\n')[0] if '\n' in response.text else response.text
                    logger.error(f"SEMrush API error: {error_msg}")
                    return None
                else:
                    logger.error(f"SEMrush API HTTP error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("SEMrush API request timeout")
            return None
        except Exception as e:
            logger.error(f"Error fetching keyword overview from SEMrush: {str(e)}")
            return None
    
    def _parse_keyword_overview(self, response_text: str, keyword: str) -> Dict[str, Any]:
        """پارس کردن پاسخ SEMrush"""
        lines = response_text.strip().split('\n')
        
        if not lines or len(lines) < 2:
            logger.warning("Empty response from SEMrush")
            return None
        
        # فرمت: Phrase;Search Volume;CPC;Competition;Number of Results;Trend
        # یا: Phrase;Search Volume;CPC;Competition;Number of Results;Trend;KD
        data = lines[1].split(';')
        
        if len(data) < 6:
            logger.warning(f"Unexpected response format: {len(data)} columns")
            return None
        
        try:
            # استخراج داده‌ها
            phrase = data[0].strip() if len(data) > 0 else keyword
            search_volume = int(data[1]) if len(data) > 1 and data[1] else 0
            cpc = float(data[2]) if len(data) > 2 and data[2] else 0.0
            competition = float(data[3]) if len(data) > 3 and data[3] else 0.0
            number_of_results = int(data[4]) if len(data) > 4 and data[4] else 0
            
            # Trend (12 ماه - فرمت: "1,2,3,4,5,6,7,8,9,10,11,12")
            trend_data = data[5].split(',') if len(data) > 5 and data[5] else []
            trend = [int(x.strip()) for x in trend_data[:12] if x.strip().isdigit()]
            
            # Keyword Difficulty (اگر موجود باشد)
            difficulty = int(data[6]) if len(data) > 6 and data[6] else None
            
            # اگر Difficulty موجود نبود، محاسبه می‌کنیم
            if difficulty is None:
                difficulty = self._calculate_difficulty_from_competition(competition, search_volume)
            
            # تعیین سطح رقابت
            if competition < 0.3:
                competition_level = 'Low'
            elif competition < 0.7:
                competition_level = 'Medium'
            else:
                competition_level = 'High'
            
            # تعیین سطح سختی
            if difficulty < 30:
                difficulty_level = 'Easy'
            elif difficulty < 70:
                difficulty_level = 'Medium'
            else:
                difficulty_level = 'Hard'
            
            return {
                'keyword': phrase,
                'search_volume': search_volume,
                'cpc': round(cpc, 2),
                'competition': round(competition, 2),
                'competition_level': competition_level,
                'number_of_results': number_of_results,
                'trend': trend,
                'difficulty': difficulty,
                'difficulty_level': difficulty_level,
                'opportunity_score': self._calculate_opportunity_score(
                    search_volume,
                    difficulty,
                    competition
                ),
                'source': 'semrush'
            }
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing SEMrush response: {str(e)}")
            logger.debug(f"Response data: {data}")
            return None
    
    def _calculate_difficulty_from_competition(
        self,
        competition: float,
        search_volume: int
    ) -> int:
        """محاسبه Keyword Difficulty بر اساس Competition و Search Volume"""
        # فرمول ترکیبی
        base_difficulty = int(competition * 100)  # 0-100 از competition
        
        # تعدیل بر اساس Search Volume
        if search_volume > 100000:
            volume_adjustment = 20
        elif search_volume > 10000:
            volume_adjustment = 10
        elif search_volume > 1000:
            volume_adjustment = 0
        else:
            volume_adjustment = -10
        
        difficulty = base_difficulty + volume_adjustment
        return max(0, min(100, difficulty))
    
    def _calculate_opportunity_score(
        self,
        search_volume: int,
        difficulty: int,
        competition: float
    ) -> float:
        """محاسبه Opportunity Score (0-100)"""
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
        
        # محاسبه Opportunity
        opportunity = (normalized_volume * (100 - difficulty)) / 100
        
        # تعدیل بر اساس رقابت
        if competition < 0.3:
            opportunity *= 1.3
        elif competition > 0.7:
            opportunity *= 0.7
        
        return min(round(opportunity, 2), 100)
    
    async def get_related_keywords(
        self,
        keyword: str,
        database: str = 'us',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        دریافت کلمات کلیدی مرتبط
        
        Args:
            keyword: کلمه کلیدی اصلی
            database: دیتابیس
            limit: حداکثر تعداد نتایج
        
        Returns:
            لیست کلمات کلیدی مرتبط با معیارها
        """
        if not self.enabled:
            logger.warning("SEMrush API not enabled")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'type': 'phrase_related',
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Kd'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_related_keywords(response.text, limit)
                else:
                    logger.error(f"SEMrush API HTTP error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching related keywords: {str(e)}")
            return []
    
    def _parse_related_keywords(
        self,
        response_text: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """پارس کردن کلمات کلیدی مرتبط"""
        keywords = []
        lines = response_text.strip().split('\n')
        
        # خط اول header است
        for line in lines[1:limit+1]:
            if not line.strip():
                continue
            
            data = line.split(';')
            if len(data) >= 5:
                try:
                    keyword_data = {
                        'keyword': data[0].strip(),
                        'search_volume': int(data[1]) if data[1] else 0,
                        'cpc': float(data[2]) if data[2] else 0.0,
                        'competition': float(data[3]) if data[3] else 0.0,
                        'difficulty': int(data[4]) if len(data) > 4 and data[4] else 0,
                        'source': 'semrush'
                    }
                    
                    # محاسبه Opportunity Score
                    keyword_data['opportunity_score'] = self._calculate_opportunity_score(
                        keyword_data['search_volume'],
                        keyword_data['difficulty'],
                        keyword_data['competition']
                    )
                    
                    keywords.append(keyword_data)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing keyword line: {line[:50]}... Error: {str(e)}")
                    continue
        
        return keywords
    
    async def get_keyword_gap(
        self,
        site_url: str,
        competitor_urls: List[str],
        database: str = 'us',
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        تحلیل فاصله کلمات کلیدی (Keyword Gap Analysis)
        
        Args:
            site_url: آدرس سایت شما
            competitor_urls: لیست آدرس‌های رقبا
            database: دیتابیس
            limit: حداکثر تعداد کلمات کلیدی برای هر سایت
        
        Returns:
            {
                'your_keywords': List[Dict],  # کلمات کلیدی شما
                'competitor_keywords': Dict[str, List[Dict]],  # کلمات کلیدی هر رقیب
                'opportunities': List[Dict],  # کلمات کلیدی که رقبا دارند اما شما ندارید
                'advantages': List[Dict],  # کلمات کلیدی که شما دارید اما رقبا ندارند
                'common_keywords': List[Dict],  # کلمات کلیدی مشترک
                'summary': {
                    'your_total': int,
                    'competitors_total': int,
                    'opportunities_count': int,
                    'advantages_count': int,
                    'common_count': int
                }
            }
        """
        if not self.enabled:
            logger.warning("SEMrush API not enabled")
            return self._empty_gap_analysis()
        
        try:
            # دریافت کلمات کلیدی سایت شما
            your_keywords = await self._get_organic_keywords(site_url, database, limit)
            
            # دریافت کلمات کلیدی رقبا
            competitor_keywords = {}
            for competitor_url in competitor_urls:
                try:
                    keywords = await self._get_organic_keywords(
                        competitor_url,
                        database,
                        limit
                    )
                    competitor_keywords[competitor_url] = keywords
                except Exception as e:
                    logger.error(f"Error fetching keywords for {competitor_url}: {str(e)}")
                    competitor_keywords[competitor_url] = []
            
            # تحلیل Gap
            return self._analyze_keyword_gap(
                your_keywords,
                competitor_keywords
            )
            
        except Exception as e:
            logger.error(f"Error in keyword gap analysis: {str(e)}")
            return self._empty_gap_analysis()
    
    async def _get_organic_keywords(
        self,
        url: str,
        database: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی ارگانیک یک سایت"""
        try:
            # استخراج دامنه
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            
            params = {
                'key': self.api_key,
                'type': 'domain_organic',
                'domain': domain,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Tr,Tc,Sh,Ab,Fp,Fp,Ur',
                'display_limit': limit
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_organic_keywords(response.text, limit)
                else:
                    logger.error(f"Error fetching organic keywords for {domain}: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting organic keywords: {str(e)}")
            return []
    
    def _parse_organic_keywords(
        self,
        response_text: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """پارس کردن کلمات کلیدی ارگانیک"""
        keywords = []
        lines = response_text.strip().split('\n')
        
        for line in lines[1:limit+1]:
            if not line.strip():
                continue
            
            data = line.split(';')
            if len(data) >= 4:
                try:
                    keywords.append({
                        'keyword': data[0].strip(),
                        'search_volume': int(data[1]) if data[1] else 0,
                        'cpc': float(data[2]) if data[2] else 0.0,
                        'competition': float(data[3]) if data[3] else 0.0,
                        'position': int(data[4]) if len(data) > 4 and data[4] else None,
                        'source': 'semrush'
                    })
                except (ValueError, IndexError):
                    continue
        
        return keywords
    
    def _analyze_keyword_gap(
        self,
        your_keywords: List[Dict[str, Any]],
        competitor_keywords: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """تحلیل فاصله کلمات کلیدی"""
        
        # ایجاد set از کلمات کلیدی شما
        your_keyword_set = {kw['keyword'].lower() for kw in your_keywords}
        
        # ایجاد set از کلمات کلیدی رقبا
        all_competitor_keywords = {}
        competitor_keyword_set = set()
        
        for competitor_url, keywords in competitor_keywords.items():
            keyword_set = {kw['keyword'].lower() for kw in keywords}
            competitor_keyword_set.update(keyword_set)
            all_competitor_keywords[competitor_url] = keyword_set
        
        # فرصت‌ها: کلمات کلیدی که رقبا دارند اما شما ندارید
        opportunities_keywords = competitor_keyword_set - your_keyword_set
        
        # مزیت‌ها: کلمات کلیدی که شما دارید اما رقبا ندارند
        advantages_keywords = your_keyword_set - competitor_keyword_set
        
        # کلمات کلیدی مشترک
        common_keywords = your_keyword_set & competitor_keyword_set
        
        # تبدیل به لیست با جزئیات
        opportunities = [
            self._find_keyword_details(kw, competitor_keywords)
            for kw in opportunities_keywords
        ]
        
        advantages = [
            self._find_keyword_details(kw, your_keywords, is_yours=True)
            for kw in advantages_keywords
        ]
        
        common = [
            self._find_keyword_details(kw, your_keywords, is_yours=True)
            for kw in common_keywords
        ]
        
        # مرتب‌سازی بر اساس Search Volume
        opportunities.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
        advantages.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
        common.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
        
        return {
            'your_keywords': your_keywords,
            'competitor_keywords': {
                url: keywords
                for url, keywords in competitor_keywords.items()
            },
            'opportunities': opportunities[:50],  # 50 فرصت برتر
            'advantages': advantages[:50],  # 50 مزیت برتر
            'common_keywords': common[:50],  # 50 کلمه کلیدی مشترک برتر
            'summary': {
                'your_total': len(your_keywords),
                'competitors_total': sum(len(kws) for kws in competitor_keywords.values()),
                'opportunities_count': len(opportunities),
                'advantages_count': len(advantages),
                'common_count': len(common)
            }
        }
    
    def _find_keyword_details(
        self,
        keyword: str,
        keyword_list: List[Dict[str, Any]],
        is_yours: bool = False
    ) -> Dict[str, Any]:
        """پیدا کردن جزئیات یک کلمه کلیدی"""
        keyword_lower = keyword.lower()
        
        for kw in keyword_list:
            if kw['keyword'].lower() == keyword_lower:
                return kw.copy()
        
        # اگر پیدا نشد، یک ساختار پیش‌فرض برمی‌گرداند
        return {
            'keyword': keyword,
            'search_volume': 0,
            'cpc': 0.0,
            'competition': 0.0,
            'source': 'semrush'
        }
    
    def _empty_gap_analysis(self) -> Dict[str, Any]:
        """برگرداندن ساختار خالی برای Gap Analysis"""
        return {
            'your_keywords': [],
            'competitor_keywords': {},
            'opportunities': [],
            'advantages': [],
            'common_keywords': [],
            'summary': {
                'your_total': 0,
                'competitors_total': 0,
                'opportunities_count': 0,
                'advantages_count': 0,
                'common_count': 0
            }
        }
    
    async def get_bulk_keyword_overview(
        self,
        keywords: List[str],
        database: str = 'us',
        max_concurrent: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        دریافت معیارهای چند کلمه کلیدی به صورت همزمان
        
        Args:
            keywords: لیست کلمات کلیدی
            database: دیتابیس
            max_concurrent: حداکثر درخواست همزمان
        
        Returns:
            Dictionary با کلید کلمه کلیدی و مقدار معیارها
        """
        results = {}
        
        # استفاده از semaphore برای محدود کردن درخواست‌های همزمان
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(keyword: str):
            async with semaphore:
                overview = await self.get_keyword_overview(keyword, database)
                if overview:
                    results[keyword.lower()] = overview
                # تاخیر کوتاه برای جلوگیری از Rate Limiting
                await asyncio.sleep(0.5)
        
        # اجرای همزمان
        tasks = [fetch_with_semaphore(kw) for kw in keywords]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results

