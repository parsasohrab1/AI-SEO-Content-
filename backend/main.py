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


class ApplyFixesRequest(BaseModel):
    """مدل درخواست اعمال اصلاحات"""
    fixes: Optional[List[str]] = Field(default=[], description="لیست عنوان‌های اصلاحات")
    recommendation_ids: Optional[List[str]] = Field(default=[], description="لیست ID پیشنهادات")


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
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
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


@app.post("/dashboard/{analysis_id}/analyze-competitors")
async def analyze_competitors(analysis_id: str, request_data: Dict):
    """تحلیل رقبا و استخراج کلمات کلیدی"""
    try:
        from core.dashboard_manager import DashboardManager
        from core.competitor_analyzer import CompetitorAnalyzer
        
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404,
                detail="Dashboard یافت نشد. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        site_url = dashboard_data.get('site_url', '')
        if not site_url:
            raise HTTPException(status_code=400, detail="Site URL not found")
        
        # دریافت لیست رقبا از درخواست یا پیدا کردن خودکار
        competitor_urls = request_data.get('competitor_urls', [])
        industry_keywords = request_data.get('industry_keywords', [])
        
        competitor_analyzer = CompetitorAnalyzer()
        
        # اگر رقبا داده نشده، پیدا کردن خودکار
        if not competitor_urls:
            competitor_urls = await competitor_analyzer.find_competitors(site_url, industry_keywords)
        
        # تحلیل رقبا
        analysis_result = await competitor_analyzer.analyze_multiple_competitors(competitor_urls)
        
        # دریافت کلمات کلیدی برای انتخاب
        keywords_for_selection = await competitor_analyzer.get_competitor_keywords_for_selection(competitor_urls)
        
        # ذخیره در dashboard
        await dashboard_manager.update_dashboard(
            analysis_id,
            {
                'competitor_analysis': {
                    'competitors': analysis_result['competitors'],
                    'keywords': keywords_for_selection,
                    'total_competitors': analysis_result['total_competitors_analyzed'],
                    'total_keywords': analysis_result['total_keywords_found'],
                    'analyzed_at': datetime.now().isoformat()
                }
            }
        )
        
        return {
            'message': f'{len(competitor_urls)} رقیب تحلیل شد و {len(keywords_for_selection)} کلمه کلیدی استخراج شد',
            'competitors': analysis_result['competitors'],
            'keywords': keywords_for_selection,
            'total_competitors': analysis_result['total_competitors_analyzed'],
            'total_keywords': len(keywords_for_selection)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{analysis_id}/competitor-keywords")
async def get_competitor_keywords(analysis_id: str):
    """دریافت کلمات کلیدی رقبا برای نمایش"""
    try:
        from core.dashboard_manager import DashboardManager
        
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404,
                detail="Dashboard یافت نشد."
            )
        
        competitor_analysis = dashboard_data.get('competitor_analysis', {})
        
        if not competitor_analysis:
            return {
                'keywords': [],
                'competitors': [],
                'message': 'هنوز تحلیل رقبا انجام نشده است'
            }
        
        return {
            'keywords': competitor_analysis.get('keywords', []),
            'competitors': competitor_analysis.get('competitors', []),
            'total_competitors': competitor_analysis.get('total_competitors', 0),
            'total_keywords': competitor_analysis.get('total_keywords', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting competitor keywords: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional Endpoints
@app.post("/dashboard/{analysis_id}/save-credentials")
async def save_cms_credentials(analysis_id: str, request_data: Dict):
    """ذخیره اطلاعات لاگین CMS"""
    try:
        from core.dashboard_manager import DashboardManager
        
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        # ذخیره اطلاعات لاگین
        credentials = {
            'cms_type': request_data.get('cms_type', 'wordpress'),
            'admin_url': request_data.get('admin_url', ''),
            'username': request_data.get('username', ''),
            'password': request_data.get('password', ''),  # در production باید encrypt شود
            'api_key': request_data.get('api_key', ''),
            'saved_at': datetime.now().isoformat()
        }
        
        await dashboard_manager.update_dashboard(
            analysis_id,
            {
                'cms_credentials': credentials
            }
        )
        
        return {
            'message': 'اطلاعات لاگین با موفقیت ذخیره شد',
            'cms_type': credentials['cms_type']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dashboard/{analysis_id}/apply-fixes")
async def apply_specific_fixes(analysis_id: str, request_data: ApplyFixesRequest):
    """اعمال اصلاحات خاص"""
    try:
        from core.dashboard_manager import DashboardManager
        from core.seo_implementation import AutoSEOImplementation
        from core.report_generator import ReportGenerator
        
        # تبدیل Pydantic model به dict
        request_dict = request_data.dict()
        fixes = request_dict.get('fixes', []) or []
        recommendation_ids = request_dict.get('recommendation_ids', []) or []
        
        # بررسی اینکه حداقل یکی از فیلدها پر باشد
        if not fixes and not recommendation_ids:
            raise HTTPException(status_code=400, detail="حداقل باید یک پیشنهاد انتخاب شود")
        
        # دریافت داده‌های داشبورد
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        site_url = dashboard_data.get('site_url', '')
        if not site_url:
            raise HTTPException(status_code=400, detail="Site URL not found")
        
        # دریافت اطلاعات لاگین CMS (اگر موجود باشد)
        cms_credentials = dashboard_data.get('cms_credentials', {})
        cms_type = cms_credentials.get('cms_type') if cms_credentials else None
        
        # دریافت نوع CMS از تحلیل سایت
        site_analysis = dashboard_data.get('data', {}).get('site_analysis', {})
        detected_cms = site_analysis.get('cms_type', 'custom') if site_analysis else 'custom'
        
        # استفاده از نوع CMS از credentials یا از تحلیل
        final_cms_type = cms_type or detected_cms
        
        # دریافت weaknesses برای استفاده در کل تابع
        weaknesses = dashboard_data.get('weaknesses', [])
        
        # دریافت پیشنهادات - اگر در dashboard موجود نبود، از weaknesses تولید می‌کنیم
        recommendations = dashboard_data.get('recommendations', [])
        
        # اضافه کردن مشکلات سئو به عنوان پیشنهادات
        seo_analysis = dashboard_data.get('data', {}).get('seo_analysis', {})
        seo_issues = seo_analysis.get('issues', []) if isinstance(seo_analysis, dict) else []
        
        if seo_issues:
            for i, issue in enumerate(seo_issues):
                if isinstance(issue, dict):
                    # تبدیل مشکل سئو به پیشنهاد
                    issue_title = issue.get('title', '')
                    issue_type = issue.get('type', 'general')
                    
                    # بررسی اینکه آیا این پیشنهاد قبلاً وجود دارد
                    existing_rec = next((r for r in recommendations if r.get('title') == issue_title), None)
                    if not existing_rec:
                        recommendations.append({
                            'id': f'seo_issue_{i}',
                            'title': issue_title,
                            'description': issue.get('description', ''),
                            'category': issue_type,
                            'priority': issue.get('severity', 'medium'),
                            'automated': issue_type in ['headings_h1', 'images_alt', 'meta_tags'],
                            'recommendation': issue.get('recommendation', ''),
                            'source': 'seo_analysis'
                        })
        
        # اگر recommendations موجود نبود، از weaknesses تولید می‌کنیم
        if not recommendations and weaknesses:
                # تبدیل weaknesses به recommendations
                recommendations = []
                for i, weakness in enumerate(weaknesses):
                    recommendations.append({
                        'id': f"rec_{i}",
                        'title': weakness.get('title', ''),
                        'description': weakness.get('description', ''),
                        'category': weakness.get('category', 'عمومی'),
                        'priority': weakness.get('priority', 'medium'),
                        'automated': False
                    })
        
        # فیلتر کردن پیشنهادات انتخاب شده
        selected_recommendations = []
        
        logger.info(f"Received recommendation_ids: {recommendation_ids}, fixes: {fixes}")
        logger.info(f"Available recommendations count: {len(recommendations)}")
        
        if recommendation_ids and len(recommendation_ids) > 0:
            for rec_id in recommendation_ids:
                # پیدا کردن پیشنهاد بر اساس ID
                rec = None
                # اول سعی می‌کنیم با ID دقیق match کنیم
                for r in recommendations:
                    if r.get('id') == rec_id:
                        rec = r
                        break
                
                # اگر پیدا نشد، با index match می‌کنیم
                if not rec:
                    # اگر rec_id به صورت "rec_0" است، index را استخراج می‌کنیم
                    if rec_id.startswith('rec_'):
                        try:
                            index = int(rec_id.split('_')[1])
                            if 0 <= index < len(recommendations):
                                rec = recommendations[index]
                        except (ValueError, IndexError):
                            pass
                    # اگر rec_id به صورت "seo_issue_0" است، از مشکلات سئو استفاده می‌کنیم
                    elif rec_id.startswith('seo_issue_'):
                        try:
                            issue_index = int(rec_id.replace('seo_issue_', ''))
                            seo_issues = seo_analysis.get('issues', []) if isinstance(seo_analysis, dict) else []
                            if 0 <= issue_index < len(seo_issues):
                                issue = seo_issues[issue_index]
                                if isinstance(issue, dict):
                                    rec = {
                                        'id': rec_id,
                                        'title': issue.get('title', ''),
                                        'description': issue.get('description', ''),
                                        'category': issue.get('type', 'general'),
                                        'priority': issue.get('severity', 'medium'),
                                        'automated': issue.get('type', '') in ['headings_h1', 'images_alt', 'meta_tags'],
                                        'recommendation': issue.get('recommendation', ''),
                                        'source': 'seo_analysis'
                                    }
                        except (ValueError, IndexError):
                            pass
                
                if rec:
                    selected_recommendations.append(rec)
                    logger.info(f"Found recommendation: {rec.get('title')}")
                else:
                    logger.warning(f"Recommendation ID not found: {rec_id}")
        
        # اگر با ID پیدا نکردیم، از عنوان استفاده می‌کنیم
        if not selected_recommendations and fixes and len(fixes) > 0:
            for fix_title in fixes:
                rec = next((r for r in recommendations if r.get('title') == fix_title), None)
                if rec:
                    selected_recommendations.append(rec)
                    logger.info(f"Found recommendation by title: {rec.get('title')}")
        
        if not selected_recommendations:
            # اگر هیچ پیشنهادی پیدا نشد، سعی می‌کنیم از weaknesses مستقیماً استفاده کنیم
            if weaknesses and recommendation_ids:
                logger.info("Trying to create recommendations from weaknesses directly")
                for rec_id in recommendation_ids:
                    if rec_id.startswith('rec_'):
                        try:
                            index = int(rec_id.split('_')[1])
                            weaknesses_list = dashboard_data.get('weaknesses', [])
                            if 0 <= index < len(weaknesses_list):
                                weakness = weaknesses_list[index]
                                selected_recommendations.append({
                                    'id': rec_id,
                                    'title': weakness.get('title', ''),
                                    'description': weakness.get('description', ''),
                                    'category': weakness.get('category', 'عمومی'),
                                    'priority': weakness.get('priority', 'medium'),
                                    'automated': False
                                })
                                logger.info(f"Created recommendation from weakness: {weakness.get('title')}")
                        except (ValueError, IndexError):
                            pass
            
            if not selected_recommendations:
                error_detail = f"هیچ پیشنهاد معتبری یافت نشد. "
                error_detail += f"درخواست شده: {recommendation_ids if recommendation_ids else fixes}. "
                error_detail += f"تعداد پیشنهادات موجود: {len(recommendations)}"
                if recommendations:
                    error_detail += f". IDهای موجود: {[r.get('id', f'rec_{i}') for i, r in enumerate(recommendations[:5])]}"
                weaknesses_list = dashboard_data.get('weaknesses', [])
                if weaknesses_list:
                    error_detail += f". تعداد weaknesses: {len(weaknesses_list)}"
                raise HTTPException(status_code=400, detail=error_detail)
        
        # اعمال پیشنهادات
        implementor = AutoSEOImplementation(site_url, cms_credentials if cms_credentials else None, final_cms_type)
        results = []
        
        for rec in selected_recommendations:
            try:
                # تبدیل پیشنهاد به issue format
                issue = {
                    'type': rec.get('category', 'general'),
                    'priority': rec.get('priority', 'medium'),
                    'title': rec.get('title', ''),
                    'description': rec.get('description', ''),
                    'automated': rec.get('automated', False)
                }
                
                # اگر اطلاعات لاگین موجود باشد، همه پیشنهادات را خودکار اعمال می‌کنیم
                has_credentials = bool(cms_credentials and cms_credentials.get('username') and cms_credentials.get('password'))
                can_auto_apply = has_credentials or rec.get('automated', False)
                
                # اعمال fix
                if can_auto_apply:
                    result = await implementor.implement_fix(issue, cms_credentials if has_credentials else None)
                    results.append({
                        'recommendation_id': rec.get('id', ''),
                        'title': rec.get('title', ''),
                        'status': 'success' if result.get('success') else 'failed',
                        'message': result.get('message', 'اعمال شد'),
                        'changes': result.get('changes', [])
                    })
                else:
                    # برای پیشنهادات غیرخودکار
                    # بررسی اینکه آیا این پیشنهاد نیاز به تنظیمات سرور دارد (مثل HTTPS)
                    title_lower = rec.get('title', '').lower()
                    needs_server_config = 'https' in title_lower or 'ssl' in title_lower or 'گواهینامه' in title_lower
                    
                    if has_credentials and needs_server_config:
                        # اگر credentials موجود است اما نیاز به تنظیمات سرور دارد
                        results.append({
                            'recommendation_id': rec.get('id', ''),
                            'title': rec.get('title', ''),
                            'status': 'pending',
                            'message': f'این پیشنهاد ({rec.get("title")}) نیاز به تنظیمات دستی در سطح سرور دارد و نمی‌تواند به صورت خودکار اعمال شود. لطفاً با مدیر سرور تماس بگیرید.',
                            'manual_required': True
                        })
                    elif has_credentials:
                        # اگر credentials موجود است اما automated نیست، سعی می‌کنیم اعمال کنیم
                        try:
                            result = await implementor.implement_fix(issue, cms_credentials)
                            results.append({
                                'recommendation_id': rec.get('id', ''),
                                'title': rec.get('title', ''),
                                'status': 'success' if result.get('success') else 'pending',
                                'message': result.get('message', 'در حال اعمال...'),
                                'changes': result.get('changes', [])
                            })
                        except Exception as e:
                            logger.error(f"Error applying fix with credentials: {str(e)}")
                            results.append({
                                'recommendation_id': rec.get('id', ''),
                                'title': rec.get('title', ''),
                                'status': 'pending',
                                'message': f'خطا در اعمال: {str(e)}',
                                'manual_required': True
                            })
                    else:
                        # اگر credentials موجود نیست
                        results.append({
                            'recommendation_id': rec.get('id', ''),
                            'title': rec.get('title', ''),
                            'status': 'pending',
                            'message': 'این پیشنهاد نیاز به اعمال دستی دارد. لطفاً اطلاعات لاگین CMS را وارد کنید.',
                            'manual_required': True
                        })
                    
            except Exception as e:
                logger.error(f"Error applying fix for {rec.get('title')}: {str(e)}")
                results.append({
                    'recommendation_id': rec.get('id', ''),
                    'title': rec.get('title', ''),
                    'status': 'failed',
                    'message': f'خطا: {str(e)}'
                })
        
        # به‌روزرسانی داشبورد
        await dashboard_manager.update_dashboard(
            analysis_id,
            {
                'applied_fixes': results,
                'last_applied_at': datetime.now().isoformat()
            }
        )
        
        return {
            'message': f'{len([r for r in results if r.get("status") == "success"])} پیشنهاد با موفقیت اعمال شد',
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r.get('status') == 'success']),
            'failed': len([r for r in results if r.get('status') == 'failed']),
            'pending': len([r for r in results if r.get('status') == 'pending'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying fixes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for live monitoring
def _get_response_time_status(response_time):
    """تعیین وضعیت زمان پاسخ"""
    if not response_time:
        return 'unknown'
    if response_time < 1:
        return 'excellent'
    elif response_time < 2:
        return 'good'
    elif response_time < 3:
        return 'fair'
    else:
        return 'poor'


def _calculate_security_score(security):
    """محاسبه امتیاز امنیت"""
    score = 0
    if security.get('ssl_enabled'):
        score += 50
    security_headers = security.get('security_headers', {})
    header_count = sum(1 for v in security_headers.values() if v)
    score += header_count * 12.5
    return min(100, score)


def _calculate_time_since(timestamp_str):
    """محاسبه زمان از آخرین به‌روزرسانی"""
    if not timestamp_str:
        return 'unknown'
    try:
        last_update = datetime.fromisoformat(timestamp_str)
        delta = datetime.now() - last_update
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())} ثانیه پیش"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)} دقیقه پیش"
        else:
            return f"{int(delta.total_seconds() / 3600)} ساعت پیش"
    except:
        return 'unknown'


def _generate_alerts(dashboard_data, site_analysis, seo_analysis):
    """تولید هشدارها"""
    alerts = []
    current_time = datetime.now()
    
    # بررسی وضعیت
    status = dashboard_data.get('status', 'unknown')
    if status == 'failed':
        error_msg = dashboard_data.get('error') or dashboard_data.get('data', {}).get('error', 'خطای نامشخص')
        alerts.append({
            'type': 'error',
            'message': f'تحلیل با خطا مواجه شده است: {error_msg}',
            'priority': 'high',
            'timestamp': current_time.isoformat()
        })
    
    # بررسی اینکه آیا داده‌ها وجود دارند
    if not site_analysis and not seo_analysis:
        alerts.append({
            'type': 'warning',
            'message': 'داده‌های تحلیل هنوز آماده نشده است. لطفاً صبر کنید یا تحلیل جدیدی ایجاد کنید.',
            'priority': 'medium',
            'timestamp': current_time.isoformat()
        })
        return alerts  # اگر داده‌ای نیست، فقط این هشدار را برگردان
    
    # بررسی امنیت
    if site_analysis:
        security = site_analysis.get('security', {})
        if security and not security.get('ssl_enabled'):
            alerts.append({
                'type': 'warning',
                'message': 'HTTPS فعال نیست',
                'priority': 'high',
                'timestamp': current_time.isoformat()
            })
        
        # بررسی عملکرد
        performance = site_analysis.get('performance', {})
        if performance:
            response_time = performance.get('response_time')
            if response_time and response_time > 3:
                alerts.append({
                    'type': 'warning',
                    'message': f'زمان پاسخ سرور کند است ({response_time:.2f}s)',
                    'priority': 'medium',
                    'timestamp': current_time.isoformat()
                })
        
        # بررسی Sitemap
        sitemap = site_analysis.get('sitemap', {})
        if sitemap and not sitemap.get('found'):
            alerts.append({
                'type': 'info',
                'message': 'Sitemap یافت نشد',
                'priority': 'medium',
                'timestamp': current_time.isoformat()
            })
    
    return alerts


def _generate_response_time_history(performance):
    """تولید تاریخچه زمان پاسخ"""
    from datetime import timedelta
    response_time = performance.get('response_time')
    if not response_time:
        return []
    
    # در حالت واقعی، این داده‌ها از دیتابیس یا cache می‌آید
    return [
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'value': response_time * 0.9  # شبیه‌سازی
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'value': response_time * 0.95
        },
        {
            'timestamp': datetime.now().isoformat(),
            'value': response_time
        }
    ]


def _estimate_completion(dashboard_data):
    """تخمین زمان تکمیل"""
    from datetime import timedelta
    status = dashboard_data.get('status', 'unknown')
    if status == 'completed':
        return 'completed'
    elif status == 'processing':
        # تخمین بر اساس زمان گذشته
        created_at = datetime.fromisoformat(dashboard_data.get('created_at', datetime.now().isoformat()))
        elapsed = (datetime.now() - created_at).total_seconds()
        estimated_total = 900  # 15 دقیقه
        remaining = max(0, estimated_total - elapsed)
        return f"{int(remaining / 60)} دقیقه"
    else:
        return 'unknown'


@app.get("/dashboard/{analysis_id}/live-monitoring")
async def get_live_monitoring(analysis_id: str):
    """دریافت داده‌های مانیتورینگ بلادرنگ"""
    try:
        from core.dashboard_manager import DashboardManager
        from datetime import timedelta
        import time
        
        # دریافت داده‌های داشبورد
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        # استخراج داده‌ها - با fallback برای داده‌های خالی
        data_dict = dashboard_data.get('data', {})
        site_analysis = data_dict.get('site_analysis', {}) or {}
        seo_analysis = data_dict.get('seo_analysis', {}) or {}
        performance = site_analysis.get('performance', {}) or {}
        security = site_analysis.get('security', {}) or {}
        
        # استخراج پیام خطا اگر وجود دارد
        error_message = dashboard_data.get('error') or data_dict.get('error')
        
        # محاسبه تغییرات (مقایسه با زمان قبلی)
        current_time = datetime.now()
        created_at = datetime.fromisoformat(dashboard_data.get('created_at', current_time.isoformat()))
        time_since_creation = (current_time - created_at).total_seconds()
        
        # بررسی اینکه آیا داده‌های اولیه وجود دارد
        has_site_data = bool(site_analysis)
        has_seo_data = bool(seo_analysis)
        
        # مانیتورینگ زنده
        live_data = {
            'analysis_id': analysis_id,
            'site_url': dashboard_data.get('site_url', ''),
            'timestamp': current_time.isoformat(),
            'status': dashboard_data.get('status', 'unknown'),
            'uptime_seconds': int(time_since_creation),
            'error': error_message,
            'has_data': has_site_data or has_seo_data,
            
            # وضعیت فعلی
            'current_status': {
                'site_accessible': has_site_data,  # اگر داده‌ای وجود دارد، سایت قابل دسترسی است
                'ssl_status': security.get('ssl_enabled', False) if security else False,
                'response_time': performance.get('response_time') if performance else None,
                'status_code': performance.get('status_code') if performance else None,
                'last_check': current_time.isoformat()
            },
            
            # متریک‌های عملکرد
            'performance_metrics': {
                'response_time': performance.get('response_time') if performance else None,
                'response_time_status': _get_response_time_status(performance.get('response_time')) if performance else 'unknown',
                'content_length': performance.get('content_length') if performance else None,
                'status_code': performance.get('status_code') if performance else None,
                'server_time': time.time()
            },
            
            # متریک‌های امنیت
            'security_metrics': {
                'ssl_enabled': security.get('ssl_enabled', False) if security else False,
                'security_headers_count': sum(
                    1 for v in security.get('security_headers', {}).values() if v
                ) if security else 0,
                'vulnerabilities_count': len(security.get('vulnerabilities', [])) if security else 0,
                'security_score': _calculate_security_score(security) if security else 0
            },
            
            # متریک‌های سئو
            'seo_metrics': {
                'crawlability': seo_analysis.get('technical', {}).get('crawlability', 'unknown') if seo_analysis else 'unknown',
                'indexability': seo_analysis.get('technical', {}).get('indexability', 'unknown') if seo_analysis else 'unknown',
                'keywords_count': len(seo_analysis.get('content', {}).get('keywords', [])) if seo_analysis else 0,
                'readability_score': seo_analysis.get('content', {}).get('readability', 0) if seo_analysis else 0,
                'issues_count': len(seo_analysis.get('issues', [])) if seo_analysis else 0
            },
            
            # تغییرات اخیر
            'recent_changes': {
                'strengths_count': len(dashboard_data.get('strengths', [])),
                'weaknesses_count': len(dashboard_data.get('weaknesses', [])),
                'last_update': dashboard_data.get('updated_at', current_time.isoformat()),
                'time_since_update': _calculate_time_since(dashboard_data.get('updated_at'))
            },
            
            # هشدارها
            'alerts': _generate_alerts(dashboard_data, site_analysis, seo_analysis),
            
            # روند تغییرات (برای نمایش در نمودار)
            'trends': {
                'response_time_history': _generate_response_time_history(performance) if performance else [],
                'status_history': [
                    {
                        'timestamp': created_at.isoformat(),
                        'status': 'started'
                    },
                    {
                        'timestamp': dashboard_data.get('updated_at', current_time.isoformat()),
                        'status': dashboard_data.get('status', 'unknown')
                    }
                ]
            },
            
            # پیش‌بینی
            'predictions': {
                'estimated_completion': _estimate_completion(dashboard_data),
                'next_check_recommended': (current_time + timedelta(minutes=5)).isoformat()
            }
        }
        
        return live_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{analysis_id}/content/{content_id}/download")
async def download_content_file(analysis_id: str, content_id: str):
    """دانلود فایل محتوا"""
    try:
        from core.dashboard_manager import DashboardManager
        from fastapi.responses import FileResponse
        import os
        from pathlib import Path
        
        # دریافت داده‌های داشبورد
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        # پیدا کردن محتوا
        generated_content = dashboard_data.get('data', {}).get('generated_content', {})
        content_items = generated_content.get('content_items', [])
        
        content_item = None
        for item in content_items:
            if item.get('id') == content_id:
                content_item = item
                break
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path = content_item.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # تعیین نوع فایل
        file_type = content_item.get('file_type', 'txt')
        media_type_map = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'mp4': 'video/mp4',
            'txt': 'text/plain'
        }
        media_type = media_type_map.get(file_type, 'application/octet-stream')
        
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=os.path.basename(file_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading content file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{analysis_id}/rank")
async def get_site_rank(analysis_id: str):
    """دریافت رنک سایت (جهانی و ایران)"""
    try:
        from core.dashboard_manager import DashboardManager
        from core.rank_checker import RankChecker
        
        # دریافت داده‌های داشبورد
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        site_url = dashboard_data.get('site_url', '')
        if not site_url:
            raise HTTPException(status_code=400, detail="Site URL not found in dashboard")
        
        # دریافت رنک سایت
        rank_checker = RankChecker()
        try:
            rank_data = await rank_checker.get_comprehensive_rank(site_url)
            
            # ذخیره رنک در داشبورد
            await dashboard_manager.update_dashboard(
                analysis_id,
                {
                    'rank_data': rank_data
                }
            )
            
            return rank_data
        finally:
            await rank_checker.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site rank: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dashboard/{analysis_id}/generate-content-by-keywords")
async def generate_content_by_keywords(analysis_id: str, request_data: Dict):
    """تولید محتوا بر اساس کلمات کلیدی انتخاب شده از رقبا"""
    try:
        from core.dashboard_manager import DashboardManager
        from core.content_generator import ContentGenerator
        
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404,
                detail="Dashboard یافت نشد."
            )
        
        site_url = dashboard_data.get('site_url', '')
        keywords = request_data.get('keywords', [])
        content_types = request_data.get('content_types', ['text'])
        language = request_data.get('language', 'fa')
        
        if not keywords:
            raise HTTPException(status_code=400, detail="کلمات کلیدی انتخاب نشده است")
        
        # تولید محتوا بر اساس کلمات کلیدی
        generator = ContentGenerator()
        generated_content = await generator.generate_by_keywords(
            keywords,
            site_url,
            content_types,
            language
        )
        
        # ذخیره محتوای پیشنهادی
        await dashboard_manager.update_dashboard(
            analysis_id,
            {
                'suggested_content': generated_content,
                'suggested_content_keywords': keywords,
                'suggested_content_created_at': datetime.now().isoformat()
            }
        )
        
        return {
            'message': f'محتوای پیشنهادی برای {len(keywords)} کلمه کلیدی تولید شد',
            'content': generated_content,
            'keywords_used': keywords
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content by keywords: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dashboard/{analysis_id}/generate-content")
async def generate_additional_content(analysis_id: str, content_spec: Dict = None):
    """تولید محتوای اضافی یا تولید مجدد محتوا"""
    try:
        from core.dashboard_manager import DashboardManager
        from core.content_generator import ContentGenerator
        
        # دریافت داده‌های داشبورد
        dashboard_manager = DashboardManager()
        dashboard_data = await dashboard_manager.get_dashboard_data(analysis_id)
        
        if not dashboard_data:
            raise HTTPException(
                status_code=404, 
                detail="Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید."
            )
        
        # استخراج داده‌های تحلیل
        site_analysis = dashboard_data.get('data', {}).get('site_analysis', {})
        seo_analysis = dashboard_data.get('data', {}).get('seo_analysis', {})
        
        # اگر داده‌های تحلیل موجود نیست، از داده‌های خالی استفاده کن
        if not site_analysis:
            site_analysis = {'url': dashboard_data.get('site_url', '')}
        if not seo_analysis:
            seo_analysis = {}
        
        # تعیین انواع محتوا
        content_types = content_spec.get('content_types', ['text', 'image', 'video']) if content_spec else ['text', 'image', 'video']
        
        # تولید محتوا
        generator = ContentGenerator()
        generated_content = await generator.generate_all(
            site_analysis,
            seo_analysis,
            content_types
        )
        
        # به‌روزرسانی داشبورد
        await dashboard_manager.update_dashboard(
            analysis_id,
            {
                'generated_content': generated_content
            }
        )
        
        return {
            'message': 'محتوای تولید شده با موفقیت',
            'content': generated_content,
            'analysis_id': analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # Changed to 8002 to avoid conflict
        reload=True,
        log_level="info"
    )

