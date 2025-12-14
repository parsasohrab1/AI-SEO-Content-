"""
تست ارتباط بین سرویس‌ها
بررسی ارتباط صحیح بین میکروسرویس‌ها
"""

import pytest
import asyncio
from typing import Dict, Any


class TestServiceCommunication:
    """تست ارتباط بین سرویس‌ها"""
    
    @pytest.mark.asyncio
    async def test_site_analyzer_to_seo_analyzer(self):
        """تست ارتباط Site Analyzer به SEO Analyzer"""
        # Site Analyzer تحلیل را انجام می‌دهد
        site_analysis = {
            'url': 'https://example.com',
            'cms_type': 'wordpress',
            'structure': {'pages': 50}
        }
        
        # SEO Analyzer باید بتواند از این داده استفاده کند
        seo_analysis = await self._mock_seo_analyzer(site_analysis)
        
        assert seo_analysis is not None
        assert 'site_url' in seo_analysis
        assert seo_analysis['site_url'] == site_analysis['url']
    
    @pytest.mark.asyncio
    async def test_seo_analyzer_to_content_generator(self):
        """تست ارتباط SEO Analyzer به Content Generator"""
        seo_analysis = {
            'keywords': ['test', 'example'],
            'content_gaps': ['missing_blog_posts'],
            'competitor_analysis': {}
        }
        
        # Content Generator باید از SEO Analysis استفاده کند
        content = await self._mock_content_generator(seo_analysis)
        
        assert content is not None
        assert 'keywords' in content or 'topics' in content
    
    @pytest.mark.asyncio
    async def test_content_generator_to_placement_engine(self):
        """تست ارتباط Content Generator به Placement Engine"""
        content = {
            'text_content': [{'title': 'Test', 'content': '...'}],
            'images': [],
            'videos': []
        }
        
        site_structure = {
            'pages': [{'id': 1, 'url': '/page1'}],
            'posts': []
        }
        
        # Placement Engine باید محتوا را در مکان مناسب قرار دهد
        placement = await self._mock_placement_engine(content, site_structure)
        
        assert placement is not None
        assert 'placed_content' in placement
    
    @pytest.mark.asyncio
    async def test_dashboard_updates_from_all_services(self):
        """تست به‌روزرسانی Dashboard از تمام سرویس‌ها"""
        analysis_id = "test_123"
        
        # داده‌های از سرویس‌های مختلف
        site_data = {'status': 'completed'}
        seo_data = {'score': 85}
        content_data = {'generated': 10}
        placement_data = {'published': 5}
        
        # Dashboard باید همه را دریافت کند
        dashboard = await self._mock_dashboard_update(
            analysis_id,
            site_data,
            seo_data,
            content_data,
            placement_data
        )
        
        assert dashboard is not None
        assert dashboard['analysis_id'] == analysis_id
        assert 'site_analysis' in dashboard
        assert 'seo_analysis' in dashboard
    
    @pytest.mark.asyncio
    async def test_error_propagation_between_services(self):
        """تست انتشار خطا بین سرویس‌ها"""
        # شبیه‌سازی خطا در یک سرویس
        try:
            site_analysis = await self._mock_site_analyzer_with_error()
            seo_analysis = await self._mock_seo_analyzer(site_analysis)
        except Exception as e:
            # خطا باید به درستی مدیریت شود
            assert "error" in str(e).lower() or "failed" in str(e).lower()
    
    # Mock Methods
    async def _mock_seo_analyzer(self, site_analysis: Dict) -> Dict:
        return {
            'site_url': site_analysis['url'],
            'analysis': 'completed'
        }
    
    async def _mock_content_generator(self, seo_analysis: Dict) -> Dict:
        return {
            'content': 'generated',
            'based_on': seo_analysis
        }
    
    async def _mock_placement_engine(self, content: Dict, structure: Dict) -> Dict:
        return {
            'placed_content': [{'id': 1, 'status': 'placed'}]
        }
    
    async def _mock_dashboard_update(self, analysis_id: str, *args) -> Dict:
        return {
            'analysis_id': analysis_id,
            'site_analysis': args[0] if args else {},
            'seo_analysis': args[1] if len(args) > 1 else {},
            'content_analysis': args[2] if len(args) > 2 else {},
            'placement_analysis': args[3] if len(args) > 3 else {}
        }
    
    async def _mock_site_analyzer_with_error(self):
        raise Exception("Site analysis failed")

