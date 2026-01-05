# راهنمای Local AI Content Generator

## 📋 معرفی

این ماژول تولید محتوا با استفاده از مدل‌های Open Source (Llama 2, Mistral و غیره) را انجام می‌دهد. این یک جایگزین رایگان برای OpenAI API است که می‌تواند به صورت محلی اجرا شود.

## ✨ ویژگی‌ها

- ✅ استفاده از مدل‌های Open Source (Mistral, Llama 2, GPT-2)
- ✅ اجرای محلی (بدون نیاز به API)
- ✅ کاهش هزینه (رایگان)
- ✅ پشتیبانی از CPU و GPU
- ✅ پشتیبانی از 8-bit و 4-bit quantization
- ✅ تولید محتوای بهینه برای SEO
- ✅ پشتیبانی از فارسی و انگلیسی

## 🚀 نصب

### وابستگی‌های مورد نیاز

```bash
# پایه
pip install transformers torch

# برای GPU (اختیاری)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# برای quantization (اختیاری)
pip install bitsandbytes accelerate
```

### تنظیمات

```bash
# در فایل .env
LOCAL_AI_MODEL=mistralai/Mistral-7B-Instruct-v0.2  # یا llama2, gpt2
LOCAL_AI_DEVICE=auto  # auto, cpu, cuda
LOCAL_AI_8BIT=false  # استفاده از 8-bit quantization
LOCAL_AI_4BIT=false  # استفاده از 4-bit quantization
```

## 📖 استفاده

### مثال 1: تولید ساده

```python
from backend.core.content_generator import LocalAIContentGenerator

generator = LocalAIContentGenerator()

result = await generator.generate_article(
    keyword="seo optimization",
    target_length=1500,
    language='en'
)

print(f"Title: {result['title']}")
print(f"Content: {result['content']}")
print(f"SEO Score: {result['seo_score']}/100")
```

### مثال 2: استفاده از مدل خاص

```python
# استفاده از مدل کوچک‌تر برای تست
generator = LocalAIContentGenerator(model_name="gpt2")

result = await generator.generate_article(
    keyword="seo",
    target_length=1000,
    language='en'
)
```

### مثال 3: استفاده با GPU

```python
# تنظیم device به cuda
generator = LocalAIContentGenerator()
# به صورت خودکار GPU را تشخیص می‌دهد
```

## 📊 ساختار داده‌های بازگشتی

```python
{
    'content': str,
    'title': str,
    'meta_description': str,
    'seo_score': float,
    'keyword_density': float,
    'readability': float,
    'word_count': int,
    'headings': List[str],
    'faq': List[Dict],
    'recommendations': List[str],
    'keyword': str,
    'language': str,
    'model': str  # نام مدل استفاده شده
}
```

## 🎯 مدل‌های پشتیبانی شده

### 1. Mistral
- `mistralai/Mistral-7B-Instruct-v0.2` (پیش‌فرض)
- کیفیت بالا
- نیاز به RAM: ~14 GB

### 2. Llama 2
- `meta-llama/Llama-2-7b-chat-hf`
- کیفیت بالا
- نیاز به RAM: ~14 GB

### 3. GPT-2
- `gpt2` (برای تست)
- کیفیت متوسط
- نیاز به RAM: ~2 GB

### 4. سایر مدل‌ها
- هر مدل Hugging Face که از `text-generation` pipeline پشتیبانی کند

## 🔧 تنظیمات پیشرفته

### استفاده از Quantization

```bash
# 8-bit quantization (کاهش استفاده از RAM)
LOCAL_AI_8BIT=true

# 4-bit quantization (کاهش بیشتر)
LOCAL_AI_4BIT=true
```

### انتخاب Device

```python
# CPU
generator = LocalAIContentGenerator()
# device به صورت خودکار CPU انتخاب می‌شود

# GPU (اگر موجود باشد)
# به صورت خودکار GPU را تشخیص می‌دهد
```

## 📝 مثال کامل

```python
import asyncio
from backend.core.content_generator import LocalAIContentGenerator

async def main():
    generator = LocalAIContentGenerator()
    
    if not generator.enabled:
        print("⚠️ Model not loaded")
        return
    
    result = await generator.generate_article(
        keyword="seo optimization",
        keyword_metrics={
            'search_volume': 12000,
            'difficulty': 65
        },
        target_length=2000,
        language='en'
    )
    
    print(f"Title: {result['title']}")
    print(f"SEO Score: {result['seo_score']}/100")
    print(f"Word Count: {result['word_count']}")

asyncio.run(main())
```

## ⚠️ محدودیت‌ها

### RAM
- مدل‌های بزرگ نیاز به RAM زیادی دارند
- Mistral/Llama 2: ~14 GB RAM
- GPT-2: ~2 GB RAM
- استفاده از quantization برای کاهش RAM

### سرعت
- CPU: کندتر از GPU
- GPU: سریع‌تر اما نیاز به GPU مناسب
- اولین بار: دانلود مدل زمان‌بر است

### کیفیت
- کیفیت ممکن است کمتر از GPT-4 باشد
- بستگی به مدل انتخاب شده دارد
- نیاز به ویرایش و بهبود

## 💡 بهترین روش‌ها

1. **شروع با GPT-2**: برای تست از GPT-2 استفاده کنید
2. **استفاده از GPU**: برای سرعت بیشتر از GPU استفاده کنید
3. **Quantization**: برای کاهش RAM از quantization استفاده کنید
4. **ویرایش**: همیشه محتوا را ویرایش کنید

## 🔍 مقایسه با OpenAI

| ویژگی | OpenAI GPT-4 | Local AI |
|-------|--------------|----------|
| هزینه | پولی | رایگان |
| کیفیت | بالا | متوسط-بالا |
| سرعت | سریع | کندتر |
| نیاز به RAM | ندارد | دارد |
| نیاز به GPU | ندارد | اختیاری |
| Privacy | API | محلی |

## 📚 منابع

- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Mistral Models](https://huggingface.co/mistralai)
- [Llama 2](https://huggingface.co/meta-llama)
- [Quantization Guide](https://huggingface.co/docs/transformers/quantization)

---

**نویسنده:** AI-SEO-Content Team  
**تاریخ:** 2024

