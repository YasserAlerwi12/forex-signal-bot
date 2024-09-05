from telethon import TelegramClient, events
import re
import sqlite3
import requests
from requests_oauthlib import OAuth2Session
import asyncio

# إعدادات الاتصال
api_id = '17271604'  # استبدل بـ API ID الخاص بك
api_hash = '078eef1324b45722acc3505d359773a9'  # استبدل بـ API Hash الخاص بك
phone_number = '+967734231449'  # استبدل برقم هاتفك الدولي
channel_ids = ['https://t.me/+suemhFyB0m4zYTg0']  # استبدل بـ ID القناة الخاص بك

# إعداد OAuth2
redirect_uri = 'http://localhost'
client_id = '11593_Cy4lDavoQIcjOIwAeOv85eT1ByxcSokhbIIVovV4zaVsiABZtw'
client_secret = 'mzxWPsJYFB8YBosiTkh4O4S2028XSwU6PJdSOMO8VctTrNKzlA'
authorization_base_url = 'https://connect.spotware.com/apps/auth'
token_url = 'https://openapi.ctrader.com/apps/auth?client_id=11593_Cy4lDavoQIcjOIwAeOv85eT1ByxcSokhbIIVovV4zaVsiABZtw&redirect_uri=https%3A%2F%2Fopenapi.ctrader.com%2Fapps%2F11593%2Fplayground&scope=accounts'

# إنشاء عميل Telegram
client = TelegramClient('session_name', api_id, api_hash)

# نمط لاستخراج تفاصيل الإشارة
signal_pattern = re.compile(r"(BUY|SELL)\s+@?\s+(\d+\.\d+)\s*/?\s*(\d+\.\d+)?", re.IGNORECASE)
tp_pattern = re.compile(r"TP:?\s*(\d+\.\d+)")
sl_pattern = re.compile(r"SL:?\s*(\d+\.\d+)")

# إنشاء قاعدة البيانات SQLite لحفظ الإشارات
conn = sqlite3.connect('trading_signals.db')
c = conn.cursor()

# إنشاء جدول الإشارات إذا لم يكن موجوداً
c.execute('''CREATE TABLE IF NOT EXISTS signals
             (id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, signal_type TEXT, entry_price REAL, tp_levels TEXT, stop_loss REAL, status TEXT)''')
conn.commit()

# إعداد OAuth2
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

def get_access_token():
    try:
        authorization_url, state = oauth.authorization_url(authorization_base_url)
        print(f"اذهب إلى هذا الرابط لتفويض التطبيق: {authorization_url}")
        authorization_response = input('أدخل الرابط الذي تم توجيهك إليه بعد التفويض: ')
        token = oauth.fetch_token(token_url, authorization_response=authorization_response, client_secret=client_secret)
        return token['access_token']
    except Exception as e:
        print(f"فشل الحصول على رمز الوصول: {e}")
        return None

def send_trade_to_ctrader(signal):
    access_token = get_access_token()  # الحصول على Access Token
    if not access_token:
        print("لا يمكن الحصول على رمز الوصول، لا يمكن إرسال الصفقة.")
        return

    headers = {'Authorization': f'Bearer {access_token}'}
    
    trade_details = {
        'symbol': 'GBPJPY',  # استبدل بالرمز الفعلي إذا كان موجودًا
        'action': signal['action'],  # 'BUY' أو 'SELL'
        'price': signal['price'],
        'tp': signal['tp'],
        'sl': signal['sl']
    }
    
    try:
        response = requests.post('https://api.spotware.com/v1/orders', json=trade_details, headers=headers)
        response.raise_for_status()  # ستثير استثناء إذا كانت الاستجابة تحتوي على رمز حالة غير 2xx
        print("تم فتح الصفقة بنجاح")
    except requests.exceptions.RequestException as e:
        print(f"فشل فتح الصفقة: {e}")

async def save_signal(message_id, signal_type, entry_price, tp_levels, stop_loss):
    tp_levels_str = ",".join(map(str, tp_levels))  # تخزين TP كمجموعة
    c.execute('INSERT INTO signals (message_id, signal_type, entry_price, tp_levels, stop_loss, status) VALUES (?, ?, ?, ?, ?, ?)',
              (message_id, signal_type, entry_price, tp_levels_str, stop_loss, 'open'))
    conn.commit()
    signal = {
        'symbol': 'GBPJPY',  # استبدل بالرمز الفعلي إذا كان موجودًا
        'action': signal_type,
        'price': entry_price,
        'tp': tp_levels,
        'sl': stop_loss
    }
    send_trade_to_ctrader(signal)

async def update_signal(message_id, new_sl=None, new_status=None):
    if new_sl:
        c.execute('UPDATE signals SET stop_loss = ? WHERE message_id = ?', (new_sl, message_id))
    if new_status:
        c.execute('UPDATE signals SET status = ? WHERE message_id = ?', (new_status, message_id))
    conn.commit()

async def handle_signal(message):
    text = message.message
    signal_match = signal_pattern.search(text)
    tp_matches = tp_pattern.findall(text)
    sl_match = sl_pattern.search(text)
    
    if signal_match:
        signal_type = signal_match.group(1)
        entry_price = float(signal_match.group(2))
        tp_levels = [float(tp) for tp in tp_matches]
        stop_loss = float(sl_match.group(1)) if sl_match else None
        
        print(f"معالجة إشارة جديدة: {signal_type} عند {entry_price} مع TP {tp_levels} و SL {stop_loss}")
        await save_signal(message.id, signal_type, entry_price, tp_levels, stop_loss)

async def handle_update(message):
    original_message_id = message.reply_to_msg_id
    if original_message_id:
        if "Move SL" in message.message:
            new_sl = extract_new_sl_from_message(message.message)  # افترض أنك لديك دالة لاستخراج SL الجديد
            await update_signal(original_message_id, new_sl=new_sl)
        elif "SL hit" in message.message:
            await update_signal(original_message_id, new_status="closed")

@client.on(events.NewMessage(chats=channel_ids))
async def new_message_listener(event):
    if event.message.is_reply:
        await handle_update(event.message)
    else:
        await handle_signal(event.message)

async def main():
    await client.start(phone=phone_number)
    print("Client started")
    await client.run_until_disconnected()

# تشغيل العميل
if __name__ == '__main__':
    asyncio.run(main())
