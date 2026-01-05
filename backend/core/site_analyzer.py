"""
ماژول تحلیل اولیه سایت
شامل: URL Validation, CMS Detection, Technology Stack, Site Structure
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class SiteAnalyzer:
    """کلاس اصلی تحلیل سایت"""
    
    def __init__(self):
        import ssl
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
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        تحلیل کامل سایت
        
        Args:
            url: آدرس سایت
            
        Returns:
            Dict شامل تمام اطلاعات تحلیل شده
        """
        logger.info(f"Starting site analysis for: {url}")
        
        # اعتبارسنجی URL
        validated_url = self.validate_url(url)
        
        # دریافت صفحه اصلی
        html_content = await self.fetch_page(validated_url)
        
        # تحلیل‌های مختلف
        cms_info = await self.detect_cms(html_content, validated_url)
        technology_stack = await self.detect_technology_stack(html_content)
        structure = await self.analyze_structure(html_content, validated_url)
        performance = await self.analyze_performance(validated_url)
        security = await self.analyze_security(validated_url, html_content)
        sitemap = await self.find_sitemap(validated_url)
        
        # اگر cms_info یک string است (برای سازگاری با کد قدیمی)
        if isinstance(cms_info, str):
            cms_type = cms_info
            cms_details = {}
        else:
            cms_type = cms_info.get('cms_type', 'custom')
            cms_details = cms_info
        
        return {
            'url': validated_url,
            'cms_type': cms_type,
            'cms_details': cms_details,  # جزئیات کامل CMS
            'technology_stack': technology_stack,
            'structure': structure,
            'performance': performance,
            'security': security,
            'sitemap': sitemap,
            'analysis_timestamp': asyncio.get_event_loop().time()
        }
    
    def validate_url(self, url: str) -> str:
        """اعتبارسنجی و نرمال‌سازی URL"""
        # اضافه کردن https:// در صورت نیاز
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        # برگرداندن URL کامل
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path or ''}"
    
    async def fetch_page(self, url: str) -> str:
        """دریافت محتوای صفحه"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            # اگر خطای SSL بود، سعی می‌کنیم با HTTP (بدون SSL) تلاش کنیم
            if 'SSL' in str(e) or 'certificate' in str(e).lower():
                logger.warning(f"SSL error for {url}, trying HTTP fallback")
                try:
                    # تبدیل HTTPS به HTTP
                    fallback_url = url.replace('https://', 'http://')
                    response = await self.client.get(fallback_url)
                    response.raise_for_status()
                    return response.text
                except Exception as fallback_error:
                    logger.error(f"Error fetching page {url} (HTTP fallback also failed): {str(fallback_error)}")
                    raise
            logger.error(f"Error fetching page {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching page {url}: {str(e)}")
            raise
    
    async def detect_cms(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        شناسایی CMS و جزئیات آن
        
        Returns:
            Dict شامل:
            - cms_type: نوع CMS (wordpress, joomla, drupal, custom)
            - cms_version: نسخه CMS
            - page_builder: صفحه‌ساز (elementor, divi, etc.)
            - programming_language: زبان برنامه‌نویسی (PHP, Python, etc.)
            - php_version: نسخه PHP (اگر PHP باشد)
            - database: نوع دیتابیس (MySQL, PostgreSQL, etc.)
            - social_media: شبکه‌های اجتماعی
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {
            'cms_type': 'custom',
            'cms_version': None,
            'page_builder': None,
            'page_builder_version': None,
            'programming_language': None,
            'php_version': None,
            'database': None,
            'social_media': []
        }
        
        # بررسی WordPress
        if any([
            'wp-content' in html_content.lower(),
            'wp-includes' in html_content.lower(),
            soup.find('link', {'href': re.compile(r'wp-content')}),
            soup.find('script', {'src': re.compile(r'wp-includes')})
        ]):
            result['cms_type'] = 'wordpress'
            result['programming_language'] = 'PHP'
            
            # استخراج نسخه WordPress
            generator_meta = soup.find('meta', {'name': 'generator'})
            if generator_meta and generator_meta.get('content'):
                content = generator_meta.get('content', '')
                version_match = re.search(r'WordPress\s+([\d.]+)', content, re.I)
                if version_match:
                    result['cms_version'] = version_match.group(1)
            
            # بررسی در HTML comments
            if not result['cms_version']:
                version_match = re.search(r'wp-version-([\d.]+)', html_content, re.I)
                if version_match:
                    result['cms_version'] = version_match.group(1)
            
            # بررسی Elementor
            if any([
                'elementor' in html_content.lower(),
                'elementor-frontend' in html_content.lower(),
                soup.find('link', {'href': re.compile(r'elementor')}),
                soup.find('script', {'src': re.compile(r'elementor')})
            ]):
                result['page_builder'] = 'Elementor'
                # استخراج نسخه Elementor از script/link tags
                elementor_scripts = soup.find_all(['script', 'link'], src=True)
                for tag in elementor_scripts:
                    src = tag.get('src', '')
                    # الگوهای مختلف برای نسخه Elementor
                    version_match = re.search(r'elementor[^/]*/([\d.]+)', src, re.I)
                    if version_match:
                        result['page_builder_version'] = version_match.group(1)
                        break
                
                # اگر نسخه پیدا نشد، از HTML content جستجو می‌کنیم
                if not result['page_builder_version']:
                    version_match = re.search(r'elementor[^/]*/([\d.]+)', html_content, re.I)
                    if version_match:
                        result['page_builder_version'] = version_match.group(1)
            
            # بررسی Divi
            elif any([
                'et-', 'divi' in html_content.lower(),
                soup.find('link', {'href': re.compile(r'et-')})
            ]):
                result['page_builder'] = 'Divi'
            
            # بررسی Beaver Builder
            elif 'fl-builder' in html_content.lower():
                result['page_builder'] = 'Beaver Builder'
            
            # بررسی نسخه PHP از headers یا HTML
            php_match = re.search(r'PHP/([\d.]+)', html_content, re.I)
            if php_match:
                result['php_version'] = php_match.group(1)
            
            # بررسی MySQL
            if any([
                'mysql' in html_content.lower(),
                'mysqli' in html_content.lower()
            ]):
                result['database'] = 'MySQL'
            
            # استخراج شبکه‌های اجتماعی
            result['social_media'] = self._extract_social_media(soup, html_content)
            
            # استخراج پلاگین‌ها
            plugins = await self._detect_plugins(html_content, url, result['cms_type'])
            result['plugins'] = plugins
            
            # استخراج قالب‌ها
            themes = await self._detect_wordpress_themes(html_content, soup, url)
            result['themes'] = themes
            
            return result
        
        # بررسی Joomla
        if any([
            '/joomla' in html_content.lower(),
            'joomla' in html_content.lower(),
            soup.find('meta', {'name': 'generator', 'content': re.compile(r'Joomla', re.I)})
        ]):
            result['cms_type'] = 'joomla'
            result['programming_language'] = 'PHP'
            result['database'] = 'MySQL'  # معمولاً Joomla از MySQL استفاده می‌کند
            result['social_media'] = self._extract_social_media(soup, html_content)
            result['plugins'] = await self._detect_plugins(html_content, url, result['cms_type'])
            # استخراج قالب‌های Joomla
            themes = await self._detect_joomla_templates(html_content, soup, url)
            result['themes'] = themes
            return result
        
        # بررسی Drupal
        if any([
            'drupal' in html_content.lower(),
            soup.find('meta', {'name': 'generator', 'content': re.compile(r'Drupal', re.I)}),
            soup.find('script', {'src': re.compile(r'misc/drupal')})
        ]):
            result['cms_type'] = 'drupal'
            result['programming_language'] = 'PHP'
            result['database'] = 'MySQL'  # معمولاً Drupal از MySQL استفاده می‌کند
            result['social_media'] = self._extract_social_media(soup, html_content)
            result['plugins'] = await self._detect_plugins(html_content, url, result['cms_type'])
            # استخراج قالب‌های Drupal
            themes = await self._detect_drupal_themes(html_content, soup, url)
            result['themes'] = themes
            return result
        
        # بررسی Shopify
        if any([
            'shopify' in html_content.lower(),
            soup.find('script', {'src': re.compile(r'shopify')})
        ]):
            result['cms_type'] = 'shopify'
            result['programming_language'] = 'Liquid'
            result['social_media'] = self._extract_social_media(soup, html_content)
            result['plugins'] = await self._detect_plugins(html_content, url, result['cms_type'])
            # استخراج قالب‌های Shopify
            themes = await self._detect_shopify_themes(html_content, soup, url)
            result['themes'] = themes
            return result
        
        # در غیر این صورت Custom - اما باز هم سعی می‌کنیم اطلاعات را استخراج کنیم
        result['social_media'] = self._extract_social_media(soup, html_content)
        
        # بررسی PHP
        php_match = re.search(r'PHP/([\d.]+)', html_content, re.I)
        if php_match:
            result['programming_language'] = 'PHP'
            result['php_version'] = php_match.group(1)
        
        # بررسی MySQL
        if any(['mysql' in html_content.lower(), 'mysqli' in html_content.lower()]):
            result['database'] = 'MySQL'
        
        # استخراج پلاگین‌ها برای سایت‌های custom
        result['plugins'] = await self._detect_plugins(html_content, url, result['cms_type'])
        
        # برای سایت‌های custom، سعی می‌کنیم قالب‌های عمومی را پیدا کنیم
        # (اگر CMS خاصی تشخیص داده نشد)
        if result['cms_type'] == 'custom':
            result['themes'] = []  # برای custom، قالب‌ها را خالی می‌گذاریم
        
        return result
    
    def _extract_social_media(self, soup: BeautifulSoup, html_content: str) -> List[Dict[str, str]]:
        """استخراج لینک‌های شبکه‌های اجتماعی"""
        social_media = []
        
        # الگوهای مختلف برای شبکه‌های اجتماعی
        social_patterns = {
            'LinkedIn': [
                r'linkedin\.com/company/([^/\s"\'<>]+)',
                r'linkedin\.com/in/([^/\s"\'<>]+)',
                r'linkedin\.com/profile/([^/\s"\'<>]+)'
            ],
            'Facebook': [
                r'facebook\.com/([^/\s"\'<>]+)',
                r'fb\.com/([^/\s"\'<>]+)'
            ],
            'Twitter': [
                r'twitter\.com/([^/\s"\'<>]+)',
                r'x\.com/([^/\s"\'<>]+)'
            ],
            'Instagram': [
                r'instagram\.com/([^/\s"\'<>]+)'
            ],
            'YouTube': [
                r'youtube\.com/(?:channel|c|user)/([^/\s"\'<>]+)',
                r'youtube\.com/@([^/\s"\'<>]+)'
            ],
            'Telegram': [
                r't\.me/([^/\s"\'<>]+)',
                r'telegram\.me/([^/\s"\'<>]+)'
            ]
        }
        
        # جستجو در لینک‌ها
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            for platform, patterns in social_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, href, re.I)
                    if match:
                        profile = match.group(1) if match.lastindex else ''
                        url = href if href.startswith('http') else f'https://{href}'
                        
                        # جلوگیری از تکرار
                        if not any(sm['platform'] == platform and sm['url'] == url for sm in social_media):
                            social_media.append({
                                'platform': platform,
                                'profile': profile,
                                'url': url
                            })
        
        # جستجو در meta tags
        meta_tags = soup.find_all('meta', property=True)
        for meta in meta_tags:
            property_val = meta.get('property', '')
            content = meta.get('content', '')
            
            if 'og:url' in property_val.lower() or 'twitter:url' in property_val.lower():
                for platform, patterns in social_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, content, re.I)
                        if match:
                            profile = match.group(1) if match.lastindex else ''
                            url = content if content.startswith('http') else f'https://{content}'
                            
                            if not any(sm['platform'] == platform and sm['url'] == url for sm in social_media):
                                social_media.append({
                                    'platform': platform,
                                    'profile': profile,
                                    'url': url
                                })
        
        return social_media
    
    async def _detect_plugins(self, html_content: str, url: str, cms_type: str) -> List[Dict[str, Any]]:
        """
        تشخیص پلاگین‌های نصب شده
        
        Args:
            html_content: محتوای HTML
            url: آدرس سایت
            cms_type: نوع CMS
            
        Returns:
            لیست پلاگین‌های تشخیص داده شده
        """
        plugins = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if cms_type == 'wordpress':
            plugins = await self._detect_wordpress_plugins(html_content, soup, url)
        elif cms_type == 'joomla':
            plugins = await self._detect_joomla_extensions(html_content, soup, url)
        elif cms_type == 'drupal':
            plugins = await self._detect_drupal_modules(html_content, soup, url)
        else:
            # برای سایر CMS‌ها یا سایت‌های custom، سعی می‌کنیم پلاگین‌های عمومی را پیدا کنیم
            plugins = await self._detect_general_plugins(html_content, soup, url)
        
        return plugins
    
    async def _detect_wordpress_plugins(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص پلاگین‌های WordPress"""
        plugins = []
        detected_plugins = set()
        
        # لیست پلاگین‌های رایج WordPress
        common_plugins = {
            'yoast': {'name': 'Yoast SEO', 'category': 'SEO'},
            'rank-math': {'name': 'Rank Math', 'category': 'SEO'},
            'all-in-one-seo': {'name': 'All in One SEO', 'category': 'SEO'},
            'elementor': {'name': 'Elementor', 'category': 'Page Builder'},
            'divi': {'name': 'Divi Builder', 'category': 'Page Builder'},
            'beaver-builder': {'name': 'Beaver Builder', 'category': 'Page Builder'},
            'woocommerce': {'name': 'WooCommerce', 'category': 'E-commerce'},
            'contact-form-7': {'name': 'Contact Form 7', 'category': 'Forms'},
            'wpforms': {'name': 'WPForms', 'category': 'Forms'},
            'gravityforms': {'name': 'Gravity Forms', 'category': 'Forms'},
            # Database & Performance
            'advanced-database-cleaner': {'name': 'Advanced Database Cleaner', 'category': 'Database'},
            'wp-rocket': {'name': 'WP Rocket', 'category': 'Performance'},
            'rocket': {'name': 'راکت وردپرس', 'category': 'Performance'},
            # Security
            'safe-svg': {'name': 'Safe SVG', 'category': 'Security'},
            # Theme Support
            'woodmart-core': {'name': 'Woodmart Core', 'category': 'Theme Support'},
            'woodmart': {'name': 'Woodmart', 'category': 'Theme Support'},
            'persian-woodmart': {'name': 'فارسی ساز وودمارت', 'category': 'Theme Support'},
            # Widgets
            'classic-widgets': {'name': 'ابزارک‌های کلاسیک', 'category': 'Widgets'},
            # Sliders
            'revslider': {'name': 'Slider Revolution', 'category': 'Slider'},
            'revolution-slider': {'name': 'Slider Revolution', 'category': 'Slider'},
            # Payment Gateways
            'zarinpal': {'name': 'افزونه پرداخت امن زرین‌پال برای ووکامرس', 'category': 'Payment'},
            'zarinpal-woocommerce': {'name': 'افزونه پرداخت امن زرین‌پال برای ووکامرس', 'category': 'Payment'},
            # Calendar
            'persian-calendar': {'name': 'تقویم فارسی', 'category': 'Localization'},
            'shamsi': {'name': 'تقویم فارسی', 'category': 'Localization'},
            # Backup & Migration
            'duplicator': {'name': 'تکثیرکننده', 'category': 'Backup'},
            'advanced-database-cleaner': {'name': 'Advanced Database Cleaner', 'category': 'Database'},
            # User Management & Login
            'digits': {'name': 'دیجیتس: عضویت و ورود با شماره موبایل', 'category': 'User Management'},
            'digits-login': {'name': 'دیجیتس: عضویت و ورود با شماره موبایل', 'category': 'User Management'},
            'digits-addon': {'name': 'دیجیتس: افزودنی فرم مشترک ورود/عضویت', 'category': 'User Management'},
            'digits-addon-merasaweb': {'name': 'دیجیتس: افزودنی فرم مشترک ورود/عضویت- مرسا وب', 'category': 'User Management'},
            # WooCommerce Extensions
            'woocommerce-invoice-pro': {'name': 'فاکتور حرفه‌ای ووکامرس', 'category': 'E-commerce'},
            'woocommerce-checkout-field-editor': {'name': 'ویرایشگر فرم پرداخت برای ووکامرس', 'category': 'E-commerce'},
            'thwcfe': {'name': 'ویرایشگر فرم پرداخت برای ووکامرس', 'category': 'E-commerce'},
            'woocommerce-sms': {'name': 'پیامک حرفه ای ووکامرس', 'category': 'E-commerce'},
            'woocommerce-persian': {'name': 'ووکامرس فارسی', 'category': 'E-commerce'},
            'persian-woodmart': {'name': 'فارسی ساز وودمارت', 'category': 'Theme Support'},
            # Email Marketing
            'mailchimp': {'name': 'میل چیمپ برای وردپرس', 'category': 'Email Marketing'},
            'mailchimp-for-wp': {'name': 'میل چیمپ برای وردپرس', 'category': 'Email Marketing'},
            # Editor
            'classic-editor': {'name': 'ویرایشگر کلاسیک', 'category': 'Editor'},
            'jetpack': {'name': 'Jetpack', 'category': 'Performance'},
            'wp-super-cache': {'name': 'WP Super Cache', 'category': 'Performance'},
            'w3-total-cache': {'name': 'W3 Total Cache', 'category': 'Performance'},
            'wp-rocket': {'name': 'WP Rocket', 'category': 'Performance'},
            'akismet': {'name': 'Akismet', 'category': 'Security'},
            'wordfence': {'name': 'Wordfence', 'category': 'Security'},
            'sucuri': {'name': 'Sucuri Security', 'category': 'Security'},
            'polylang': {'name': 'Polylang', 'category': 'Multilingual'},
            'wpml': {'name': 'WPML', 'category': 'Multilingual'},
            'google-analytics': {'name': 'Google Analytics', 'category': 'Analytics'},
            'monsterinsights': {'name': 'MonsterInsights', 'category': 'Analytics'},
            'redirection': {'name': 'Redirection', 'category': 'SEO'},
            'broken-link-checker': {'name': 'Broken Link Checker', 'category': 'SEO'},
            'schema': {'name': 'Schema.org', 'category': 'SEO'},
            'breadcrumb': {'name': 'Breadcrumb NavXT', 'category': 'SEO'},
            'wp-pagenavi': {'name': 'WP-PageNavi', 'category': 'Navigation'},
            'nextgen-gallery': {'name': 'NextGEN Gallery', 'category': 'Media'},
            'smush': {'name': 'Smush', 'category': 'Performance'},
            'imagify': {'name': 'Imagify', 'category': 'Performance'},
            'shortpixel': {'name': 'ShortPixel', 'category': 'Performance'},
            'updraftplus': {'name': 'UpdraftPlus', 'category': 'Backup'},
            'backwpup': {'name': 'BackWPup', 'category': 'Backup'},
            'duplicator': {'name': 'Duplicator', 'category': 'Backup'},
            'advanced-custom-fields': {'name': 'Advanced Custom Fields', 'category': 'Customization'},
            'custom-post-type-ui': {'name': 'Custom Post Type UI', 'category': 'Customization'},
            'wp-user-frontend': {'name': 'WP User Frontend', 'category': 'User Management'},
            'members': {'name': 'Members', 'category': 'User Management'},
            'wp-mail-smtp': {'name': 'WP Mail SMTP', 'category': 'Email'},
            'wp-optimize': {'name': 'WP-Optimize', 'category': 'Performance'},
            'autoptimize': {'name': 'Autoptimize', 'category': 'Performance'},
            'litespeed-cache': {'name': 'LiteSpeed Cache', 'category': 'Performance'},
            'wp-fastest-cache': {'name': 'WP Fastest Cache', 'category': 'Performance'},
            'really-simple-ssl': {'name': 'Really Simple SSL', 'category': 'Security'},
            'i-themes-security': {'name': 'iThemes Security', 'category': 'Security'},
            'all-in-one-wp-migration': {'name': 'All-in-One WP Migration', 'category': 'Backup'},
            'wp-migrate-db': {'name': 'WP Migrate DB', 'category': 'Backup'},
            'wp-sweep': {'name': 'WP-Sweep', 'category': 'Maintenance'},
            'wp-dbmanager': {'name': 'WP-DBManager', 'category': 'Database'},
            'wp-security-audit-log': {'name': 'WP Security Audit Log', 'category': 'Security'},
            'wp-cerber': {'name': 'WP Cerber Security', 'category': 'Security'},
            'ninja-forms': {'name': 'Ninja Forms', 'category': 'Forms'},
            'caldera-forms': {'name': 'Caldera Forms', 'category': 'Forms'},
            'formidable': {'name': 'Formidable Forms', 'category': 'Forms'},
            'wp-google-maps': {'name': 'WP Google Maps', 'category': 'Maps'},
            'wp-google-maps-pro': {'name': 'WP Google Maps Pro', 'category': 'Maps'},
            'map-multi-marker': {'name': 'Map Multi Marker', 'category': 'Maps'},
            'wp-google-fonts': {'name': 'WP Google Fonts', 'category': 'Typography'},
            'easy-google-fonts': {'name': 'Easy Google Fonts', 'category': 'Typography'},
            'wp-polls': {'name': 'WP-Polls', 'category': 'Polls'},
            'wp-polls-widget': {'name': 'WP-Polls Widget', 'category': 'Polls'},
            'wp-postratings': {'name': 'WP-PostRatings', 'category': 'Ratings'},
            'wp-user-avatar': {'name': 'WP User Avatar', 'category': 'User Management'},
            'user-registration': {'name': 'User Registration', 'category': 'User Management'},
            'wp-user-manager': {'name': 'WP User Manager', 'category': 'User Management'},
            'bbpress': {'name': 'bbPress', 'category': 'Forums'},
            'buddypress': {'name': 'BuddyPress', 'category': 'Social Network'},
            'wp-job-manager': {'name': 'WP Job Manager', 'category': 'Job Board'},
            'events-manager': {'name': 'Events Manager', 'category': 'Events'},
            'the-events-calendar': {'name': 'The Events Calendar', 'category': 'Events'},
            'wp-events-manager': {'name': 'WP Events Manager', 'category': 'Events'},
            'wp-google-analytics-events': {'name': 'WP Google Analytics Events', 'category': 'Analytics'},
            'google-analytics-dashboard': {'name': 'Google Analytics Dashboard', 'category': 'Analytics'},
            'wp-statistics': {'name': 'WP Statistics', 'category': 'Analytics'},
            'matomo': {'name': 'Matomo Analytics', 'category': 'Analytics'},
            'wp-google-analytics': {'name': 'WP Google Analytics', 'category': 'Analytics'},
            'wp-google-tag-manager': {'name': 'WP Google Tag Manager', 'category': 'Analytics'},
            'wp-google-tag-manager-pro': {'name': 'WP Google Tag Manager Pro', 'category': 'Analytics'},
            'wp-google-analytics-pro': {'name': 'WP Google Analytics Pro', 'category': 'Analytics'},
            'wp-google-analytics-events-pro': {'name': 'WP Google Analytics Events Pro', 'category': 'Analytics'},
            'wp-google-analytics-dashboard-pro': {'name': 'WP Google Analytics Dashboard Pro', 'category': 'Analytics'},
            'wp-google-analytics-dashboard': {'name': 'WP Google Analytics Dashboard', 'category': 'Analytics'},
            'wp-google-analytics-events': {'name': 'WP Google Analytics Events', 'category': 'Analytics'},
        }
        
        # جستجو در script و link tags
        all_tags = soup.find_all(['script', 'link', 'style'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        # همچنین جستجو در تمام محتوای HTML برای پیدا کردن همه پلاگین‌ها
        html_lower = html_content.lower()
        
        # استخراج همه plugin slugs از wp-content/plugins/
        all_plugin_slugs = set(re.findall(r'wp-content/plugins/([^/]+)', html_lower))
        
        for plugin_slug in all_plugin_slugs:
            if plugin_slug in detected_plugins:
                continue
            
            # پیدا کردن نام پلاگین از لیست
            plugin_info = None
            plugin_slug_normalized = plugin_slug.replace('-', '').replace('_', '').lower()
            
            for key, info in common_plugins.items():
                key_normalized = key.replace('-', '').replace('_', '').lower()
                # تطبیق دقیق‌تر
                if (key_normalized == plugin_slug_normalized or 
                    key_normalized in plugin_slug_normalized or 
                    plugin_slug_normalized in key_normalized or
                    key.replace('-', '') in plugin_slug.replace('-', '') or
                    plugin_slug.replace('-', '') in key.replace('-', '')):
                    plugin_info = info.copy()
                    plugin_info['slug'] = plugin_slug
                    break
            
            if not plugin_info:
                # اگر در لیست نبود، از slug استفاده می‌کنیم
                plugin_name = plugin_slug.replace('-', ' ').replace('_', ' ').title()
                plugin_info = {
                    'name': plugin_name,
                    'slug': plugin_slug,
                    'category': 'Unknown'
                }
            
            detected_plugins.add(plugin_slug)
            plugins.append(plugin_info)
        
        # همچنین جستجو در script/link tags برای پلاگین‌های اضافی
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            
            # جستجو در wp-content/plugins/
            plugin_match = re.search(r'wp-content/plugins/([^/]+)', src_lower)
            if plugin_match:
                plugin_slug = plugin_match.group(1)
                
                if plugin_slug in detected_plugins:
                    continue
                
                # پیدا کردن نام پلاگین از لیست
                plugin_info = None
                plugin_slug_normalized = plugin_slug.replace('-', '').replace('_', '').lower()
                
                for key, info in common_plugins.items():
                    key_normalized = key.replace('-', '').replace('_', '').lower()
                    if (key_normalized == plugin_slug_normalized or 
                        key_normalized in plugin_slug_normalized or 
                        plugin_slug_normalized in key_normalized):
                        plugin_info = info.copy()
                        plugin_info['slug'] = plugin_slug
                        break
                
                if not plugin_info:
                    # اگر در لیست نبود، از slug استفاده می‌کنیم
                    plugin_name = plugin_slug.replace('-', ' ').replace('_', ' ').title()
                    plugin_info = {
                        'name': plugin_name,
                        'slug': plugin_slug,
                        'category': 'Unknown'
                    }
                
                detected_plugins.add(plugin_slug)
                plugins.append(plugin_info)
            
            # جستجو مستقیم در src برای پلاگین‌های خاص
            for key, info in common_plugins.items():
                # جستجوی دقیق‌تر - باید در مسیر plugins باشد
                if key in src_lower and ('plugins/' in src_lower or 'wp-content' in src_lower):
                    if key not in [p.get('slug', '') for p in plugins]:
                        plugin_info = info.copy()
                        plugin_info['slug'] = key
                        if key not in detected_plugins:
                            detected_plugins.add(key)
                            plugins.append(plugin_info)
        
        # جستجو در HTML content برای پلاگین‌های خاص - بهبود یافته
        html_lower = html_content.lower()
        
        # استخراج همه plugin slugs از کل HTML (نه فقط script/link tags)
        all_plugin_slugs_from_html = set(re.findall(r'wp-content/plugins/([^/\s"\'<>]+)', html_lower))
        
        for plugin_slug in all_plugin_slugs_from_html:
            if plugin_slug in detected_plugins:
                continue
            
            # پیدا کردن نام پلاگین از لیست
            plugin_info = None
            plugin_slug_normalized = plugin_slug.replace('-', '').replace('_', '').lower()
            
            for key, info in common_plugins.items():
                key_normalized = key.replace('-', '').replace('_', '').lower()
                if (key_normalized == plugin_slug_normalized or 
                    key_normalized in plugin_slug_normalized or 
                    plugin_slug_normalized in key_normalized):
                    plugin_info = info.copy()
                    plugin_info['slug'] = plugin_slug
                    break
            
            if not plugin_info:
                # اگر در لیست نبود، از slug استفاده می‌کنیم
                plugin_name = plugin_slug.replace('-', ' ').replace('_', ' ').title()
                plugin_info = {
                    'name': plugin_name,
                    'slug': plugin_slug,
                    'category': 'Unknown'
                }
            
            detected_plugins.add(plugin_slug)
            plugins.append(plugin_info)
        
        # همچنین جستجو برای پلاگین‌های خاص از لیست
        for key, info in common_plugins.items():
            if key in detected_plugins:
                continue
            
            key_normalized = key.replace('-', '').replace('_', '')
            html_normalized = html_lower.replace('-', '').replace('_', '')
            
            # جستجوی دقیق‌تر - باید در wp-content/plugins/ باشد
            if (f'wp-content/plugins/{key}' in html_lower or 
                f'plugins/{key}' in html_lower or
                (key_normalized in html_normalized and 'plugins' in html_lower)):
                plugin_info = info.copy()
                plugin_info['slug'] = key
                detected_plugins.add(key)
                plugins.append(plugin_info)
        
        # جستجوی پلاگین‌های فارسی و خاص با الگوهای مختلف
        persian_plugin_patterns = {
            'zarinpal': ['zarinpal', 'zarin-pal', 'زرین‌پال'],
            'digits': ['digits', 'دیجیتس'],
            'persian-calendar': ['persian-calendar', 'shamsi', 'تقویم', 'شمسی'],
            'woodmart': ['woodmart', 'wood-mart', 'وودمارت'],
            'rocket': ['wp-rocket', 'rocket', 'راکت'],
            'mailchimp': ['mailchimp', 'mail-chimp', 'میل چیمپ'],
            'classic-editor': ['classic-editor', 'classic-editor', 'ویرایشگر کلاسیک'],
            'classic-widgets': ['classic-widgets', 'classic-widget', 'ابزارک'],
            'revslider': ['revslider', 'revolution-slider', 'revolution', 'slider-revolution'],
            'advanced-database-cleaner': ['advanced-database-cleaner', 'database-cleaner', 'پاک‌کننده'],
            'safe-svg': ['safe-svg', 'safe-svg', 'svg'],
            'woocommerce-invoice-pro': ['woocommerce-invoice', 'invoice-pro', 'فاکتور'],
            'woocommerce-checkout-field-editor': ['checkout-field-editor', 'thwcfe', 'ویرایشگر فرم'],
            'woocommerce-sms': ['woocommerce-sms', 'woocommerce-sms', 'پیامک'],
        }
        
        for plugin_key, patterns in persian_plugin_patterns.items():
            if plugin_key in detected_plugins:
                continue
            
            for pattern in patterns:
                if pattern in html_lower and ('plugins/' in html_lower or 'wp-content' in html_lower):
                    if plugin_key in common_plugins:
                        plugin_info = common_plugins[plugin_key].copy()
                        plugin_info['slug'] = plugin_key
                        detected_plugins.add(plugin_key)
                        plugins.append(plugin_info)
                        break
        
        # استخراج نسخه پلاگین‌ها از script/link tags
        for plugin in plugins:
            slug = plugin.get('slug', '')
            if slug:
                version_match = re.search(rf'{re.escape(slug)}[^/]*/([\d.]+)', html_content, re.I)
                if version_match:
                    plugin['version'] = version_match.group(1)
        
        return plugins
    
    async def _detect_joomla_extensions(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص Extension‌های Joomla"""
        extensions = []
        detected = set()
        
        # جستجو در script و link tags
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            # جستجو در media/ یا components/
            ext_match = re.search(r'(?:media|components|modules|plugins)/([^/]+)', src.lower())
            if ext_match:
                ext_slug = ext_match.group(1)
                if ext_slug not in detected and ext_slug not in ['system', 'joomla', 'jui']:
                    detected.add(ext_slug)
                    extensions.append({
                        'name': ext_slug.replace('-', ' ').title(),
                        'slug': ext_slug,
                        'category': 'Extension'
                    })
        
        return extensions
    
    async def _detect_drupal_modules(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص Module‌های Drupal"""
        modules = []
        detected = set()
        
        # جستجو در script و link tags
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            # جستجو در modules/
            module_match = re.search(r'modules/([^/]+)', src.lower())
            if module_match:
                module_slug = module_match.group(1)
                if module_slug not in detected and module_slug not in ['system', 'core', 'drupal']:
                    detected.add(module_slug)
                    modules.append({
                        'name': module_slug.replace('-', ' ').replace('_', ' ').title(),
                        'slug': module_slug,
                        'category': 'Module'
                    })
        
        return modules
    
    async def _detect_wordpress_themes(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص قالب‌های WordPress"""
        themes = []
        detected_themes = set()
        
        # لیست قالب‌های رایج WordPress
        common_themes = {
            'astra': {'name': 'Astra', 'type': 'Free/Pro', 'category': 'Multipurpose'},
            'generatepress': {'name': 'GeneratePress', 'type': 'Free/Pro', 'category': 'Multipurpose'},
            'oceanwp': {'name': 'OceanWP', 'type': 'Free/Pro', 'category': 'Multipurpose'},
            'neve': {'name': 'Neve', 'type': 'Free/Pro', 'category': 'Multipurpose'},
            'kadence': {'name': 'Kadence', 'type': 'Free/Pro', 'category': 'Multipurpose'},
            'storefront': {'name': 'Storefront', 'type': 'Free', 'category': 'WooCommerce'},
            'flatsome': {'name': 'Flatsome', 'type': 'Premium', 'category': 'E-commerce'},
            'avada': {'name': 'Avada', 'type': 'Premium', 'category': 'Multipurpose'},
            'divi': {'name': 'Divi', 'type': 'Premium', 'category': 'Page Builder'},
            'the7': {'name': 'The7', 'type': 'Premium', 'category': 'Multipurpose'},
            'enfold': {'name': 'Enfold', 'type': 'Premium', 'category': 'Multipurpose'},
            'bethemes': {'name': 'BeTheme', 'type': 'Premium', 'category': 'Multipurpose'},
            'salient': {'name': 'Salient', 'type': 'Premium', 'category': 'Multipurpose'},
            'bridge': {'name': 'Bridge', 'type': 'Premium', 'category': 'Multipurpose'},
            'impreza': {'name': 'Impreza', 'type': 'Premium', 'category': 'Multipurpose'},
            'woodmart': {'name': 'WoodMart', 'type': 'Premium', 'category': 'E-commerce'},
            'porto': {'name': 'Porto', 'type': 'Premium', 'category': 'E-commerce'},
            'xstore': {'name': 'XStore', 'type': 'Premium', 'category': 'E-commerce'},
            'shopkeeper': {'name': 'Shopkeeper', 'type': 'Premium', 'category': 'E-commerce'},
            'twenty': {'name': 'Twenty Series', 'type': 'Free', 'category': 'Default'},
            'twentytwenty': {'name': 'Twenty Twenty', 'type': 'Free', 'category': 'Default'},
            'twentytwentyone': {'name': 'Twenty Twenty-One', 'type': 'Free', 'category': 'Default'},
            'twentytwentytwo': {'name': 'Twenty Twenty-Two', 'type': 'Free', 'category': 'Default'},
            'twentytwentythree': {'name': 'Twenty Twenty-Three', 'type': 'Free', 'category': 'Default'},
            'twentytwentyfour': {'name': 'Twenty Twenty-Four', 'type': 'Free', 'category': 'Default'},
            'hello': {'name': 'Hello Elementor', 'type': 'Free', 'category': 'Page Builder'},
            'hello-elementor': {'name': 'Hello Elementor', 'type': 'Free', 'category': 'Page Builder'},
            'beaver-builder': {'name': 'Beaver Builder Theme', 'type': 'Free/Pro', 'category': 'Page Builder'},
            'genesis': {'name': 'Genesis Framework', 'type': 'Premium', 'category': 'Framework'},
            'thesis': {'name': 'Thesis', 'type': 'Premium', 'category': 'Framework'},
            'canvas': {'name': 'Canvas', 'type': 'Premium', 'category': 'Framework'},
            'newspaper': {'name': 'Newspaper', 'type': 'Premium', 'category': 'News/Magazine'},
            'jnews': {'name': 'JNews', 'type': 'Premium', 'category': 'News/Magazine'},
            'soledad': {'name': 'Soledad', 'type': 'Premium', 'category': 'News/Magazine'},
            'newsmag': {'name': 'NewsMag', 'type': 'Premium', 'category': 'News/Magazine'},
            'magazine': {'name': 'Magazine Pro', 'type': 'Premium', 'category': 'News/Magazine'},
            'newsmagazine': {'name': 'NewsMagazine', 'type': 'Premium', 'category': 'News/Magazine'},
            'betheme': {'name': 'BeTheme', 'type': 'Premium', 'category': 'Multipurpose'},
            'kallyas': {'name': 'Kallyas', 'type': 'Premium', 'category': 'Multipurpose'},
            'jupiter': {'name': 'Jupiter', 'type': 'Premium', 'category': 'Multipurpose'},
            'kalium': {'name': 'Kalium', 'type': 'Premium', 'category': 'Portfolio'},
            'uncode': {'name': 'Uncode', 'type': 'Premium', 'category': 'Portfolio'},
            'thegem': {'name': 'TheGem', 'type': 'Premium', 'category': 'Portfolio'},
            'jevelin': {'name': 'Jevelin', 'type': 'Premium', 'category': 'Multipurpose'},
            'rehub': {'name': 'ReHub', 'type': 'Premium', 'category': 'Affiliate'},
            'reviews': {'name': 'Reviews', 'type': 'Premium', 'category': 'Review'},
        }
        
        # جستجو در script و link tags برای wp-content/themes/
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            
            # جستجو در wp-content/themes/
            theme_match = re.search(r'wp-content/themes/([^/]+)', src_lower)
            if theme_match:
                theme_slug = theme_match.group(1)
                
                # پیدا کردن نام قالب از لیست
                theme_info = None
                for key, info in common_themes.items():
                    if key.replace('-', '') in theme_slug.replace('-', '') or theme_slug.replace('-', '') in key.replace('-', ''):
                        theme_info = info.copy()
                        theme_info['slug'] = theme_slug
                        break
                
                if not theme_info:
                    # اگر در لیست نبود، از slug استفاده می‌کنیم
                    theme_name = theme_slug.replace('-', ' ').replace('_', ' ').title()
                    theme_info = {
                        'name': theme_name,
                        'slug': theme_slug,
                        'type': 'Unknown',
                        'category': 'Unknown'
                    }
                
                if theme_slug not in detected_themes:
                    detected_themes.add(theme_slug)
                    themes.append(theme_info)
            
            # جستجو مستقیم در src برای قالب‌های خاص
            for key, info in common_themes.items():
                if key in src_lower and key not in [t.get('slug', '') for t in themes]:
                    theme_info = info.copy()
                    theme_info['slug'] = key
                    if key not in detected_themes:
                        detected_themes.add(key)
                        themes.append(theme_info)
        
        # جستجو در HTML content برای قالب‌های خاص
        html_lower = html_content.lower()
        for key, info in common_themes.items():
            if key.replace('-', '') in html_lower and key not in detected_themes:
                # بررسی دقیق‌تر - باید در wp-content/themes/ باشد
                if f'wp-content/themes/{key}' in html_lower or f'themes/{key}' in html_lower:
                    theme_info = info.copy()
                    theme_info['slug'] = key
                    detected_themes.add(key)
                    themes.append(theme_info)
        
        # استخراج نسخه قالب از script/link tags
        for theme in themes:
            slug = theme.get('slug', '')
            if slug:
                version_match = re.search(rf'{re.escape(slug)}[^/]*/([\d.]+)', html_content, re.I)
                if version_match:
                    theme['version'] = version_match.group(1)
                
                # تلاش برای استخراج اطلاعات بیشتر از style.css
                # (این نیاز به درخواست HTTP اضافی دارد، پس فعلاً skip می‌کنیم)
        
        # اگر قالب پیدا نشد، سعی می‌کنیم از body class استفاده کنیم
        if not themes:
            body = soup.find('body')
            if body:
                body_classes = body.get('class', [])
                for class_name in body_classes:
                    if 'theme-' in class_name.lower():
                        theme_slug = class_name.replace('theme-', '').replace('-', ' ').title()
                        themes.append({
                            'name': theme_slug,
                            'slug': class_name.replace('theme-', ''),
                            'type': 'Unknown',
                            'category': 'Unknown'
                        })
                        break
        
        return themes
    
    async def _detect_joomla_templates(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص قالب‌های Joomla"""
        templates = []
        detected = set()
        
        # لیست قالب‌های رایج Joomla
        common_templates = {
            'protostar': {'name': 'Protostar', 'type': 'Free', 'category': 'Default'},
            'beez3': {'name': 'Beez3', 'type': 'Free', 'category': 'Default'},
            'isis': {'name': 'Isis', 'type': 'Free', 'category': 'Admin'},
            'hathor': {'name': 'Hathor', 'type': 'Free', 'category': 'Admin'},
            'helix': {'name': 'Helix Ultimate', 'type': 'Free/Pro', 'category': 'Framework'},
            'gantry': {'name': 'Gantry', 'type': 'Free', 'category': 'Framework'},
            'wright': {'name': 'Wright', 'type': 'Free', 'category': 'Framework'},
            't3': {'name': 'T3 Framework', 'type': 'Free', 'category': 'Framework'},
            'ja-t3': {'name': 'JA T3', 'type': 'Free', 'category': 'Framework'},
            'yootheme': {'name': 'YOOtheme', 'type': 'Premium', 'category': 'Framework'},
            'joomshaper': {'name': 'JoomShaper', 'type': 'Premium', 'category': 'Framework'},
            'shape5': {'name': 'Shape5', 'type': 'Premium', 'category': 'Framework'},
            'rockettheme': {'name': 'RocketTheme', 'type': 'Premium', 'category': 'Framework'},
            'joomlart': {'name': 'JoomlArt', 'type': 'Premium', 'category': 'Framework'},
        }
        
        # جستجو در script و link tags برای templates/
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            
            # جستجو در templates/
            template_match = re.search(r'templates/([^/]+)', src_lower)
            if template_match:
                template_slug = template_match.group(1)
                
                # پیدا کردن نام قالب از لیست
                template_info = None
                for key, info in common_templates.items():
                    if key.replace('-', '') in template_slug.replace('-', '') or template_slug.replace('-', '') in key.replace('-', ''):
                        template_info = info.copy()
                        template_info['slug'] = template_slug
                        break
                
                if not template_info:
                    # اگر در لیست نبود، از slug استفاده می‌کنیم
                    template_name = template_slug.replace('-', ' ').replace('_', ' ').title()
                    template_info = {
                        'name': template_name,
                        'slug': template_slug,
                        'type': 'Unknown',
                        'category': 'Unknown'
                    }
                
                if template_slug not in detected:
                    detected.add(template_slug)
                    templates.append(template_info)
        
        return templates
    
    async def _detect_drupal_themes(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص قالب‌های Drupal"""
        themes = []
        detected = set()
        
        # لیست قالب‌های رایج Drupal
        common_themes = {
            'bartik': {'name': 'Bartik', 'type': 'Free', 'category': 'Default'},
            'seven': {'name': 'Seven', 'type': 'Free', 'category': 'Admin'},
            'stark': {'name': 'Stark', 'type': 'Free', 'category': 'Default'},
            'olivero': {'name': 'Olivero', 'type': 'Free', 'category': 'Default'},
            'claro': {'name': 'Claro', 'type': 'Free', 'category': 'Admin'},
            'zen': {'name': 'Zen', 'type': 'Free', 'category': 'Framework'},
            'omega': {'name': 'Omega', 'type': 'Free', 'category': 'Framework'},
            'adaptivetheme': {'name': 'AdaptiveTheme', 'type': 'Free', 'category': 'Framework'},
            'bootstrap': {'name': 'Bootstrap', 'type': 'Free', 'category': 'Framework'},
            'foundation': {'name': 'Foundation', 'type': 'Free', 'category': 'Framework'},
            'materialize': {'name': 'Materialize', 'type': 'Free', 'category': 'Framework'},
            'radix': {'name': 'Radix', 'type': 'Free', 'category': 'Framework'},
            'aurora': {'name': 'Aurora', 'type': 'Free', 'category': 'Framework'},
        }
        
        # جستجو در script و link tags برای themes/
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            
            # جستجو در themes/
            theme_match = re.search(r'themes/([^/]+)', src_lower)
            if theme_match:
                theme_slug = theme_match.group(1)
                
                # پیدا کردن نام قالب از لیست
                theme_info = None
                for key, info in common_themes.items():
                    if key.replace('-', '') in theme_slug.replace('-', '') or theme_slug.replace('-', '') in key.replace('-', ''):
                        theme_info = info.copy()
                        theme_info['slug'] = theme_slug
                        break
                
                if not theme_info:
                    # اگر در لیست نبود، از slug استفاده می‌کنیم
                    theme_name = theme_slug.replace('-', ' ').replace('_', ' ').title()
                    theme_info = {
                        'name': theme_name,
                        'slug': theme_slug,
                        'type': 'Unknown',
                        'category': 'Unknown'
                    }
                
                if theme_slug not in detected:
                    detected.add(theme_slug)
                    themes.append(theme_info)
        
        return themes
    
    async def _detect_shopify_themes(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص قالب‌های Shopify"""
        themes = []
        detected = set()
        
        # لیست قالب‌های رایج Shopify
        common_themes = {
            'dawn': {'name': 'Dawn', 'type': 'Free', 'category': 'Modern'},
            'debut': {'name': 'Debut', 'type': 'Free', 'category': 'Classic'},
            'brooklyn': {'name': 'Brooklyn', 'type': 'Free', 'category': 'Classic'},
            'venture': {'name': 'Venture', 'type': 'Free', 'category': 'Classic'},
            'narrative': {'name': 'Narrative', 'type': 'Free', 'category': 'Classic'},
            'supply': {'name': 'Supply', 'type': 'Free', 'category': 'Classic'},
            'minimal': {'name': 'Minimal', 'type': 'Free', 'category': 'Classic'},
            'simple': {'name': 'Simple', 'type': 'Free', 'category': 'Classic'},
            'boundless': {'name': 'Boundless', 'type': 'Free', 'category': 'Classic'},
            'express': {'name': 'Express', 'type': 'Free', 'category': 'Classic'},
            'dawn': {'name': 'Dawn', 'type': 'Free', 'category': 'Modern'},
            'craft': {'name': 'Craft', 'type': 'Premium', 'category': 'Modern'},
            'impulse': {'name': 'Impulse', 'type': 'Premium', 'category': 'Modern'},
            'prestige': {'name': 'Prestige', 'type': 'Premium', 'category': 'Modern'},
            'turbo': {'name': 'Turbo', 'type': 'Premium', 'category': 'Modern'},
            'venture': {'name': 'Venture', 'type': 'Premium', 'category': 'Modern'},
            'parallax': {'name': 'Parallax', 'type': 'Premium', 'category': 'Modern'},
            'responsive': {'name': 'Responsive', 'type': 'Premium', 'category': 'Modern'},
            'retina': {'name': 'Retina', 'type': 'Premium', 'category': 'Modern'},
            'shoppe': {'name': 'Shoppe', 'type': 'Premium', 'category': 'Modern'},
        }
        
        # جستجو در script و link tags برای themes/
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            
            # جستجو در themes/ یا cdn.shopify.com/s/files/
            theme_match = re.search(r'themes/([^/]+)', src_lower)
            if not theme_match:
                # جستجو در shopify CDN
                theme_match = re.search(r'shopify.*theme[_-]?([a-z0-9_-]+)', src_lower)
            
            if theme_match:
                theme_slug = theme_match.group(1)
                
                # پیدا کردن نام قالب از لیست
                theme_info = None
                for key, info in common_themes.items():
                    if key.replace('-', '') in theme_slug.replace('-', '') or theme_slug.replace('-', '') in key.replace('-', ''):
                        theme_info = info.copy()
                        theme_info['slug'] = theme_slug
                        break
                
                if not theme_info:
                    # اگر در لیست نبود، از slug استفاده می‌کنیم
                    theme_name = theme_slug.replace('-', ' ').replace('_', ' ').title()
                    theme_info = {
                        'name': theme_name,
                        'slug': theme_slug,
                        'type': 'Unknown',
                        'category': 'Unknown'
                    }
                
                if theme_slug not in detected:
                    detected.add(theme_slug)
                    themes.append(theme_info)
            
            # جستجو در body class یا HTML attributes
            body = soup.find('body')
            if body:
                body_id = body.get('id', '')
                if 'theme' in body_id.lower():
                    theme_slug = body_id.replace('theme-', '').replace('-', ' ').title()
                    if theme_slug not in detected:
                        detected.add(theme_slug)
                        themes.append({
                            'name': theme_slug,
                            'slug': body_id.replace('theme-', ''),
                            'type': 'Unknown',
                            'category': 'Unknown'
                        })
        
        return themes
    
    async def _detect_general_plugins(self, html_content: str, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """تشخیص پلاگین‌های عمومی (برای سایت‌های custom)"""
        plugins = []
        detected = set()
        
        # پلاگین‌های عمومی که ممکن است در هر سایتی استفاده شوند
        general_plugins = {
            'jquery': {'name': 'jQuery', 'category': 'JavaScript Library'},
            'bootstrap': {'name': 'Bootstrap', 'category': 'CSS Framework'},
            'font-awesome': {'name': 'Font Awesome', 'category': 'Icons'},
            'google-analytics': {'name': 'Google Analytics', 'category': 'Analytics'},
            'recaptcha': {'name': 'reCAPTCHA', 'category': 'Security'},
            'paypal': {'name': 'PayPal', 'category': 'Payment'},
            'stripe': {'name': 'Stripe', 'category': 'Payment'},
        }
        
        all_tags = soup.find_all(['script', 'link'], src=True)
        all_tags.extend(soup.find_all(['script', 'link'], href=True))
        
        for tag in all_tags:
            src = tag.get('src', '') or tag.get('href', '')
            if not src:
                continue
            
            src_lower = src.lower()
            for key, info in general_plugins.items():
                if key in src_lower and key not in detected:
                    detected.add(key)
                    plugins.append(info.copy())
        
        return plugins
    
    async def detect_technology_stack(self, html_content: str) -> Dict[str, Any]:
        """شناسایی فناوری‌های استفاده شده"""
        soup = BeautifulSoup(html_content, 'html.parser')
        stack = {
            'frontend_framework': None,
            'javascript_libraries': [],
            'css_frameworks': [],
            'analytics': [],
            'cms': None
        }
        
        # بررسی JavaScript Libraries
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            if 'jquery' in src:
                stack['javascript_libraries'].append('jQuery')
            if 'react' in src or 'reactjs' in src:
                stack['javascript_libraries'].append('React')
            if 'vue' in src:
                stack['javascript_libraries'].append('Vue.js')
            if 'angular' in src:
                stack['javascript_libraries'].append('Angular')
        
        # بررسی CSS Frameworks
        links = soup.find_all('link', rel='stylesheet')
        for link in links:
            href = link.get('href', '').lower()
            if 'bootstrap' in href:
                stack['css_frameworks'].append('Bootstrap')
            if 'tailwind' in href:
                stack['css_frameworks'].append('Tailwind CSS')
            if 'material' in href:
                stack['css_frameworks'].append('Material Design')
        
        # بررسی Analytics
        if 'google-analytics' in html_content.lower() or 'gtag' in html_content.lower():
            stack['analytics'].append('Google Analytics')
        if 'facebook' in html_content.lower() and 'pixel' in html_content.lower():
            stack['analytics'].append('Facebook Pixel')
        
        return stack
    
    async def analyze_structure(self, html_content: str, url: str) -> Dict[str, Any]:
        """تحلیل ساختار سایت"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # شمارش عناصر
        structure = {
            'total_pages': 0,  # نیاز به Crawl دارد
            'total_posts': 0,  # نیاز به Crawl دارد
            'headings': {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
            },
            'links': {
                'internal': len([a for a in soup.find_all('a', href=True) 
                               if a['href'].startswith('/') or url in a['href']]),
                'external': len([a for a in soup.find_all('a', href=True) 
                               if not (a['href'].startswith('/') or url in a['href'])])
            },
            'images': len(soup.find_all('img')),
            'forms': len(soup.find_all('form'))
        }
        
        # استخراج زبان از HTML
        html_tag = soup.find('html')
        if html_tag:
            html_lang = html_tag.get('lang', '')
            if html_lang:
                structure['html_lang'] = html_lang
        
        return structure
    
    async def analyze_performance(self, url: str) -> Dict[str, Any]:
        """تحلیل اولیه عملکرد"""
        # این یک تحلیل ساده است
        # برای تحلیل کامل باید از Lighthouse API استفاده شود
        try:
            import time
            start_time = time.time()
            response = await self.client.get(url)
            load_time = time.time() - start_time
            
            return {
                'response_time': load_time,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'headers': dict(response.headers)
            }
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            return {
                'response_time': None,
                'error': str(e)
            }
    
    async def analyze_security(self, url: str, html_content: str) -> Dict[str, Any]:
        """تحلیل اولیه امنیت"""
        security = {
            'ssl_enabled': url.startswith('https://'),
            'security_headers': {},
            'vulnerabilities': []
        }
        
        try:
            response = await self.client.get(url)
            headers = response.headers
            
            # بررسی Security Headers
            security['security_headers'] = {
                'x_frame_options': headers.get('X-Frame-Options'),
                'x_content_type_options': headers.get('X-Content-Type-Options'),
                'strict_transport_security': headers.get('Strict-Transport-Security'),
                'content_security_policy': headers.get('Content-Security-Policy')
            }
            
            # بررسی SSL
            if not security['ssl_enabled']:
                security['vulnerabilities'].append({
                    'type': 'missing_ssl',
                    'severity': 'high',
                    'message': 'Site is not using HTTPS'
                })
            
        except Exception as e:
            logger.error(f"Error analyzing security: {str(e)}")
        
        return security
    
    async def find_sitemap(self, url: str) -> Optional[Dict[str, Any]]:
        """یافتن Sitemap"""
        sitemap_urls = [
            f"{url}/sitemap.xml",
            f"{url}/sitemap_index.xml",
            f"{url}/sitemaps.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = await self.client.get(sitemap_url)
                if response.status_code == 200:
                    return {
                        'url': sitemap_url,
                        'found': True,
                        'content_type': response.headers.get('Content-Type')
                    }
            except:
                continue
        
        return {
            'url': None,
            'found': False
        }
    
    async def close(self):
        """بستن Client"""
        await self.client.aclose()

