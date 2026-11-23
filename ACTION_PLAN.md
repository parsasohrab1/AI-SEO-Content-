# برنامه عملی رفع مشکلات - شناسایی کلمات کلیدی و تولید محتوا

## 🎯 هدف
رفع مشکلات شناسایی شده در خطوط 13-29 از `IMPROVEMENT_RECOMMENDATIONS.md` با راه‌حل‌های عملی و قابل پیاده‌سازی

---

## 📋 مشکلات و راه‌حل‌های عملی

### بخش 1: شناسایی کلمات کلیدی

#### ❌ مشکل 1: فقط استخراج ساده بر اساس تکرار کلمات

**Current status:**
```python
# در seo_analyzer.py - خط 321
def _extract_keywords(self, text: str) -> List[Dict[str, Any]]:
    # فقط شمارش تکرار کلمات
    word_freq = Counter(filtered_words)
    keywords = [{'word': word, 'count': count} for word, count in word_freq.most_common(50)]
```

**راه‌حل: پیاده‌سازی Keyword Extractor پیشرفته**

```python
# ایجاد فایل جدید: backend/core/keyword_research/advanced_keyword_extractor.py

import re
from collections import Counter
from typing import List, Dict, Any
import logging
from keybert import KeyBERT
from rake_nltk import Rake
import yake

logger = logging.getLogger(__name__)


class AdvancedKeywordExtractor:
    """استخراج پیشرفته کلمات کلیدی با استفاده از چند روش"""
    
    def __init__(self, language: str = 'fa'):
        self.language = language
        # استفاده از KeyBERT برای استخراج معنایی
        try:
            model_name = 'paraphrase-multilingual-MiniLM-L12-v2' if language == 'fa' else 'all-MiniLM-L6-v2'
            self.keybert = KeyBERT(model=model_name)
        except:
            self.keybert = None
            logger.warning("KeyBERT not available, using fallback methods")
        
        # استفاده از RAKE
        self.rake = Rake(language=language if language == 'en' else None)
        
        # استفاده از YAKE
        self.yake = yake.KeywordExtractor(
            lan=language,
            n=3,  # حداکثر 3 کلمه
            dedupLim=0.7,
            top=50
        )
    
    def extract_keywords(
        self,
        text: str,
        min_length: int = 2,
        max_length: int = 3,
        top_n: int = 50
    ) -> List[Dict[str, Any]]:
        """
        استخراج کلمات کلیدی با ترکیب چند روش
        
        Returns:
            لیست کلمات کلیدی با امتیاز و منبع
        """
        all_keywords = {}
        
        # روش 1: KeyBERT (معنایی)
        if self.keybert:
            try:
                keybert_keywords = self.keybert.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, max_length),
                    stop_words=None,
                    top_n=top_n
                )
                for keyword, score in keybert_keywords:
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {
                            'keyword': keyword,
                            'score': score,
                            'method': 'keybert',
                            'frequency': 0
                        }
            except Exception as e:
                logger.error(f"KeyBERT extraction failed: {str(e)}")
        
        # روش 2: RAKE (Rapid Automatic Keyword Extraction)
        try:
            self.rake.extract_keywords_from_text(text)
            rake_keywords = self.rake.get_ranked_phrases()[:top_n]
            for keyword in rake_keywords:
                if len(keyword.split()) <= max_length:
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {
                            'keyword': keyword,
                            'score': 0.5,
                            'method': 'rake',
                            'frequency': 0
                        }
        except Exception as e:
            logger.error(f"RAKE extraction failed: {str(e)}")
        
        # روش 3: YAKE
        try:
            yake_keywords = self.yake.extract_keywords(text)
            for score, keyword in yake_keywords:
                if keyword not in all_keywords:
                    all_keywords[keyword] = {
                        'keyword': keyword,
                        'score': 1 - score,  # تبدیل به امتیاز مثبت
                        'method': 'yake',
                        'frequency': 0
                    }
        except Exception as e:
            logger.error(f"YAKE extraction failed: {str(e)}")
        
        # روش 4: Frequency-based (روش فعلی به عنوان fallback)
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        for word, count in word_freq.most_common(top_n):
            if len(word) >= min_length and word not in all_keywords:
                all_keywords[word] = {
                    'keyword': word,
                    'score': count / max(word_freq.values()) if word_freq else 0,
                    'method': 'frequency',
                    'frequency': count
                }
        
        # محاسبه امتیاز ترکیبی
        for keyword_data in all_keywords.values():
            keyword_data['combined_score'] = self._calculate_combined_score(keyword_data)
        
        # مرتب‌سازی بر اساس امتیاز ترکیبی
        sorted_keywords = sorted(
            all_keywords.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        return sorted_keywords[:top_n]
    
    def _calculate_combined_score(self, keyword_data: Dict[str, Any]) -> float:
        """محاسبه امتیاز ترکیبی"""
        score = keyword_data.get('score', 0)
        frequency = keyword_data.get('frequency', 0)
        method = keyword_data.get('method', '')
        
        # وزن‌دهی بر اساس روش
        method_weights = {
            'keybert': 1.0,
            'yake': 0.8,
            'rake': 0.7,
            'frequency': 0.5
        }
        
        method_weight = method_weights.get(method, 0.5)
        
        # ترکیب امتیاز و تکرار
        combined = (score * method_weight) + (min(frequency / 10, 1.0) * 0.3)
        
        return min(combined, 1.0)
```

