"""
Pipeline Manager - مدیریت یکپارچه Pipeline
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """وضعیت‌های Pipeline"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStep:
    """کلاس برای مدیریت هر Step در Pipeline"""
    
    def __init__(self, name: str, func, dependencies: List[str] = None):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.status = PipelineStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    async def execute(self, context: Dict[str, Any]) -> Any:
        """اجرای Step"""
        self.status = PipelineStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            logger.info(f"Executing step: {self.name}")
            self.result = await self.func(context)
            self.status = PipelineStatus.COMPLETED
            self.end_time = datetime.now()
            
            # اضافه کردن نتیجه به Context
            context[f"{self.name}_result"] = self.result
            
            logger.info(f"Step {self.name} completed successfully")
            return self.result
            
        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.error = str(e)
            self.end_time = datetime.now()
            logger.error(f"Step {self.name} failed: {str(e)}")
            raise
    
    def get_duration(self) -> float:
        """محاسبه مدت زمان اجرا"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class PipelineManager:
    """مدیریت Pipeline کامل"""
    
    def __init__(self):
        self.steps: List[PipelineStep] = []
        self.context: Dict[str, Any] = {}
        self.status = PipelineStatus.PENDING
    
    def add_step(self, step: PipelineStep):
        """اضافه کردن Step به Pipeline"""
        self.steps.append(step)
    
    async def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        اجرای کامل Pipeline
        
        Args:
            initial_context: Context اولیه
            
        Returns:
            نتایج Pipeline
        """
        self.context = initial_context or {}
        self.status = PipelineStatus.RUNNING
        
        results = {}
        
        try:
            # اجرای Steps به ترتیب
            for step in self.steps:
                # بررسی Dependencies
                if not self._check_dependencies(step):
                    raise ValueError(f"Dependencies not met for step: {step.name}")
                
                # اجرای Step
                result = await step.execute(self.context)
                results[step.name] = {
                    'status': step.status.value,
                    'result': result,
                    'duration': step.get_duration()
                }
            
            self.status = PipelineStatus.COMPLETED
            logger.info("Pipeline completed successfully")
            
            return {
                'status': 'completed',
                'results': results,
                'context': self.context
            }
            
        except Exception as e:
            self.status = PipelineStatus.FAILED
            logger.error(f"Pipeline failed: {str(e)}")
            
            return {
                'status': 'failed',
                'error': str(e),
                'results': results,
                'context': self.context
            }
    
    def _check_dependencies(self, step: PipelineStep) -> bool:
        """بررسی Dependencies یک Step"""
        for dep in step.dependencies:
            if f"{dep}_result" not in self.context:
                return False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """دریافت وضعیت Pipeline"""
        return {
            'status': self.status.value,
            'steps': [
                {
                    'name': step.name,
                    'status': step.status.value,
                    'duration': step.get_duration(),
                    'error': step.error
                }
                for step in self.steps
            ]
        }


async def create_full_pipeline(
    analysis_id: str,
    site_url: str,
    auto_implement: bool,
    content_types: List[str]
) -> PipelineManager:
    """
    ایجاد Pipeline کامل برای تحلیل و بهینه‌سازی سایت
    
    Args:
        analysis_id: شناسه تحلیل
        site_url: آدرس سایت
        auto_implement: آیا تغییرات خودکار اعمال شود؟
        content_types: انواع محتوای تولیدی
        
    Returns:
        PipelineManager آماده برای اجرا
    """
    from core.site_analyzer import SiteAnalyzer
    from core.seo_analyzer import SEOAnalyzer
    from core.content_generator import ContentGenerator
    from core.seo_implementation import AutoSEOImplementation
    from core.content_placement import ContentPlacementEngine
    from core.dashboard_manager import DashboardManager
    
    pipeline = PipelineManager()
    
    # Step 1: Site Analysis
    async def site_analysis_step(context: Dict[str, Any]) -> Dict[str, Any]:
        analyzer = SiteAnalyzer()
        result = await analyzer.analyze(site_url)
        await analyzer.close()
        return result
    
    pipeline.add_step(PipelineStep("site_analysis", site_analysis_step))
    
    # Step 2: SEO Analysis (وابسته به Site Analysis)
    async def seo_analysis_step(context: Dict[str, Any]) -> Dict[str, Any]:
        analyzer = SEOAnalyzer()
        try:
            result = await analyzer.deep_analysis(site_url)
            return result
        finally:
            await analyzer.close()
    
    pipeline.add_step(PipelineStep(
        "seo_analysis",
        seo_analysis_step,
        dependencies=["site_analysis"]
    ))
    
    # Step 3: Content Generation (وابسته به Site و SEO Analysis)
    if content_types:
        async def content_generation_step(context: Dict[str, Any]) -> Dict[str, Any]:
            generator = ContentGenerator()
            site_analysis = context.get("site_analysis_result")
            seo_analysis = context.get("seo_analysis_result")
            result = await generator.generate_all(
                site_analysis,
                seo_analysis,
                content_types
            )
            return result
        
        pipeline.add_step(PipelineStep(
            "content_generation",
            content_generation_step,
            dependencies=["site_analysis", "seo_analysis"]
        ))
    
    # Step 4: SEO Implementation (وابسته به SEO Analysis)
    if auto_implement:
        async def seo_implementation_step(context: Dict[str, Any]) -> Dict[str, Any]:
            implementor = AutoSEOImplementation(site_url)
            seo_analysis = context.get("seo_analysis_result")
            issues = seo_analysis.get('issues', []) if seo_analysis else []
            result = await implementor.implement_all(issues)
            return result
        
        pipeline.add_step(PipelineStep(
            "seo_implementation",
            seo_implementation_step,
            dependencies=["seo_analysis"]
        ))
    
    # Step 5: Content Placement
    async def content_placement_step(context: Dict[str, Any]) -> Dict[str, Any]:
        engine = ContentPlacementEngine()
        site_analysis = context.get("site_analysis_result", {})
        generated_content = context.get("content_generation_result") if content_types else None
        seo_implementation = context.get("seo_implementation_result") if auto_implement else None
        
        result = await engine.place_and_publish(
            generated_content,
            seo_implementation,
            site_analysis.get('structure', {})
        )
        return result
    
    dependencies = ["site_analysis"]
    if content_types:
        dependencies.append("content_generation")
    if auto_implement:
        dependencies.append("seo_implementation")
    
    pipeline.add_step(PipelineStep(
        "content_placement",
        content_placement_step,
        dependencies=dependencies
    ))
    
    # Step 6: Dashboard Update
    async def dashboard_update_step(context: Dict[str, Any]) -> Dict[str, Any]:
        manager = DashboardManager()
        await manager.update_dashboard(
            analysis_id,
            {
                'site_analysis': context.get("site_analysis_result"),
                'seo_analysis': context.get("seo_analysis_result"),
                'generated_content': context.get("content_generation_result"),
                'implementation': context.get("seo_implementation_result"),
                'placement': context.get("content_placement_result"),
                'status': 'completed'
            }
        )
        return {'updated': True}
    
    pipeline.add_step(PipelineStep(
        "dashboard_update",
        dashboard_update_step,
        dependencies=["content_placement"]
    ))
    
    # تنظیم Context اولیه
    pipeline.context = {
        'analysis_id': analysis_id,
        'site_url': site_url,
        'auto_implement': auto_implement,
        'content_types': content_types
    }
    
    return pipeline

