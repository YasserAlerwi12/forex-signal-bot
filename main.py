from telethon import TelegramClient, events
import re

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '15903885'
api_hash = '6626160405d02b9e9e3eb7879d7e498a'
phone_number = '+967781487926'

# قنوات الإشارات والوجهة
source_channel = 'https://t.me/+suemhFyB0m4zYTg0'
destination_channel = 'https://t.me/+LTQBpmC_DGQ2MjU0'

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

# دالة لاستخراج معرف الرسالة المرجعية
def extract_reference_id(text):
    # نبحث عن الرقم الذي يشير إلى الإشارة السابقة
    match = re.search(r'(\d+)', text)
    return match.group(0) if match else None

@client.on(events.NewMessage(chats=source_channel))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    if contains_link(message.text):
        return

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # إذا كانت رسالة تحتوي على إشارة، نقوم بتخزينها مع معرف فريد
        signal_id = f"{message.id}"
        signals[signal_id] = message
        await client.send_message(destination_channel, message)
    
    # تحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
    elif is_update(message.text):
        reference_id = extract_reference_id(message.text)
        if reference_id and reference_id in signals:
            original_message = signals[reference_id]
            modified_text = f"Update on signal {reference_id}:\n{message.text}"
            # إرسال الرسالة المعدلة كرد على الرسالة الأصلية
            await client.send_message(destination_channel, modified_text, reply_to=original_message.id)
            return

    # إذا لم تكن الرسالة إشارة أو تعديل، نقوم بنسخ الرسالة إلى القناة الوجهة
    await client.send_message(destination_channel, message)

# تشغيل العميل
client.run_until_disconnected()