**فایل‌های مورد نیاز:**
- `backend/core/keyword_research/__init__.py`
- `backend/core/keyword_research/advanced_keyword_extractor.py`

**وابستگی‌های جدید:**
```txt
keybert==0.8.0
rake-nltk==1.0.7
yake==0.4.8
```

---

#### ❌ مشکل 2: عدم استفاده از APIهای تخصصی تحقیق کلمات کلیدی

**راه‌حل: یکپارچه‌سازی Google Keyword Planner (رایگان)**

```python
# ایجاد فایل: backend/core/keyword_research/google_keyword_planner.py

import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class GoogleKeywordPlanner:
    """استفاده از Google Keyword Planner (رایگان با Google Ads account)"""
    
    def __init__(self):
        # Google Keyword Planner نیاز به Google Ads API دارد
        # اما می‌توانیم از Google Trends و Autocomplete استفاده کنیم
        self.base_url = "https://www.google.com"
    
    async def get_keyword_suggestions(
        self,
        seed_keyword: str,
        language: str = 'fa',
        country: str = 'ir'
    ) -> List[Dict[str, Any]]:
        """
        دریافت پیشنهادات کلمات کلیدی از Google Autocomplete
        
        این روش رایگان است و نیاز به API Key ندارد
        """
        suggestions = []
        
        try:
            # استفاده از Google Autocomplete API (غیررسمی اما کار می‌کند)
            url = f"http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': seed_keyword,
                'hl': language,
                'gl': country
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                
                if response.status_code == 200:
                    import json
                    data = json.loads(response.text)
                    if len(data) > 1:
                        suggestions = [
                            {
                                'keyword': keyword,
                                'type': 'autocomplete',
                                'source': 'google'
                            }
                            for keyword in data[1][:10]
                        ]
        except Exception as e:
            logger.error(f"Error fetching Google suggestions: {str(e)}")
        
        return suggestions
    
    async def get_related_searches(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> List[str]:
        """
        دریافت جستجوهای مرتبط از Google
        (از طریق scraping صفحه نتایج)
        """
        related = []
        
        try:
            url = f"https://www.google.com/search"
            params = {
                'q': keyword,
                'hl': language
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # پیدا کردن بخش "People also ask"
                    related_sections = soup.find_all('div', class_='related-question-pair')
                    for section in related_sections[:5]:
                        text = section.get_text(strip=True)
                        if text:
                            related.append(text)
        except Exception as e:
            logger.error(f"Error fetching related searches: {str(e)}")
        
        return related
```

---

#### ❌ مشکل 3: عدم وجود تحلیل سختی کلمات کلیدی (Keyword Difficulty)

**راه‌حل: محاسبه Keyword Difficulty بدون نیاز به API**

