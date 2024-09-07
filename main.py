import re
import os
import psycopg2
from telethon import TelegramClient, events
from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from dotenv import load_dotenv
from twisted.internet import reactor

# تحميل المعلومات الحساسة من .env ملف
load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

# إعدادات cTrader API
CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET')
hostType = os.getenv('CTRADER_HOST_TYPE', 'demo')  # يمكن التعديل بين live و demo
host = EndPoints.PROTOBUF_LIVE_HOST if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
ctrader_client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)

# إعداد عميل Telegram
client = TelegramClient('session_name', api_id, api_hash)

# إعداد اتصال PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise e

# إنشاء الجداول في قاعدة البيانات PostgreSQL
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        message_id BIGINT PRIMARY KEY,
        signal_type TEXT,
        entry_price REAL,
        tp_prices TEXT,
        sl_price REAL
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# وظيفة لإضافة إشارة جديدة إلى قاعدة البيانات
def add_signal_to_db(message_id, signal_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        tp_prices_str = ','.join(map(str, signal_data['tp']))
        cursor.execute('''
        INSERT INTO signals (message_id, signal_type, entry_price, tp_prices, sl_price) 
        VALUES (%s, %s, %s, %s, %s)
        ''', (message_id, signal_data['type'], signal_data['entry_price'], tp_prices_str, signal_data['sl']))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error adding signal to database: {e}")
    finally:
        cursor.close()
        conn.close()

# وظيفة لاسترجاع إشارة من قاعدة البيانات
def get_signal_from_db(message_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM signals WHERE message_id = %s', (message_id,))
        signal = cursor.fetchone()
        return signal
    except psycopg2.Error as e:
        print(f"Error retrieving signal from database: {e}")
    finally:
        cursor.close()
        conn.close()

# تسجيل الدخول إلى حساب Telegram الشخصي
async def start_telegram_client():
    await client.start(phone_number)
    print("Telegram client started. Listening for signals...")

# تحليل الإشارة
def parse_signal(message):
    pattern = r"(BUY|SELL)\s*@\s*(\d+\.\d+)"
    match = re.search(pattern, message)
    if match:
        signal_type = match.group(1)
        entry_price = float(match.group(2))
        tp_pattern = r"TP:\s*(\d+\.\d+)"
        sl_pattern = r"SL:\s*(\d+\.\d+)"
        tp_match = re.findall(tp_pattern, message)
        sl_match = re.search(sl_pattern, message)
        if tp_match and sl_match:
            tp_prices = list(map(float, tp_match))
            sl_price = float(sl_match.group(1))
            return {"type": signal_type, "entry_price": entry_price, "tp": tp_prices, "sl": sl_price}
    return None

# إرسال طلب التداول باستخدام ctrader_open_api.Client
def execute_trade(signal_data):
    direction = 1 if signal_data['type'] == 'BUY' else 2  # 1: BUY, 2: SELL
    request = Protobuf.NewOrderRequest(
        accountId=int(os.getenv('CTRADER_ACCOUNT_ID')),  # استبدل بـ Account ID الخاص بك
        symbolId="GBPJPY",
        tradeSide=direction,
        volume=100000,  # هنا نحدد حجم الصفقة
        stopLoss=signal_data['sl'],
        takeProfit=signal_data['tp'][0]
    )
    
    try:
        # إرسال الطلب إلى cTrader API
        ctrader_client.send(request)
        print("Trade Executed")
    except Exception as e:
        print(f"Error executing trade: {e}")
        async_send_telegram_notification(f"Error executing trade: {e}")

# التعامل مع الرسائل الجديدة في القنوات المحددة
@client.on(events.NewMessage(chats=('channel_username1', 'channel_username2')))  # ضع أسماء القنوات هنا
async def signal_handler(event):
    message = event.message.message
    reply_to_msg_id = event.message.reply_to_msg_id
    
    if reply_to_msg_id:
        signal_data = get_signal_from_db(reply_to_msg_id)
        if signal_data:
            print(f"Received update for signal {reply_to_msg_id}: {message}")
            handle_update(signal_data, message)
    
    elif "BUY" in message or "SELL" in message:
        signal_data = parse_signal(message)
        if signal_data:
            message_id = event.message.id
            add_signal_to_db(message_id, signal_data)
            execute_trade(signal_data)

# التعامل مع التحديثات (مثل تحريك SL)
def handle_update(signal_data, message):
    if "Move SL to your entry price" in message:
        print("Updating SL to entry price...")
    elif "SL hit on breakeven" in message:
        print("SL hit on breakeven. Closing trade or handling accordingly.")
    elif "TP1 Hit" in message:
        print("TP1 Hit. Updating SL or handling TP.")

# إرسال إشعار عبر Telegram
async def async_send_telegram_notification(message):
    await client.send_message('your_telegram_username', message)

# تشغيل عميل Telegram
async def main():
    await start_telegram_client()
    create_tables()  # إنشاء الجداول عند بدء التطبيق
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
