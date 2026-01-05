"""
استخراج کلمات کلیدی Long-tail
استفاده از Google Autocomplete, People Also Ask, Related Searches
"""

import logging
import httpx
import json
import asyncio
from typing import Dict, Any, List, Set
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode
import re

logger = logging.getLogger(__name__)


class LongTailKeywordExtractor:
    """
    کلاس استخراج کلمات کلیدی Long-tail
    
    روش‌ها:
    1. Google Autocomplete
    2. People Also Ask (PAA)
    3. Related Searches
    4. ترکیب با Modifiers
    5. Question-based Keywords
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        
        # Modifiers برای ترکیب با کلمات کلیدی
        self.modifiers = {
            'fa': [
                'چگونه', 'بهترین', 'راهنمای', 'آموزش', 'مقایسه',
                'قیمت', 'خرید', 'فروش', 'رایگان', 'دانلود',
                'نقد و بررسی', 'مزایا و معایب', 'راهنمای خرید',
                'کدام بهتر است', 'تفاوت', 'مشکلات', 'راه حل'
            ],
            'en': [
                'how to', 'best', 'guide', 'tutorial', 'compare',
                'price', 'buy', 'sell', 'free', 'download',
                'review', 'pros and cons', 'buying guide',
                'which is better', 'difference', 'problems', 'solution'
            ]
        }
        
        # Question words
        self.question_words = {
            'fa': ['چیست', 'چگونه', 'کجا', 'کی', 'چرا', 'چه', 'کدام'],
            'en': ['what', 'how', 'where', 'when', 'why', 'which', 'who']
        }
    
    async def extract_long_tail_keywords(
        self,
        seed_keywords: List[str],
        min_length: int = 4,
        max_results: int = 100,
        language: str = 'fa',
        use_all_methods: bool = True
    ) -> List[Dict[str, Any]]:
        """
        استخراج کلمات کلیدی Long-tail
        
        Args:
            seed_keywords: لیست کلمات کلیدی اولیه
            min_length: حداقل طول کلمه کلیدی (تعداد کلمات)
            max_results: حداکثر تعداد نتایج
            language: زبان ('fa' یا 'en')
            use_all_methods: استفاده از تمام روش‌ها
        
        Returns:
            لیست کلمات کلیدی Long-tail با معیارها:
            {
                'keyword': str,
                'source': str,  # autocomplete, paa, related, combination, question
                'seed_keyword': str,
                'word_count': int,
                'estimated_difficulty': str  # low, medium, high
            }
        """
        all_keywords = []
        
        for seed_keyword in seed_keywords:
            try:
                # روش 1: Google Autocomplete
                if use_all_methods:
                    autocomplete_keywords = await self._get_autocomplete_keywords(
                        seed_keyword,
                        language
                    )
                    all_keywords.extend(autocomplete_keywords)
                
                # روش 2: People Also Ask
                if use_all_methods:
                    paa_keywords = await self._get_people_also_ask(
                        seed_keyword,
                        language
                    )
                    all_keywords.extend(paa_keywords)
                
                # روش 3: Related Searches
                if use_all_methods:
                    related_keywords = await self._get_related_searches(
                        seed_keyword,
                        language
                    )
                    all_keywords.extend(related_keywords)
                
                # روش 4: ترکیب با Modifiers
                combination_keywords = self._generate_combinations(
                    seed_keyword,
                    language
                )
                all_keywords.extend(combination_keywords)
                
                # روش 5: Question-based Keywords
                question_keywords = self._generate_questions(
                    seed_keyword,
                    language
                )
                all_keywords.extend(question_keywords)
                
            except Exception as e:
                logger.error(f"Error extracting long-tail for {seed_keyword}: {str(e)}")
                continue
        
        # فیلتر کردن بر اساس min_length
        filtered_keywords = [
            kw for kw in all_keywords
            if kw.get('word_count', 0) >= min_length
        ]
        
        # حذف تکراری‌ها
        unique_keywords = self._remove_duplicates(filtered_keywords)
        
        # مرتب‌سازی بر اساس طول (Long-tail اول)
        unique_keywords.sort(key=lambda x: x.get('word_count', 0), reverse=True)
        
        # محاسبه Estimated Difficulty
        for kw in unique_keywords:
            kw['estimated_difficulty'] = self._estimate_difficulty(kw)
        
        return unique_keywords[:max_results]
    
    async def _get_autocomplete_keywords(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی از Google Autocomplete"""
        keywords = []
        
        try:
            # استفاده از Google Autocomplete API
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': seed_keyword,
                'hl': language,
                'gl': 'ir' if language == 'fa' else 'us'
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = json.loads(response.text)
                if len(data) > 1:
                    for suggestion in data[1][:10]:  # 10 پیشنهاد اول
                        word_count = len(suggestion.split())
                        if word_count >= 3:  # Long-tail حداقل 3 کلمه
                            keywords.append({
                                'keyword': suggestion,
                                'source': 'autocomplete',
                                'seed_keyword': seed_keyword,
                                'word_count': word_count
                            })
        except Exception as e:
            logger.error(f"Error fetching autocomplete: {str(e)}")
        
        return keywords
    
    async def _get_people_also_ask(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """دریافت سوالات People Also Ask"""
        keywords = []
        
        try:
            url = "https://www.google.com/search"
            params = {
                'q': seed_keyword,
                'hl': language
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # پیدا کردن بخش People Also Ask
                # Google از ساختارهای مختلفی استفاده می‌کند
                paa_sections = soup.find_all('div', class_='related-question-pair')
                
                for section in paa_sections[:10]:
                    question = section.get_text(strip=True)
                    if question and len(question.split()) >= 3:
                        keywords.append({
                            'keyword': question,
                            'source': 'people_also_ask',
                            'seed_keyword': seed_keyword,
                            'word_count': len(question.split())
                        })
                
                # روش جایگزین: جستجوی در ساختارهای دیگر
                if not keywords:
                    # جستجوی در divهای با classهای مختلف
                    all_divs = soup.find_all('div')
                    for div in all_divs:
                        text = div.get_text(strip=True)
                        # بررسی اینکه آیا سوال است
                        if any(qw in text.lower() for qw in self.question_words.get(language, [])):
                            if len(text.split()) >= 3 and len(text) < 200:
                                keywords.append({
                                    'keyword': text,
                                    'source': 'people_also_ask',
                                    'seed_keyword': seed_keyword,
                                    'word_count': len(text.split())
                                })
                                if len(keywords) >= 10:
                                    break
        except Exception as e:
            logger.error(f"Error fetching People Also Ask: {str(e)}")
        
        return keywords
    
    async def _get_related_searches(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """دریافت جستجوهای مرتبط"""
        keywords = []
        
        try:
            url = "https://www.google.com/search"
            params = {
                'q': seed_keyword,
                'hl': language
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # پیدا کردن Related Searches
                # Google از ساختارهای مختلفی استفاده می‌کند
                related_divs = soup.find_all('div', class_='brs_col')
                
                for div in related_divs:
                    link = div.find('a')
                    if link:
                        text = link.get_text(strip=True)
                        if text and len(text.split()) >= 3:
                            keywords.append({
                                'keyword': text,
                                'source': 'related_searches',
                                'seed_keyword': seed_keyword,
                                'word_count': len(text.split())
                            })
                
                # روش جایگزین: جستجوی در بخش "Searches related to"
                if not keywords:
                    # جستجوی متن "Searches related to" یا معادل فارسی
                    page_text = soup.get_text()
                    if 'related to' in page_text.lower() or 'مرتبط' in page_text:
                        # استخراج کلمات کلیدی از اطراف این متن
                        for div in soup.find_all('div'):
                            text = div.get_text(strip=True)
                            if len(text.split()) >= 3 and len(text) < 100:
                                # بررسی اینکه آیا کلمه کلیدی است
                                if not any(char in text for char in ['|', '•', '→']):
                                    keywords.append({
                                        'keyword': text,
                                        'source': 'related_searches',
                                        'seed_keyword': seed_keyword,
                                        'word_count': len(text.split())
                                    })
                                    if len(keywords) >= 10:
                                        break
        except Exception as e:
            logger.error(f"Error fetching related searches: {str(e)}")
        
        return keywords
    
    def _generate_combinations(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """تولید کلمات کلیدی با ترکیب Modifiers"""
        keywords = []
        modifiers = self.modifiers.get(language, self.modifiers['en'])
        
        for modifier in modifiers[:10]:  # 10 modifier اول
            # ترکیب modifier + seed keyword
            if language == 'fa':
                combined = f"{modifier} {seed_keyword}"
            else:
                combined = f"{modifier} {seed_keyword}"
            
            keywords.append({
                'keyword': combined,
                'source': 'combination',
                'seed_keyword': seed_keyword,
                'word_count': len(combined.split())
            })
        
        return keywords
    
    def _generate_questions(
        self,
        seed_keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """تولید کلمات کلیدی سوالی"""
        keywords = []
        question_words = self.question_words.get(language, self.question_words['en'])
        
        if language == 'fa':
            question_templates = [
                f"{seed_keyword} چیست",
                f"چگونه {seed_keyword}",
                f"بهترین {seed_keyword}",
                f"راهنمای {seed_keyword}",
                f"آموزش {seed_keyword}",
                f"مقایسه {seed_keyword}",
                f"تفاوت {seed_keyword}",
                f"مزایا و معایب {seed_keyword}",
                f"قیمت {seed_keyword}",
                f"خرید {seed_keyword}"
            ]
        else:
            question_templates = [
                f"what is {seed_keyword}",
                f"how to {seed_keyword}",
                f"best {seed_keyword}",
                f"{seed_keyword} guide",
                f"{seed_keyword} tutorial",
                f"compare {seed_keyword}",
                f"difference between {seed_keyword}",
                f"{seed_keyword} pros and cons",
                f"{seed_keyword} price",
                f"buy {seed_keyword}"
            ]
        
        for template in question_templates:
            keywords.append({
                'keyword': template,
                'source': 'question',
                'seed_keyword': seed_keyword,
                'word_count': len(template.split())
            })
        
        return keywords
    
    def _remove_duplicates(
        self,
        keywords: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """حذف کلمات کلیدی تکراری"""
        seen = set()
        unique_keywords = []
        
        for kw in keywords:
            keyword_lower = kw['keyword'].lower().strip()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def _estimate_difficulty(self, keyword_data: Dict[str, Any]) -> str:
        """تخمین Difficulty برای کلمه کلیدی Long-tail"""
        word_count = keyword_data.get('word_count', 0)
        source = keyword_data.get('source', '')
        
        # Long-tail keywords معمولاً Difficulty کمتری دارند
        if word_count >= 5:
            return 'low'
        elif word_count >= 4:
            return 'low' if source in ['question', 'people_also_ask'] else 'medium'
        else:
            return 'medium'
    
    async def extract_with_metrics(
        self,
        seed_keywords: List[str],
        min_length: int = 4,
        max_results: int = 50,
        language: str = 'fa',
        get_metrics: bool = False
    ) -> List[Dict[str, Any]]:
        """
        استخراج Long-tail Keywords با معیارها (اگر API موجود باشد)
        
        Args:
            get_metrics: دریافت معیارها از APIهای خارجی
        """
        # استخراج Long-tail keywords
        long_tail_keywords = await self.extract_long_tail_keywords(
            seed_keywords=seed_keywords,
            min_length=min_length,
            max_results=max_results,
            language=language
        )
        
        # اگر get_metrics=True، معیارها را دریافت می‌کنیم
        if get_metrics:
            try:
                # استفاده از Google Keyword Planner برای دریافت معیارها
                from .google_keyword_planner import GoogleKeywordPlanner
                planner = GoogleKeywordPlanner()
                
                # دریافت معیارها برای کلمات کلیدی برتر
                top_keywords = [kw['keyword'] for kw in long_tail_keywords[:20]]
                metrics = await planner.get_keyword_metrics(
                    keywords=top_keywords,
                    language=language
                )
                
                # اضافه کردن معیارها به کلمات کلیدی
                for kw in long_tail_keywords:
                    keyword_lower = kw['keyword'].lower()
                    if keyword_lower in metrics:
                        kw.update({
                            'search_volume': metrics[keyword_lower].get('search_volume', 0),
                            'competition': metrics[keyword_lower].get('competition', 'Unknown'),
                            'difficulty': metrics[keyword_lower].get('difficulty', 0),
                            'opportunity_score': metrics[keyword_lower].get('opportunity_score', 0)
                        })
            except Exception as e:
                logger.warning(f"Could not fetch metrics: {str(e)}")
        
        return long_tail_keywords
    
    async def extract_by_intent(
        self,
        seed_keyword: str,
        intent: str = 'informational',  # informational, commercial, transactional
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """
        استخراج Long-tail Keywords بر اساس Intent
        
        Args:
            intent: نوع Intent
                - informational: جستجوی اطلاعات
                - commercial: جستجوی تجاری
                - transactional: جستجوی خرید
        """
        intent_modifiers = {
            'fa': {
                'informational': ['چیست', 'چگونه', 'راهنمای', 'آموزش', 'تفاوت'],
                'commercial': ['بهترین', 'مقایسه', 'نقد و بررسی', 'مزایا و معایب'],
                'transactional': ['خرید', 'قیمت', 'فروش', 'تخفیف', 'ارزان']
            },
            'en': {
                'informational': ['what is', 'how to', 'guide', 'tutorial', 'difference'],
                'commercial': ['best', 'compare', 'review', 'pros and cons'],
                'transactional': ['buy', 'price', 'sell', 'discount', 'cheap']
            }
        }
        
        modifiers = intent_modifiers.get(language, intent_modifiers['en']).get(
            intent,
            intent_modifiers['en']['informational']
        )
        
        keywords = []
        for modifier in modifiers:
            if language == 'fa':
                combined = f"{modifier} {seed_keyword}"
            else:
                combined = f"{modifier} {seed_keyword}"
            
            keywords.append({
                'keyword': combined,
                'source': 'intent_based',
                'seed_keyword': seed_keyword,
                'word_count': len(combined.split()),
                'intent': intent
            })
        
        return keywords
    
    async def close(self):
        """بستن client"""
        await self.client.aclose()

