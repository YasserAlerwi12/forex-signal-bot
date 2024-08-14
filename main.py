from telethon import TelegramClient, events, sync
import re

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '22301177'
api_hash = '5a3f28febb80ee1d2ba92e12ee6b4c40'
phone_number = '+967774530312'

# قنوات الإشارات والوجهة
source_channel = 'https://t.me/+suemhFyB0m4zYTg0'
destination_channel = 'https://t.me/+xT-LSNPSRSYyNzVk'

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

@client.on(events.NewMessage(chats=source_channel))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط أو لا تحتوي على إشارة
    if not contains_link(message.text):
        if contains_signal(message.text):
            # إذا كانت رسالة تحتوي على إشارة، نقوم بتخزينها مع معرف فريد
            signal_id = f"{message.id}"
            signals[signal_id] = message.text
            await client.send_message(destination_channel, message)

        else:
            # إذا كانت رسالة تحتوي على تعديل، نبحث عن الرسالة الأصلية
            reference_id = extract_reference_text(message.text)
            if reference_id and reference_id in signals:
                original_signal_text = signals[reference_id]
                modified_text = f"Update on signal {reference_id}:\n{message.text}"
                await client.send_message(destination_channel, modified_text)

def extract_reference_text(text):
    # هذه الدالة تقوم باستخراج النص المرجعي من الرسالة المعدلة
    # نفترض أن النص المرجعي يتم الإشارة إليه باستخدام رقم معين
    match = re.search(r'(\d+)', text)  # استخراج الرقم من النص
    return match.group(1) if match else None

# تشغيل العميل
client.run_until_disconnected()