```python
# ایجاد فایل: backend/core/keyword_research/keyword_difficulty.py

import httpx
import logging
from typing import Dict, Any
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class KeywordDifficultyCalculator:
    """محاسبه Keyword Difficulty بدون نیاز به API پولی"""
    
    async def calculate_difficulty(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        محاسبه Keyword Difficulty بر اساس:
        1. تعداد نتایج جستجو
        2. Domain Authority صفحات رتبه‌دار (تقریبی)
        3. کیفیت محتوای رقبا
        4. سن دامنه (تقریبی)
        """
        try:
            # دریافت نتایج جستجو
            search_results = await self._get_search_results(keyword, language)
            
            if not search_results:
                return {
                    'difficulty': 50,
                    'level': 'medium',
                    'confidence': 'low'
                }
            
            # تحلیل نتایج
            total_results = search_results.get('total_results', 0)
            top_domains = search_results.get('top_domains', [])
            
            # محاسبه Difficulty
            difficulty_score = 0
            
            # فاکتور 1: تعداد نتایج (هرچه بیشتر، سخت‌تر)
            if total_results > 10000000:
                difficulty_score += 40
            elif total_results > 1000000:
                difficulty_score += 30
            elif total_results > 100000:
                difficulty_score += 20
            else:
                difficulty_score += 10
            
            # فاکتور 2: قدرت دامنه‌های رتبه‌دار
            strong_domains = ['wikipedia.org', 'youtube.com', 'amazon.com', 'facebook.com']
            strong_count = sum(1 for domain in top_domains if any(sd in domain for sd in strong_domains))
            
            if strong_count >= 3:
                difficulty_score += 40
            elif strong_count >= 2:
                difficulty_score += 30
            elif strong_count >= 1:
                difficulty_score += 20
            else:
                difficulty_score += 10
            
            # فاکتور 3: طول کلمه کلیدی (Long-tail آسان‌تر است)
            keyword_length = len(keyword.split())
            if keyword_length >= 4:
                difficulty_score -= 20
            elif keyword_length >= 3:
                difficulty_score -= 10
            
            # محدود کردن به بازه 0-100
            difficulty_score = max(0, min(100, difficulty_score))
            
            # تعیین سطح
            if difficulty_score >= 70:
                level = 'hard'
            elif difficulty_score >= 40:
                level = 'medium'
            else:
                level = 'easy'
            
            return {
                'difficulty': difficulty_score,
                'level': level,
                'total_results': total_results,
                'top_domains': top_domains[:5],
                'confidence': 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error calculating keyword difficulty: {str(e)}")
            return {
                'difficulty': 50,
                'level': 'medium',
                'confidence': 'low',
                'error': str(e)
            }
    
    async def _get_search_results(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """دریافت نتایج جستجو از Google"""
        try:
            url = "https://www.google.com/search"
            params = {
                'q': keyword,
                'hl': language,
                'num': 10
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # استخراج تعداد کل نتایج
                    result_stats = soup.find('div', {'id': 'result-stats'})
                    total_results = 0
                    if result_stats:
                        text = result_stats.get_text()
                        numbers = re.findall(r'[\d,]+', text.replace(',', ''))
                        if numbers:
                            total_results = int(numbers[0].replace(',', ''))
                    
                    # استخراج دامنه‌های رتبه‌دار
                    top_domains = []
                    search_results = soup.find_all('div', class_='g')[:10]
                    for result in search_results:
                        link = result.find('a', href=True)
                        if link:
                            href = link['href']
                            if 'http' in href:
                                from urllib.parse import urlparse
                                domain = urlparse(href).netloc
                                if domain and domain not in top_domains:
                                    top_domains.append(domain)
                    
                    return {
                        'total_results': total_results,
                        'top_domains': top_domains
                    }
        except Exception as e:
            logger.error(f"Error getting search results: {str(e)}")
        
        return {}
```

---

#### ❌ مشکل 4: عدم دسترسی به حجم جستجو (Search Volume)

**راه‌حل: استفاده از Google Trends (رایگان)**

