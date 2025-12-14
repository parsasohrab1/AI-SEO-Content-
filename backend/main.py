"""
AI Content Factory Pro - Main Application
سیستم تولید و بهینه‌سازی محتوای خودکار با هوش مصنوعی
"""

import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)
from core.pipeline import create_full_pipeline
from core.monitoring import monitor_request, monitor_pipeline
from core.cache import cache_manager

# تنظیمات logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ایجاد FastAPI App
app = FastAPI(
    title="AI Content Factory Pro",
    description="سیستم تولید و بهینه‌سازی محتوای خودکار با هوش مصنوعی",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در Production باید محدود شود
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Initialize Cache
@app.on_event("startup")
async def startup_event():
    """Event Handler برای Startup"""
    await cache_manager.connect()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    """Event Handler برای Shutdown"""
    await cache_manager.close()
    logger.info("Application shutdown")


# Models
class SiteRequest(BaseModel):
    """مدل درخواست تحلیل سایت"""
    url: str = Field(..., description="آدرس سایت هدف")
    auto_implement: bool = Field(True, description="آیا تغییرات به صورت خودکار اعمال شود؟")
    content_types: List[str] = Field(
        default=["text", "image", "video"],
        description="انواع محتوای تولیدی"
    )
    schedule_monitoring: bool = Field(
        True,
        description="آیا مانیتورینگ دوره‌ای فعال شود؟"
    )


class SiteAnalysisResponse(BaseModel):
    """مدل پاسخ تحلیل سایت"""
    analysis_id: str
    site_url: str
    status: str
    initial_findings: Dict
    estimated_time: int
    dashboard_url: Optional[str] = None


# Health Check
@app.get("/")
async def root():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "service": "AI Content Factory Pro",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health Check با جزئیات بیشتر"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "checking...",
            "redis": "checking...",
            "queue": "checking..."
        }
    }


# Main Endpoint
@app.post("/analyze-site", response_model=SiteAnalysisResponse)
@monitor_request
async def analyze_and_optimize_site(
    request: SiteRequest,
    background_tasks: BackgroundTasks
):
    """
    نقطه شروع سیستم - دریافت URL سایت و شروع فرآیند کامل
    """
    try:
        # Import modules (lazy import)
        from core.site_analyzer import SiteAnalyzer
        from core.dashboard_manager import DashboardManager
        
        # ایجاد ID منحصر به فرد
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # شروع فرآیند در پس‌زمینه
        background_tasks.add_task(
            full_automation_pipeline,
            analysis_id,
            request.url,
            request.auto_implement,
            request.content_types
        )
        
        # ایجاد داشبورد
        dashboard_manager = DashboardManager()
        dashboard_url = await dashboard_manager.create_dashboard(analysis_id, request.url)
        
        return SiteAnalysisResponse(
            analysis_id=analysis_id,
            site_url=request.url,
            status="processing_started",
            initial_findings={
                "message": "فرآیند تحلیل و بهینه‌سازی شروع شد",
                "estimated_steps": 5,
                "current_step": 1
            },
            estimated_time=900,  # 15 دقیقه
            dashboard_url=dashboard_url
        )
        
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@monitor_pipeline("full_automation")
async def full_automation_pipeline(
    analysis_id: str,
    site_url: str,
    auto_implement: bool,
    content_types: List[str]
):
    """پایپ‌لاین کامل اتوماسیون با Pipeline Manager"""
    logger.info(f"Starting full automation pipeline for {site_url}")
    
    try:
        # ایجاد Pipeline
        pipeline = await create_full_pipeline(
            analysis_id,
            site_url,
            auto_implement,
            content_types
        )
        
        # اجرای Pipeline
        result = await pipeline.execute()
        
        if result['status'] == 'completed':
            logger.info(f"Pipeline completed successfully for {site_url}")
        else:
            logger.error(f"Pipeline failed: {result.get('error')}")
            # به‌روزرسانی وضعیت خطا در داشبورد
            try:
                from core.dashboard_manager import DashboardManager
                dashboard_manager = DashboardManager()
                await dashboard_manager.update_dashboard(
                    analysis_id,
                    {'status': 'failed', 'error': result.get('error')}
                )
            except:
                pass
        
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        # به‌روزرسانی وضعیت خطا در داشبورد
        try:
            from core.dashboard_manager import DashboardManager
            dashboard_manager = DashboardManager()
            await dashboard_manager.update_dashboard(
                analysis_id,
                {'status': 'failed', 'error': str(e)}
            )
        except:
            pass
        raise


# Dashboard Endpoints
@app.get("/dashboard/{analysis_id}")
async def get_dashboard(analysis_id: str):
    """دریافت داده‌های داشبورد"""
    try:
        from core.dashboard_manager import DashboardManager
        
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{analysis_id}/seo-report")
async def get_seo_report(analysis_id: str):
    """دریافت گزارش کامل سئو"""
    try:
        from core.report_generator import ReportGenerator
        
        report_generator = ReportGenerator()
        report = await report_generator.generate_seo_report(analysis_id)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating SEO report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional Endpoints
@app.post("/dashboard/{analysis_id}/apply-fixes")
async def apply_specific_fixes(analysis_id: str, fixes: List[str]):
    """اعمال اصلاحات خاص"""
    # TODO: Implement
    return {"message": "Not implemented yet", "fixes": fixes}


@app.get("/dashboard/{analysis_id}/live-monitoring")
async def get_live_monitoring(analysis_id: str):
    """دریافت داده‌های مانیتورینگ بلادرنگ"""
    # TODO: Implement
    return {"message": "Not implemented yet", "analysis_id": analysis_id}


@app.post("/dashboard/{analysis_id}/generate-content")
async def generate_additional_content(analysis_id: str, content_spec: Dict):
    """تولید محتوای اضافی"""
    # TODO: Implement
    return {"message": "Not implemented yet", "content_spec": content_spec}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

