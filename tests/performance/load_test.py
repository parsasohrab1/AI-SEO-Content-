"""
Load Testing با Locust
تست عملکرد سیستم با بارهای مختلف
"""

from locust import HttpUser, task, between
import json
from typing import Dict


class AIContentFactoryUser(HttpUser):
    """User Class برای Load Testing"""
    
    wait_time = between(1, 3)  # زمان انتظار بین درخواست‌ها
    
    def on_start(self):
        """شروع Session"""
        self.analysis_id = None
        self.site_url = "https://example.com"
    
    @task(3)
    def analyze_site(self):
        """تست تحلیل سایت"""
        payload = {
            "url": self.site_url,
            "auto_implement": True,
            "content_types": ["text", "image"],
            "schedule_monitoring": True
        }
        
        response = self.client.post(
            "/analyze-site",
            json=payload,
            name="Analyze Site"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.analysis_id = data.get('analysis_id')
    
    @task(2)
    def get_dashboard(self):
        """تست دریافت Dashboard"""
        if self.analysis_id:
            self.client.get(
                f"/dashboard/{self.analysis_id}",
                name="Get Dashboard"
            )
    
    @task(1)
    def get_seo_report(self):
        """تست دریافت گزارش سئو"""
        if self.analysis_id:
            self.client.get(
                f"/dashboard/{self.analysis_id}/seo-report",
                name="Get SEO Report"
            )
    
    @task(1)
    def get_live_monitoring(self):
        """تست مانیتورینگ بلادرنگ"""
        if self.analysis_id:
            self.client.get(
                f"/dashboard/{self.analysis_id}/live-monitoring",
                name="Live Monitoring"
            )


# Configuration برای تست‌های مختلف
LOAD_TEST_SCENARIOS = {
    "light": {
        "users": 10,
        "spawn_rate": 2,
        "duration": "5m",
        "description": "تست با 10 کاربر همزمان"
    },
    "medium": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "10m",
        "description": "تست با 100 کاربر همزمان"
    },
    "heavy": {
        "users": 500,
        "spawn_rate": 50,
        "duration": "15m",
        "description": "تست با 500 کاربر همزمان"
    },
    "extreme": {
        "users": 1000,
        "spawn_rate": 100,
        "duration": "20m",
        "description": "تست با 1000 کاربر همزمان"
    }
}


def run_load_test(scenario: str = "medium"):
    """
    اجرای Load Test
    
    Usage:
        locust -f load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=10m
    """
    config = LOAD_TEST_SCENARIOS.get(scenario, LOAD_TEST_SCENARIOS["medium"])
    print(f"Running {scenario} load test: {config['description']}")
    return config


if __name__ == "__main__":
    # برای اجرای مستقیم
    import sys
    scenario = sys.argv[1] if len(sys.argv) > 1 else "medium"
    config = run_load_test(scenario)
    print(f"Configuration: {config}")