```python
# ایجاد فایل: backend/core/keyword_research/google_trends.py

import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GoogleTrendsAnalyzer:
    """تحلیل Google Trends برای دریافت حجم جستجو (تقریبی)"""
    
    async def get_trend_data(
        self,
        keyword: str,
        timeframe: str = '12m'  # 12 ماه گذشته
    ) -> Dict[str, Any]:
        """
        دریافت داده‌های Trend از Google Trends
        
        Returns:
            {
                'average_volume': int,  # حجم متوسط (نسبی)
                'trend': List[int],    # روند 12 ماهه
                'peak_month': str,      # ماه پیک
                'growth_rate': float    # نرخ رشد
            }
        """
        try:
            # استفاده از pytrends (کتابخانه Python)
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='fa-IR', tz=360)
            pytrends.build_payload([keyword], timeframe=timeframe)
            
            # دریافت داده‌های trend
            trend_data = pytrends.interest_over_time()
            
            if not trend_data.empty:
                values = trend_data[keyword].tolist()
                avg_volume = sum(values) / len(values) if values else 0
                
                # پیدا کردن ماه پیک
                peak_index = values.index(max(values))
                peak_month = trend_data.index[peak_index].strftime('%Y-%m')
                
                # محاسبه نرخ رشد
                if len(values) >= 2:
                    growth_rate = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                else:
                    growth_rate = 0
                
                return {
                    'average_volume': int(avg_volume),
                    'trend': values,
                    'peak_month': peak_month,
                    'growth_rate': round(growth_rate, 2),
                    'relative_volume': self._estimate_absolute_volume(avg_volume)
                }
        except Exception as e:
            logger.error(f"Error getting Google Trends data: {str(e)}")
        
        return {
            'average_volume': 0,
            'trend': [],
            'peak_month': None,
            'growth_rate': 0,
            'relative_volume': 'unknown'
        }
    
    def _estimate_absolute_volume(self, relative_volume: float) -> str:
        """تخمین حجم مطلق بر اساس حجم نسبی"""
        if relative_volume >= 80:
            return 'very_high'  # 100K+
        elif relative_volume >= 50:
            return 'high'  # 10K-100K
        elif relative_volume >= 20:
            return 'medium'  # 1K-10K
        elif relative_volume >= 5:
            return 'low'  # 100-1K
        else:
            return 'very_low'  # <100
```

**وابستگی جدید:**
```txt
pytrends==4.9.2
```

---

#### ❌ مشکل 5: عدم شناسایی کلمات کلیدی Long-tail

**راه‌حل: استخراج Long-tail Keywords**

```python
# اضافه کردن به: backend/core/keyword_research/advanced_keyword_extractor.py

class LongTailKeywordExtractor:
    """استخراج کلمات کلیدی Long-tail"""
    
    def __init__(self):
        self.google_planner = GoogleKeywordPlanner()
    
    async def extract_long_tail_keywords(
        self,
        seed_keywords: List[str],
        min_length: int = 4,  # حداقل 4 کلمه
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        استخراج کلمات کلیدی Long-tail
        
        روش‌ها:
        1. Google Autocomplete
        2. People Also Ask
        3. Related Searches
        4. ترکیب کلمات کلیدی
        """
        all_long_tail = []
        
        for seed_keyword in seed_keywords:
            # روش 1: Google Autocomplete
            suggestions = await self.google_planner.get_keyword_suggestions(seed_keyword)
            for suggestion in suggestions:
                keyword = suggestion['keyword']
                if len(keyword.split()) >= min_length:
                    all_long_tail.append({
                        'keyword': keyword,
                        'type': 'autocomplete',
                        'seed': seed_keyword
                    })
            
            # روش 2: Related Searches
            related = await self.google_planner.get_related_searches(seed_keyword)
            for rel_keyword in related:
                if len(rel_keyword.split()) >= min_length:
                    all_long_tail.append({
                        'keyword': rel_keyword,
                        'type': 'related',
                        'seed': seed_keyword
                    })
            
            # روش 3: ترکیب با کلمات اضافی
            modifiers = ['چگونه', 'بهترین', 'راهنمای', 'آموزش', 'مقایسه']
            for modifier in modifiers:
                long_tail = f"{modifier} {seed_keyword}"
                all_long_tail.append({
                    'keyword': long_tail,
                    'type': 'combination',
                    'seed': seed_keyword
                })
        
        # حذف تکراری‌ها
        unique_keywords = {}
        for item in all_long_tail:
            keyword = item['keyword'].lower().strip()
            if keyword not in unique_keywords:
                unique_keywords[keyword] = item
        
        return list(unique_keywords.values())[:max_results]
```

---

### بخش 2: تولید محتوا

#### ❌ مشکل 6: استفاده از الگوهای ثابت (Template-based)

**راه‌حل: یکپارچه‌سازی OpenAI (موجود در requirements.txt)**

