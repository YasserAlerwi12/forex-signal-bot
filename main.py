

from telethon import TelegramClient, events
import re
import socket
import simplefix

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '17271604'
api_hash = '078eef1324b45722acc3505d359773a9'
phone_number = '+967734231449'
# قنوات الإشارات والوجهة
#ٍsource_channels = ['https://t.me/+suemhFyB0m4zYTg0', 'https://t.me/+SCKJv5s6V4o5YTlk']
destination_channel = 'https://t.me/+suemhFyB0m4zYTg0'

#إنشاء عميل Telegram باستخدام حسابك الشخصي# إعداد FIX# معلومات الاتصال بـ cTrader FIX API
fix_server = 'demo-uk-eqx-01.p.ctrader.com'
fix_port = 5212
sender_comp_id = 'demo.topfx.3135973'
target_comp_id = 'cServer'

# قنوات الإشارات
source_channels = ['https://t.me/+suemhFyB0m4zYTg0', 'https://t.me/+SCKJv5s6V4o5YTlk']

# إنشاء عميل Telegram
client = TelegramClient('forwarder', api_id, api_hash)

# تسجيل الدخول
client.start(phone=phone_number)

# لتخزين الإشارات الأصلية
signals = {}

# إعداد FIX socket
fix_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fix_socket.connect((fix_server, fix_port))

# إعداد FIX parser والمولد
fix_parser = simplefix.parser.FixParser()
fix_builder = simplefix.FixMessage()

# دالة للتحقق مما إذا كانت الرسالة تحتوي على إشارة
def contains_signal(text):
    return "BUY" in text.upper() or "SELL" in text.upper()

# دالة للتحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
def is_update(text):
    return "TP" in text or "SL" in text or "Secure This trade" in text

# دالة لإرسال رسالة FIX
def send_fix_message(fix_message):
    fix_socket.sendall(fix_message.encode())

# دالة لإنشاء رسالة FIX جديدة بناءً على الإشارة
def create_fix_order(signal_type, symbol, price, volume):
    fix_builder.clear()
    fix_builder.append_pair(8, 'FIX.4.4')  # BeginString
    fix_builder.append_pair(35, 'D')  # MsgType: New Order - Single
    fix_builder.append_pair(49, sender_comp_id)  # SenderCompID
    fix_builder.append_pair(56, target_comp_id)  # TargetCompID
    fix_builder.append_pair(11, 'ORDER12345')  # ClOrdID - Unique order ID, needs to be unique for each order
    fix_builder.append_pair(55, symbol)  # Symbol
    fix_builder.append_pair(54, '1' if signal_type == 'BUY' else '2')  # Side: 1 = Buy, 2 = Sell
    fix_builder.append_pair(38, str(volume))  # OrderQty
    fix_builder.append_pair(44, str(price))  # Price
    fix_builder.append_pair(40, '2')  # OrdType: 2 = Limit

    return fix_builder

@client.on(events.NewMessage(chats=source_channels))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # استخراج المعلومات من الرسالة (يجب تعديل هذا الجزء لاستخراج المعلومات الصحيحة)
        signal_type = 'BUY' if 'BUY' in message.text.upper() else 'SELL'
        symbol = 'EURUSD'  # على سبيل المثال، يجب استخراج هذا من الرسالة
        price = 1.1234  # على سبيل المثال، يجب استخراج هذا من الرسالة
        volume = 100000  # حجم اللوت، على سبيل المثال

        # إنشاء رسالة FIX جديدة وإرسالها
        fix_message = create_fix_order(signal_type, symbol, price, volume)
        send_fix_message(fix_message)

# تشغيل العميل
client.run_until_disconnected()