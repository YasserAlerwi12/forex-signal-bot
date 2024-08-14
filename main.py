import os
from telethon import TelegramClient, events

# قراءة المتغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')  # أو يمكن استخدام توكن البوت هنا

# إنشاء العميل باستخدام المتغيرات
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start(phone=lambda: phone_number)  # استخدام رقم الهاتف من المتغير البيئة

    @client.on(events.NewMessage(chats=('اسم القناة')))
    async def handler(event):
        if not event.message.message:
            return

        # إرسال الرسالة إلى القناة الأخرى
        await client.send_message('اسم القناة المستهدفة', event.message.message)

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
