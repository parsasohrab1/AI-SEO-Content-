"""
Cache Manager - مدیریت Cache برای بهبود Performance
"""

import json
import hashlib
import logging
from typing import Any, Optional
from datetime import datetime, timedelta
try:
    import redis.asyncio as redis
except ImportError:
    # Fallback برای زمانی که redis نصب نیست
    redis = None

logger = logging.getLogger(__name__)


class CacheManager:
    """مدیریت Cache با Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """اتصال به Redis"""
        if redis is None:
            logger.warning("Redis not available, caching disabled")
            self._connected = False
            return
        
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            self._connected = True
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {str(e)}")
            self._connected = False
    
    async def close(self):
        """بستن اتصال"""
        if self.client:
            await self.client.close()
            self._connected = False
    
    def _generate_key(self, prefix: str, *args) -> str:
        """تولید Cache Key"""
        key_data = "_".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """دریافت از Cache"""
        if not self._connected:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600  # 1 hour default
    ):
        """ذخیره در Cache"""
        if not self._connected:
            return
        
        try:
            value_str = json.dumps(value, default=str)
            await self.client.setex(key, ttl, value_str)
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
    
    async def delete(self, key: str):
        """حذف از Cache"""
        if not self._connected:
            return
        
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
    
    async def get_or_set(
        self,
        key: str,
        func,
        ttl: int = 3600,
        *args,
        **kwargs
    ) -> Any:
        """
        دریافت از Cache یا اجرای Function و ذخیره
        
        Args:
            key: Cache Key
            func: Function برای اجرا در صورت عدم وجود Cache
            ttl: Time To Live (ثانیه)
            *args, **kwargs: Arguments برای Function
            
        Returns:
            نتیجه از Cache یا Function
        """
        # تلاش برای دریافت از Cache
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached
        
        # اجرای Function
        logger.debug(f"Cache miss for key: {key}, executing function")
        result = await func(*args, **kwargs)
        
        # ذخیره در Cache
        await self.set(key, result, ttl)
        
        return result


# Global Cache Manager Instance
cache_manager = CacheManager()

