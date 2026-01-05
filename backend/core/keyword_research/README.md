# ماژول تحقیق کلمات کلیدی

این ماژول شامل یکپارچه‌سازی با Google Keyword Planner و ابزارهای تحقیق کلمات کلیدی است.

## 📋 ویژگی‌ها

- ✅ دریافت ایده‌های کلمات کلیدی از Google Autocomplete
- ✅ دریافت جستجوهای مرتبط (Related Searches)
- ✅ تخمین حجم جستجو (Search Volume)
- ✅ تخمین سطح رقابت (Competition)
- ✅ محاسبه Keyword Difficulty
- ✅ محاسبه Opportunity Score
- ✅ یکپارچه‌سازی با Google Trends (اختیاری)
- ✅ پشتیبانی از Google Ads API (رسمی - نیاز به API Key)

## 🚀 نصب

### وابستگی‌های اصلی (موجود در requirements.txt):
```bash
pip install httpx beautifulsoup4
```

### وابستگی‌های اختیاری:

#### Google Trends (برای تحلیل روند):
```bash
pip install pytrends
```

#### Google Ads API (برای داده‌های دقیق):
```bash
pip install google-ads
```

## 📖 استفاده

### مثال 1: دریافت ایده‌های کلمات کلیدی

```python
from backend.core.keyword_research import GoogleKeywordPlanner

planner = GoogleKeywordPlanner()

# دریافت ایده‌های کلمات کلیدی
keywords = await planner.get_keyword_ideas(
    seed_keyword="بهینه‌سازی سئو",
    language='fa',
    country='ir',
    max_results=50
)

for kw in keywords:
    print(f"{kw['keyword']} - منبع: {kw.get('source')}")
```

### مثال 2: دریافت معیارهای کلمات کلیدی

```python
keywords_to_analyze = ["سئو", "بهینه‌سازی سایت", "آموزش سئو"]

metrics = await planner.get_keyword_metrics(
    keywords=keywords_to_analyze,
    language='fa',
    country='ir'
)

for keyword, data in metrics.items():
    print(f"\nکلمه کلیدی: {keyword}")
    print(f"  حجم جستجو: {data.get('search_volume')}")
    print(f"  رقابت: {data.get('competition')}")
    print(f"  سختی: {data.get('difficulty')}/100")
    print(f"  امتیاز فرصت: {data.get('opportunity_score')}/100")
```

### مثال 3: استفاده از Google Trends

```python
from backend.core.keyword_research import GoogleTrendsIntegration

trends = GoogleTrendsIntegration()

trend_data = await trends.get_trend_data(
    keyword="سئو",
    timeframe='12m'  # 12 ماه گذشته
)

print(f"حجم متوسط: {trend_data['average_volume']}")
print(f"نرخ رشد: {trend_data['growth_rate']}%")
print(f"ماه پیک: {trend_data['peak_month']}")
```

## ⚙️ تنظیمات

### Environment Variables (اختیاری):

برای استفاده از Google Ads API (داده‌های دقیق‌تر):

```env
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
```

**نکته:** اگر این متغیرها تنظیم نشوند، سیستم به صورت خودکار از روش‌های رایگان استفاده می‌کند.

## 🔧 روش‌های استفاده شده

### روش‌های رایگان (پیش‌فرض):
1. **Google Autocomplete**: دریافت پیشنهادات از Google Autocomplete
2. **Related Searches**: استخراج جستجوهای مرتبط از صفحه نتایج
3. **People Also Ask**: استخراج سوالات مرتبط
4. **تخمین معیارها**: بر اساس تعداد نتایج جستجو

### روش‌های پولی (اختیاری):
1. **Google Ads API**: داده‌های دقیق حجم جستجو، CPC، و رقابت
2. **Google Trends API**: تحلیل روند جستجو

## 📊 معیارهای بازگشتی

### get_keyword_ideas():
```python
{
    'keyword': str,           # کلمه کلیدی
    'source': str,            # منبع (autocomplete, related_searches, etc.)
    'search_volume': int,     # حجم جستجو (اگر موجود باشد)
    'competition': str,        # سطح رقابت (اگر موجود باشد)
    'cpc': float             # هزینه هر کلیک (اگر موجود باشد)
}
```

### get_keyword_metrics():
```python
{
    'search_volume': int,         # حجم جستجو (تخمینی)
    'competition': str,            # Low, Medium, High
    'cpc': float,                  # هزینه هر کلیک (تخمینی)
    'trend': List[int],            # روند جستجو (12 ماه)
    'difficulty': int,             # 0-100
    'opportunity_score': float,    # 0-100
    'total_results': int,          # تعداد کل نتایج
    'source': str                   # 'estimated' یا 'google_ads_api'
}
```

## 🎯 Opportunity Score

امتیاز فرصت (Opportunity Score) ترکیبی از:
- حجم جستجو (هرچه بیشتر بهتر)
- سختی کلمه کلیدی (هرچه کمتر بهتر)
- سطح رقابت (هرچه کمتر بهتر)

فرمول: `(Volume × (100 - Difficulty)) / 100`

## ⚠️ محدودیت‌ها

1. **روش‌های رایگان**: داده‌ها تخمینی هستند و ممکن است دقیق نباشند
2. **Rate Limiting**: Google ممکن است درخواست‌های زیاد را محدود کند
3. **Google Ads API**: نیاز به حساب Google Ads و OAuth2 دارد

## 🔍 مثال کامل

```python
import asyncio
from backend.core.keyword_research import GoogleKeywordPlanner

async def main():
    planner = GoogleKeywordPlanner()
    
    # 1. دریافت ایده‌های کلمات کلیدی
    ideas = await planner.get_keyword_ideas(
        seed_keyword="سئو",
        language='fa',
        max_results=30
    )
    
    # 2. انتخاب 10 کلمه کلیدی برتر
    top_keywords = [kw['keyword'] for kw in ideas[:10]]
    
    # 3. دریافت معیارهای دقیق
    metrics = await planner.get_keyword_metrics(
        keywords=top_keywords,
        language='fa'
    )
    
    # 4. مرتب‌سازی بر اساس Opportunity Score
    sorted_keywords = sorted(
        metrics.items(),
        key=lambda x: x[1].get('opportunity_score', 0),
        reverse=True
    )
    
    # 5. نمایش نتایج
    print("🎯 کلمات کلیدی برتر:\n")
    for i, (keyword, data) in enumerate(sorted_keywords[:5], 1):
        print(f"{i}. {keyword}")
        print(f"   حجم: {data.get('search_volume')}")
        print(f"   سختی: {data.get('difficulty')}/100")
        print(f"   فرصت: {data.get('opportunity_score')}/100\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 نکات مهم

1. **استفاده مسئولانه**: از Rate Limiting استفاده کنید تا IP شما بلاک نشود
2. **کش کردن نتایج**: نتایج را cache کنید تا درخواست‌های تکراری کاهش یابد
3. **Error Handling**: همیشه try-except استفاده کنید
4. **User-Agent**: از User-Agent معتبر استفاده می‌شود

## 🐛 عیب‌یابی

### مشکل: نتایج خالی برمی‌گردد
- بررسی کنید که اینترنت متصل است
- بررسی کنید که Google در دسترس است
- User-Agent را بررسی کنید

### مشکل: Rate Limiting
- بین درخواست‌ها delay اضافه کنید
- از cache استفاده کنید
- تعداد درخواست‌ها را کاهش دهید

## 📚 منابع

- [Google Keyword Planner](https://ads.google.com/aw/keywordplanner)
- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [pytrends Documentation](https://github.com/GeneralMills/pytrends)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

