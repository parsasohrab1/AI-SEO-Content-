"""
ماژول تحلیل سئو عمیق
تحلیل کامل صفحات، سرفصل‌ها، تصاویر و محتوا
"""

import asyncio
import logging
from typing import Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import re
from collections import Counter

logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """کلاس تحلیل سئو"""
    
    def __init__(self):
        import ssl
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            verify=False,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        self.visited_urls: Set[str] = set()
        self.max_pages = 20  # حداکثر تعداد صفحات برای crawl
        self.pages_data: List[Dict[str, Any]] = []
    
    async def deep_analysis(self, url: str) -> Dict[str, Any]:
        """
        تحلیل عمیق سئو
        
        Args:
            url: آدرس سایت
            
        Returns:
            نتایج تحلیل سئو
        """
        logger.info(f"Starting deep SEO analysis for: {url}")
        
        # Reset state
        self.visited_urls.clear()
        self.pages_data.clear()
        
        try:
            # Crawl صفحات
            await self._crawl_site(url)
        except Exception as e:
            logger.error(f"Error during crawl: {str(e)}")
            # اگر crawl با خطا مواجه شد، حداقل صفحه اصلی را تحلیل می‌کنیم
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                page_data = {
                    'url': url,
                    'html': html_content,
                    'soup': soup,
                    'title': soup.find('title').text if soup.find('title') else '',
                    'meta_description': self._get_meta_description(soup),
                    'headings': self._extract_headings(soup),
                    'images': self._extract_images(soup, url),
                    'links': self._extract_links(soup, url),
                    'text_content': self._extract_text_content(soup)
                }
                
                self.pages_data.append(page_data)
                self.visited_urls.add(url)
            except Exception as e2:
                logger.error(f"Error analyzing main page: {str(e2)}")
        
        # تحلیل داده‌های جمع‌آوری شده
        technical = await self._analyze_technical()
        content = await self._analyze_content()
        images = await self._analyze_images()
        headings = await self._analyze_headings()
        issues = await self._identify_issues(technical, content, images, headings)
        
        return {
            'url': url,
            'technical': technical,
            'content': content,
            'images': images,
            'headings': headings,
            'issues': issues,
            'pages_analyzed': len(self.pages_data),
            'total_pages_found': len(self.visited_urls)
        }
    
    async def _crawl_site(self, start_url: str) -> None:
        """Crawl صفحات سایت"""
        from urllib.parse import urljoin, urlparse
        
        base_domain = urlparse(start_url).netloc
        urls_to_visit = [start_url]
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            try:
                logger.info(f"Crawling: {current_url}")
                response = await self.client.get(current_url)
                response.raise_for_status()
                
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # ذخیره داده‌های صفحه
                page_data = {
                    'url': current_url,
                    'html': html_content,
                    'soup': soup,
                    'title': soup.find('title').text if soup.find('title') else '',
                    'meta_description': self._get_meta_description(soup),
                    'headings': self._extract_headings(soup),
                    'images': self._extract_images(soup, current_url),
                    'links': self._extract_links(soup, current_url),
                    'text_content': self._extract_text_content(soup)
                }
                
                self.pages_data.append(page_data)
                self.visited_urls.add(current_url)
                
                # پیدا کردن لینک‌های داخلی جدید
                for link in page_data['links']['internal']:
                    if link not in self.visited_urls and len(self.visited_urls) < self.max_pages:
                        parsed_link = urlparse(link)
                        if parsed_link.netloc == base_domain or not parsed_link.netloc:
                            full_url = urljoin(current_url, link)
                            if full_url not in self.visited_urls:
                                urls_to_visit.append(full_url)
                
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {str(e)}")
                continue
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """استخراج meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        return ''
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, Any]]]:
        """استخراج تمام headings"""
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in range(1, 7):
            tag = f'h{level}'
            for heading in soup.find_all(tag):
                headings[tag].append({
                    'text': heading.get_text(strip=True),
                    'id': heading.get('id', ''),
                    'class': heading.get('class', [])
                })
        
        return headings
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """استخراج تمام تصاویر"""
        images = []
        
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'full_url': urljoin(base_url, img.get('src', ''))
            }
            images.append(img_data)
        
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[str]]:
        """استخراج لینک‌ها"""
        internal = []
        external = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed = urlparse(href)
            
            if not parsed.netloc or parsed.netloc == base_domain:
                full_url = urljoin(base_url, href)
                if full_url not in internal:
                    internal.append(full_url)
            else:
                if href not in external:
                    external.append(href)
        
        return {
            'internal': internal,
            'external': external
        }
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """استخراج محتوای متنی"""
        # حذف script و style
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        # پاک کردن فضاهای اضافی
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def _analyze_technical(self) -> Dict[str, Any]:
        """تحلیل فنی"""
        crawlability_score = 0
        indexability_score = 0
        
        # بررسی robots.txt
        robots_found = False
        noindex_found = False
        
        if self.pages_data:
            first_url = self.pages_data[0]['url']
            base_url = '/'.join(first_url.split('/')[:3])
            
            try:
                robots_response = await self.client.get(f"{base_url}/robots.txt")
                if robots_response.status_code == 200:
                    robots_found = True
            except:
                pass
        
        # بررسی meta robots
        for page in self.pages_data:
            soup = page['soup']
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            if robots_meta:
                content = robots_meta.get('content', '').lower()
                if 'noindex' in content:
                    noindex_found = True
        
        # محاسبه امتیاز
        if robots_found:
            crawlability_score += 20
        if not noindex_found:
            indexability_score += 50
        
        # بررسی sitemap
        sitemap_found = False
        if self.pages_data:
            first_url = self.pages_data[0]['url']
            base_url = '/'.join(first_url.split('/')[:3])
            try:
                sitemap_response = await self.client.get(f"{base_url}/sitemap.xml")
                if sitemap_response.status_code == 200:
                    sitemap_found = True
                    crawlability_score += 30
            except:
                pass
        
        return {
            'crawlability': 'good' if crawlability_score >= 40 else 'needs_improvement' if crawlability_score >= 20 else 'poor',
            'indexability': 'good' if indexability_score >= 50 else 'needs_improvement' if indexability_score >= 25 else 'poor',
            'core_web_vitals': {
                'lcp': None,  # نیاز به ابزارهای خاص
                'fid': None,
                'cls': None
            },
            'robots_txt': robots_found,
            'sitemap_found': sitemap_found
        }
    
    async def _analyze_content(self) -> Dict[str, Any]:
        """تحلیل محتوا"""
        all_text = ' '.join([page['text_content'] for page in self.pages_data])
        
        # استخراج کلمات کلیدی
        keywords = self._extract_keywords(all_text)
        
        # محاسبه امتیاز خوانایی
        readability_score = self._calculate_readability(all_text)
        
        # بررسی meta tags
        meta_tags_analysis = {
            'pages_with_title': sum(1 for page in self.pages_data if page['title']),
            'pages_with_meta_description': sum(1 for page in self.pages_data if page['meta_description']),
            'total_pages': len(self.pages_data)
        }
        
        return {
            'keywords': keywords[:20],  # 20 کلمه کلیدی برتر
            'readability': readability_score,
            'readability_status': self._get_readability_status(readability_score),
            'meta_tags': meta_tags_analysis,
            'total_words': len(all_text.split()),
            'unique_words': len(set(all_text.lower().split()))
        }
    
    def _extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        """استخراج کلمات کلیدی"""
        # حذف کاراکترهای خاص و تبدیل به حروف کوچک
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # فیلتر کردن کلمات کوتاه و stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'از', 'به', 'در', 'که', 'این', 'آن', 'با', 'برای', 'است', 'هست', 'بود', 'شد', 'می', 'را', 'تا', 'هم', 'یا', 'ولی', 'اما'}
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # شمارش کلمات
        word_freq = Counter(filtered_words)
        
        # تبدیل به لیست
        keywords = [{'word': word, 'count': count} for word, count in word_freq.most_common(50)]
        
        return keywords
    
    def _calculate_readability(self, text: str) -> float:
        """محاسبه امتیاز خوانایی (Flesch Reading Ease)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        words = text.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(words) == 0 or len(sentences) == 0:
            return 0
        
        # فرمول Flesch Reading Ease (برای فارسی ساده شده)
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words) if len(words) > 0 else 0
        
        # محاسبه ساده شده برای فارسی
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # محدود کردن به بازه 0-100
        score = max(0, min(100, score))
        
        return round(score, 2)
    
    def _count_syllables(self, word: str) -> int:
        """شمارش هجاهای یک کلمه (ساده شده)"""
        word = word.lower()
        vowels = 'aeiouyآاایو'
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        if count == 0:
            count = 1
        
        return count
    
    def _get_readability_status(self, score: float) -> str:
        """تعیین وضعیت خوانایی"""
        if score >= 70:
            return 'عالی'
        elif score >= 50:
            return 'خوب'
        elif score >= 30:
            return 'متوسط'
        else:
            return 'نیاز به بهبود'
    
    async def _analyze_images(self) -> Dict[str, Any]:
        """تحلیل تصاویر"""
        all_images = []
        for page in self.pages_data:
            all_images.extend(page['images'])
        
        total_images = len(all_images)
        images_with_alt = sum(1 for img in all_images if img['alt'])
        images_without_alt = total_images - images_with_alt
        
        # بررسی اندازه تصاویر
        large_images = 0
        for img in all_images:
            try:
                width = int(img.get('width', 0) or 0)
                height = int(img.get('height', 0) or 0)
                if width > 1920 or height > 1080:
                    large_images += 1
            except:
                pass
        
        return {
            'total': total_images,
            'with_alt': images_with_alt,
            'without_alt': images_without_alt,
            'alt_coverage': round((images_with_alt / total_images * 100) if total_images > 0 else 0, 2),
            'large_images': large_images,
            'issues': [
                {
                    'type': 'missing_alt',
                    'count': images_without_alt,
                    'severity': 'high' if images_without_alt > 0 else 'none'
                },
                {
                    'type': 'large_images',
                    'count': large_images,
                    'severity': 'medium' if large_images > 0 else 'none'
                }
            ]
        }
    
    async def _analyze_headings(self) -> Dict[str, Any]:
        """تحلیل سرفصل‌ها"""
        all_headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        pages_with_multiple_h1 = []
        pages_without_h1 = []
        
        for page in self.pages_data:
            page_headings = page['headings']
            
            for level in range(1, 7):
                tag = f'h{level}'
                all_headings[tag].extend(page_headings[tag])
            
            # بررسی H1
            h1_count = len(page_headings['h1'])
            if h1_count == 0:
                pages_without_h1.append(page['url'])
            elif h1_count > 1:
                pages_with_multiple_h1.append({
                    'url': page['url'],
                    'count': h1_count,
                    'headings': [h['text'] for h in page_headings['h1']]
                })
        
        # بررسی ساختار سلسله مراتبی
        structure_issues = []
        for page in self.pages_data:
            headings = page['headings']
            # بررسی اینکه آیا H2 قبل از H1 آمده یا نه
            if len(headings['h2']) > 0 and len(headings['h1']) == 0:
                structure_issues.append({
                    'url': page['url'],
                    'issue': 'H2 بدون H1'
                })
        
        return {
            'total': {
                'h1': len(all_headings['h1']),
                'h2': len(all_headings['h2']),
                'h3': len(all_headings['h3']),
                'h4': len(all_headings['h4']),
                'h5': len(all_headings['h5']),
                'h6': len(all_headings['h6'])
            },
            'pages_without_h1': pages_without_h1,
            'pages_with_multiple_h1': pages_with_multiple_h1,
            'structure_issues': structure_issues,
            'status': 'good' if len(pages_without_h1) == 0 and len(pages_with_multiple_h1) == 0 else 'needs_improvement'
        }
    
    async def _identify_issues(
        self,
        technical: Dict[str, Any],
        content: Dict[str, Any],
        images: Dict[str, Any],
        headings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """شناسایی مشکلات"""
        issues = []
        
        # مشکلات فنی
        if technical['crawlability'] != 'good':
            issues.append({
                'type': 'crawlability',
                'severity': 'high',
                'title': 'مشکل در Crawlability',
                'description': 'سایت ممکن است برای موتورهای جستجو قابل crawl نباشد',
                'recommendation': 'بررسی robots.txt و sitemap.xml'
            })
        
        if technical['indexability'] != 'good':
            issues.append({
                'type': 'indexability',
                'severity': 'high',
                'title': 'مشکل در Indexability',
                'description': 'برخی صفحات ممکن است index نشوند',
                'recommendation': 'بررسی meta robots tags'
            })
        
        # مشکلات محتوا
        if content['readability'] < 50:
            issues.append({
                'type': 'readability',
                'severity': 'medium',
                'title': 'امتیاز خوانایی پایین',
                'description': f'امتیاز خوانایی: {content["readability"]}',
                'recommendation': 'ساده‌سازی محتوا و استفاده از جملات کوتاه‌تر'
            })
        
        if len(content['keywords']) == 0:
            issues.append({
                'type': 'keywords',
                'severity': 'medium',
                'title': 'کلمات کلیدی شناسایی نشد',
                'description': 'هیچ کلمه کلیدی معنی‌داری در محتوا یافت نشد',
                'recommendation': 'افزودن کلمات کلیدی مرتبط به محتوا'
            })
        
        # مشکلات تصاویر
        if images['without_alt'] > 0:
            issues.append({
                'type': 'images_alt',
                'severity': 'high',
                'title': f'{images["without_alt"]} تصویر بدون Alt Text',
                'description': 'تصاویر بدون alt text برای سئو مناسب نیستند',
                'recommendation': 'افزودن alt text به تمام تصاویر'
            })
        
        # مشکلات سرفصل‌ها
        if len(headings['pages_without_h1']) > 0:
            issues.append({
                'type': 'headings_h1',
                'severity': 'high',
                'title': f'{len(headings["pages_without_h1"])} صفحه بدون H1',
                'description': 'هر صفحه باید یک تگ H1 داشته باشد',
                'recommendation': 'افزودن تگ H1 به صفحات بدون H1'
            })
        
        if len(headings['pages_with_multiple_h1']) > 0:
            issues.append({
                'type': 'headings_multiple_h1',
                'severity': 'medium',
                'title': f'{len(headings["pages_with_multiple_h1"])} صفحه با چند H1',
                'description': 'هر صفحه باید فقط یک تگ H1 داشته باشد',
                'recommendation': 'کاهش تعداد H1 به یک عدد در هر صفحه'
            })
        
        return issues
    
    async def close(self):
        """بستن client"""
        await self.client.aclose()
