"""
Security Middleware - برای امنیت API
"""

import logging
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

logger = logging.getLogger(__name__)

# Rate Limiting Storage (در Production باید از Redis استفاده شود)
rate_limit_storage: dict = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware برای Rate Limiting"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        # دریافت IP Client
        client_ip = request.client.host if request.client else "unknown"
        
        # بررسی Rate Limit
        current_time = time.time()
        minute_window = int(current_time / 60)
        key = f"{client_ip}:{minute_window}"
        
        # شمارش درخواست‌ها
        request_count = rate_limit_storage.get(key, 0)
        
        if request_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # افزایش شمارنده
        rate_limit_storage[key] = request_count + 1
        
        # پاک کردن کلیدهای قدیمی
        for old_key in list(rate_limit_storage.keys()):
            if old_key != key:
                del rate_limit_storage[old_key]
        
        # ادامه Request
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware برای اضافه کردن Security Headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # اضافه کردن Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware برای Logging درخواست‌ها"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log Request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # اجرای Request
        response = await call_next(request)
        
        # محاسبه Duration
        duration = time.time() - start_time
        
        # Log Response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.3f}s"
        )
        
        return response

