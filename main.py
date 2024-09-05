from telethon import TelegramClient, events
import re
import sqlite3
import asyncio
from flask import Flask, jsonify

# إعدادات الاتصال
api_id = '17271604'  # استبدل بـ API ID الخاص بك
api_hash = '078eef1324b45722acc3505d359773a9'  # استبدل بـ API Hash الخاص بك
phone_number = '+967734231449'  # استبدل برقم هاتفك الدولي
channel_ids = ['https://t.me/+suemhFyB0m4zYTg0']  # استبدل بأسماء القنوات الخاصة بك

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

async def save_signal(message_id, signal_type, entry_price, tp_levels, stop_loss):
    tp_levels_str = ",".join(map(str, tp_levels))  # تخزين TP كمجموعة
    print(f"Saving signal: {signal_type} at {entry_price} with TP {tp_levels_str} and SL {stop_loss}")
    c.execute('INSERT INTO signals (message_id, signal_type, entry_price, tp_levels, stop_loss, status) VALUES (?, ?, ?, ?, ?, ?)',
              (message_id, signal_type, entry_price, tp_levels_str, stop_loss, 'open'))
    conn.commit()

async def update_signal(message_id, new_sl=None, new_status=None):
    if new_sl:
        print(f"Updating stop loss for message ID {message_id} to {new_sl}")
        c.execute('UPDATE signals SET stop_loss = ? WHERE message_id = ?', (new_sl, message_id))
    if new_status:
        print(f"Updating status for message ID {message_id} to {new_status}")
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
        
        await save_signal(message.id, signal_type, entry_price, tp_levels, stop_loss)

async def handle_update(message):
    original_message_id = message.reply_to_msg_id
    if original_message_id:
        if "Move SL" in message.message:
            new_sl = re.search(r"Move SL to (\d+\.\d+)", message.message)
            if new_sl:
                await update_signal(original_message_id, new_sl=new_sl.group(1))
        elif "SL hit" in message.message:
            await update_signal(original_message_id, new_status="closed")

@client.on(events.NewMessage(chats=channel_ids))
async def new_message_listener(event):
    print(f"New message from channel: {event.chat_id}")
    print(f"Message content: {event.message.text}")
    if event.message.is_reply:
        print("Message is a reply")
        await handle_update(event.message)
    else:
        print("Message is a new signal")
        await handle_signal(event.message)

async def main():
    await client.start(phone=phone_number)
    print("Client started")
    await client.run_until_disconnected()

# تشغيل العميل
if __name__ == '__main__':
    asyncio.run(main())

app = Flask(__name__)

# الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('trading_signals.db')
    conn.row_factory = sqlite3.Row  # لتنسيق البيانات كقواميس
    return conn

@app.route('/get_signals', methods=['GET'])
def get_signals():
    conn = get_db_connection()
    signals = conn.execute('SELECT * FROM signals WHERE status = "open"').fetchall()
    conn.close()

    signal_list = []
    for signal in signals:
        signal_list.append({
            'id': signal['id'],
            'signal_type': signal['signal_type'],
            'entry_price': signal['entry_price'],
            'tp_levels': signal['tp_levels'].split(','),
            'stop_loss': signal['stop_loss'],
            'status': signal['status']
        })
    return jsonify(signal_list)

if __name__ == '__main__':
    app.run(debug=True)

