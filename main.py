import os
from telethon import TelegramClient, events

# قراءة المتغيرات البيئة
api_id = os.getenv('22301177')
api_hash = os.getenv('5a3f28febb80ee1d2ba92e12ee6b4c40')
phone_number = os.getenv('+967774530312')  # أو يمكن استخدام توكن البوت هنا

# إنشاء العميل باستخدام المتغيرات
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start(phone=lambda: phone_number)  # استخدام رقم الهاتف من المتغير البيئة

    @client.on(events.NewMessage(chats=('suemhFyB0m4zYTg0')))
    async def handler(event):
        if not event.message.message:
            return

        # إرسال الرسالة إلى القناة الأخرى
        await client.send_message('xT-LSNPSRSYyNzVk', event.message.message)

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
