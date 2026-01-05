"""
تحلیل فاصله کلمات کلیدی (Keyword Gap Analysis)
شناسایی فرصت‌ها و مزیت‌های کلمات کلیدی نسبت به رقبا
"""

import logging
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse
from collections import Counter
import asyncio

logger = logging.getLogger(__name__)


class KeywordGapAnalyzer:
    """
    کلاس تحلیل فاصله کلمات کلیدی
    
    تحلیل:
    - کلمات کلیدی که رقبا دارند اما شما ندارید (Opportunities)
    - کلمات کلیدی که شما دارید اما رقبا ندارند (Advantages)
    - کلمات کلیدی مشترک (Competition)
    """
    
    def __init__(self):
        self.semrush = None
        self.ahrefs = None
        
        # سعی می‌کنیم APIهای خارجی را بارگذاری کنیم
        try:
            from .semrush_client import SEMrushKeywordAnalyzer
            self.semrush = SEMrushKeywordAnalyzer()
            if not self.semrush.enabled:
                self.semrush = None
        except Exception as e:
            logger.warning(f"SEMrush not available: {str(e)}")
        
        try:
            from .ahrefs_client import AhrefsKeywordAnalyzer
            self.ahrefs = AhrefsKeywordAnalyzer()
            if not self.ahrefs.enabled:
                self.ahrefs = None
        except Exception as e:
            logger.warning(f"Ahrefs not available: {str(e)}")
    
    async def analyze_gap(
        self,
        site_url: str,
        competitor_urls: List[str],
        use_apis: bool = True,
        limit_per_site: int = 100,
        language: str = 'fa'
    ) -> Dict[str, Any]:
        """
        تحلیل فاصله کلمات کلیدی
        
        Args:
            site_url: آدرس سایت شما
            competitor_urls: لیست آدرس‌های رقبا
            use_apis: استفاده از APIهای خارجی (SEMrush, Ahrefs)
            limit_per_site: حداکثر تعداد کلمات کلیدی برای هر سایت
            language: زبان
        
        Returns:
            {
                'opportunities': List[Dict],  # فرصت‌ها
                'advantages': List[Dict],      # مزیت‌ها
                'competition': List[Dict],    # رقابت
                'recommendations': List[str], # پیشنهادات
                'summary': Dict,
                'competitor_analysis': Dict
            }
        """
        try:
            # دریافت کلمات کلیدی سایت شما
            your_keywords = await self._get_site_keywords(
                site_url,
                use_apis,
                limit_per_site
            )
            
            # دریافت کلمات کلیدی رقبا
            competitor_keywords = {}
            for competitor_url in competitor_urls:
                try:
                    keywords = await self._get_site_keywords(
                        competitor_url,
                        use_apis,
                        limit_per_site
                    )
                    competitor_keywords[competitor_url] = keywords
                except Exception as e:
                    logger.error(f"Error getting keywords for {competitor_url}: {str(e)}")
                    competitor_keywords[competitor_url] = []
            
            # تحلیل Gap
            gap_analysis = self._analyze_keyword_gap(
                your_keywords,
                competitor_keywords
            )
            
            # تولید پیشنهادات
            recommendations = self._generate_recommendations(
                gap_analysis,
                language
            )
            
            # محاسبه خلاصه
            summary = self._calculate_summary(
                your_keywords,
                competitor_keywords,
                gap_analysis
            )
            
            return {
                'opportunities': gap_analysis['opportunities'],
                'advantages': gap_analysis['advantages'],
                'competition': gap_analysis['competition'],
                'recommendations': recommendations,
                'summary': summary,
                'competitor_analysis': {
                    'your_keywords_count': len(your_keywords),
                    'competitors_analyzed': len(competitor_keywords),
                    'total_competitor_keywords': sum(len(kws) for kws in competitor_keywords.values())
                }
            }
            
        except Exception as e:
            logger.error(f"Error in keyword gap analysis: {str(e)}")
            return self._empty_gap_result()
    
    async def _get_site_keywords(
        self,
        url: str,
        use_apis: bool,
        limit: int
    ) -> List[Dict[str, Any]]:
        """دریافت کلمات کلیدی یک سایت"""
        keywords = []
        
        # استفاده از SEMrush اگر موجود باشد
        if use_apis and self.semrush and self.semrush.enabled:
            try:
                semrush_keywords = await self.semrush.get_ranking_keywords(
                    url=url,
                    limit=limit
                )
                if semrush_keywords:
                    keywords.extend(semrush_keywords)
                    logger.info(f"Retrieved {len(semrush_keywords)} keywords from SEMrush for {url}")
            except Exception as e:
                logger.warning(f"SEMrush failed for {url}: {str(e)}")
        
        # استفاده از Ahrefs اگر موجود باشد
        if use_apis and self.ahrefs and self.ahrefs.enabled:
            try:
                ahrefs_keywords = await self.ahrefs.get_ranking_keywords(
                    url=url,
                    limit=limit
                )
                if ahrefs_keywords:
                    # تبدیل فرمت Ahrefs به فرمت یکسان
                    converted = [
                        {
                            'keyword': kw.get('keyword', ''),
                            'position': kw.get('position', 0),
                            'search_volume': kw.get('search_volume', 0),
                            'cpc': kw.get('cpc', 0.0),
                            'url': kw.get('url', ''),
                            'traffic': kw.get('traffic', 0),
                            'source': 'ahrefs'
                        }
                        for kw in ahrefs_keywords
                    ]
                    keywords.extend(converted)
                    logger.info(f"Retrieved {len(converted)} keywords from Ahrefs for {url}")
            except Exception as e:
                logger.warning(f"Ahrefs failed for {url}: {str(e)}")
        
        # اگر APIها موجود نبودند یا نتایج کافی نبود، از روش‌های رایگان استفاده می‌کنیم
        if len(keywords) < 10:
            try:
                free_keywords = await self._extract_keywords_free(url)
                keywords.extend(free_keywords)
            except Exception as e:
                logger.warning(f"Free extraction failed for {url}: {str(e)}")
        
        # حذف تکراری‌ها
        unique_keywords = {}
        for kw in keywords:
            keyword_lower = kw.get('keyword', '').lower().strip()
            if keyword_lower and keyword_lower not in unique_keywords:
                unique_keywords[keyword_lower] = kw
            elif keyword_lower in unique_keywords:
                # ترکیب داده‌ها اگر تکراری بود
                existing = unique_keywords[keyword_lower]
                if not existing.get('search_volume') and kw.get('search_volume'):
                    existing['search_volume'] = kw['search_volume']
                if not existing.get('position') and kw.get('position'):
                    existing['position'] = kw['position']
        
        return list(unique_keywords.values())[:limit]
    
    async def _extract_keywords_free(self, url: str) -> List[Dict[str, Any]]:
        """استخراج کلمات کلیدی با روش‌های رایگان"""
        keywords = []
        
        try:
            # استفاده از SEOAnalyzer موجود
            from ..seo_analyzer import SEOAnalyzer
            seo_analyzer = SEOAnalyzer()
            
            # تحلیل SEO
            seo_analysis = await seo_analyzer.deep_analysis(url)
            
            # استخراج کلمات کلیدی از تحلیل
            content_analysis = seo_analysis.get('content', {})
            seo_keywords = content_analysis.get('keywords', [])
            
            for kw_data in seo_keywords[:50]:  # 50 کلمه کلیدی اول
                if isinstance(kw_data, dict):
                    keyword = kw_data.get('word', '')
                    count = kw_data.get('count', 0)
                else:
                    keyword = str(kw_data)
                    count = 1
                
                if keyword and len(keyword) > 2:
                    keywords.append({
                        'keyword': keyword,
                        'position': None,
                        'search_volume': None,
                        'cpc': None,
                        'url': url,
                        'traffic': None,
                        'frequency': count,
                        'source': 'free_extraction'
                    })
            
            await seo_analyzer.close()
            
        except Exception as e:
            logger.error(f"Error in free keyword extraction: {str(e)}")
        
        return keywords
    
    def _analyze_keyword_gap(
        self,
        your_keywords: List[Dict[str, Any]],
        competitor_keywords: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """تحلیل فاصله کلمات کلیدی"""
        
        # ایجاد set از کلمات کلیدی شما
        your_keyword_set = {kw['keyword'].lower().strip() for kw in your_keywords if kw.get('keyword')}
        
        # جمع‌آوری تمام کلمات کلیدی رقبا
        all_competitor_keywords = {}
        competitor_keyword_set = set()
        
        for competitor_url, keywords in competitor_keywords.items():
            keyword_set = {kw['keyword'].lower().strip() for kw in keywords if kw.get('keyword')}
            competitor_keyword_set.update(keyword_set)
            
            # ذخیره جزئیات هر کلمه کلیدی
            for kw in keywords:
                keyword_lower = kw['keyword'].lower().strip()
                if keyword_lower not in all_competitor_keywords:
                    all_competitor_keywords[keyword_lower] = {
                        'keyword': kw['keyword'],
                        'competitors': [competitor_url],
                        'search_volume': kw.get('search_volume', 0),
                        'position': kw.get('position'),
                        'cpc': kw.get('cpc', 0.0),
                        'traffic': kw.get('traffic', 0)
                    }
                else:
                    # اضافه کردن رقیب دیگر
                    if competitor_url not in all_competitor_keywords[keyword_lower]['competitors']:
                        all_competitor_keywords[keyword_lower]['competitors'].append(competitor_url)
                    # به‌روزرسانی معیارها (میانگین)
                    existing = all_competitor_keywords[keyword_lower]
                    if kw.get('search_volume'):
                        existing['search_volume'] = max(existing['search_volume'], kw.get('search_volume', 0))
        
        # فرصت‌ها: کلمات کلیدی که رقبا دارند اما شما ندارید
        opportunities_keywords = competitor_keyword_set - your_keyword_set
        opportunities = [
            {
                **all_competitor_keywords[kw],
                'opportunity_score': self._calculate_opportunity_score(
                    all_competitor_keywords[kw]
                ),
                'competitor_count': len(all_competitor_keywords[kw]['competitors'])
            }
            for kw in opportunities_keywords
            if kw in all_competitor_keywords
        ]
        
        # مزیت‌ها: کلمات کلیدی که شما دارید اما رقبا ندارند
        advantages_keywords = your_keyword_set - competitor_keyword_set
        advantages = [
            {
                'keyword': kw['keyword'],
                'search_volume': kw.get('search_volume', 0),
                'position': kw.get('position'),
                'cpc': kw.get('cpc', 0.0),
                'traffic': kw.get('traffic', 0),
                'advantage_score': self._calculate_advantage_score(kw)
            }
            for kw in your_keywords
            if kw['keyword'].lower().strip() in advantages_keywords
        ]
        
        # کلمات کلیدی مشترک
        common_keywords = your_keyword_set & competitor_keyword_set
        competition = []
        
        for kw in your_keywords:
            keyword_lower = kw['keyword'].lower().strip()
            if keyword_lower in common_keywords:
                competitor_data = all_competitor_keywords.get(keyword_lower, {})
                competition.append({
                    'keyword': kw['keyword'],
                    'your_position': kw.get('position'),
                    'competitor_positions': [
                        comp_kw.get('position')
                        for comp_url, comp_keywords in competitor_keywords.items()
                        for comp_kw in comp_keywords
                        if comp_kw['keyword'].lower().strip() == keyword_lower
                    ],
                    'search_volume': kw.get('search_volume', 0) or competitor_data.get('search_volume', 0),
                    'competition_level': self._calculate_competition_level(
                        kw.get('position'),
                        competitor_data.get('position')
                    )
                })
        
        # مرتب‌سازی
        opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        advantages.sort(key=lambda x: x.get('advantage_score', 0), reverse=True)
        competition.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
        
        return {
            'opportunities': opportunities[:100],  # 100 فرصت برتر
            'advantages': advantages[:100],  # 100 مزیت برتر
            'competition': competition[:100]  # 100 کلمه کلیدی مشترک برتر
        }
    
    def _calculate_opportunity_score(self, keyword_data: Dict[str, Any]) -> float:
        """محاسبه Opportunity Score برای کلمات کلیدی رقبا"""
        score = 0.0
        
        # فاکتور 1: Search Volume (40%)
        search_volume = keyword_data.get('search_volume', 0)
        if search_volume > 0:
            if search_volume >= 10000:
                score += 40
            elif search_volume >= 1000:
                score += 30
            elif search_volume >= 100:
                score += 20
            else:
                score += 10
        
        # فاکتور 2: تعداد رقبا (30%)
        competitor_count = len(keyword_data.get('competitors', []))
        if competitor_count >= 3:
            score += 30  # اگر چند رقیب دارند، فرصت خوبی است
        elif competitor_count >= 2:
            score += 20
        else:
            score += 10
        
        # فاکتور 3: Position رقبا (20%)
        position = keyword_data.get('position')
        if position:
            if position <= 3:
                score += 20  # رقبا رتبه خوبی دارند، فرصت خوبی است
            elif position <= 10:
                score += 15
            elif position <= 20:
                score += 10
            else:
                score += 5
        
        # فاکتور 4: CPC (10%)
        cpc = keyword_data.get('cpc', 0.0)
        if cpc > 0:
            if cpc >= 5.0:
                score += 10  # CPC بالا = ارزش بالا
            elif cpc >= 2.0:
                score += 7
            elif cpc >= 1.0:
                score += 5
            else:
                score += 3
        
        return min(score, 100.0)
    
    def _calculate_advantage_score(self, keyword_data: Dict[str, Any]) -> float:
        """محاسبه Advantage Score برای کلمات کلیدی شما"""
        score = 0.0
        
        # فاکتور 1: Search Volume (50%)
        search_volume = keyword_data.get('search_volume', 0)
        if search_volume > 0:
            if search_volume >= 10000:
                score += 50
            elif search_volume >= 1000:
                score += 40
            elif search_volume >= 100:
                score += 30
            else:
                score += 20
        
        # فاکتور 2: Position شما (30%)
        position = keyword_data.get('position')
        if position:
            if position <= 3:
                score += 30
            elif position <= 10:
                score += 25
            elif position <= 20:
                score += 20
            else:
                score += 10
        
        # فاکتور 3: Traffic (20%)
        traffic = keyword_data.get('traffic', 0)
        if traffic > 0:
            if traffic >= 1000:
                score += 20
            elif traffic >= 100:
                score += 15
            else:
                score += 10
        
        return min(score, 100.0)
    
    def _calculate_competition_level(
        self,
        your_position: Optional[int],
        competitor_position: Optional[int]
    ) -> str:
        """تعیین سطح رقابت"""
        if not your_position and not competitor_position:
            return 'unknown'
        
        if your_position and competitor_position:
            if your_position < competitor_position:
                return 'winning'  # شما برنده‌اید
            elif your_position == competitor_position:
                return 'tied'  # مساوی
            else:
                return 'losing'  # شما در حال باخت هستید
        elif your_position:
            return 'you_only'  # فقط شما رتبه دارید
        else:
            return 'competitor_only'  # فقط رقیب رتبه دارد
    
    def _calculate_summary(
        self,
        your_keywords: List[Dict[str, Any]],
        competitor_keywords: Dict[str, List[Dict[str, Any]]],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """محاسبه خلاصه"""
        total_competitor_keywords = sum(len(kws) for kws in competitor_keywords.values())
        
        # محاسبه معیارهای فرصت‌ها
        opportunities = gap_analysis.get('opportunities', [])
        high_opportunity_count = sum(1 for opp in opportunities if opp.get('opportunity_score', 0) >= 70)
        medium_opportunity_count = sum(1 for opp in opportunities if 40 <= opp.get('opportunity_score', 0) < 70)
        
        # محاسبه معیارهای مزیت‌ها
        advantages = gap_analysis.get('advantages', [])
        high_advantage_count = sum(1 for adv in advantages if adv.get('advantage_score', 0) >= 70)
        
        # محاسبه معیارهای رقابت
        competition = gap_analysis.get('competition', [])
        winning_count = sum(1 for comp in competition if comp.get('competition_level') == 'winning')
        losing_count = sum(1 for comp in competition if comp.get('competition_level') == 'losing')
        
        return {
            'your_total_keywords': len(your_keywords),
            'competitors_total_keywords': total_competitor_keywords,
            'opportunities_count': len(opportunities),
            'high_opportunities': high_opportunity_count,
            'medium_opportunities': medium_opportunity_count,
            'advantages_count': len(advantages),
            'high_advantages': high_advantage_count,
            'competition_count': len(competition),
            'winning_keywords': winning_count,
            'losing_keywords': losing_count,
            'coverage_ratio': round(len(your_keywords) / total_competitor_keywords * 100, 2) if total_competitor_keywords > 0 else 0
        }
    
    def _generate_recommendations(
        self,
        gap_analysis: Dict[str, Any],
        language: str
    ) -> List[str]:
        """تولید پیشنهادات عملی"""
        recommendations = []
        
        opportunities = gap_analysis.get('opportunities', [])
        advantages = gap_analysis.get('advantages', [])
        competition = gap_analysis.get('competition', [])
        
        if language == 'fa':
            # پیشنهادات بر اساس فرصت‌ها
            if opportunities:
                high_opp = [opp for opp in opportunities if opp.get('opportunity_score', 0) >= 70]
                if high_opp:
                    recommendations.append(
                        f"✅ {len(high_opp)} فرصت عالی شناسایی شد. پیشنهاد می‌شود محتوا برای این کلمات کلیدی تولید کنید."
                    )
                
                recommendations.append(
                    f"📝 {len(opportunities)} کلمه کلیدی که رقبا دارند اما شما ندارید. این فرصت‌ها را در اولویت قرار دهید."
                )
            
            # پیشنهادات بر اساس مزیت‌ها
            if advantages:
                recommendations.append(
                    f"💪 {len(advantages)} مزیت شناسایی شد. روی این کلمات کلیدی سرمایه‌گذاری کنید و محتوای بیشتری تولید کنید."
                )
            
            # پیشنهادات بر اساس رقابت
            losing = [comp for comp in competition if comp.get('competition_level') == 'losing']
            if losing:
                recommendations.append(
                    f"⚠️ {len(losing)} کلمه کلیدی که رقبا رتبه بهتری دارند. محتوای خود را بهبود دهید."
                )
            
            winning = [comp for comp in competition if comp.get('competition_level') == 'winning']
            if winning:
                recommendations.append(
                    f"🎯 {len(winning)} کلمه کلیدی که شما رتبه بهتری دارید. این موقعیت را حفظ کنید."
                )
            
            # پیشنهادات کلی
            if len(opportunities) > len(advantages):
                recommendations.append(
                    "💡 فرصت‌های بیشتری نسبت به مزیت‌ها وجود دارد. روی تولید محتوا برای فرصت‌ها تمرکز کنید."
                )
            else:
                recommendations.append(
                    "💡 شما مزیت‌های خوبی دارید. روی تقویت این مزیت‌ها و تولید محتوای بیشتر تمرکز کنید."
                )
        else:
            # English recommendations
            if opportunities:
                high_opp = [opp for opp in opportunities if opp.get('opportunity_score', 0) >= 70]
                if high_opp:
                    recommendations.append(
                        f"✅ {len(high_opp)} high-opportunity keywords identified. Consider creating content for these."
                    )
                recommendations.append(
                    f"📝 {len(opportunities)} keywords that competitors have but you don't. Prioritize these opportunities."
                )
            
            if advantages:
                recommendations.append(
                    f"💪 {len(advantages)} advantages identified. Invest in these keywords and create more content."
                )
            
            losing = [comp for comp in competition if comp.get('competition_level') == 'losing']
            if losing:
                recommendations.append(
                    f"⚠️ {len(losing)} keywords where competitors rank better. Improve your content."
                )
        
        return recommendations
    
    def _empty_gap_result(self) -> Dict[str, Any]:
        """برگرداندن نتیجه خالی"""
        return {
            'opportunities': [],
            'advantages': [],
            'competition': [],
            'recommendations': [],
            'summary': {
                'your_total_keywords': 0,
                'competitors_total_keywords': 0,
                'opportunities_count': 0,
                'advantages_count': 0,
                'competition_count': 0
            },
            'competitor_analysis': {}
        }

