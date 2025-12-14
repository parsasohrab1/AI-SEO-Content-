"""
Monitoring و Metrics - برای ردیابی Performance
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus Metrics
request_count = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

pipeline_duration = Histogram(
    'pipeline_duration_seconds',
    'Pipeline execution duration in seconds',
    ['pipeline_type', 'status']
)

active_pipelines = Gauge(
    'active_pipelines',
    'Number of active pipelines'
)


def monitor_request(func):
    """Decorator برای Monitoring API Requests"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = "GET"  # Default
        endpoint = func.__name__
        status = "success"
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)
            
            return result
            
        except Exception as e:
            status = "error"
            duration = time.time() - start_time
            
            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)
            
            logger.error(f"Error in {endpoint}: {str(e)}")
            raise
    
    return wrapper


def monitor_pipeline(pipeline_type: str):
    """Decorator برای Monitoring Pipeline"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            active_pipelines.inc()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                pipeline_duration.labels(
                    pipeline_type=pipeline_type,
                    status=status
                ).observe(duration)
                
                return result
                
            except Exception as e:
                status = "failed"
                duration = time.time() - start_time
                
                pipeline_duration.labels(
                    pipeline_type=pipeline_type,
                    status=status
                ).observe(duration)
                
                logger.error(f"Pipeline {pipeline_type} failed: {str(e)}")
                raise
                
            finally:
                active_pipelines.dec()
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """کلاس برای ردیابی Performance"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    def start_timer(self, name: str):
        """شروع Timer"""
        self.metrics[name] = {
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        }
    
    def end_timer(self, name: str) -> float:
        """پایان Timer و برگرداندن Duration"""
        if name in self.metrics:
            self.metrics[name]['end_time'] = time.time()
            duration = self.metrics[name]['end_time'] - self.metrics[name]['start_time']
            self.metrics[name]['duration'] = duration
            return duration
        return 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """دریافت تمام Metrics"""
        return self.metrics
    
    def get_duration(self, name: str) -> Optional[float]:
        """دریافت Duration یک Metric"""
        if name in self.metrics:
            return self.metrics[name].get('duration')
        return None

