"""
Configuration و Fixtures مشترک برای تمام تست‌ها
"""

import pytest
import asyncio
from typing import AsyncGenerator
from tests.fixtures.mock_data import (
    get_mock_site_analysis,
    get_mock_seo_analysis,
    get_mock_generated_content,
    get_mock_dashboard_data
)


@pytest.fixture(scope="session")
def event_loop():
    """Event loop برای async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_site_analysis():
    """Fixture برای داده Mock تحلیل سایت"""
    return get_mock_site_analysis()


@pytest.fixture
def mock_seo_analysis():
    """Fixture برای داده Mock تحلیل سئو"""
    return get_mock_seo_analysis()


@pytest.fixture
def mock_generated_content():
    """Fixture برای داده Mock محتوای تولید شده"""
    return get_mock_generated_content()


@pytest.fixture
def mock_dashboard_data():
    """Fixture برای داده Mock Dashboard"""
    return get_mock_dashboard_data()


@pytest.fixture
async def async_client():
    """Fixture برای Async HTTP Client"""
    # این باید با httpx یا aiohttp پیاده‌سازی شود
    yield None


@pytest.fixture
def test_site_url():
    """Fixture برای URL تست"""
    return "https://example.com"


@pytest.fixture
def test_analysis_id():
    """Fixture برای Analysis ID تست"""
    return "test_analysis_123"

