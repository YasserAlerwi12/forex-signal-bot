

from telethon import TelegramClient, events
import re

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '17271604'
api_hash = '078eef1324b45722acc3505d359773a9'
phone_number = '+967734231449'
# قنوات الإشارات والوجهة
source_channels = ['https://t.me/+LTQBpmC_DGQ2MjU0', 'https://t.me/+ce1dsIGK0Iw4Mzk0']
destination_channel = 'https://t.me/+suemhFyB0m4zYTg0'

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

# دالة لاستخراج معرف الرسالة المرجعية من النص
def extract_reference_id(text):
    match = re.search(r'\b(\d+)\b', text)
    return match.group(0) if match else None

@client.on(events.NewMessage(chats=source_channels))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    if contains_link(message.text):
        return

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # إنشاء مفتاح فريد لكل إشارة (باستخدام نص الرسالة ومعرف القناة)
        signal_key = f"{event.chat_id}_{message.text[:50]}"  # استخدام أول 50 حرف فقط كمفتاح
        signals[signal_key] = message
        await client.send_message(destination_channel, message)

    # تحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
    elif is_update(message.text):
        reference_id = extract_reference_id(message.text)
        if reference_id:
            # محاولة العثور على الرسالة الأصلية باستخدام مفتاح الإشارة
            for signal_key, original_message in signals.items():
                if reference_id in original_message.text:
                    await client.send_message(destination_channel, message, reply_to=original_message.id)
                    break
        else:
            # إذا لم يكن هناك إشارة مرجعية، قم بنسخ الرسالة كما هي
            await client.send_message(destination_channel, message)

    # إذا كانت الرسالة ليست إشارة ولا تعديل، ننسخ الرسالة كما هي
    else:
        await client.send_message(destination_channel, message)

# تشغيل العميل
client.run_until_disconnected()