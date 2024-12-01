import uuid
import json
import socket
import ssl
from config import (
    CTRADER_CLIENT_ID,
    CTRADER_CLIENT_SECRET,
    CTID_TRADER_ACCOUNT_ID,
    TELEGRAM_TOKEN,
    CHAT_ID
)

class CTradingAPI:
    def __init__(self, host='demo.ctraderapi.com', port=5035):
        self.host = host
        self.port = port
        self.context = ssl.create_default_context()

    def _send_request(self, message):
        """إرسال طلب إلى خادم cTrader"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s = self.context.wrap_socket(s, server_hostname=self.host)
            s.connect((self.host, self.port))
            s.sendall(message.asJsonString().encode('utf-8'))
            return s.recv(1024)

    def authenticate(self):
        """مصادقة التطبيق مع cTrader"""
        auth_req = ApplicationAuthReq(CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET)
        return self._send_request(auth_req)

    def place_order(self, symbol_id, order_type, trade_side, volume):
        """إنشاء أمر تداول جديد"""
        order_req = OrderRequest(
            CTID_TRADER_ACCOUNT_ID,
            symbol_id,
            order_type,
            trade_side,
            volume
        )
        return self._send_request(order_req)

    def send_message(self, message):
        """إرسال رسالة إلى تليجرام"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=params)
        return response.json()

class OpenAPIMessage:
    def __init__(self):
        self.client_msg_id = str(uuid.uuid4())

    def asJsonString(self):
        return json.dumps({
            "clientMsgId": self.client_msg_id,
            "payloadType": self.payloadType,
            "payload": self.payload
        })

class ApplicationAuthReq(OpenAPIMessage):
    def __init__(self, client_id, client_secret):
        super().__init__()
        self.payloadType = 2100
        self.payload = {
            "clientId": client_id,
            "clientSecret": client_secret
        }

class OrderRequest(OpenAPIMessage):
    def __init__(self, account_id, symbol_id, order_type, trade_side, volume):
        super().__init__()
        self.payloadType = 2200
        self.payload = {
            "accountId": account_id,
            "symbolId": symbol_id,
            "orderType": order_type,
            "tradeSide": trade_side,
            "volume": volume
        }
