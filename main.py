import re
import logging
from telethon import TelegramClient, events
from ctrader_open_api.messages.OpenApiMessages_pb2 import (
    ProtoOAOrderType,
    ProtoOATradeSide
)
from twisted.internet import reactor
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_PHONE_NUMBER,
    TELEGRAM_CHANNEL_IDS,
    CURRENCY_PAIRS,
    SIGNAL_PATTERN,
    TP_PATTERN,
    SL_PATTERN
)
from database import Database
from api import CTradingAPI

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ForexSignalBot:
    def __init__(self):
        self.db = Database()
        self.ctrader = CTradingAPI()
        self.telegram = TelegramClient(
            'session_name',
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH
        )
        self.setup_telegram_handlers()

    def setup_telegram_handlers(self):
        """إعداد معالجات أحداث Telegram"""
        @self.telegram.on(events.NewMessage(chats=TELEGRAM_CHANNEL_IDS))
        async def handle_new_message(event):
            await self.process_signal(event.message)

    async def process_signal(self, message):
        """معالجة إشارة تداول جديدة"""
        try:
            signal_data = self.parse_signal(message.text)
            if signal_data:
                self.db.save_signal(**signal_data, message_id=message.id)
                await self.execute_trade(signal_data)
                logger.info(f"تم معالجة الإشارة: {signal_data}")
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {str(e)}")

    def parse_signal(self, text):
        """تحليل نص الإشارة لاستخراج المعلومات"""
        signal_match = re.search(SIGNAL_PATTERN, text, re.IGNORECASE)
        if not signal_match:
            return None

        tp_levels = [float(tp) for tp in re.findall(TP_PATTERN, text)]
        sl_match = re.search(SL_PATTERN, text)

        return {
            'signal_type': signal_match.group(1).upper(),
            'currency_pair': signal_match.group(2),
            'entry_price_min': float(signal_match.group(3)),
            'entry_price_max': float(signal_match.group(4)) if signal_match.group(4) else float(signal_match.group(3)),
            'stop_loss': float(sl_match.group(1)) if sl_match else None,
            'tp_levels': tp_levels
        }

    async def execute_trade(self, signal_data):
        """تنفيذ الصفقة على منصة cTrader"""
        if signal_data['currency_pair'] not in CURRENCY_PAIRS:
            logger.warning(f"زوج العملات غير مدعوم: {signal_data['currency_pair']}")
            return

        symbol_id = CURRENCY_PAIRS[signal_data['currency_pair']]
        trade_side = (ProtoOATradeSide.BUY if signal_data['signal_type'] == 'BUY'
                     else ProtoOATradeSide.SELL)

        try:
            response = self.ctrader.place_order(
                symbol_id=symbol_id,
                order_type=ProtoOAOrderType.MARKET,
                trade_side=trade_side,
                volume=0.01  # حجم افتراضي، يمكن تعديله حسب الحاجة
            )
            logger.info(f"تم إرسال الأمر: {response}")
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة: {str(e)}")

    async def start(self):
        """بدء تشغيل البوت"""
        await self.telegram.start(phone=TELEGRAM_PHONE_NUMBER)
        logger.info("تم بدء تشغيل بوت إشارات الفوركس")
        await self.telegram.run_until_disconnected()

if __name__ == "__main__":
    bot = ForexSignalBot()
    reactor.run()
