

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

@client.on(events.NewMessage(chats=source_channel))
async def handle_new_message(event):
    message = event.message

    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    if contains_link(message.text):
        return

    # تحقق مما إذا كانت الرسالة تحتوي على إشارة
    if contains_signal(message.text):
        # إذا كانت رسالة تحتوي على إشارة، نقوم بتخزينها مع معرف فريد
        signal_id = message.id
        signals[signal_id] = message
        # إرسال الإشارة الأصلية
        sent_message = await client.send_message(destination_channel, message)
        # تحديث القاموس لتخزين معرف الرسالة المرسلة في القناة الوجهة
        signals[signal_id] = sent_message

    # تحقق مما إذا كانت الرسالة تعديلاً على إشارة سابقة
    elif is_update(message.text):
        # يجب أن تكون الرسالة التحديثية ردًا على الإشارة الأصلية
        for original_signal_id, original_message in signals.items():
            # نتحقق مما إذا كانت الرسالة المعدلة مرتبطة بالإشارة الأصلية
            if message.is_reply and message.reply_to_msg_id == original_signal_id:
                await client.send_message(destination_channel, message, reply_to=original_message.id)
                break

    # إذا كانت الرسالة ليست إشارة ولا تعديل، ننسخ الرسالة كما هي
    else:
        await client.send_message(destination_channel, message)

# تشغيل العميل
client.run_until_disconnected()
