# Forex Trading Signal Bot

برنامج آلي لمراقبة وتنفيذ إشارات تداول الفوركس من Telegram باستخدام منصة cTrader.

## المميزات
- استقبال إشارات التداول تلقائياً من قنوات Telegram المحددة
- تحليل الإشارات واستخراج معلومات الصفقة (نقطة الدخول، الهدف، وقف الخسارة)
- تخزين الإشارات في قاعدة بيانات محلية
- تنفيذ الصفقات تلقائياً على منصة cTrader
- إرسال إشعارات عن حالة الصفقات

## المتطلبات
- Python 3.8+
- حساب Telegram
- حساب cTrader (تجريبي أو حقيقي)

## التثبيت
1. قم بنسخ المستودع:
```bash
git clone https://github.com/yourusername/forex-trading-bot.git
cd forex-trading-bot
```

2. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

3. قم بإنشاء ملف `.env` وأضف المتغيرات المطلوبة:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=your_phone_number
CTRADER_CLIENT_ID=your_client_id
CTRADER_CLIENT_SECRET=your_client_secret
CTRADER_ACCESS_TOKEN=your_access_token
CTID_TRADER_ACCOUNT_ID=your_account_id
```

## الاستخدام
1. قم بتشغيل البرنامج:
```bash
python main.py
```

2. سيقوم البرنامج تلقائياً بـ:
   - الاتصال بـ Telegram
   - مراقبة القنوات المحددة
   - تحليل الإشارات الواردة
   - تنفيذ الصفقات على منصة cTrader

## هيكل المشروع
```
forex-trading-bot/
├── main.py           # النقطة الرئيسية للبرنامج
├── api.py           # التعامل مع API الخاص بـ cTrader
├── database.py      # إدارة قواعد البيانات
├── config.py        # إعدادات البرنامج
├── utils.py         # أدوات مساعدة
├── requirements.txt # متطلبات البرنامج
└── .env            # متغيرات البيئة
```

## الترخيص
MIT License

## تنويه
هذا البرنامج للأغراض التعليمية فقط. تداول الفوركس ينطوي على مخاطر عالية.
