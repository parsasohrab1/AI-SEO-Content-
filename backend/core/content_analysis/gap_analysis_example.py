"""
مثال استفاده از Content Gap Analyzer
"""

import asyncio
import logging
from .content_gap_analyzer import ContentGapAnalyzer

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_analysis():
    """مثال: تحلیل ساده Content Gap"""
    
    analyzer = ContentGapAnalyzer()
    
    # محتوای سایت شما
    site_content = {
        'articles': [
            {
                'title': 'SEO Optimization Guide',
                'content': 'Basic SEO optimization tips...',
                'topics': ['seo', 'optimization'],
                'word_count': 1200,
                'headings': ['Introduction', 'Basic Tips'],
                'content_type': 'article'
            }
        ],
        'topics': ['seo', 'optimization'],
        'content_types': ['article']
    }
    
    # محتوای رقبا
    competitor_content = [
        {
            'title': 'Complete SEO Guide 2024',
            'content': 'Comprehensive SEO guide with advanced techniques...',
            'topics': ['seo', 'advanced seo', 'technical seo'],
            'word_count': 2500,
            'headings': ['Introduction', 'Advanced Techniques', 'Technical SEO', 'FAQ'],
            'content_type': 'article',
            'has_faq': True
        },
        {
            'title': 'SEO Video Tutorial',
            'content': 'Video content about SEO...',
            'topics': ['seo', 'tutorial'],
            'word_count': 500,
            'content_type': 'video'
        },
        {
            'title': 'How to Optimize SEO',
            'content': 'Step by step guide...',
            'topics': ['seo', 'how to'],
            'word_count': 1800,
            'content_type': 'article'
        }
    ]
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content,
        language='en'
    )
    
    print(f"\n✅ نتایج تحلیل Content Gap:\n")
    
    # خلاصه
    summary = result.get('summary', {})
    print("📊 خلاصه:")
    print(f"  Topic Gaps: {summary.get('total_topic_gaps', 0)}")
    print(f"  High Importance Topics: {summary.get('high_importance_topics', 0)}")
    print(f"  Angle Gaps: {summary.get('total_angle_gaps', 0)}")
    print(f"  Depth Gaps: {summary.get('total_depth_gaps', 0)}")
    print(f"  Content Type Gaps: {summary.get('total_content_type_gaps', 0)}")
    print(f"  Overall Gap Score: {summary.get('overall_gap_score', 0):.1f}/100")
    
    # Topic Gaps
    topic_gaps = result.get('topic_gaps', [])
    if topic_gaps:
        print(f"\n🎯 Topic Gaps ({len(topic_gaps)}):")
        for i, gap in enumerate(topic_gaps[:5], 1):
            print(f"  {i}. {gap['topic']}")
            print(f"     Importance: {gap['importance']:.1f}/100")
            print(f"     Competitor Count: {gap['competitor_count']}")


async def example_angle_analysis():
    """مثال: تحلیل زوایا"""
    
    analyzer = ContentGapAnalyzer()
    
    site_content = {
        'articles': [
            {
                'title': 'What is SEO?',
                'content': 'SEO definition...',
                'content_type': 'article'
            }
        ],
        'content_types': ['article']
    }
    
    competitor_content = [
        {
            'title': 'How to Do SEO',
            'content': 'Step by step guide...',
            'content_type': 'article'
        },
        {
            'title': 'Best SEO Tools',
            'content': 'List of best tools...',
            'content_type': 'article'
        },
        {
            'title': 'SEO vs SEM Comparison',
            'content': 'Comparison between SEO and SEM...',
            'content_type': 'article'
        }
    ]
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content,
        language='en'
    )
    
    angle_gaps = result.get('angle_gaps', [])
    if angle_gaps:
        print(f"\n🎯 Angle Gaps ({len(angle_gaps)}):")
        for gap in angle_gaps[:5]:
            print(f"  • {gap['angle']} ({gap['competitor_count']} محتوا)")


async def example_depth_analysis():
    """مثال: تحلیل عمق"""
    
    analyzer = ContentGapAnalyzer()
    
    site_content = {
        'articles': [
            {
                'title': 'SEO Guide',
                'content': 'Basic SEO tips...',
                'word_count': 800,
                'headings': ['Introduction'],
                'content_type': 'article'
            }
        ]
    }
    
    competitor_content = [
        {
            'title': 'Complete SEO Guide',
            'content': 'Comprehensive guide with detailed sections...',
            'word_count': 3000,
            'headings': ['Introduction', 'Basics', 'Advanced', 'Tools', 'FAQ'],
            'has_faq': True,
            'has_images': True,
            'content_type': 'article'
        }
    ]
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content,
        language='en'
    )
    
    depth_gaps = result.get('depth_gaps', [])
    if depth_gaps:
        print(f"\n📊 Depth Gaps:")
        for gap in depth_gaps:
            if gap.get('gap_type') == 'depth':
                print(f"  Your Average Depth: {gap.get('your_average_depth', 0):.1f}")
                print(f"  Competitor Average Depth: {gap.get('competitor_average_depth', 0):.1f}")
                print(f"  Difference: {gap.get('difference', 0):.1f}")


async def example_content_type_analysis():
    """مثال: تحلیل انواع محتوا"""
    
    analyzer = ContentGapAnalyzer()
    
    site_content = {
        'articles': [
            {'title': 'Article 1', 'content_type': 'article'}
        ],
        'content_types': ['article']
    }
    
    competitor_content = [
        {'title': 'Video 1', 'content_type': 'video'},
        {'title': 'Infographic 1', 'content_type': 'infographic'},
        {'title': 'Article 1', 'content_type': 'article'},
        {'title': 'Video 2', 'content_type': 'video'}
    ]
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content,
        language='en'
    )
    
    content_type_gaps = result.get('content_type_gaps', [])
    if content_type_gaps:
        print(f"\n🎨 Content Type Gaps ({len(content_type_gaps)}):")
        for gap in content_type_gaps:
            print(f"  • {gap['content_type']}")
            print(f"    Your Count: {gap.get('your_count', 0)}")
            print(f"    Competitor Count: {gap.get('competitor_count', 0)}")


