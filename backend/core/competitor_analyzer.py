"""
ماژول تحلیل رقبا و استخراج کلمات کلیدی
"""

import asyncio
import logging
from typing import Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import re
from collections import Counter
import json

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """کلاس تحلیل رقبا و استخراج کلمات کلیدی"""
    
    def __init__(self):
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
    
    async def find_competitors(self, site_url: str, industry_keywords: List[str] = None) -> List[str]:
        """
        پیدا کردن سایت‌های رقیب بر اساس کلمات کلیدی صنعت
        
        Args:
            site_url: آدرس سایت اصلی
            industry_keywords: کلمات کلیدی صنعت (اختیاری)
            
        Returns:
            لیست آدرس‌های سایت‌های رقیب
        """
        logger.info(f"Finding competitors for: {site_url}")
        
        # استخراج دامنه اصلی
        parsed = urlparse(site_url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        domain_parts = domain.replace('www.', '').split('.')
        site_name = domain_parts[0] if domain_parts else ''
        
        competitors = []
        
        # اگر کلمات کلیدی صنعت داده نشده، از محتوای سایت استخراج می‌کنیم
        if not industry_keywords:
            industry_keywords = await self._extract_industry_keywords(site_url)
        
        # جستجوی رقبا (این یک نمونه است - در production می‌توان از Google Search API استفاده کرد)
        # برای حال حاضر، از لیست پیش‌فرض استفاده می‌کنیم
        competitors = await self._search_competitors_by_keywords(industry_keywords, site_url)
        
        return competitors[:5]  # حداکثر 5 رقیب
    
    async def _extract_industry_keywords(self, site_url: str) -> List[str]:
        """استخراج کلمات کلیدی صنعت از سایت"""
        try:
            response = await self.client.get(site_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج از meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = []
            if meta_keywords and meta_keywords.get('content'):
                meta_kw = [k.strip().lower() for k in meta_keywords.get('content', '').split(',')]
                keywords.extend([kw for kw in meta_kw if self._is_valid_keyword(kw)])
            
            # استخراج از title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # فیلتر کردن اعداد و کلمات نامعتبر
                title_words = [w.strip().lower() for w in title_text.split() if len(w) > 3]
                keywords.extend([w for w in title_words if self._is_valid_keyword(w)])
            
            # استخراج از h1
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags[:3]:
                h1_text = h1.get_text()
                h1_words = [w.strip().lower() for w in h1_text.split() if len(w) > 3]
                keywords.extend([w for w in h1_words if self._is_valid_keyword(w)])
            
            # فیلتر کردن meta keywords هم
            filtered_keywords = [kw for kw in keywords if self._is_valid_keyword(kw.strip().lower())]
            
            return list(set(filtered_keywords))[:10]  # حداکثر 10 کلمه کلیدی
        except Exception as e:
            logger.error(f"Error extracting industry keywords: {str(e)}")
            return []
    
    async def _search_competitors_by_keywords(self, keywords: List[str], original_site: str) -> List[str]:
        """
        جستجوی رقبا بر اساس کلمات کلیدی
        این یک پیاده‌سازی ساده است - در production می‌توان از Google Search API استفاده کرد
        """
        competitors = []
        
        # برای نمونه، از دامنه‌های مشابه استفاده می‌کنیم
        # در production، این باید از Google Search API یا ابزارهای SEO استفاده کند
        parsed = urlparse(original_site)
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # نمونه رقبا (در production باید از API استفاده شود)
        # این فقط برای نمایش است
        sample_competitors = [
            f"https://competitor1-{domain.split('.')[0]}.com",
            f"https://competitor2-{domain.split('.')[0]}.com",
        ]
        
        return competitors
    
    async def analyze_competitor(self, competitor_url: str) -> Dict[str, Any]:
        """
        تحلیل یک رقیب و استخراج کلمات کلیدی
        
        Args:
            competitor_url: آدرس سایت رقیب
            
        Returns:
            اطلاعات تحلیل شده رقیب
        """
        logger.info(f"Analyzing competitor: {competitor_url}")
        
        try:
            # دریافت صفحه اصلی
            response = await self.client.get(competitor_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج کلمات کلیدی
            keywords = await self._extract_keywords(soup, competitor_url)
            
            # استخراج اطلاعات اضافی
            meta_info = self._extract_meta_info(soup)
            
            # تحلیل محتوا
            content_analysis = await self._analyze_content(soup, competitor_url)
            
            return {
                'url': competitor_url,
                'keywords': keywords,
                'meta_info': meta_info,
                'content_analysis': content_analysis,
                'analyzed_at': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitor {competitor_url}: {str(e)}")
            return {
                'url': competitor_url,
                'error': str(e),
                'keywords': [],
                'meta_info': {},
                'content_analysis': {}
            }
    
    def _is_product_page(self, soup: BeautifulSoup, url: str) -> bool:
        """تشخیص صفحات محصول"""
        # بررسی URL
        url_lower = url.lower()
        product_indicators = ['product', 'shop', 'buy', 'price', 'cart', 'محصول', 'خرید', 'فروش']
        if any(indicator in url_lower for indicator in product_indicators):
            return True
        
        # بررسی محتوا
        text_content = soup.get_text().lower()
        product_keywords = ['price', 'buy', 'add to cart', 'محصول', 'قیمت', 'خرید', 'فروش', 'تخفیف']
        if any(kw in text_content for kw in product_keywords):
            return True
        
        # بررسی structured data
        if soup.find('script', type='application/ld+json'):
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') in ['Product', 'Offer']:
                            return True
                except:
                    pass
        
        return False
    
    def _is_article_page(self, soup: BeautifulSoup, url: str) -> bool:
        """تشخیص صفحات مقاله"""
        # بررسی URL
        url_lower = url.lower()
        article_indicators = ['article', 'blog', 'post', 'news', 'مقاله', 'بلاگ', 'خبر']
        if any(indicator in url_lower for indicator in article_indicators):
            return True
        
        # بررسی structured data
        if soup.find('script', type='application/ld+json'):
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') in ['Article', 'BlogPosting', 'NewsArticle']:
                            return True
                except:
                    pass
        
        # بررسی تگ‌های article
        if soup.find('article'):
            return True
        
        # بررسی محتوا (مقالات معمولاً محتوای بیشتری دارند)
        paragraphs = soup.find_all('p')
        if len(paragraphs) >= 3:  # حداقل 3 پاراگراف
            return True
        
        return False
    
    def _extract_phrases(self, text: str, keyword_frequency: Counter, weight: int = 1):
        """
        استخراج عبارات دو و سه کلمه‌ای از متن
        """
        # استخراج کلمات معتبر
        words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', text.lower(), re.UNICODE)
        valid_words = [w for w in words if self._is_valid_keyword(w)]
        
        if len(valid_words) < 2:
            return
        
        # استخراج عبارات دو کلمه‌ای (bigrams)
        for i in range(len(valid_words) - 1):
            bigram = f"{valid_words[i]} {valid_words[i+1]}"
            if len(bigram) <= 50:  # محدود کردن طول
                keyword_frequency[bigram] += weight
        
        # استخراج عبارات سه کلمه‌ای (trigrams)
        for i in range(len(valid_words) - 2):
            trigram = f"{valid_words[i]} {valid_words[i+1]} {valid_words[i+2]}"
            if len(trigram) <= 60:  # محدود کردن طول
                keyword_frequency[trigram] += weight
    
    def _extract_phrases_with_source(self, text: str, keyword_frequency: Counter, 
                                     keyword_sources: Dict[str, int], weight: int = 1):
        """
        استخراج عبارات دو و سه کلمه‌ای از متن با ذخیره منبع
        """
        # استخراج کلمات معتبر
        words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', text.lower(), re.UNICODE)
        valid_words = [w for w in words if self._is_valid_keyword(w)]
        
        if len(valid_words) < 2:
            return
        
        # استخراج عبارات دو کلمه‌ای (bigrams)
        for i in range(len(valid_words) - 1):
            bigram = f"{valid_words[i]} {valid_words[i+1]}"
            if len(bigram) <= 50:  # محدود کردن طول
                keyword_frequency[bigram] += weight
                keyword_sources[bigram] = max(keyword_sources.get(bigram, 0), weight)
        
        # استخراج عبارات سه کلمه‌ای (trigrams)
        for i in range(len(valid_words) - 2):
            trigram = f"{valid_words[i]} {valid_words[i+1]} {valid_words[i+2]}"
            if len(trigram) <= 60:  # محدود کردن طول
                keyword_frequency[trigram] += weight
                keyword_sources[trigram] = max(keyword_sources.get(trigram, 0), weight)
    
    def _calculate_priority(self, keyword: str, frequency: int, word_count: int, 
                           is_product_page: bool, is_article_page: bool, 
                           source_weight: int) -> str:
        """
        محاسبه اولویت کلمه کلیدی
        
        Args:
            keyword: کلمه کلیدی
            frequency: فرکانس
            word_count: تعداد کلمات (1, 2, 3)
            is_product_page: آیا صفحه محصول است
            is_article_page: آیا صفحه مقاله است
            source_weight: وزن منبع (5 برای meta, 4 برای title, ...)
            
        Returns:
            'high', 'medium', یا 'low'
        """
        priority_score = 0
        
        # 1. فرکانس (0-30 امتیاز)
        if frequency >= 10:
            priority_score += 30
        elif frequency >= 5:
            priority_score += 20
        elif frequency >= 3:
            priority_score += 10
        else:
            priority_score += 5
        
        # 2. نوع کلمه کلیدی (عبارات چند کلمه‌ای اولویت بالاتر)
        if word_count == 3:
            priority_score += 25  # عبارات سه کلمه‌ای
        elif word_count == 2:
            priority_score += 20  # عبارات دو کلمه‌ای
        else:
            priority_score += 10  # تک کلمه‌ای
        
        # 3. منبع (meta keywords و title اولویت بالاتر)
        if source_weight >= 5:
            priority_score += 20  # Meta Keywords
        elif source_weight >= 4:
            priority_score += 15  # Title
        elif source_weight >= 3:
            priority_score += 10  # Meta Description
        elif source_weight >= 2:
            priority_score += 5   # Headings, Links
        
        # 4. صفحات محصول و مقاله (اولویت بالاتر)
        if is_product_page or is_article_page:
            priority_score += 15
        
        # 5. طول کلمه کلیدی (کلمات کلیدی معقول)
        keyword_length = len(keyword)
        if 5 <= keyword_length <= 50:
            priority_score += 5
        elif keyword_length > 50:
            priority_score -= 5  # خیلی طولانی
        
        # تعیین اولویت نهایی
        if priority_score >= 60:
            return 'high'
        elif priority_score >= 35:
            return 'medium'
        else:
            return 'low'
    
    def _is_valid_keyword(self, keyword: str) -> bool:
        """
        بررسی معتبر بودن کلمه کلیدی
        - نباید فقط عدد باشد
        - باید حداقل یک حرف داشته باشد
        - نباید کلمات فنی رایج باشد
        """
        if not keyword or len(keyword) < 2:
            return False
        
        # حذف اعداد خالص
        if keyword.isdigit():
            return False
        
        # حذف کلمات که فقط عدد و کاراکترهای خاص دارند
        if not any(c.isalpha() for c in keyword):
            return False
        
        # حذف کلمات فنی رایج
        technical_words = {
            'http', 'https', 'www', 'com', 'org', 'net', 'ir', 'co', 'io',
            'html', 'css', 'js', 'php', 'asp', 'xml', 'json', 'api',
            'div', 'span', 'class', 'id', 'src', 'href', 'alt', 'title'
        }
        if keyword.lower() in technical_words:
            return False
        
        # حذف کلمات خیلی کوتاه (کمتر از 2 کاراکتر) مگر اینکه حروف فارسی باشد
        if len(keyword) < 2:
            return False
        
        # برای کلمات 2 کاراکتری، فقط فارسی را قبول می‌کنیم
        if len(keyword) == 2:
            has_persian = any('\u0600' <= c <= '\u06FF' for c in keyword)
            if not has_persian:
                return False
        
        return True
    
    async def _extract_keywords(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """استخراج کلمات کلیدی از صفحه (تک کلمه‌ای، دو کلمه‌ای و سه کلمه‌ای)"""
        keywords = []
        keyword_frequency = Counter()
        keyword_sources = {}  # ذخیره منبع و وزن هر کلمه کلیدی
        
        # تشخیص صفحات محصول و مقاله
        is_product_page = self._is_product_page(soup, url)
        is_article_page = self._is_article_page(soup, url)
        
        logger.info(f"Extracting keywords from {url} - Product: {is_product_page}, Article: {is_article_page}")
        
        # 1. از Meta Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            meta_kw = [k.strip().lower() for k in meta_keywords.get('content', '').split(',')]
            for kw in meta_kw:
                if len(kw) > 2 and self._is_valid_keyword(kw):
                    keyword_frequency[kw] += 5  # وزن بیشتر برای meta keywords
                    keyword_sources[kw] = max(keyword_sources.get(kw, 0), 5)  # ذخیره وزن منبع
                    # استخراج عبارات چند کلمه‌ای از meta keywords
                    self._extract_phrases_with_source(kw, keyword_frequency, keyword_sources, weight=5)
        
        # 2. از Title
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            # استفاده از regex که فقط حروف را می‌گیرد (نه اعداد)
            title_words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', title_text, re.UNICODE)
            for word in title_words:
                if self._is_valid_keyword(word):
                    keyword_frequency[word] += 4
                    keyword_sources[word] = max(keyword_sources.get(word, 0), 4)
            
            # استخراج عبارات چند کلمه‌ای از title
            self._extract_phrases_with_source(title_text, keyword_frequency, keyword_sources, weight=4)
        
        # 3. از Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_text = meta_desc.get('content', '').lower()
            desc_words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', desc_text, re.UNICODE)
            for word in desc_words:
                if self._is_valid_keyword(word):
                    keyword_frequency[word] += 3
                    keyword_sources[word] = max(keyword_sources.get(word, 0), 3)
            
            # استخراج عبارات چند کلمه‌ای از description
            self._extract_phrases_with_source(desc_text, keyword_frequency, keyword_sources, weight=3)
        
        # 4. از H1-H3
        for tag_name in ['h1', 'h2', 'h3']:
            tags = soup.find_all(tag_name)
            for tag in tags:
                tag_text = tag.get_text().lower()
                tag_words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', tag_text, re.UNICODE)
                weight = 3 if tag_name == 'h1' else (2 if tag_name == 'h2' else 1)
                for word in tag_words:
                    if self._is_valid_keyword(word):
                        keyword_frequency[word] += weight
                        keyword_sources[word] = max(keyword_sources.get(word, 0), weight)
                
                # استخراج عبارات چند کلمه‌ای از headings
                self._extract_phrases_with_source(tag_text, keyword_frequency, keyword_sources, weight=weight)
        
        # 5. از محتوای اصلی (پاراگراف‌ها) - تمرکز روی صفحات محصول و مقاله
        paragraphs = soup.find_all('p')
        para_limit = 30 if (is_product_page or is_article_page) else 20  # بیشتر برای صفحات محصول/مقاله
        
        for para in paragraphs[:para_limit]:
            para_text = para.get_text().lower()
            para_words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', para_text, re.UNICODE)
            for word in para_words:
                if self._is_valid_keyword(word):
                    # وزن بیشتر برای صفحات محصول و مقاله
                    weight = 2 if (is_product_page or is_article_page) else 1
                    keyword_frequency[word] += weight
            
            # استخراج عبارات چند کلمه‌ای از پاراگراف‌ها (فقط برای صفحات محصول و مقاله)
            if is_product_page or is_article_page:
                self._extract_phrases_with_source(para_text, keyword_frequency, keyword_sources, weight=1)
        
        # 6. از لینک‌ها (anchor text)
        links = soup.find_all('a', href=True)
        for link in links[:30]:  # محدود کردن به 30 لینک اول
            link_text = link.get_text().lower().strip()
            if link_text and len(link_text) < 50:  # فقط anchor text کوتاه
                link_words = re.findall(r'\b[a-z\u0600-\u06FF]{3,}\b', link_text, re.UNICODE)
                for word in link_words:
                    if self._is_valid_keyword(word):
                        keyword_frequency[word] += 2
                        keyword_sources[word] = max(keyword_sources.get(word, 0), 2)
        
        # لاگ برای دیباگ
        logger.info(f"Total keywords found before filtering: {len(keyword_frequency)}")
        if len(keyword_frequency) > 0:
            logger.info(f"Top 10 keywords by frequency: {keyword_frequency.most_common(10)}")
        
        # تبدیل به لیست و مرتب‌سازی
        # افزایش تعداد برای شامل کردن عبارات چند کلمه‌ای
        limit = 100 if (is_product_page or is_article_page) else 50
        
        for keyword, frequency in keyword_frequency.most_common(limit):
            # برای عبارات چند کلمه‌ای، بررسی جداگانه
            if ' ' in keyword:
                # عبارات چند کلمه‌ای - بررسی معتبر بودن هر کلمه
                words = keyword.split()
                if all(self._is_valid_keyword(w) for w in words) and len(words) <= 3:
                    if frequency >= 1:  # فرکانس کمتر برای عبارات چند کلمه‌ای
                        source_weight = keyword_sources.get(keyword, 1)
                        priority = self._calculate_priority(
                            keyword, frequency, len(words), 
                            is_product_page, is_article_page, source_weight
                        )
                        keywords.append({
                            'keyword': keyword,
                            'frequency': frequency,
                            'source': 'competitor_analysis',
                            'competitor_url': url,
                            'type': 'phrase',
                            'word_count': len(words),
                            'priority': priority,
                            'source_weight': source_weight
                        })
            else:
                # کلمات تک کلمه‌ای - کاهش حداقل فرکانس برای استخراج بیشتر
                if frequency >= 1 and self._is_valid_keyword(keyword):
                    source_weight = keyword_sources.get(keyword, 1)
                    priority = self._calculate_priority(
                        keyword, frequency, 1, 
                        is_product_page, is_article_page, source_weight
                    )
                    keywords.append({
                        'keyword': keyword,
                        'frequency': frequency,
                        'source': 'competitor_analysis',
                        'competitor_url': url,
                        'type': 'single',
                        'word_count': 1,
                        'priority': priority,
                        'source_weight': source_weight
                    })
        
        # مرتب‌سازی: اول بر اساس اولویت، سپس عبارات چند کلمه‌ای، سپس فرکانس
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        keywords.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'low'), 1),  # اول اولویت
            x.get('word_count', 1) > 1,  # سپس عبارات چند کلمه‌ای
            -x.get('frequency', 0)  # سپس فرکانس
        ), reverse=True)
        
        return keywords[:100]  # حداکثر 100 کلمه کلیدی
    
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """استخراج اطلاعات متا"""
        meta_info = {}
        
        # Title
        title = soup.find('title')
        if title:
            meta_info['title'] = title.get_text().strip()
        
        # Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_info['description'] = meta_desc.get('content', '').strip()
        
        # Meta Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            meta_info['keywords'] = meta_keywords.get('content', '').strip()
        
        # Open Graph
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            meta_info['og_title'] = og_title.get('content', '').strip()
        
        og_description = soup.find('meta', attrs={'property': 'og:description'})
        if og_description:
            meta_info['og_description'] = og_description.get('content', '').strip()
        
        return meta_info
    
    async def _analyze_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """تحلیل محتوا"""
        content_analysis = {
            'total_words': 0,
            'h1_count': 0,
            'h2_count': 0,
            'h3_count': 0,
            'image_count': 0,
            'link_count': 0
        }
        
        # شمارش کلمات
        text_content = soup.get_text()
        words = re.findall(r'\b\w+\b', text_content)
        content_analysis['total_words'] = len(words)
        
        # شمارش تگ‌های هدینگ
        content_analysis['h1_count'] = len(soup.find_all('h1'))
        content_analysis['h2_count'] = len(soup.find_all('h2'))
        content_analysis['h3_count'] = len(soup.find_all('h3'))
        
        # شمارش تصاویر
        content_analysis['image_count'] = len(soup.find_all('img'))
        
        # شمارش لینک‌ها
        content_analysis['link_count'] = len(soup.find_all('a', href=True))
        
        return content_analysis
    
    async def analyze_multiple_competitors(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """
        تحلیل چندین رقیب به صورت موازی
        
        Args:
            competitor_urls: لیست آدرس‌های رقبا
            
        Returns:
            نتایج تحلیل تمام رقبا
        """
        logger.info(f"Analyzing {len(competitor_urls)} competitors")
        
        # تحلیل موازی
        tasks = [self.analyze_competitor(url) for url in competitor_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ترکیب کلمات کلیدی
        all_keywords = {}
        competitor_data = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error analyzing competitor {competitor_urls[i]}: {str(result)}")
                continue
            
            competitor_data.append(result)
            
            # ترکیب کلمات کلیدی
            for kw_data in result.get('keywords', []):
                keyword = kw_data['keyword']
                if keyword not in all_keywords:
                    all_keywords[keyword] = {
                        'keyword': keyword,
                        'total_frequency': 0,
                        'competitors_count': 0,
                        'competitors': [],
                        'priorities': [],  # لیست اولویت‌ها از رقبا
                        'word_count': kw_data.get('word_count', 1),
                        'type': kw_data.get('type', 'single')
                    }
                
                all_keywords[keyword]['total_frequency'] += kw_data['frequency']
                all_keywords[keyword]['competitors_count'] += 1
                all_keywords[keyword]['competitors'].append({
                    'url': kw_data['competitor_url'],
                    'frequency': kw_data['frequency']
                })
                
                # جمع‌آوری اولویت‌ها
                if 'priority' in kw_data:
                    all_keywords[keyword]['priorities'].append(kw_data['priority'])
        
        # محاسبه اولویت نهایی برای هر کلمه کلیدی
        for kw in all_keywords.values():
            priorities = kw.get('priorities', [])
            if priorities:
                # اگر اکثر رقبا اولویت بالا دارند، اولویت بالا
                high_count = priorities.count('high')
                medium_count = priorities.count('medium')
                if high_count >= len(priorities) * 0.5:  # 50% یا بیشتر
                    kw['priority'] = 'high'
                elif high_count + medium_count >= len(priorities) * 0.5:
                    kw['priority'] = 'medium'
                else:
                    kw['priority'] = 'low'
            else:
                # اگر اولویت نداشت، بر اساس فرکانس و تعداد رقبا تعیین می‌شود
                if kw['competitors_count'] >= 3 and kw['total_frequency'] >= 10:
                    kw['priority'] = 'high'
                elif kw['competitors_count'] >= 2 and kw['total_frequency'] >= 5:
                    kw['priority'] = 'medium'
                else:
                    kw['priority'] = 'low'
        
        # مرتب‌سازی کلمات کلیدی: اول اولویت، سپس تعداد رقبا، سپس فرکانس
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_keywords = sorted(
            all_keywords.values(),
            key=lambda x: (
                priority_order.get(x.get('priority', 'low'), 1),
                x['competitors_count'],
                x['total_frequency']
            ),
            reverse=True
        )
        
        return {
            'competitors': competitor_data,
            'keywords': sorted_keywords[:100],  # 100 کلمه کلیدی برتر
            'total_competitors_analyzed': len(competitor_data),
            'total_keywords_found': len(sorted_keywords)
        }
    
    async def get_competitor_keywords_for_selection(self, competitor_urls: List[str]) -> List[Dict[str, Any]]:
        """
        دریافت کلمات کلیدی رقبا برای انتخاب در فرانت‌اند
        
        Args:
            competitor_urls: لیست آدرس‌های رقبا
            
        Returns:
            لیست کلمات کلیدی با اطلاعات کامل برای نمایش
        """
        analysis = await self.analyze_multiple_competitors(competitor_urls)
        
        # فرمت کردن برای نمایش در فرانت‌اند
        keywords_for_selection = []
        for kw in analysis['keywords']:
            keywords_for_selection.append({
                'id': f"comp_kw_{hash(kw['keyword'])}",
                'keyword': kw['keyword'],
                'frequency': kw['total_frequency'],
                'competitors_count': kw['competitors_count'],
                'competitors': kw['competitors'],
                'selected': False,  # برای انتخاب در فرانت‌اند
                'priority': kw.get('priority', 'low'),  # استفاده از اولویت محاسبه شده
                'word_count': kw.get('word_count', 1),
                'type': kw.get('type', 'single')
            })
        
        return keywords_for_selection

