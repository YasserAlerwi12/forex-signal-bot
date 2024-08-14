import os
from telethon import TelegramClient, events

# الحصول على متغيرات البيئة من Heroku
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
phone_number = os.environ.get('PHONE_NUMBER')

# إنشاء جلسة جديدة مع Telegram
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # بدء الجلسة مع Telegram
    await client.start(phone_number)

    # مراقبة الرسائل الجديدة في القنوات المحددة
    @client.on(events.NewMessage(chats=['suemhFyB0m4zYTg0']))
    async def handler(event):
        message = event.message.message
        
        # تحقق من أن الرسالة لا تحتوي على روابط
        if 'http' not in message and 'https' not in message:
            # إرسال الرسالة إلى قناتك
            await client.send_message('xT-LSNPSRSYyNzVk', message)
            
            # متابعة الرسائل التي تشير إلى الإشارة الأصلية
            print(f"Message forwarded: {message}")

    # تشغيل السكريبت بشكل دائم
    await client.run_until_disconnected()

# تشغيل السكريبت
with client:
    client.loop.run_until_complete(main())
