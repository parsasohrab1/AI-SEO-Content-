"""
ماژول تولید گزارش
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """کلاس تولید گزارش"""
    
    async def generate_seo_report(self, analysis_id: str) -> Dict[str, Any]:
        """
        تولید گزارش کامل سئو
        
        Args:
            analysis_id: شناسه تحلیل
            
        Returns:
            گزارش سئو
        """
        logger.info(f"Generating SEO report for: {analysis_id}")
        
        try:
            from core.dashboard_manager import DashboardManager
            
            # دریافت داده‌های داشبورد
            dashboard_manager = DashboardManager()
            dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
            
            if not dashboard_data:
                return {
                    'analysis_id': analysis_id,
                    'error': 'Dashboard not found',
                    'generated_at': datetime.now().isoformat()
                }
            
            # استخراج داده‌ها
            site_analysis = dashboard_data.get('data', {}).get('site_analysis', {})
            seo_analysis = dashboard_data.get('data', {}).get('seo_analysis', {})
            strengths = dashboard_data.get('strengths', [])
            weaknesses = dashboard_data.get('weaknesses', [])
            implementation = dashboard_data.get('data', {}).get('implementation', {})
            generated_content = dashboard_data.get('data', {}).get('generated_content', {})
            
            # تولید گزارش
            report = {
                'analysis_id': analysis_id,
                'site_url': dashboard_data.get('site_url', ''),
                'status': dashboard_data.get('status', 'unknown'),
                'generated_at': datetime.now().isoformat(),
                'created_at': dashboard_data.get('created_at'),
                'updated_at': dashboard_data.get('updated_at'),
                
                # خلاصه اجرایی
                'executive_summary': self._generate_executive_summary(
                    site_analysis, seo_analysis, strengths, weaknesses
                ),
                
                # تحلیل فنی
                'technical_analysis': self._generate_technical_analysis(site_analysis, seo_analysis),
                
                # تحلیل محتوا
                'content_analysis': self._generate_content_analysis(site_analysis, seo_analysis),
                
                # تحلیل امنیت
                'security_analysis': self._generate_security_analysis(site_analysis),
                
                # تحلیل عملکرد
                'performance_analysis': self._generate_performance_analysis(site_analysis),
                
                # نقاط قوت و ضعف
                'strengths': strengths,
                'weaknesses': weaknesses,
                
                # مشکلات و راه‌حل‌ها
                'issues_and_solutions': self._generate_issues_solutions(weaknesses, seo_analysis),
                
                # نتایج پیاده‌سازی
                'implementation_results': implementation,
                
                # محتوای تولید شده
                'generated_content_summary': self._generate_content_summary(generated_content),
                
                # امتیاز کلی
                'overall_score': self._calculate_overall_score(
                    site_analysis, seo_analysis, strengths, weaknesses
                ),
                
                # توصیه‌های اولویت‌دار
                'priority_recommendations': self._generate_priority_recommendations(weaknesses),
                
                # جدول زمانی پیشنهادی
                'implementation_timeline': self._generate_implementation_timeline(weaknesses)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating SEO report: {str(e)}")
            return {
                'analysis_id': analysis_id,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _generate_executive_summary(
        self, 
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any],
        strengths: list,
        weaknesses: list
    ) -> Dict[str, Any]:
        """تولید خلاصه اجرایی"""
        total_issues = len(weaknesses)
        high_priority_issues = len([w for w in weaknesses if w.get('priority') == 'high'])
        
        return {
            'total_strengths': len(strengths),
            'total_weaknesses': total_issues,
            'high_priority_issues': high_priority_issues,
            'medium_priority_issues': len([w for w in weaknesses if w.get('priority') == 'medium']),
            'low_priority_issues': len([w for w in weaknesses if w.get('priority') == 'low']),
            'cms_type': site_analysis.get('cms_type', 'unknown'),
            'has_ssl': site_analysis.get('security', {}).get('ssl_enabled', False),
            'has_sitemap': site_analysis.get('sitemap', {}).get('found', False),
            'summary': f"این سایت دارای {len(strengths)} نقطه قوت و {total_issues} نقطه ضعف است. "
                      f"{high_priority_issues} مشکل با اولویت بالا نیاز به توجه فوری دارد."
        }
    
    def _generate_technical_analysis(
        self, 
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تولید تحلیل فنی"""
        technical = seo_analysis.get('technical', {})
        structure = site_analysis.get('structure', {})
        headings = structure.get('headings', {})
        
        return {
            'crawlability': technical.get('crawlability', 'unknown'),
            'indexability': technical.get('indexability', 'unknown'),
            'core_web_vitals': technical.get('core_web_vitals', {}),
            'headings_structure': {
                'h1_count': headings.get('h1', 0),
                'h2_count': headings.get('h2', 0),
                'h3_count': headings.get('h3', 0),
                'h1_status': 'good' if headings.get('h1', 0) == 1 else 'needs_improvement'
            },
            'sitemap': {
                'found': site_analysis.get('sitemap', {}).get('found', False),
                'url': site_analysis.get('sitemap', {}).get('url')
            },
            'links': structure.get('links', {}),
            'images_count': structure.get('images', 0),
            'forms_count': structure.get('forms', 0)
        }
    
    def _generate_content_analysis(
        self,
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تولید تحلیل محتوا"""
        content = seo_analysis.get('content', {})
        
        return {
            'keywords': content.get('keywords', []),
            'readability_score': content.get('readability', 0),
            'readability_status': self._get_readability_status(content.get('readability', 0)),
            'content_structure': {
                'has_meta_description': True,  # TODO: Extract from actual analysis
                'has_meta_title': True,
                'has_og_tags': False
            }
        }
    
    def _generate_security_analysis(self, site_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """تولید تحلیل امنیت"""
        security = site_analysis.get('security', {})
        security_headers = security.get('security_headers', {})
        
        return {
            'ssl_enabled': security.get('ssl_enabled', False),
            'security_headers': {
                'x_frame_options': security_headers.get('x_frame_options'),
                'x_content_type_options': security_headers.get('x_content_type_options'),
                'strict_transport_security': security_headers.get('strict_transport_security'),
                'content_security_policy': security_headers.get('content_security_policy')
            },
            'vulnerabilities': security.get('vulnerabilities', []),
            'security_score': self._calculate_security_score(security)
        }
    
    def _generate_performance_analysis(self, site_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """تولید تحلیل عملکرد"""
        performance = site_analysis.get('performance', {})
        response_time = performance.get('response_time')
        
        return {
            'response_time': response_time,
            'response_time_status': self._get_response_time_status(response_time),
            'status_code': performance.get('status_code'),
            'content_length': performance.get('content_length'),
            'performance_score': self._calculate_performance_score(performance)
        }
    
    def _generate_issues_solutions(
        self,
        weaknesses: list,
        seo_analysis: Dict[str, Any]
    ) -> list:
        """تولید لیست مشکلات و راه‌حل‌ها"""
        issues = []
        
        for weakness in weaknesses:
            solution = self._get_solution_for_weakness(weakness)
            issues.append({
                'issue': weakness.get('title', ''),
                'description': weakness.get('description', ''),
                'priority': weakness.get('priority', 'medium'),
                'category': weakness.get('category', ''),
                'solution': solution,
                'estimated_time': solution.get('estimated_time', 'N/A'),
                'difficulty': solution.get('difficulty', 'medium')
            })
        
        # اضافه کردن مشکلات از seo_analysis
        seo_issues = seo_analysis.get('issues', [])
        for issue in seo_issues:
            issues.append({
                'issue': issue.get('title', 'SEO Issue'),
                'description': issue.get('description', ''),
                'priority': issue.get('priority', 'medium'),
                'category': 'سئو',
                'solution': {
                    'steps': issue.get('solution', ['بررسی و اصلاح مورد نیاز']),
                    'estimated_time': '1-2 ساعت',
                    'difficulty': 'medium'
                }
            })
        
        return issues
    
    def _generate_content_summary(self, generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """خلاصه محتوای تولید شده"""
        if not generated_content:
            return {
                'total_items': 0,
                'total_words': 0,
                'content_types': []
            }
        
        content_items = generated_content.get('content_items', [])
        return {
            'total_items': len(content_items),
            'total_words': generated_content.get('total_words', 0),
            'content_types': generated_content.get('content_types', []),
            'items': content_items[:5]  # فقط 5 مورد اول
        }
    
    def _calculate_overall_score(
        self,
        site_analysis: Dict[str, Any],
        seo_analysis: Dict[str, Any],
        strengths: list,
        weaknesses: list
    ) -> Dict[str, Any]:
        """محاسبه امتیاز کلی"""
        scores = {
            'technical': 0,
            'content': 0,
            'security': 0,
            'performance': 0
        }
        
        # امتیاز فنی
        technical = seo_analysis.get('technical', {})
        if technical.get('crawlability') == 'good':
            scores['technical'] += 25
        if technical.get('indexability') == 'good':
            scores['technical'] += 25
        if site_analysis.get('sitemap', {}).get('found'):
            scores['technical'] += 25
        
        # امتیاز محتوا
        content = seo_analysis.get('content', {})
        readability = content.get('readability', 0)
        scores['content'] = min(readability, 100)
        
        # امتیاز امنیت
        security = site_analysis.get('security', {})
        if security.get('ssl_enabled'):
            scores['security'] += 50
        security_headers = security.get('security_headers', {})
        header_count = sum(1 for v in security_headers.values() if v)
        scores['security'] += header_count * 12.5
        
        # امتیاز عملکرد
        performance = site_analysis.get('performance', {})
        response_time = performance.get('response_time')
        if response_time:
            if response_time < 1:
                scores['performance'] = 100
            elif response_time < 2:
                scores['performance'] = 80
            elif response_time < 3:
                scores['performance'] = 60
            else:
                scores['performance'] = 40
        
        # محاسبه امتیاز کلی
        overall = sum(scores.values()) / len(scores)
        
        # تعدیل بر اساس نقاط قوت و ضعف
        strength_bonus = len(strengths) * 2
        weakness_penalty = len(weaknesses) * 3
        
        overall = max(0, min(100, overall + strength_bonus - weakness_penalty))
        
        return {
            'overall': round(overall, 1),
            'breakdown': scores,
            'grade': self._get_grade(overall)
        }
    
    def _generate_priority_recommendations(self, weaknesses: list) -> list:
        """تولید توصیه‌های اولویت‌دار"""
        recommendations = []
        
        high_priority = [w for w in weaknesses if w.get('priority') == 'high']
        for weakness in high_priority[:5]:  # فقط 5 مورد اول
            recommendations.append({
                'title': weakness.get('title', ''),
                'priority': 'high',
                'impact': 'تأثیر بالا بر سئو و عملکرد سایت',
                'action': self._get_action_for_weakness(weakness)
            })
        
        return recommendations
    
    def _generate_implementation_timeline(self, weaknesses: list) -> list:
        """تولید جدول زمانی پیشنهادی"""
        timeline = []
        
        high_priority = [w for w in weaknesses if w.get('priority') == 'high']
        medium_priority = [w for w in weaknesses if w.get('priority') == 'medium']
        low_priority = [w for w in weaknesses if w.get('priority') == 'low']
        
        if high_priority:
            timeline.append({
                'phase': 'فاز 1: فوری (هفته اول)',
                'items': [w.get('title') for w in high_priority[:3]],
                'estimated_time': '5-10 ساعت'
            })
        
        if medium_priority:
            timeline.append({
                'phase': 'فاز 2: مهم (هفته 2-3)',
                'items': [w.get('title') for w in medium_priority[:5]],
                'estimated_time': '10-15 ساعت'
            })
        
        if low_priority:
            timeline.append({
                'phase': 'فاز 3: بهبود (ماه بعد)',
                'items': [w.get('title') for w in low_priority[:5]],
                'estimated_time': '5-10 ساعت'
            })
        
        return timeline
    
    # Helper methods
    def _get_readability_status(self, score: int) -> str:
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _get_response_time_status(self, response_time: Optional[float]) -> str:
        if not response_time:
            return 'unknown'
        if response_time < 1:
            return 'excellent'
        elif response_time < 2:
            return 'good'
        elif response_time < 3:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_security_score(self, security: Dict[str, Any]) -> int:
        score = 0
        if security.get('ssl_enabled'):
            score += 50
        security_headers = security.get('security_headers', {})
        header_count = sum(1 for v in security_headers.values() if v)
        score += header_count * 12.5
        return min(100, score)
    
    def _calculate_performance_score(self, performance: Dict[str, Any]) -> int:
        response_time = performance.get('response_time')
        if not response_time:
            return 0
        if response_time < 1:
            return 100
        elif response_time < 2:
            return 80
        elif response_time < 3:
            return 60
        else:
            return 40
    
    def _get_grade(self, score: float) -> str:
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_solution_for_weakness(self, weakness: Dict[str, Any]) -> Dict[str, Any]:
        """دریافت راه‌حل برای نقطه ضعف"""
        title = weakness.get('title', '')
        
        solutions = {
            'عدم استفاده از HTTPS': {
                'steps': [
                    'دریافت گواهینامه SSL از ارائه‌دهنده هاست',
                    'نصب و فعال‌سازی SSL',
                    'تنظیم redirect از HTTP به HTTPS',
                    'به‌روزرسانی تمام لینک‌های داخلی'
                ],
                'estimated_time': '1-2 ساعت',
                'difficulty': 'easy'
            },
            'عدم وجود Sitemap': {
                'steps': [
                    'ایجاد فایل sitemap.xml',
                    'اضافه کردن تمام صفحات مهم',
                    'ثبت sitemap در Google Search Console',
                    'اضافه کردن لینک sitemap به robots.txt'
                ],
                'estimated_time': '30 دقیقه',
                'difficulty': 'easy'
            },
            'عدم وجود تگ H1': {
                'steps': [
                    'افزودن تگ H1 به هر صفحه',
                    'اطمینان از وجود فقط یک H1 در هر صفحه',
                    'استفاده از کلمات کلیدی در H1'
                ],
                'estimated_time': '15 دقیقه',
                'difficulty': 'easy'
            }
        }
        
        return solutions.get(title, {
            'steps': ['بررسی و اصلاح مورد نیاز'],
            'estimated_time': '1 ساعت',
            'difficulty': 'medium'
        })
    
    def _get_action_for_weakness(self, weakness: Dict[str, Any]) -> str:
        """دریافت اقدام برای نقطه ضعف"""
        title = weakness.get('title', '')
        
        actions = {
            'عدم استفاده از HTTPS': 'فعال‌سازی فوری SSL/TLS',
            'عدم وجود Sitemap': 'ایجاد و ثبت Sitemap',
            'عدم وجود تگ H1': 'افزودن تگ H1 به صفحات',
            'زمان بارگذاری کند': 'بهینه‌سازی سرعت سایت'
        }
        
        return actions.get(title, 'بررسی و اصلاح')

