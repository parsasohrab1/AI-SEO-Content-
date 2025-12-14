"""
Database Models با SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class SiteAnalysis(Base):
    """مدل تحلیل سایت"""
    __tablename__ = "site_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True)
    site_url = Column(String, nullable=False)
    cms_type = Column(String)
    technology_stack = Column(JSON)
    structure = Column(JSON)
    performance = Column(JSON)
    security = Column(JSON)
    sitemap = Column(JSON)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seo_analyses = relationship("SEOAnalysis", back_populates="site_analysis")
    content_items = relationship("ContentItem", back_populates="site_analysis")
    seo_implementations = relationship("SEOImplementation", back_populates="site_analysis")


class SEOAnalysis(Base):
    """مدل تحلیل سئو"""
    __tablename__ = "seo_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("site_analyses.analysis_id"), index=True)
    technical_seo = Column(JSON)
    content_seo = Column(JSON)
    external_seo = Column(JSON)
    competitor_analysis = Column(JSON)
    issues = Column(JSON)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    site_analysis = relationship("SiteAnalysis", back_populates="seo_analyses")


class ContentItem(Base):
    """مدل محتوای تولید شده"""
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("site_analyses.analysis_id"), index=True)
    content_type = Column(String)  # text, image, video, infographic
    title = Column(String)
    content = Column(Text)
    metadata = Column(JSON)
    status = Column(String, default="generated")  # generated, placed, published
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    site_analysis = relationship("SiteAnalysis", back_populates="content_items")


class SEOImplementation(Base):
    """مدل پیاده‌سازی سئو"""
    __tablename__ = "seo_implementations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("site_analyses.analysis_id"), index=True)
    change_type = Column(String)  # meta_tags, image_optimization, etc.
    changes_applied = Column(JSON)
    rollback_data = Column(JSON)
    status = Column(String, default="pending")  # pending, applied, failed, rolled_back
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    site_analysis = relationship("SiteAnalysis", back_populates="seo_implementations")


class Dashboard(Base):
    """مدل Dashboard"""
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True)
    site_url = Column(String)
    summary = Column(JSON)
    charts_data = Column(JSON)
    alerts = Column(JSON)
    recent_activities = Column(JSON)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

