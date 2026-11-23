"""
مثال استفاده از Content Quality Scorer
"""

import asyncio
import logging
from .content_quality_scorer import ContentQualityScorer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_scoring():
    """مثال: امتیازدهی ساده"""
    
    scorer = ContentQualityScorer()
    
    content = """
# SEO Optimization Guide

This is a comprehensive guide to SEO optimization. SEO optimization is crucial for improving your website's visibility.

## What is SEO?

SEO stands for Search Engine Optimization. It helps your website rank higher in search results.

## How to Optimize SEO

1. Use relevant keywords
2. Create quality content
3. Build backlinks
4. Optimize images

## FAQ

### What is SEO?
SEO is the process of optimizing your website for search engines.

### How long does SEO take?
SEO typically takes 3-6 months to show results.
"""
    
    keyword = "seo optimization"
    
    result = scorer.score_content(
        content=content,
        keyword=keyword,
        title="SEO Optimization Guide",
        meta_description="Complete guide to SEO optimization with tips and best practices",
        language='en'
    )
    
    print(f"\n✅ نتایج امتیازدهی:\n")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Readability: {result['readability_score']}/100")
    print(f"Keyword Optimization: {result['keyword_optimization']}/100")
    print(f"Content Depth: {result['content_depth']}/100")
    print(f"Uniqueness: {result['uniqueness']}/100")
    print(f"Engagement Potential: {result['engagement_potential']}/100")
    
    # نمایش Breakdown
    breakdown = result.get('breakdown', {})
    print(f"\n📊 Breakdown:")
    print(f"  Word Count: {breakdown.get('word_count', 0)}")
    print(f"  Heading Count: {breakdown.get('heading_count', 0)}")
    print(f"  Has Title: {breakdown.get('has_title', False)}")
    print(f"  Has Meta Description: {breakdown.get('has_meta_description', False)}")
    print(f"  Has H1: {breakdown.get('has_h1', False)}")
    print(f"  Has FAQ: {breakdown.get('has_faq', False)}")
    
    # نمایش توصیه‌ها
    if result.get('recommendations'):
        print(f"\n💡 توصیه‌ها:")
        for rec in result['recommendations']:
            print(f"  • {rec}")


def example_with_metrics():
    """مثال: امتیازدهی با معیارهای کلمه کلیدی"""
    
    scorer = ContentQualityScorer()
    
    content = """
# Complete SEO Guide 2024

SEO optimization is essential for any website. In this comprehensive guide, we'll cover everything you need to know about SEO optimization.

## Introduction to SEO

Search Engine Optimization (SEO) is the practice of improving your website's visibility in search engine results.

## Advanced SEO Techniques

### On-Page SEO
On-page SEO involves optimizing individual pages of your website.

### Off-Page SEO
Off-page SEO focuses on building authority through backlinks.

## FAQ

### What is SEO optimization?
SEO optimization is the process of improving your website for search engines.

### How to do SEO optimization?
Follow these steps: keyword research, content creation, link building.
"""
    
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65,
        'competition': 'high'
    }
    
    result = scorer.score_content(
        content=content,
        keyword="seo optimization",
        keyword_metrics=keyword_metrics,
        title="Complete SEO Guide 2024",
        meta_description="Learn everything about SEO optimization with this comprehensive guide",
        language='en'
    )
    
    print(f"\n✅ نتایج با معیارها:\n")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Keyword Optimization: {result['keyword_optimization']}/100")


