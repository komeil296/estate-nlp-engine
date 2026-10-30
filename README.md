# Estate NLP Engine

موتور مستقل پردازش زبان فارسی تخصصی املاک؛ زیرسامانه هوشمند یک CRM موبایل‌محور و Offline-First.

## هدف

ورودی موتور متن فارسی آگهی یا درخواست مرتبط با ملک است. خروجی، اطلاعات ساختاریافته همراه با شواهد، وضعیت استخراج و ابهام‌هاست. نسخه اول قواعدمحور و قابل اجرای محلی است؛ آموزش مدل در این مرحله انجام نمی‌شود.

## وضعیت تأییدشده در 2026-10-30

- نرمال‌سازی پایه فارسی پیاده‌سازی شده است.
- استخراج اولیه نوع معامله، نوع ملک، متراژ، اتاق، ویژگی‌های بولی و شرایط اجاره پیاده‌سازی شده است.
- استخراج محافظه‌کارانه اشاره‌های مالی پیاده‌سازی شده است.
- مدل‌های داده و JSON Schema نسخه `0.2` موجودند؛ Schema هنوز Draft است.
- نگاشت برچسب‌های منبع Divar به weak labelهای قابل ردیابی اضافه شده است.
- دیتابیس Divar با 1,000,000 رکورد و 61 ستون ممیزی شده است.
- ارزیابی توافق با برچسب‌های منبع روی نمونه طبقه‌بندی‌شده انجام شده است؛ این ارزیابی جایگزین مجموعه طلایی انسانی نیست.
- **89 تست موفق** در محیط بررسی اجرا شده‌اند.

## ساختار کد

```text
src/estate_nlp/
  normalization.py       # نرمال‌سازی قطعی متن فارسی
  extractor.py           # استخراج قواعدمحور اطلاعات ملک
  financial.py           # استخراج اشاره‌های مالی
  models.py              # مدل‌های تایپ‌شده خروجی
  divar_dataset.py        # نگاشت محافظه‌کارانه برچسب‌های منبع Divar

schemas/
  extraction.schema.json

scripts/
  audit_divar_sqlite.py
  evaluate_divar_extractor.py

tests/
```

## نصب و تست

Python 3.13 توصیه می‌شود.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## ممیزی دیتابیس محلی

دیتابیس خام را داخل Git قرار ندهید. مسیر دیتابیس را به اسکریپت بدهید؛ دیتابیس فقط در حالت read-only باز می‌شود.

```powershell
python .\scripts\audit_divar_sqlite.py `
  --database "E:\projects\estate-assistant\data\processed\divar_ads.sqlite" `
  --output ".\docs\DATASET_AUDIT_LOCAL.md"
```

برای بررسی کامل نشانگرهای Unicode در عنوان و توضیحات، گزینه `--scan-unicode` را اضافه کنید. این اسکن کندتر است و متن آگهی را چاپ نمی‌کند.

## ارزیابی موتور روی نمونه منبع

```powershell
python .\scripts\evaluate_divar_extractor.py `
  --database "E:\projects\estate-assistant\data\processed\divar_ads.sqlite" `
  --sample-per-category 300 `
  --output ".\docs\EXTRACTOR_WEAK_LABEL_EVALUATION_LOCAL.md"
```

خروجی این اسکریپت میزان توافق با برچسب‌های ساختاریافته منبع را نشان می‌دهد، نه دقت روی داده طلایی. متن آگهی در گزارش چاپ یا ذخیره نمی‌شود.

## اصول داده

- دیتابیس خام، فایل‌های CSV، متن آگهی و اطلاعات شخصی وارد Git نشوند.
- NULL با false یا صفر یکی نیست.
- مقدار صفر و حالت «مجانی» حفظ شود؛ مقدار NULL همراه با «توافقی» نیز جدا بماند.
- واحد و ارز مالی بدون شواهد تبدیل یا حدس زده نشود.
- دسته `house-villa-*` بدون شواهد بیشتر به خانه یا ویلا تفکیک نشود.
- برچسب‌های منبع فقط weak label هستند؛ ادعای متن با حقیقت تأییدشده ملک متفاوت است.

## مستندات

- [زمینه و محدوده پروژه](docs/PROJECT_CONTEXT.md)
- [معماری](docs/ARCHITECTURE.md)
- [گزارش پیشرفت](docs/DEVELOPMENT_LOG.md)
- [تصمیم‌های فنی](docs/DECISIONS.md)
- [راهنمای دیتاست](docs/DATASET.md)
- [ممیزی دیتابیس یک‌میلیونی](docs/DATASET_AUDIT_2026-10-30.md)
- [ارزیابی توافق weak-label](docs/EXTRACTOR_WEAK_LABEL_EVALUATION_2026-10-30.md)
- [قرارداد خروجی](docs/EXTRACTION_SCHEMA.md)

## مرزهای فعلی

این مخزن هنوز اپلیکیشن موبایل، CRM، سرور، همگام‌سازی، مدل آموزش‌دیده یا pipeline نهایی تولید دیتاست آموزشی را پیاده‌سازی نمی‌کند. هدف فعلی تکمیل و ارزیابی موتور NLP مستقل است.
