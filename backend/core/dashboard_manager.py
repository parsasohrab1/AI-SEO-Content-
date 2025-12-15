"""
ماژول مدیریت Dashboard
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardManager:
    """کلاس مدیریت Dashboard"""
    
    _instance = None
    _dashboards = {}  # Shared in-memory storage
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(DashboardManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # در آینده اینجا Connection به Database خواهد بود
        # Use class-level storage so all instances share the same data
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
    async def create_dashboard(self, analysis_id: str, site_url: str) -> str:
        """
        ایجاد Dashboard جدید
        
        Args:
            analysis_id: شناسه تحلیل
            site_url: آدرس سایت
            
        Returns:
            URL داشبورد
        """
        logger.info(f"Creating dashboard for analysis: {analysis_id}")
        
        dashboard_data = {
            'analysis_id': analysis_id,
            'site_url': site_url,
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'data': {}
        }
        
        DashboardManager._dashboards[analysis_id] = dashboard_data
        
        # در Production این URL واقعی خواهد بود
        dashboard_url = f"/dashboard/{analysis_id}"
        
        return dashboard_url
    
    async def update_dashboard(
        self,
        analysis_id: str,
        data: Dict[str, Any]
    ):
        """
        به‌روزرسانی Dashboard
        
        Args:
            analysis_id: شناسه تحلیل
            data: داده‌های جدید
        """
        logger.info(f"Updating dashboard: {analysis_id}")
        
        if analysis_id not in DashboardManager._dashboards:
            logger.warning(f"Dashboard not found: {analysis_id}")
            return
        
        DashboardManager._dashboards[analysis_id]['data'].update(data)
        DashboardManager._dashboards[analysis_id]['updated_at'] = datetime.now().isoformat()
        
        if 'status' in data:
            DashboardManager._dashboards[analysis_id]['status'] = data['status']
    
    async def get_dashboard_data(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت داده‌های Dashboard
        
        Args:
            analysis_id: شناسه تحلیل
            
        Returns:
            داده‌های Dashboard یا None
        """
        if analysis_id not in DashboardManager._dashboards:
            logger.warning(f"Dashboard not found: {analysis_id}")
            return None
        
        dashboard = DashboardManager._dashboards[analysis_id].copy()
        
        # استخراج نقاط قوت و ضعف از داده‌های تحلیل
        strengths, weaknesses = self._extract_strengths_weaknesses(dashboard.get('data', {}))
        dashboard['strengths'] = strengths
        dashboard['weaknesses'] = weaknesses
        
        return dashboard
    
    def _extract_strengths_weaknesses(self, data: Dict[str, Any]) -> tuple:
        """
        استخراج نقاط قوت و ضعف از داده‌های تحلیل
        
        Returns:
            (strengths, weaknesses) - لیست نقاط قوت و ضعف
        """
        strengths = []
        weaknesses = []
        
        site_analysis = data.get('site_analysis', {})
        seo_analysis = data.get('seo_analysis', {})
        
        # تحلیل امنیت
        security = site_analysis.get('security', {})
        if security.get('ssl_enabled'):
            strengths.append({
                'title': 'استفاده از HTTPS',
                'description': 'سایت از پروتکل امن HTTPS استفاده می‌کند',
                'category': 'امنیت'
            })
        else:
            weaknesses.append({
                'title': 'عدم استفاده از HTTPS',
                'description': 'سایت از پروتکل امن HTTPS استفاده نمی‌کند',
                'category': 'امنیت',
                'priority': 'high'
            })
        
        # تحلیل Sitemap
        sitemap = site_analysis.get('sitemap', {})
        if sitemap.get('found'):
            strengths.append({
                'title': 'وجود Sitemap',
                'description': 'سایت دارای فایل Sitemap است که به موتورهای جستجو کمک می‌کند',
                'category': 'سئو'
            })
        else:
            weaknesses.append({
                'title': 'عدم وجود Sitemap',
                'description': 'سایت فایل Sitemap ندارد که می‌تواند بر ایندکس شدن صفحات تأثیر بگذارد',
                'category': 'سئو',
                'priority': 'medium'
            })
        
        # تحلیل ساختار
        structure = site_analysis.get('structure', {})
        headings = structure.get('headings', {})
        if headings.get('h1', 0) == 1:
            strengths.append({
                'title': 'ساختار صحیح H1',
                'description': 'صفحه دارای یک تگ H1 است که برای سئو مناسب است',
                'category': 'ساختار'
            })
        elif headings.get('h1', 0) == 0:
            weaknesses.append({
                'title': 'عدم وجود تگ H1',
                'description': 'صفحه اصلی فاقد تگ H1 است که برای سئو ضروری است',
                'category': 'ساختار',
                'priority': 'high'
            })
        elif headings.get('h1', 0) > 1:
            weaknesses.append({
                'title': 'چندین تگ H1',
                'description': f'صفحه دارای {headings.get("h1")} تگ H1 است که باید فقط یک عدد باشد',
                'category': 'ساختار',
                'priority': 'medium'
            })
        
        # تحلیل لینک‌ها
        links = structure.get('links', {})
        if links.get('internal', 0) > 0:
            strengths.append({
                'title': 'وجود لینک‌های داخلی',
                'description': f'صفحه دارای {links.get("internal")} لینک داخلی است که به سئو کمک می‌کند',
                'category': 'ساختار'
            })
        
        # تحلیل عملکرد
        performance = site_analysis.get('performance', {})
        response_time = performance.get('response_time')
        if response_time and response_time < 2.0:
            strengths.append({
                'title': 'زمان بارگذاری مناسب',
                'description': f'زمان پاسخ سرور {response_time:.2f} ثانیه است که مناسب است',
                'category': 'عملکرد'
            })
        elif response_time and response_time > 3.0:
            weaknesses.append({
                'title': 'زمان بارگذاری کند',
                'description': f'زمان پاسخ سرور {response_time:.2f} ثانیه است که می‌تواند بهبود یابد',
                'category': 'عملکرد',
                'priority': 'medium'
            })
        
        # تحلیل CMS
        cms_type = site_analysis.get('cms_type', 'custom')
        if cms_type != 'custom':
            strengths.append({
                'title': f'استفاده از CMS ({cms_type})',
                'description': f'سایت از سیستم مدیریت محتوای {cms_type} استفاده می‌کند',
                'category': 'فناوری'
            })
        
        # تحلیل Technology Stack
        tech_stack = site_analysis.get('technology_stack', {})
        if tech_stack.get('analytics'):
            strengths.append({
                'title': 'نصب ابزارهای آنالیتیکس',
                'description': f'سایت از {", ".join(tech_stack.get("analytics", []))} استفاده می‌کند',
                'category': 'فناوری'
            })
        
        # SEO Issues
        seo_issues = seo_analysis.get('issues', [])
        if not seo_issues:
            strengths.append({
                'title': 'عدم وجود مشکل سئو',
                'description': 'هیچ مشکل سئوی شناسایی شده‌ای وجود ندارد',
                'category': 'سئو'
            })
        else:
            for issue in seo_issues:
                weaknesses.append({
                    'title': issue.get('title', 'مشکل سئو'),
                    'description': issue.get('description', ''),
                    'category': 'سئو',
                    'priority': issue.get('priority', 'medium')
                })
        
        # اگر هیچ نقطه قوت یا ضعفی پیدا نشد
        if not strengths:
            strengths.append({
                'title': 'تحلیل در حال انجام است',
                'description': 'داده‌های تحلیل هنوز کامل نشده است',
                'category': 'وضعیت'
            })
        
        if not weaknesses:
            weaknesses.append({
                'title': 'هیچ نقطه ضعفی شناسایی نشد',
                'description': 'تحلیل اولیه هیچ مشکل خاصی نشان نداده است',
                'category': 'وضعیت',
                'priority': 'low'
            })
        
        return strengths, weaknesses

