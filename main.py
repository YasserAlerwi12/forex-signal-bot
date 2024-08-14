from telethon.sync import TelegramClient
import os
import logging

# إعداد التسجيل لتتبع الأخطاء والمعلومات
logging.basicConfig(level=logging.INFO)

# قراءة القيم من المتغيرات البيئية
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE_NUMBER')

# التحقق من أن جميع القيم موجودة
if not api_id or not api_hash or not phone:
    raise ValueError("API_ID, API_HASH, and PHONE_NUMBER must be set as environment variables.")

# إنشاء جلسة Telegram
client = TelegramClient(phone, api_id, api_hash)

async def main():
    # تسجيل الدخول
    await client.start(phone)
    
    logging.info("Client started and connected.")
    
    # هنا يمكنك إضافة الكود الخاص بمتابعة القنوات ونقل الرسائل
    # مثال:
    async for message in client.iter_messages('source_channel'):
        if 'link' not in message.message:  # تجاهل الرسائل التي تحتوي على روابط
            await client.send_message('destination_channel', message)

# تشغيل العميل والتأكد من بقاء الاتصال قائماً
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
