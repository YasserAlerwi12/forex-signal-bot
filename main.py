

import quickfix as fix
from telethon import TelegramClient, events
import re

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '17271604'
api_hash = '078eef1324b45722acc3505d359773a9'
phone_number = '+967734231449'
# قنوات الإشارات والوجهة
source_channels = ['https://t.me/+suemhFyB0m4zYTg0', 'https://t.me/+SCKJv5s6V4o5YTlk']
destination_channel = 'https://t.me/+suemhFyB0m4zYTg0'

#إنشاء عميل Telegram باستخدام حسابك الشخصي# إعداد FIX
settings = fix.SessionSettings('fix.cfg')
application = fix.Application()
storeFactory = fix.FileStoreFactory(settings)
logFactory = fix.FileLogFactory(settings)
initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
initiator.start()

# إنشاء عميل Telegram باستخدام حسابك الشخصي
client = TelegramClient('forwarder', api_id, api_hash)

# تسجيل الدخول
client.start(phone=phone_number)

# لتخزين الإشارات الأصلية
signals = {}

# دالة للتحقق مما إذا كانت الرسالة تحتوي على رابط
def contains_link(text):
    url_pattern = re.compile(r"https?://\S+|www\.\S+")
    return bool(url_pattern.search(text))

# دالة للتحقق مما إذا كانت الرسالة تحتوي على إشارة
def contains_signal(text):
    return "BUY" in text.upper() or "SELL" in text.upper()

# دالة للتحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
def is_update(text):
    return "TP" in text or "SL" in text or "Secure This trade" in text

# دالة لإرسال أمر تداول إلى cTrader
def send_trade_order(symbol, side, entry, stoploss, takeprofit):
    order = fix.Message()
    order.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
    order.setField(fix.Symbol(symbol))
    order.setField(fix.Side(side))
    order.setField(fix.OrderQty(100))  # تعديل الحجم حسب الحاجة
    order.setField(fix.Price(entry))
    order.setField(fix.StopPx(stoploss))
    order.setField(fix.Text(takeprofit))  # تعديل الحقول حسب الحاجة
    fix.Session.sendToTarget(order, "demo.topfx.3135973", "cServer")

@client.on(events.NewMessage(chats=source_channels))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    if contains_link(message.text):
        return

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # استخراج المعلومات المطلوبة من الإشارة
        signal = extract_signal_details(message.text)
        if signal:
            # إرسال أمر التداول إلى cTrader
            send_trade_order(signal['symbol'], signal['side'], signal['entry'], signal['stoploss'], signal['takeprofit'])
        
def extract_signal_details(text):
    # هنا يمكنك كتابة كود لاستخراج البيانات من النص مثل الرمز، النوع، السعر، الوقف، والأهداف
    # يجب عليك تعديل الكود حسب تنسيق الرسائل في قنوات التيلجرام
    # مثال:
    match = re.search(r'(BUY|SELL) ([A-Z]+) @ (\d+\.\d+)', text)
    if match:
        return {
            'side': match.group(1),
            'symbol': match.group(2),
            'entry': float(match.group(3)),
            'stoploss': 1.2929,  # قيم افتراضية، يجب تعديلها لاستخراجها من النص
            'takeprofit': "1.2839 | 1.2809 | 1.2759"
        }
    return None

# تشغيل العميل
client.run_until_disconnected()