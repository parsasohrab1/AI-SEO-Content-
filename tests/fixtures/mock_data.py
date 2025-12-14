"""
داده‌های Mock برای تست
شامل داده‌های نمونه برای تست‌های مختلف
"""

from typing import Dict, List, Any
from datetime import datetime


def get_mock_site_analysis() -> Dict[str, Any]:
    """داده Mock برای تحلیل سایت"""
    return {
        "url": "https://example.com",
        "cms_type": "wordpress",
        "technology_stack": {
            "cms": "WordPress",
            "version": "6.4",
            "php_version": "8.2",
            "plugins": ["yoast-seo", "woocommerce"]
        },
        "structure": {
            "total_pages": 50,
            "total_posts": 100,
            "categories": 10,
            "tags": 50
        },
        "performance": {
            "speed_score": 85,
            "mobile_score": 90,
            "accessibility_score": 80,
            "best_practices_score": 75
        },
        "security": {
            "ssl_enabled": True,
            "security_headers": True,
            "vulnerabilities": []
        },
        "sitemap": {
            "url": "https://example.com/sitemap.xml",
            "total_urls": 150,
            "last_modified": datetime.now().isoformat()
        }
    }


def get_mock_seo_analysis() -> Dict[str, Any]:
    """داده Mock برای تحلیل سئو"""
    return {
        "technical_seo": {
            "core_web_vitals": {
                "lcp": 2.5,
                "fid": 100,
                "cls": 0.1,
                "score": "good"
            },
            "crawlability": {
                "status": "good",
                "crawl_errors": 0,
                "blocked_pages": 0
            },
            "indexability": {
                "indexed_pages": 145,
                "not_indexed": 5,
                "reasons": []
            },
            "structured_data": {
                "present": True,
                "types": ["Article", "Organization", "BreadcrumbList"],
                "errors": []
            }
        },
        "content_seo": {
            "keywords": [
                {"keyword": "test", "density": 2.5, "position": 1},
                {"keyword": "example", "density": 1.8, "position": 2}
            ],
            "readability": {
                "score": 75,
                "level": "good",
                "avg_sentence_length": 15
            },
            "content_structure": {
                "h1_count": 50,
                "h2_count": 200,
                "internal_links": 500,
                "external_links": 100
            },
            "images": {
                "total": 200,
                "with_alt": 180,
                "optimized": 150,
                "missing_alt": 20
            }
        },
        "external_seo": {
            "backlinks": {
                "total": 1000,
                "dofollow": 800,
                "nofollow": 200,
                "domain_authority": 65
            },
            "social_signals": {
                "facebook_shares": 500,
                "twitter_shares": 300,
                "linkedin_shares": 200
            }
        },
        "competitor_analysis": {
            "competitors": [
                {
                    "domain": "competitor1.com",
                    "domain_authority": 70,
                    "backlinks": 1500
                }
            ],
            "keyword_gaps": [
                {"keyword": "missing_keyword", "opportunity": "high"}
            ]
        },
        "issues": [
            {
                "type": "missing_meta_description",
                "priority": "high",
                "affected_pages": 10,
                "fix": "Add meta descriptions"
            },
            {
                "type": "slow_images",
                "priority": "medium",
                "affected_pages": 20,
                "fix": "Optimize images"
            }
        ]
    }


def get_mock_generated_content() -> Dict[str, Any]:
    """داده Mock برای محتوای تولید شده"""
    return {
        "text_content": [
            {
                "id": "content_1",
                "title": "10 Tips for Better SEO",
                "content": "This is a comprehensive guide...",
                "word_count": 1500,
                "readability_score": 80,
                "keywords": ["seo", "tips", "optimization"],
                "status": "ready"
            }
        ],
        "images": [
            {
                "id": "img_1",
                "url": "https://example.com/images/seo-tips.jpg",
                "alt_text": "SEO Tips Infographic",
                "size": "1024x768",
                "format": "webp",
                "optimized": True
            }
        ],
        "videos": [
            {
                "id": "vid_1",
                "url": "https://example.com/videos/seo-guide.mp4",
                "duration": 300,
                "thumbnail": "https://example.com/thumbnails/seo-guide.jpg",
                "status": "ready"
            }
        ],
        "infographics": [
            {
                "id": "infographic_1",
                "url": "https://example.com/infographics/seo-stats.png",
                "title": "SEO Statistics 2024",
                "status": "ready"
            }
        ]
    }


def get_mock_seo_implementation() -> Dict[str, Any]:
    """داده Mock برای پیاده‌سازی سئو"""
    return {
        "changes_applied": [
            {
                "type": "meta_tags",
                "pages_affected": 10,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "image_optimization",
                "images_optimized": 20,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "structured_data",
                "pages_updated": 5,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "rollback_available": True,
        "rollback_id": "rollback_123",
        "total_changes": 3,
        "successful_changes": 3,
        "failed_changes": 0
    }


def get_mock_dashboard_data() -> Dict[str, Any]:
    """داده Mock برای Dashboard"""
    return {
        "analysis_id": "analysis_123",
        "site_url": "https://example.com",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "summary": {
            "total_pages": 50,
            "seo_score": 85,
            "content_count": 100,
            "issues_fixed": 5,
            "improvement_percentage": 15
        },
        "site_analysis": get_mock_site_analysis(),
        "seo_analysis": get_mock_seo_analysis(),
        "generated_content": get_mock_generated_content(),
        "seo_implementation": get_mock_seo_implementation(),
        "charts": {
            "seo_score_over_time": [
                {"date": "2024-01-01", "score": 70},
                {"date": "2024-01-15", "score": 80},
                {"date": "2024-02-01", "score": 85}
            ],
            "traffic_growth": [
                {"date": "2024-01-01", "visitors": 1000},
                {"date": "2024-01-15", "visitors": 1200},
                {"date": "2024-02-01", "visitors": 1500}
            ]
        },
        "alerts": [
            {
                "type": "warning",
                "message": "5 pages missing meta descriptions",
                "priority": "high"
            }
        ],
        "recent_activities": [
            {
                "action": "content_generated",
                "timestamp": datetime.now().isoformat(),
                "details": "Generated 10 new articles"
            }
        ]
    }


def get_mock_error_response() -> Dict[str, Any]:
    """داده Mock برای پاسخ خطا"""
    return {
        "error": True,
        "error_code": "ANALYSIS_FAILED",
        "message": "Site analysis failed",
        "details": "Unable to connect to the site",
        "timestamp": datetime.now().isoformat()
    }


def get_multiple_sites_data(count: int = 10) -> List[Dict[str, Any]]:
    """تولید داده Mock برای چند سایت"""
    sites = []
    for i in range(count):
        site_data = get_mock_site_analysis()
        site_data["url"] = f"https://example{i}.com"
        site_data["analysis_id"] = f"analysis_{i}"
        sites.append(site_data)
    return sites

