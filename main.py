import os
from telethon import TelegramClient, events

# الحصول على متغيرات البيئة من Heroku
api_id = os.environ.get('22301177')
api_hash = os.environ.get('5a3f28febb80ee1d2ba92e12ee6b4c40')
phone_number = os.environ.get('+967774530312')

# إنشاء جلسة جديدة مع Telegram
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start(phone_number)

    # مراقبة الرسائل الجديدة في القنوات المحددة
    @client.on(events.NewMessage(chats=['https://t.me/+suemhFyB0m4zYTg0']))
    async def handler(event):
        message = event.message.message
        
        # تحقق من أن الرسالة لا تحتوي على روابط
        if 'http' not in message and 'https' not in message:
            # إرسال الرسالة إلى قناتك
            await client.send_message('https://t.me/+xT-LSNPSRSYyNzVk', message)
            
            # متابعة الرسائل التي تشير إلى الإشارة الأصلية
            # هنا يمكن استخدام منطق إضافي لمتابعة الرسائل المتعلقة
            print(f"Message forwarded: {message}")

    # تشغيل السكريبت بشكل دائم
    await client.run_until_disconnected()

# تشغيل السكريبت
with client:
    client.loop.run_until_complete(main())
