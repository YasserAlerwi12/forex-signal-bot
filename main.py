

from telethon import TelegramClient, events
import re

# تعيين معلومات الدخول الخاصة بـ Telegram API
api_id = '17271604'
api_hash = '078eef1324b45722acc3505d359773a9'
phone_number = '+967734231449'
# قنوات الإشارات والوجهة
source_channels = ['https://t.me/+LTQBpmC_DGQ2MjU0', 'https://t.me/+ce1dsIGK0Iw4Mzk0']
destination_channel = 'https://t.me/+suemhFyB0m4zYTg0'

#إنشاء عميل Telegram باستخدام حسابك الشخصي
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

@client.on(events.NewMessage(chats=source_channels))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    if contains_link(message.text):
        return

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # إنشاء مفتاح فريد لكل إشارة يتكون من معرف القناة ومعرف الرسالة
        signal_key = f"{event.chat_id}_{message.id}"
        # إرسال الإشارة الأصلية وتخزين الرسالة المرسلة
        sent_message = await client.send_message(destination_channel, message)
        # تخزين معرف الرسالة المرسلة في القناة الوجهة
        signals[signal_key] = sent_message

    # تحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
    elif is_update(message.text):
        # محاولة العثور على الرسالة الأصلية بناءً على القناة ومعرف الرسالة
        for original_signal_key, original_message in signals.items():
            # إذا كان معرف القناة ومعرف الرسالة متطابقين مع الإشارة الأصلية
            if f"{event.chat_id}_{message.reply_to_msg_id}" == original_signal_key:
                await client.send_message(destination_channel, message, reply_to=original_message.id)
                break

    # إذا كانت الرسالة ليست إشارة ولا تعديل، ننسخ الرسالة كما هي
    else:
        await client.send_message(destination_channel, message)

# تشغيل العميل
client.run_until_disconnected()