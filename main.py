from telethon import TelegramClient, events
import re
import socket
import simplefix

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '17271604'
api_hash = '078eef1324b45722acc3505d359773a9'
phone_number = '+967734231449'

# قنوات الإشارات والوجهة
source_channels = ['https://t.me/+suemhFyB0m4zYTg0', 'https://t.me/+SCKJv5s6V4o5YTlk']
destination_channel = 'https://t.me/+suemhFyB0m4zYTg0'

# إعداد FIX
fix_server = 'demo-uk-eqx-01.p.ctrader.com'
fix_port = 5212
sender_comp_id = 'demo.topfx.3135973'
target_comp_id = 'cServer'

# إنشاء عميل Telegram
client = TelegramClient('forwarder', api_id, api_hash)

# تسجيل الدخول
client.start(phone=phone_number)

# لتخزين الإشارات الأصلية
signals = {}

# إعداد FIX socket
fix_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    fix_socket.connect((fix_server, fix_port))
except Exception as e:
    print(f"Error connecting to FIX server: {e}")

# دالة للتحقق مما إذا كانت الرسالة تحتوي على إشارة
def contains_signal(text):
    return "BUY" in text.upper() or "SELL" in text.upper()

# دالة للتحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
def is_update(text):
    return "TP" in text or "SL" in text or "Secure This trade" in text

# دالة لإرسال رسالة FIX
def send_fix_message(fix_message):
    try:
        fix_message_str = fix_message.to_string()
        fix_socket.sendall(fix_message_str.encode())
    except Exception as e:
        print(f"Error sending FIX message: {e}")

# دالة لإنشاء رسالة FIX جديدة بناءً على الإشارة
def create_fix_order(signal_type, symbol, price, volume):
    fix_message = simplefix.FixMessage()
    fix_message.append_pair(8, 'FIX.4.4')  # BeginString
    fix_message.append_pair(35, 'D')  # MsgType: New Order - Single
    fix_message.append_pair(49, sender_comp_id)  # SenderCompID
    fix_message.append_pair(56, target_comp_id)  # TargetCompID
    fix_message.append_pair(11, 'ORDER12345')  # ClOrdID - Unique order ID
    fix_message.append_pair(55, symbol)  # Symbol
    fix_message.append_pair(54, '1' if signal_type == 'BUY' else '2')  # Side: 1 = Buy, 2 = Sell
    fix_message.append_pair(38, str(volume))  # OrderQty
    fix_message.append_pair(44, str(price))  # Price
    fix_message.append_pair(40, '2')  # OrdType: 2 = Limit

    return fix_message

def extract_order_details(text):
    # افتراضياً، نبحث عن بعض الأنماط في الرسالة لاستخراج المعلومات.
    match = re.search(r'(\w+)\s*at\s*([\d.]+)\s*for\s*(\d+)', text, re.IGNORECASE)
    if match:
        symbol = match.group(1).upper()
        price = float(match.group(2))
        volume = int(match.group(3))
        return symbol, price, volume
    return None, None, None

@client.on(events.NewMessage(chats=source_channels))
async def handle_new_message(event):
    message = event.message

    if contains_signal(message.text):
        signal_type = 'BUY' if 'BUY' in message.text.upper() else 'SELL'
        symbol, price, volume = extract_order_details(message.text)

        if symbol and price and volume:
            fix_message = create_fix_order(signal_type, symbol, price, volume)
            send_fix_message(fix_message)

# تشغيل العميل
client.run_until_disconnected()