```python
# به‌روزرسانی: backend/core/content_generator.py

# در ابتدای فایل اضافه کنید:
import os
from openai import AsyncOpenAI

class ContentGenerator:
    def __init__(self):
        # اضافه کردن AI Generator
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI not available: {str(e)}")
    
    async def _generate_text_content_for_keyword(
        self,
        keyword: str,
        site_url: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """تولید محتوا - اولویت با AI، سپس Template"""
        
        # استفاده از AI اگر موجود باشد
        if self.openai_client:
            try:
                return await self._generate_with_ai(keyword, language)
            except Exception as e:
                logger.warning(f"AI generation failed, using template: {str(e)}")
        
        # Fallback به Template
        return await self._generate_template_content(keyword, site_url, language)
    
    async def _generate_with_ai(
        self,
        keyword: str,
        language: str = 'fa'
    ) -> List[Dict[str, Any]]:
        """تولید محتوا با OpenAI"""
        
        system_prompt = "You are an expert SEO content writer." if language == 'en' else "شما یک نویسنده متخصص SEO هستید."
        
        user_prompt = f"""
        Write a comprehensive, SEO-optimized article about "{keyword}".
        
        Requirements:
        - Language: {language}
        - Length: 1500-2000 words
        - Use keyword naturally (1-2% density)
        - Well-structured with H2 and H3 headings
        - Valuable and engaging content
        - Include introduction and conclusion
        
        Write the article now:
        """ if language == 'en' else f"""
        یک مقاله جامع و بهینه شده برای SEO درباره "{keyword}" بنویسید.
        
        الزامات:
        - زبان: فارسی
        - طول: 1500-2000 کلمه
        - استفاده طبیعی از کلمه کلیدی (چگالی 1-2%)
        - ساختار منظم با عنوان‌های H2 و H3
        - محتوای ارزشمند و جذاب
        - شامل مقدمه و نتیجه‌گیری
        
        مقاله را بنویسید:
        """
        
        response = await self.openai_client.chat.completions.create(
            model=os.getenv('AI_CONTENT_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        return [{
            'id': f"content_{hash(keyword)}_{datetime.now().timestamp()}",
            'title': self._extract_title(content),
            'content': content,
            'type': 'article',
            'word_count': len(content.split()),
            'keywords': [keyword],
            'status': 'generated',
            'seo_score': 85,
            'created_at': datetime.now().isoformat(),
            'generated_by': 'openai'
        }]
```

---

## 📦 وابستگی‌های جدید

افزودن به `backend/requirements.txt`:

```txt
# Keyword Research
keybert==0.8.0
rake-nltk==1.0.7
yake==0.4.8
pytrends==4.9.2

# OpenAI (موجود است اما باید استفاده شود)
openai==1.3.5
```

---

## 🚀 مراحل پیاده‌سازی

### مرحله 1: نصب وابستگی‌ها
```bash
cd backend
pip install keybert rake-nltk yake pytrends
```

### مرحله 2: ایجاد ساختار پوشه
```bash
mkdir -p backend/core/keyword_research
touch backend/core/keyword_research/__init__.py
```

### مرحله 3: پیاده‌سازی فایل‌ها
1. `advanced_keyword_extractor.py`
2. `google_keyword_planner.py`
3. `keyword_difficulty.py`
4. `google_trends.py`

### مرحله 4: به‌روزرسانی SEOAnalyzer
```python
# در seo_analyzer.py
from .keyword_research.advanced_keyword_extractor import AdvancedKeywordExtractor

class SEOAnalyzer:
    def __init__(self):
        # ...
        self.keyword_extractor = AdvancedKeywordExtractor(language='fa')
    
    def _extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        # استفاده از AdvancedKeywordExtractor
        return self.keyword_extractor.extract_keywords(text, top_n=50)
```

### مرحله 5: به‌روزرسانی ContentGenerator
- اضافه کردن استفاده از OpenAI (کد بالا)

---

## ✅ چک‌لیست پیاده‌سازی

- [ ] نصب وابستگی‌های جدید
- [ ] ایجاد پوشه `keyword_research`
- [ ] پیاده‌سازی `AdvancedKeywordExtractor`
- [ ] پیاده‌سازی `GoogleKeywordPlanner`
- [ ] پیاده‌سازی `KeywordDifficultyCalculator`
- [ ] پیاده‌سازی `GoogleTrendsAnalyzer`
- [ ] پیاده‌سازی `LongTailKeywordExtractor`
- [ ] به‌روزرسانی `SEOAnalyzer`
- [ ] به‌روزرسانی `ContentGenerator` با OpenAI
- [ ] تست تمام ماژول‌ها
- [ ] تنظیم Environment Variables

---

**آماده برای پیاده‌سازی!** 🚀

