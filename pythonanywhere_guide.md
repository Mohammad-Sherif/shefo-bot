# 🚀 دليل رفع بوت صاحبك (Shefo-Bot) على PythonAnywhere

هذا الدليل يشرح خطوة بخطوة كيفية استضافة بوت التليجرام على [PythonAnywhere](https://www.pythonanywhere.com/) مجاناً بالكامل.

البوت يعمل بنظام **Webhook** — يعني PythonAnywhere هتشغله كـ Web App تفضل شغالة **24/7 حتى لو قفلت المتصفح**.

---

## ١. إنشاء الحساب
1. اذهب إلى [pythonanywhere.com](https://www.pythonanywhere.com/)
2. اضغط **Pricing & signup**
3. اختر **Create a Beginner account** (مجاني)
4. سجّل بياناتك ووافق على الشروط

---

## ٢. تحميل الكود وتثبيت المكتبات

### افتح الكونسول:
1. من لوحة التحكم، انزل لقسم **Consoles**
2. تحت **New console** اضغط **Bash**

### نفّذ الأوامر التالية:
```bash
git clone https://github.com/Mohammad-Sherif/shefo-bot.git
cd shefo-bot
pip install -r requirements.txt --user
```

---

## ٣. إضافة مفاتيح الـ API

```bash
nano .env
```

انسخ والصق (مع وضع المفاتيح الخاصة بك):
```env
TELEGRAM_BOT_TOKEN=ضع_التوكن_هنا
GROQ_API_KEY=ضع_الكي_هنا
CITY=Tanta
COUNTRY=Egypt
PRAYER_METHOD=5
GROQ_MODEL=llama-3.3-70b-versatile
```

احفظ: `Ctrl + X` → `Y` → `Enter`

---

## ٤. إعداد الـ Web App (الخطوة الأهم!)

هذه الخطوة هي اللي بتخلي البوت يشتغل 24/7 بدون ما تفتح المتصفح:

1. اذهب لتاب **Web** من الشريط العلوي
2. اضغط **Add a new web app**
3. اضغط **Next** (تجاهل رسالة الدومين)
4. اختر **Manual configuration** (مش Flask!)
5. اختر **Python 3.10** (أو أحدث نسخة متاحة)
6. اضغط **Next** حتى تنتهي

### تعديل ملف الـ WSGI:
1. في صفحة الـ Web app، ابحث عن **WSGI configuration file** واضغط عليه
2. **امسح كل المحتوى** واستبدله بالكود التالي:

```python
import sys
import os
from pathlib import Path

# Add project to path
project_dir = '/home/اسم_المستخدم_بتاعك/shefo-bot'
sys.path.insert(0, project_dir)

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

# Set timezone
os.environ['TZ'] = 'Africa/Cairo'

# Import Flask app
from webapp import app as application
```

> ⚠️ **مهم جداً:** غيّر `اسم_المستخدم_بتاعك` باسم المستخدم الحقيقي بتاعك على PythonAnywhere (مثلاً: `mohammadsherif`)

3. اضغط **Save**

### تعديل Source code path:
في نفس صفحة Web app:
- في خانة **Source code**: اكتب `/home/اسم_المستخدم_بتاعك/shefo-bot`
- في خانة **Working directory**: اكتب `/home/اسم_المستخدم_بتاعك/shefo-bot`

### اضغط الزر الأخضر الكبير: **Reload** 🔄

---

## ٥. تفعيل الـ Webhook (مرة واحدة بس)

بعد ما عملت Reload، افتح الرابط ده في المتصفح:

```
https://اسم_المستخدم_بتاعك.pythonanywhere.com/setup
```

لو ظهرت رسالة فيها `"✅ تم تفعيل الـ Webhook!"` يبقى البوت **شغّال رسمياً!** 🎉

روح على تليجرام وابعت `/start` للبوت وجرّب!

---

## ٦. إعداد تذكيرات الصلاة التلقائية (cron-job.org)

البوت محتاج خدمة خارجية تنبهه كل شوية عشان يفحص مواعيد الصلاة ويبعتلك تذكيرات:

1. اذهب إلى [cron-job.org](https://cron-job.org) وسجّل حساب مجاني
2. اضغط **CREATE CRONJOB** وأضف الوظائف التالية:

### وظيفة ١: تذكيرات الصلاة (كل 5 دقائق)
| الحقل | القيمة |
|-------|--------|
| Title | Prayer Reminders |
| URL | `https://اسم_المستخدم_بتاعك.pythonanywhere.com/check_prayers` |
| Schedule | Every 5 minutes |

### وظيفة ٢: السؤال على الحال (كل ساعة)
| الحقل | القيمة |
|-------|--------|
| Title | Check In |
| URL | `https://اسم_المستخدم_بتاعك.pythonanywhere.com/check_in` |
| Schedule | Every 60 minutes |

### وظيفة ٣: تحديث مواعيد الصلاة (يومياً الساعة 12:05 AM)
| الحقل | القيمة |
|-------|--------|
| Title | Daily Reset |
| URL | `https://اسم_المستخدم_بتاعك.pythonanywhere.com/daily_reset` |
| Schedule | At 00:05 |

---

## ٧. تحديث الكود في المستقبل

لو عدّلنا الكود وعايز تحدّث البوت:

1. افتح **Bash console** من لوحة التحكم
2. اكتب:
```bash
cd shefo-bot
git pull
```
3. اذهب لتاب **Web** واضغط **Reload** 🔄

وخلاص! البوت هيشتغل بالتحديثات الجديدة فوراً.

---

## ⚠️ ملاحظات هامة

- **البوت شغال 24/7:** مش محتاج تفتح المتصفح خالص. الـ Web App شغالة لوحدها.
- **كل 3 شهور:** PythonAnywhere بيطلب منك تجدد الـ Web App المجانية بالضغط على زر في إيميل بيبعتهولك. لو منقرتش عليه في الميعاد، البوت هيقف. ده أمان، مش بفلوس.
- **أخطاء الشبكة:** لو البوت وقف فجأة عن الرد، ادخل تاب Web واضغط Reload.
- **Error logs:** لو حصلت مشكلة، شوف الـ Error log من تاب Web عشان تعرف إيه اللي حصل.
