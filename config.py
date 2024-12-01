import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعدادات Telegram
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")
TELEGRAM_CHANNEL_IDS = [-1002231055362]  # يمكن إضافة المزيد من القنوات هنا

# إعدادات cTrader
CTRADER_CLIENT_ID = os.getenv("CTRADER_CLIENT_ID")
CTRADER_CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET")
CTRADER_ACCESS_TOKEN = os.getenv("CTRADER_ACCESS_TOKEN")
CTID_TRADER_ACCOUNT_ID = int(os.getenv("CTID_TRADER_ACCOUNT_ID"))

# قائمة أزواج العملات المدعومة
CURRENCY_PAIRS = {
    'EURUSD': 1,
    'GBPUSD': 2,
    'USDJPY': 3,
    'AUDUSD': 4,
    'USDCAD': 5,
    'USDCHF': 6,
    'NZDUSD': 7,
    'EURGBP': 8,
    'EURJPY': 9,
    'GBPJPY': 10
}

# إعدادات قاعدة البيانات
DB_NAME = 'signals.db'

# أنماط تحليل الإشارات
SIGNAL_PATTERN = r"(BUY|SELL)\s+(\w+)\s+@?\s+(\d+\.\d+)\s*/?\s*(\d+\.\d+)?"
TP_PATTERN = r"TP:?\s*(\d+\.\d+)"
SL_PATTERN = r"SL:?\s*(\d+\.\d+)"
