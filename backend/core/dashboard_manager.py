"""
ماژول مدیریت Dashboard
"""

import logging
from typing import Dict, Any, Optional, List
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
        
        try:
            # استخراج نقاط قوت و ضعف از داده‌های تحلیل
            strengths, weaknesses = self._extract_strengths_weaknesses(dashboard.get('data', {}))
            dashboard['strengths'] = strengths
            dashboard['weaknesses'] = weaknesses
            
            # تولید پیشنهادات
            try:
                recommendations = self._generate_recommendations(dashboard.get('data', {}), weaknesses)
                dashboard['recommendations'] = recommendations
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                dashboard['recommendations'] = []
        except Exception as e:
            logger.error(f"Error extracting strengths/weaknesses: {str(e)}")
            dashboard['strengths'] = []
            dashboard['weaknesses'] = []
            dashboard['recommendations'] = []
        
        return dashboard
    
    def _extract_strengths_weaknesses(self, data: Dict[str, Any]) -> tuple:
        """
        استخراج نقاط قوت و ضعف از داده‌های تحلیل
        
        Returns:
            (strengths, weaknesses) - لیست نقاط قوت و ضعف
        """
        strengths = []
        weaknesses = []
        
        site_analysis = data.get('site_analysis', {}) or {}
        seo_analysis = data.get('seo_analysis', {}) or {}
        
        # اطمینان از اینکه site_analysis و seo_analysis دیکشنری هستند
        if not isinstance(site_analysis, dict):
            site_analysis = {}
        if not isinstance(seo_analysis, dict):
            seo_analysis = {}
        
        # تحلیل امنیت
        security = site_analysis.get('security', {}) if isinstance(site_analysis, dict) else {}
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
        sitemap = site_analysis.get('sitemap', {}) if isinstance(site_analysis, dict) else {}
        if isinstance(sitemap, dict) and sitemap.get('found'):
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
        structure = site_analysis.get('structure', {}) if isinstance(site_analysis, dict) else {}
        headings = structure.get('headings', {}) if isinstance(structure, dict) else {}
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
        links = structure.get('links', {}) if isinstance(structure, dict) else {}
        if isinstance(links, dict) and links.get('internal', 0) > 0:
            strengths.append({
                'title': 'وجود لینک‌های داخلی',
                'description': f'صفحه دارای {links.get("internal")} لینک داخلی است که به سئو کمک می‌کند',
                'category': 'ساختار'
            })
        
        # تحلیل عملکرد
        performance = site_analysis.get('performance', {}) if isinstance(site_analysis, dict) else {}
        response_time = performance.get('response_time') if isinstance(performance, dict) else None
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
        cms_type = site_analysis.get('cms_type', 'custom') if isinstance(site_analysis, dict) else 'custom'
        if cms_type != 'custom':
            strengths.append({
                'title': f'استفاده از CMS ({cms_type})',
                'description': f'سایت از سیستم مدیریت محتوای {cms_type} استفاده می‌کند',
                'category': 'فناوری'
            })
        
        # تحلیل Technology Stack
        tech_stack = site_analysis.get('technology_stack', {})
        analytics = tech_stack.get('analytics', []) if isinstance(tech_stack, dict) else []
        if analytics and isinstance(analytics, list) and len(analytics) > 0:
            strengths.append({
                'title': 'نصب ابزارهای آنالیتیکس',
                'description': f'سایت از {", ".join(str(a) for a in analytics)} استفاده می‌کند',
                'category': 'فناوری'
            })
        
        # SEO Issues
        seo_issues = seo_analysis.get('issues', []) if isinstance(seo_analysis, dict) else []
        if not seo_issues or not isinstance(seo_issues, list):
            strengths.append({
                'title': 'عدم وجود مشکل سئو',
                'description': 'هیچ مشکل سئوی شناسایی شده‌ای وجود ندارد',
                'category': 'سئو'
            })
        else:
            for issue in seo_issues:
                if isinstance(issue, dict):
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
    
    def _generate_recommendations(self, data: Dict[str, Any], weaknesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تولید پیشنهادات بر اساس نقاط ضعف
        
        Args:
            data: داده‌های تحلیل
            weaknesses: لیست نقاط ضعف
            
        Returns:
            لیست پیشنهادات
        """
        recommendations = []
        
        # اطمینان از اینکه weaknesses یک لیست است
        if not isinstance(weaknesses, list):
            weaknesses = []
        
        site_analysis = data.get('site_analysis', {}) or {}
        seo_analysis = data.get('seo_analysis', {}) or {}
        
        # تولید پیشنهادات بر اساس نقاط ضعف
        for weakness in weaknesses:
            if not isinstance(weakness, dict):
                continue
            title = weakness.get('title', '')
            category = weakness.get('category', 'عمومی')
            priority = weakness.get('priority', 'medium')
            
            # تولید پیشنهاد بر اساس نوع مشکل
            if 'HTTPS' in title or 'SSL' in title:
                recommendations.append({
                    'id': f'rec_{len(recommendations)}',
                    'title': 'فعال‌سازی HTTPS',
                    'description': 'برای امنیت و سئو بهتر، باید HTTPS را فعال کنید. این کار می‌تواند رتبه سایت را بهبود دهد.',
                    'category': 'امنیت',
                    'priority': 'high',
                    'impact': 'تأثیر بالا بر امنیت و سئو',
                    'estimatedTime': '1-2 ساعت',
                    'automated': False
                })
            elif 'Sitemap' in title:
                recommendations.append({
                    'id': f'rec_{len(recommendations)}',
                    'title': 'ایجاد Sitemap',
                    'description': 'ایجاد فایل Sitemap.xml به موتورهای جستجو کمک می‌کند تا صفحات سایت را بهتر ایندکس کنند.',
                    'category': 'سئو',
                    'priority': 'medium',
                    'impact': 'بهبود ایندکس شدن صفحات',
                    'estimatedTime': '30 دقیقه',
                    'automated': True
                })
            elif 'H1' in title:
                recommendations.append({
                    'id': f'rec_{len(recommendations)}',
                    'title': 'بهبود ساختار H1',
                    'description': 'هر صفحه باید دقیقاً یک تگ H1 داشته باشد که موضوع اصلی صفحه را توصیف کند.',
                    'category': 'ساختار',
                    'priority': 'high',
                    'impact': 'بهبود سئو و خوانایی',
                    'estimatedTime': '15-30 دقیقه',
                    'automated': False
                })
            elif 'زمان بارگذاری' in title or 'عملکرد' in title:
                recommendations.append({
                    'id': f'rec_{len(recommendations)}',
                    'title': 'بهینه‌سازی سرعت سایت',
                    'description': 'بهینه‌سازی تصاویر، استفاده از CDN و فشرده‌سازی فایل‌ها می‌تواند سرعت سایت را بهبود دهد.',
                    'category': 'عملکرد',
                    'priority': 'medium',
                    'impact': 'بهبود تجربه کاربری و سئو',
                    'estimatedTime': '2-4 ساعت',
                    'automated': True
                })
            else:
                # پیشنهاد عمومی
                recommendations.append({
                    'id': f'rec_{len(recommendations)}',
                    'title': f'بهبود {title}',
                    'description': weakness.get('description', 'این مشکل باید برطرف شود تا سئو سایت بهبود یابد.'),
                    'category': category,
                    'priority': priority,
                    'impact': 'بهبود سئو و عملکرد سایت',
                    'estimatedTime': '1-2 ساعت',
                    'automated': False
                })
        
        # پیشنهادات اضافی بر اساس تحلیل سئو
        seo_issues = seo_analysis.get('issues', [])
        if isinstance(seo_issues, list):
            for issue in seo_issues:
                if not isinstance(issue, dict):
                    continue
                if not any(rec.get('title') == issue.get('title') for rec in recommendations):
                    recommendations.append({
                        'id': f'rec_{len(recommendations)}',
                        'title': issue.get('title', 'بهبود سئو'),
                        'description': issue.get('description', 'این مشکل سئو باید برطرف شود.'),
                        'category': 'سئو',
                        'priority': issue.get('priority', 'medium'),
                        'impact': 'بهبود رتبه در موتورهای جستجو',
                        'estimatedTime': '1 ساعت',
                        'automated': issue.get('automated', False)
                    })
        
        # اگر هیچ پیشنهادی تولید نشد
        if not recommendations:
            recommendations.append({
                'id': 'rec_0',
                'title': 'تحلیل در حال انجام است',
                'description': 'پس از تکمیل تحلیل، پیشنهادات در اینجا نمایش داده می‌شوند.',
                'category': 'وضعیت',
                'priority': 'low',
                'impact': 'در انتظار تحلیل',
                'estimatedTime': 'N/A',
                'automated': False
            })
        
        return recommendations

