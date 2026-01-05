"""
تحلیل ویژگی‌های SERP (Search Engine Results Page)
استخراج Featured Snippets, People Also Ask, Related Searches, Image Pack, Video Results, Local Pack
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode
import re
import json

logger = logging.getLogger(__name__)


class SERPFeatureAnalyzer:
    """
    کلاس تحلیل ویژگی‌های SERP
    
    ویژگی‌های قابل تحلیل:
    - Featured Snippets
    - People Also Ask (PAA)
    - Related Searches
    - Image Pack
    - Video Results
    - Local Pack
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
    
    async def analyze_serp_features(
        self,
        keyword: str,
        language: str = 'fa',
        location: str = 'ir'
    ) -> Dict[str, Any]:
        """
        تحلیل ویژگی‌های SERP
        
        Args:
            keyword: کلمه کلیدی
            language: زبان
            location: موقعیت جغرافیایی
        
        Returns:
            {
                'keyword': str,
                'featured_snippet': Dict,
                'people_also_ask': List[Dict],
                'related_searches': List[str],
                'image_pack': Dict,
                'video_results': List[Dict],
                'local_pack': Dict,
                'organic_results': List[Dict],
                'summary': Dict
            }
        """
        try:
            # دریافت صفحه نتایج جستجو
            html_content = await self._fetch_serp(keyword, language, location)
            
            if not html_content:
                return self._empty_serp_result(keyword)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # استخراج ویژگی‌ها
            featured_snippet = self._extract_featured_snippet(soup)
            people_also_ask = self._extract_people_also_ask(soup)
            related_searches = self._extract_related_searches(soup)
            image_pack = self._extract_image_pack(soup)
            video_results = self._extract_video_results(soup)
            local_pack = self._extract_local_pack(soup)
            organic_results = self._extract_organic_results(soup)
            
            # محاسبه خلاصه
            summary = self._calculate_summary(
                featured_snippet,
                people_also_ask,
                related_searches,
                image_pack,
                video_results,
                local_pack,
                organic_results
            )
            
            return {
                'keyword': keyword,
                'featured_snippet': featured_snippet,
                'people_also_ask': people_also_ask,
                'related_searches': related_searches,
                'image_pack': image_pack,
                'video_results': video_results,
                'local_pack': local_pack,
                'organic_results': organic_results[:10],  # 10 نتیجه اول
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SERP features: {str(e)}")
            return self._empty_serp_result(keyword)
    
    async def _fetch_serp(
        self,
        keyword: str,
        language: str,
        location: str
    ) -> Optional[str]:
        """دریافت صفحه نتایج جستجو"""
        try:
            url = "https://www.google.com/search"
            params = {
                'q': keyword,
                'hl': language,
                'gl': location,
                'num': 10
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch SERP: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching SERP: {str(e)}")
            return None
    
    def _extract_featured_snippet(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """استخراج Featured Snippet"""
        featured_snippet = {
            'present': False,
            'type': None,  # paragraph, list, table
            'title': None,
            'content': None,
            'source_url': None,
            'source_title': None
        }
        
        try:
            # جستجوی Featured Snippet در ساختارهای مختلف Google
            # Google از classهای مختلفی استفاده می‌کند
            
            # روش 1: جستجوی در divهای با class خاص
            snippet_divs = soup.find_all('div', class_=re.compile(r'featured|snippet|answer'))
            
            for div in snippet_divs:
                # بررسی اینکه آیا Featured Snippet است
                text = div.get_text(strip=True)
                if len(text) > 50:  # Featured Snippet معمولاً طولانی است
                    featured_snippet['present'] = True
                    featured_snippet['content'] = text[:500]  # 500 کاراکتر اول
                    
                    # پیدا کردن لینک منبع
                    link = div.find('a', href=True)
                    if link:
                        featured_snippet['source_url'] = link.get('href', '')
                        featured_snippet['source_title'] = link.get_text(strip=True)
                    
                    # تعیین نوع
                    if div.find('ul') or div.find('ol'):
                        featured_snippet['type'] = 'list'
                    elif div.find('table'):
                        featured_snippet['type'] = 'table'
                    else:
                        featured_snippet['type'] = 'paragraph'
                    
                    break
            
            # روش 2: جستجوی در ساختارهای دیگر
            if not featured_snippet['present']:
                # جستجوی در divهای با id خاص
                answer_div = soup.find('div', id=re.compile(r'answer|snippet'))
                if answer_div:
                    text = answer_div.get_text(strip=True)
                    if len(text) > 50:
                        featured_snippet['present'] = True
                        featured_snippet['content'] = text[:500]
                        featured_snippet['type'] = 'paragraph'
        
        except Exception as e:
            logger.error(f"Error extracting featured snippet: {str(e)}")
        
        return featured_snippet
    
    def _extract_people_also_ask(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """استخراج People Also Ask"""
        paa_items = []
        
        try:
            # جستجوی People Also Ask
            # Google از ساختارهای مختلفی استفاده می‌کند
            
            # روش 1: جستجوی در divهای با class خاص
            paa_divs = soup.find_all('div', class_=re.compile(r'related-question|also-ask|people-ask'))
            
            for div in paa_divs:
                question = div.get_text(strip=True)
                if question and len(question) > 10:
                    paa_items.append({
                        'question': question,
                        'expanded': False  # در حالت اولیه expand نشده
                    })
            
            # روش 2: جستجوی در ساختارهای دیگر
            if not paa_items:
                # جستجوی در divهای با attribute خاص
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    # بررسی اینکه آیا سوال است
                    if any(qw in text.lower() for qw in ['what', 'how', 'why', 'when', 'where', 'which', 'چیست', 'چگونه', 'چرا']):
                        if 10 < len(text) < 200 and '?' in text:
                            paa_items.append({
                                'question': text,
                                'expanded': False
                            })
                            if len(paa_items) >= 10:  # حداکثر 10 سوال
                                break
        
        except Exception as e:
            logger.error(f"Error extracting People Also Ask: {str(e)}")
        
        return paa_items[:10]  # حداکثر 10 سوال
    
    def _extract_related_searches(self, soup: BeautifulSoup) -> List[str]:
        """استخراج Related Searches"""
        related_searches = []
        
        try:
            # جستجوی Related Searches
            # Google معمولاً آن‌ها را در پایین صفحه قرار می‌دهد
            
            # روش 1: جستجوی در divهای با class خاص
            related_divs = soup.find_all('div', class_=re.compile(r'related|also-search'))
            
            for div in related_divs:
                links = div.find_all('a', href=True)
                for link in links:
                    text = link.get_text(strip=True)
                    if text and len(text) > 3:
                        related_searches.append(text)
            
            # روش 2: جستجوی در بخش "Searches related to"
            page_text = soup.get_text()
            if 'related to' in page_text.lower() or 'مرتبط' in page_text:
                # استخراج کلمات کلیدی از اطراف این متن
                for div in soup.find_all('div'):
                    text = div.get_text(strip=True)
                    if len(text.split()) >= 2 and len(text) < 100:
                        # بررسی اینکه آیا کلمه کلیدی است
                        if not any(char in text for char in ['|', '•', '→', ':']):
                            related_searches.append(text)
                            if len(related_searches) >= 10:
                                break
        
        except Exception as e:
            logger.error(f"Error extracting related searches: {str(e)}")
        
        # حذف تکراری‌ها
        return list(dict.fromkeys(related_searches))[:10]
    
    def _extract_image_pack(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """استخراج Image Pack"""
        image_pack = {
            'present': False,
            'images': [],
            'total_count': 0
        }
        
        try:
            # جستجوی Image Pack
            # Google معمولاً تصاویر را در یک بخش خاص قرار می‌دهد
            
            image_divs = soup.find_all('div', class_=re.compile(r'image|photo|picture'))
            
            for div in image_divs:
                images = div.find_all('img', src=True)
                if images:
                    image_pack['present'] = True
                    for img in images[:20]:  # حداکثر 20 تصویر
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if src and 'http' in src:
                            image_pack['images'].append({
                                'url': src,
                                'alt': alt
                            })
                    image_pack['total_count'] = len(image_pack['images'])
                    break
        
        except Exception as e:
            logger.error(f"Error extracting image pack: {str(e)}")
        
        return image_pack
    
    def _extract_video_results(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """استخراج Video Results"""
        video_results = []
        
        try:
            # جستجوی Video Results
            video_divs = soup.find_all('div', class_=re.compile(r'video|youtube'))
            
            for div in video_divs:
                # پیدا کردن لینک ویدیو
                link = div.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # بررسی اینکه آیا لینک YouTube است
                    if 'youtube.com' in href or 'youtu.be' in href:
                        video_results.append({
                            'title': title,
                            'url': href,
                            'source': 'youtube'
                        })
                    elif title and len(title) > 5:
                        video_results.append({
                            'title': title,
                            'url': href,
                            'source': 'other'
                        })
        
        except Exception as e:
            logger.error(f"Error extracting video results: {str(e)}")
        
        return video_results[:10]  # حداکثر 10 ویدیو
    
    def _extract_local_pack(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """استخراج Local Pack"""
        local_pack = {
            'present': False,
            'businesses': [],
            'map_present': False
        }
        
        try:
            # جستجوی Local Pack
            # Google معمولاً Local Pack را در یک بخش خاص قرار می‌دهد
            
            local_divs = soup.find_all('div', class_=re.compile(r'local|map|business|place'))
            
            for div in local_divs:
                # بررسی اینکه آیا Local Pack است
                text = div.get_text()
                if 'map' in text.lower() or 'directions' in text.lower() or 'نقشه' in text:
                    local_pack['present'] = True
                    local_pack['map_present'] = True
                    
                    # استخراج اطلاعات کسب‌وکارها
                    business_divs = div.find_all('div', class_=re.compile(r'business|place|result'))
                    
                    for biz_div in business_divs[:5]:  # حداکثر 5 کسب‌وکار
                        name = biz_div.find('div', class_=re.compile(r'name|title'))
                        if name:
                            business_name = name.get_text(strip=True)
                            if business_name:
                                local_pack['businesses'].append({
                                    'name': business_name,
                                    'address': None,  # می‌توان استخراج کرد
                                    'rating': None,  # می‌توان استخراج کرد
                                    'phone': None  # می‌توان استخراج کرد
                                })
                    
                    break
        
        except Exception as e:
            logger.error(f"Error extracting local pack: {str(e)}")
        
        return local_pack
    
    def _extract_organic_results(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """استخراج نتایج Organic"""
        organic_results = []
        
        try:
            # جستجوی نتایج Organic
            # Google از class 'g' برای نتایج organic استفاده می‌کند
            
            result_divs = soup.find_all('div', class_='g')
            
            for div in result_divs[:10]:  # 10 نتیجه اول
                result = {
                    'title': None,
                    'url': None,
                    'snippet': None,
                    'position': len(organic_results) + 1
                }
                
                # استخراج عنوان
                title_elem = div.find('h3')
                if title_elem:
                    result['title'] = title_elem.get_text(strip=True)
                
                # استخراج URL
                link = div.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if 'http' in href:
                        result['url'] = href
                
                # استخراج snippet
                snippet_elem = div.find('span', class_=re.compile(r'snippet|description'))
                if snippet_elem:
                    result['snippet'] = snippet_elem.get_text(strip=True)
                else:
                    # جستجوی در divهای دیگر
                    text_divs = div.find_all('div')
                    for text_div in text_divs:
                        text = text_div.get_text(strip=True)
                        if 50 < len(text) < 300:
                            result['snippet'] = text
                            break
                
                if result['title'] and result['url']:
                    organic_results.append(result)
        
        except Exception as e:
            logger.error(f"Error extracting organic results: {str(e)}")
        
        return organic_results
    
    def _calculate_summary(
        self,
        featured_snippet: Dict[str, Any],
        people_also_ask: List[Dict[str, Any]],
        related_searches: List[str],
        image_pack: Dict[str, Any],
        video_results: List[Dict[str, Any]],
        local_pack: Dict[str, Any],
        organic_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """محاسبه خلاصه"""
        return {
            'featured_snippet_present': featured_snippet.get('present', False),
            'people_also_ask_count': len(people_also_ask),
            'related_searches_count': len(related_searches),
            'image_pack_present': image_pack.get('present', False),
            'image_count': image_pack.get('total_count', 0),
            'video_results_count': len(video_results),
            'local_pack_present': local_pack.get('present', False),
            'businesses_count': len(local_pack.get('businesses', [])),
            'organic_results_count': len(organic_results),
            'total_features': sum([
                1 if featured_snippet.get('present') else 0,
                1 if len(people_also_ask) > 0 else 0,
                1 if len(related_searches) > 0 else 0,
                1 if image_pack.get('present') else 0,
                1 if len(video_results) > 0 else 0,
                1 if local_pack.get('present') else 0
            ])
        }
    
    def _empty_serp_result(self, keyword: str) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'keyword': keyword,
            'featured_snippet': {'present': False},
            'people_also_ask': [],
            'related_searches': [],
            'image_pack': {'present': False, 'images': [], 'total_count': 0},
            'video_results': [],
            'local_pack': {'present': False, 'businesses': [], 'map_present': False},
            'organic_results': [],
            'summary': {
                'featured_snippet_present': False,
                'people_also_ask_count': 0,
                'related_searches_count': 0,
                'image_pack_present': False,
                'video_results_count': 0,
                'local_pack_present': False,
                'organic_results_count': 0,
                'total_features': 0
            }
        }
    
    async def close(self):
        """بستن client"""
        await self.client.aclose()

