# نظام إدارة الخطط السنوية
## Annual Plan Management System

نظام ويب لإدارة الخطط السنوية للتشكيلات الحكومية مبني على Django 5.x مع واجهة RTL عربية.

---

## متطلبات التشغيل

- Python 3.11+
- MySQL 8.x (للإنتاج) أو SQLite (للتطوير)
- WeasyPrint dependencies (GTK on Windows / pango on Linux)

---

## تثبيت وتشغيل (بيئة التطوير)

```bash
cd annual_plan_system

# 1. إنشاء البيئة الافتراضية
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. إعداد ملف البيئة
copy .env.example .env
# عدّل .env وضع SECRET_KEY وبيانات قاعدة البيانات

# 4. تهيئة قاعدة البيانات
python manage.py migrate

# 5. تحميل البيانات الأولية
python manage.py loaddata fixtures/lookups.json
python manage.py loaddata fixtures/formations.json

# 6. إنشاء حساب المشرف
python manage.py createsuperuser

# 7. تشغيل الخادم
python manage.py runserver
```

الواجهة متاحة على: http://127.0.0.1:8000/

---

## هيكل المشروع

```
annual_plan_system/
├── config/                    # إعدادات Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                  # النماذج الأساسية (AuditLog, LookupValue)
│   ├── accounts/              # إدارة المستخدمين والأدوار
│   ├── formations/            # هيكل التشكيلات
│   ├── plans/                 # الخطط السنوية (النموذج الرئيسي)
│   └── dashboard/             # لوحة التحكم
├── templates/                 # قوالب HTML المشتركة
├── static/                    # CSS/JS
├── fixtures/                  # بيانات أولية
└── manage.py
```

---

## الأدوار والصلاحيات

| الدور | الصلاحيات |
|-------|-----------|
| ADMIN | كامل الصلاحيات + إدارة المستخدمين والتشكيلات |
| MANAGER | مشاهدة وإدارة خطط تشكيله والتشكيلات التابعة + مراجعة |
| ORGANIZER | إنشاء وتعديل خطط تشكيله |
| REVIEWER | مراجعة الخطط المقدمة للمراجعة |
| VIEWER | مشاهدة فقط |

---

## سير عمل الخطة

```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED
                                 → REJECTED → DRAFT (للتعديل)
APPROVED → ARCHIVED
```

---

## تصدير PDF

يتطلب WeasyPrint. على Windows يحتاج إلى GTK3 runtime:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

---

## متغيرات البيئة (.env)

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=annual_plan_db
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
SESSION_COOKIE_AGE=1800
```