async def example_complete_workflow():
    """مثال: workflow کامل"""
    
    analyzer = ContentGapAnalyzer()
    
    # محتوای سایت شما
    site_content = {
        'articles': [
            {
                'title': 'SEO Basics',
                'content': 'Introduction to SEO...',
                'topics': ['seo', 'basics'],
                'word_count': 1000,
                'headings': ['Introduction', 'What is SEO'],
                'content_type': 'article'
            }
        ],
        'topics': ['seo', 'basics'],
        'content_types': ['article']
    }
    
    # محتوای رقبا
    competitor_content = [
        {
            'title': 'Complete SEO Guide 2024',
            'content': 'Comprehensive SEO guide...',
            'topics': ['seo', 'advanced seo', 'technical seo', 'on-page seo'],
            'word_count': 3000,
            'headings': ['Introduction', 'Basics', 'Advanced', 'Technical', 'FAQ'],
            'has_faq': True,
            'has_images': True,
            'content_type': 'article'
        },
        {
            'title': 'How to Optimize SEO',
            'content': 'Step by step guide...',
            'topics': ['seo', 'optimization', 'how to'],
            'word_count': 2000,
            'content_type': 'article'
        },
        {
            'title': 'Best SEO Tools',
            'content': 'List of best tools...',
            'topics': ['seo', 'tools', 'best'],
            'word_count': 1500,
            'content_type': 'article'
        },
        {
            'title': 'SEO Video Tutorial',
            'content': 'Video content...',
            'topics': ['seo', 'tutorial'],
            'content_type': 'video'
        }
    ]
    
    print(f"🔍 تحلیل Content Gap...\n")
    
    result = await analyzer.analyze_content_gaps(
        site_content=site_content,
        competitor_content=competitor_content,
        language='en'
    )
    
    print("=" * 60)
    print("📊 نتایج تحلیل")
    print("=" * 60)
    
    summary = result.get('summary', {})
    print(f"\n📈 خلاصه:")
    print(f"  Topic Gaps: {summary.get('total_topic_gaps', 0)}")
    print(f"  High Importance: {summary.get('high_importance_topics', 0)}")
    print(f"  Angle Gaps: {summary.get('total_angle_gaps', 0)}")
    print(f"  Depth Gaps: {summary.get('total_depth_gaps', 0)}")
    print(f"  Content Type Gaps: {summary.get('total_content_type_gaps', 0)}")
    print(f"  Overall Gap Score: {summary.get('overall_gap_score', 0):.1f}/100")
    
    # Topic Gaps
    topic_gaps = result.get('topic_gaps', [])
    if topic_gaps:
        print("\n" + "=" * 60)
        print("🎯 Topic Gaps (موضوعات موجود در رقبا اما نه در شما)")
        print("=" * 60)
        print(f"\n{len(topic_gaps)} موضوع شناسایی شد\n")
        
        high_importance = [g for g in topic_gaps if g.get('importance', 0) >= 70]
        if high_importance:
            print("🔥 موضوعات با اهمیت بالا:\n")
            for i, gap in enumerate(high_importance[:10], 1):
                print(f"{i}. {gap['topic']}")
                print(f"   Importance: {gap['importance']:.1f}/100")
                print(f"   Competitor Count: {gap['competitor_count']}")
                print()
    
    # Angle Gaps
    angle_gaps = result.get('angle_gaps', [])
    if angle_gaps:
        print("=" * 60)
        print("🎯 Angle Gaps (زوایای مختلف)")
        print("=" * 60)
        print(f"\n{len(angle_gaps)} زاویه شناسایی شد\n")
        for gap in angle_gaps[:10]:
            print(f"  • {gap['angle']} ({gap['competitor_count']} محتوا)")
    
    # Depth Gaps
    depth_gaps = result.get('depth_gaps', [])
    if depth_gaps:
        print("\n" + "=" * 60)
        print("📊 Depth Gaps (تفاوت عمق)")
        print("=" * 60)
        for gap in depth_gaps:
            if gap.get('gap_type') == 'depth':
                print(f"\n  Your Average: {gap.get('your_average_depth', 0):.1f}")
                print(f"  Competitor Average: {gap.get('competitor_average_depth', 0):.1f}")
                print(f"  Difference: {gap.get('difference', 0):.1f}")
    
    # Content Type Gaps
    content_type_gaps = result.get('content_type_gaps', [])
    if content_type_gaps:
        print("\n" + "=" * 60)
        print("🎨 Content Type Gaps")
        print("=" * 60)
        for gap in content_type_gaps:
            print(f"\n  Type: {gap['content_type']}")
            print(f"  Your Count: {gap.get('your_count', 0)}")
            print(f"  Competitor Count: {gap.get('competitor_count', 0)}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print("\n" + "=" * 60)
        print("💡 پیشنهادات")
        print("=" * 60)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")


if __name__ == "__main__":
    print("=" * 60)
    print("مثال استفاده از Content Gap Analyzer")
    print("=" * 60)
    
    # اجرای مثال‌ها
    # asyncio.run(example_basic_analysis())
    # asyncio.run(example_angle_analysis())
    # asyncio.run(example_depth_analysis())
    # asyncio.run(example_content_type_analysis())
    asyncio.run(example_complete_workflow())