def example_persian_content():
    """مثال: امتیازدهی محتوای فارسی"""
    
    scorer = ContentQualityScorer()
    
    content = """
# راهنمای کامل بهینه‌سازی سئو

بهینه‌سازی سئو برای هر وب‌سایتی ضروری است. در این راهنمای جامع، تمام نکات مهم بهینه‌سازی سئو را پوشش می‌دهیم.

## مقدمه

سئو یا بهینه‌سازی موتور جستجو، فرآیند بهبود رتبه‌بندی وب‌سایت در نتایج جستجو است.

## Important Notes

1. استفاده از کلمات کلیدی مرتبط
2. تولید محتوای با کیفیت
3. ساخت بک‌لینک
4. بهینه‌سازی تصاویر

## سوالات متداول

### بهینه‌سازی سئو چیست؟
بهینه‌سازی سئو فرآیند بهبود وب‌سایت برای موتورهای جستجو است.
"""
    
    result = scorer.score_content(
        content=content,
        keyword="بهینه‌سازی سئو",
        title="راهنمای کامل بهینه‌سازی سئو",
        meta_description="یادگیری تمام نکات بهینه‌سازی سئو با این راهنمای جامع",
        language='fa'
    )
    
    print(f"\n✅ نتایج برای محتوای فارسی:\n")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Readability: {result['readability_score']}/100")


def example_complete_workflow():
    """مثال: workflow کامل"""
    
    scorer = ContentQualityScorer()
    
    content = """
# Complete SEO Optimization Guide 2024

SEO optimization is crucial for improving your website's visibility in search engines. This comprehensive guide covers everything you need to know about SEO optimization.

## What is SEO Optimization?

SEO optimization is the process of improving your website's visibility in search engine results pages (SERPs). It involves various techniques and strategies.

## How to Optimize SEO

### 1. Keyword Research
Start with thorough keyword research to identify relevant keywords.

### 2. On-Page SEO
Optimize individual pages with relevant keywords and quality content.

### 3. Technical SEO
Ensure your website is technically sound with fast loading times.

### 4. Link Building
Build high-quality backlinks from authoritative websites.

## Best Practices

- Use keywords naturally
- Create quality content
- Optimize images
- Improve page speed

## FAQ

### What is SEO optimization?
SEO optimization is the process of improving your website for search engines.

### How long does SEO take?
SEO typically takes 3-6 months to show significant results.

### What are the best SEO tools?
Some popular SEO tools include Ahrefs, SEMrush, and Google Search Console.
"""
    
    keyword = "seo optimization"
    keyword_metrics = {
        'search_volume': 12000,
        'difficulty': 65,
        'competition': 'high'
    }
    
    print(f"🔍 امتیازدهی محتوا برای '{keyword}'\n")
    
    result = scorer.score_content(
        content=content,
        keyword=keyword,
        keyword_metrics=keyword_metrics,
        title="Complete SEO Optimization Guide 2024",
        meta_description="Learn everything about SEO optimization with this comprehensive guide covering all aspects",
        language='en'
    )
    
    print("=" * 60)
    print("📊 نتایج امتیازدهی")
    print("=" * 60)
    
    print(f"\n⭐ Overall Score: {result['overall_score']}/100")
    
    print(f"\n📈 معیارهای جزئی:")
    print(f"  SEO Score: {result['seo_score']}/100")
    print(f"  Readability: {result['readability_score']}/100")
    print(f"  Keyword Optimization: {result['keyword_optimization']}/100")
    print(f"  Content Depth: {result['content_depth']}/100")
    print(f"  Uniqueness: {result['uniqueness']}/100")
    print(f"  Engagement Potential: {result['engagement_potential']}/100")
    
    # Breakdown
    breakdown = result.get('breakdown', {})
    print(f"\n📋 Breakdown:")
    print(f"  Word Count: {breakdown.get('word_count', 0)}")
    print(f"  Heading Count: {breakdown.get('heading_count', 0)}")
    print(f"  Paragraph Count: {breakdown.get('paragraph_count', 0)}")
    print(f"  Image Count: {breakdown.get('image_count', 0)}")
    print(f"  Link Count: {breakdown.get('link_count', 0)}")
    print(f"  Has Title: {breakdown.get('has_title', False)}")
    print(f"  Has Meta Description: {breakdown.get('has_meta_description', False)}")
    print(f"  Has H1: {breakdown.get('has_h1', False)}")
    print(f"  Has FAQ: {breakdown.get('has_faq', False)}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 توصیه‌ها:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print(f"\n✅ هیچ توصیه‌ای وجود ندارد. محتوا عالی است!")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Content Quality Scorer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # example_basic_scoring()
    # example_with_metrics()
    # example_persian_content()
    example_complete_workflow()

