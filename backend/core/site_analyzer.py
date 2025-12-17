"""
ماژول تحلیل اولیه سایت
شامل: URL Validation, CMS Detection, Technology Stack, Site Structure
"""

import asyncio
import logging
from typing import Dict, Any, Optional
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
        cms_type = await self.detect_cms(html_content, validated_url)
        technology_stack = await self.detect_technology_stack(html_content)
        structure = await self.analyze_structure(html_content, validated_url)
        performance = await self.analyze_performance(validated_url)
        security = await self.analyze_security(validated_url, html_content)
        sitemap = await self.find_sitemap(validated_url)
        
        return {
            'url': validated_url,
            'cms_type': cms_type,
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
    
    async def detect_cms(self, html_content: str, url: str) -> str:
        """شناسایی CMS"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # بررسی WordPress
        if any([
            'wp-content' in html_content.lower(),
            'wp-includes' in html_content.lower(),
            soup.find('link', {'href': re.compile(r'wp-content')}),
            soup.find('script', {'src': re.compile(r'wp-includes')})
        ]):
            return 'wordpress'
        
        # بررسی Joomla
        if any([
            '/joomla' in html_content.lower(),
            'joomla' in html_content.lower(),
            soup.find('meta', {'name': 'generator', 'content': re.compile(r'Joomla', re.I)})
        ]):
            return 'joomla'
        
        # بررسی Drupal
        if any([
            'drupal' in html_content.lower(),
            soup.find('meta', {'name': 'generator', 'content': re.compile(r'Drupal', re.I)}),
            soup.find('script', {'src': re.compile(r'misc/drupal')})
        ]):
            return 'drupal'
        
        # بررسی Shopify
        if any([
            'shopify' in html_content.lower(),
            soup.find('script', {'src': re.compile(r'shopify')})
        ]):
            return 'shopify'
        
        # در غیر این صورت Custom
        return 'custom'
    
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

