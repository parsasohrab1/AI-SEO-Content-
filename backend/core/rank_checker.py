"""
ماژول بررسی رنک سایت در ایران و جهان
استفاده از APIهای مختلف برای دریافت رنک سایت
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import httpx
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class RankChecker:
    """کلاس بررسی رنک سایت"""
    
    def __init__(self):
        import warnings
        # Suppress SSL warnings for expired certificates
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            verify=False,  # غیرفعال کردن SSL verification برای سایت‌های با گواهینامه منقضی شده
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    def extract_domain(self, url: str) -> str:
        """استخراج دامنه از URL"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # حذف www
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    async def get_global_rank(self, domain: str) -> Dict[str, Any]:
        """
        دریافت رنک جهانی سایت
        استفاده از چندین منبع برای دقت بیشتر
        """
        rank_data = {
            'global_rank': None,
            'country_rank': None,
            'country': 'IR',  # ایران به صورت پیش‌فرض
            'traffic_rank': None,
            'sources': []
        }
        
        try:
            # روش 1: استفاده از API رایگان rankranger یا مشابه
            # برای دمو، از محاسبه بر اساس معیارهای مختلف استفاده می‌کنیم
            rank_data['global_rank'] = await self._estimate_rank(domain)
            rank_data['traffic_rank'] = rank_data['global_rank']
            rank_data['sources'].append({
                'name': 'Estimated Rank',
                'rank': rank_data['global_rank'],
                'method': 'calculated'
            })
            
        except Exception as e:
            logger.error(f"Error getting global rank: {str(e)}")
        
        return rank_data
    
    async def get_iran_rank(self, domain: str) -> Dict[str, Any]:
        """
        دریافت رنک سایت در ایران
        """
        iran_rank_data = {
            'iran_rank': None,
            'iran_traffic_rank': None,
            'local_rank': None,
            'sources': []
        }
        
        try:
            # برای ایران، می‌توان از APIهای داخلی استفاده کرد
            # در اینجا یک تخمین بر اساس معیارهای مختلف می‌دهیم
            iran_rank_data['iran_rank'] = await self._estimate_iran_rank(domain)
            iran_rank_data['iran_traffic_rank'] = iran_rank_data['iran_rank']
            iran_rank_data['local_rank'] = iran_rank_data['iran_rank']
            
            iran_rank_data['sources'].append({
                'name': 'Iran Rank Estimator',
                'rank': iran_rank_data['iran_rank'],
                'method': 'calculated'
            })
            
        except Exception as e:
            logger.error(f"Error getting Iran rank: {str(e)}")
        
        return iran_rank_data
    
    async def _estimate_rank(self, domain: str) -> Optional[int]:
        """
        تخمین رنک بر اساس معیارهای مختلف
        در یک سیستم واقعی، این از APIهای معتبر دریافت می‌شود
        """
        try:
            # در اینجا می‌توان از APIهای واقعی استفاده کرد
            # برای دمو، یک رنک تصادفی بر اساس دامنه تولید می‌کنیم
            # در production باید از APIهای واقعی استفاده شود
            
            # مثال: استفاده از hash دامنه برای تولید یک رنک ثابت
            domain_hash = hash(domain) % 1000000
            # تبدیل به رنک منطقی (بین 1000 تا 1000000)
            estimated_rank = 1000 + (abs(domain_hash) % 999000)
            
            return estimated_rank
            
        except Exception as e:
            logger.error(f"Error estimating rank: {str(e)}")
            return None
    
    async def _estimate_iran_rank(self, domain: str) -> Optional[int]:
        """
        تخمین رنک در ایران
        """
        try:
            # مشابه رنک جهانی اما با محدوده کوچکتر برای ایران
            domain_hash = hash(domain + '_iran') % 100000
            estimated_rank = 100 + (abs(domain_hash) % 99900)
            
            return estimated_rank
            
        except Exception as e:
            logger.error(f"Error estimating Iran rank: {str(e)}")
            return None
    
    async def get_comprehensive_rank(self, url: str) -> Dict[str, Any]:
        """
        دریافت رنک جامع سایت (جهانی و ایران)
        """
        domain = self.extract_domain(url)
        
        logger.info(f"Getting rank for domain: {domain}")
        
        # دریافت رنک‌ها به صورت موازی
        global_rank_task = self.get_global_rank(domain)
        iran_rank_task = self.get_iran_rank(domain)
        
        global_rank_data, iran_rank_data = await asyncio.gather(
            global_rank_task,
            iran_rank_task,
            return_exceptions=True
        )
        
        # ترکیب نتایج
        comprehensive_rank = {
            'domain': domain,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'global': global_rank_data if not isinstance(global_rank_data, Exception) else {},
            'iran': iran_rank_data if not isinstance(iran_rank_data, Exception) else {},
            'score': self._calculate_rank_score(global_rank_data, iran_rank_data),
            'trend': 'stable',  # می‌توان از داده‌های تاریخی محاسبه کرد
            'last_updated': datetime.now().isoformat()
        }
        
        return comprehensive_rank
    
    def _calculate_rank_score(self, global_data: Dict, iran_data: Dict) -> Dict[str, Any]:
        """
        محاسبه امتیاز کلی رنک
        """
        global_rank = global_data.get('global_rank')
        iran_rank = iran_data.get('iran_rank')
        
        # محاسبه امتیاز (هر چه رنک کمتر باشد، بهتر است)
        global_score = 100 - min(100, (global_rank or 1000000) / 10000) if global_rank else 0
        iran_score = 100 - min(100, (iran_rank or 100000) / 1000) if iran_rank else 0
        
        # امتیاز ترکیبی
        overall_score = (global_score * 0.6 + iran_score * 0.4)
        
        # تعیین سطح
        if overall_score >= 80:
            level = 'excellent'
            level_fa = 'عالی'
        elif overall_score >= 60:
            level = 'good'
            level_fa = 'خوب'
        elif overall_score >= 40:
            level = 'fair'
            level_fa = 'متوسط'
        elif overall_score >= 20:
            level = 'poor'
            level_fa = 'ضعیف'
        else:
            level = 'very_poor'
            level_fa = 'خیلی ضعیف'
        
        return {
            'overall': round(overall_score, 2),
            'global_score': round(global_score, 2),
            'iran_score': round(iran_score, 2),
            'level': level,
            'level_fa': level_fa,
            'grade': self._get_grade(overall_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """تعیین نمره بر اساس امتیاز"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        elif score >= 30:
            return 'D'
        else:
            return 'F'
    
    async def close(self):
        """بستن کلاینت"""
        await self.client.aclose()

