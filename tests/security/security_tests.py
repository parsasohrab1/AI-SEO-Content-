"""
تست‌های امنیتی
شامل تست SQL Injection، XSS، Authentication، Authorization و ...
"""

import pytest
import requests
from typing import Dict, Any


class TestSecurity:
    """کلاس تست‌های امنیتی"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_sql_injection_in_url(self):
        """تست SQL Injection در URL"""
        malicious_urls = [
            "https://example.com'; DROP TABLE sites; --",
            "https://example.com' OR '1'='1",
            "https://example.com'; SELECT * FROM users; --",
        ]
        
        for malicious_url in malicious_urls:
            payload = {
                "url": malicious_url,
                "auto_implement": True
            }
            
            response = requests.post(
                f"{self.BASE_URL}/analyze-site",
                json=payload
            )
            
            # باید خطا برگرداند یا URL را Sanitize کند
            assert response.status_code in [400, 422], \
                f"SQL Injection vulnerability detected: {malicious_url}"
    
    def test_xss_in_url(self):
        """تست XSS در URL"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for xss_payload in xss_payloads:
            payload = {
                "url": f"https://example.com/{xss_payload}",
                "auto_implement": True
            }
            
            response = requests.post(
                f"{self.BASE_URL}/analyze-site",
                json=payload
            )
            
            # باید XSS را Sanitize کند
            response_text = response.text
            assert "<script>" not in response_text.lower(), \
                f"XSS vulnerability detected: {xss_payload}"
    
    def test_authentication_required(self):
        """تست نیاز به Authentication برای Endpointهای حساس"""
        protected_endpoints = [
            "/dashboard/admin",
            "/dashboard/settings",
            "/api/admin/users",
        ]
        
        for endpoint in protected_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            
            # باید 401 یا 403 برگرداند
            assert response.status_code in [401, 403], \
                f"Authentication not required for: {endpoint}"
    
    def test_authorization_levels(self):
        """تست سطوح مختلف Authorization"""
        # این تست نیاز به Token دارد
        # باید با Roleهای مختلف تست شود
        
        admin_token = "admin_token_here"
        user_token = "user_token_here"
        
        admin_endpoints = [
            "/api/admin/users",
            "/api/admin/settings",
        ]
        
        for endpoint in admin_endpoints:
            # تست با User Token (نباید دسترسی داشته باشد)
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, \
                f"User should not access admin endpoint: {endpoint}"
            
            # تست با Admin Token (باید دسترسی داشته باشد)
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200, \
                f"Admin should access admin endpoint: {endpoint}"
    
    def test_rate_limiting(self):
        """تست Rate Limiting"""
        endpoint = f"{self.BASE_URL}/analyze-site"
        payload = {
            "url": "https://example.com",
            "auto_implement": True
        }
        
        # ارسال درخواست‌های زیاد
        responses = []
        for i in range(100):
            response = requests.post(endpoint, json=payload)
            responses.append(response.status_code)
        
        # باید برخی درخواست‌ها 429 (Too Many Requests) برگردانند
        rate_limited = sum(1 for status in responses if status == 429)
        assert rate_limited > 0, "Rate limiting not working"
    
    def test_input_validation(self):
        """تست اعتبارسنجی ورودی"""
        invalid_inputs = [
            {"url": ""},  # URL خالی
            {"url": "not-a-url"},  # URL نامعتبر
            {"url": "ftp://example.com"},  # پروتکل غیرمجاز
            {"url": "https://example.com", "auto_implement": "not-boolean"},  # نوع نامعتبر
        ]
        
        for invalid_input in invalid_inputs:
            response = requests.post(
                f"{self.BASE_URL}/analyze-site",
                json=invalid_input
            )
            
            # باید 422 (Unprocessable Entity) برگرداند
            assert response.status_code == 422, \
                f"Input validation failed for: {invalid_input}"
    
    def test_csrf_protection(self):
        """تست محافظت در برابر CSRF"""
        # این تست نیاز به Session دارد
        # باید بررسی شود که CSRF Token لازم است
        
        endpoint = f"{self.BASE_URL}/dashboard/apply-fixes"
        payload = {"fixes": ["fix1", "fix2"]}
        
        # درخواست بدون CSRF Token
        response = requests.post(endpoint, json=payload)
        
        # باید خطا برگرداند
        assert response.status_code in [400, 403], \
            "CSRF protection not working"
    
    def test_sensitive_data_exposure(self):
        """تست عدم افشای اطلاعات حساس"""
        response = requests.get(f"{self.BASE_URL}/dashboard/test-id")
        
        # بررسی عدم وجود اطلاعات حساس در Response
        sensitive_patterns = [
            "password",
            "secret",
            "api_key",
            "token",
            "private_key",
        ]
        
        response_text = response.text.lower()
        for pattern in sensitive_patterns:
            assert pattern not in response_text, \
                f"Sensitive data exposed: {pattern}"
    
    def test_https_enforcement(self):
        """تست اجباری بودن HTTPS"""
        # این تست باید در Production انجام شود
        # بررسی شود که HTTP به HTTPS Redirect می‌شود
        
        http_url = "http://example.com/api/analyze-site"
        response = requests.post(http_url, allow_redirects=False)
        
        # باید Redirect به HTTPS بدهد
        assert response.status_code in [301, 302, 307, 308], \
            "HTTPS enforcement not working"


@pytest.mark.parametrize("malicious_input", [
    "'; DROP TABLE sites; --",
    "<script>alert('XSS')</script>",
    "../../etc/passwd",
    "null",
    "undefined",
])
def test_input_sanitization(malicious_input):
    """تست Sanitization ورودی‌های مخرب"""
    payload = {
        "url": f"https://example.com/{malicious_input}",
        "auto_implement": True
    }
    
    response = requests.post(
        "http://localhost:8000/analyze-site",
        json=payload
    )
    
    # باید ورودی را Sanitize کند یا خطا برگرداند
    assert response.status_code in [200, 400, 422], \
        f"Input sanitization failed for: {malicious_input}"

