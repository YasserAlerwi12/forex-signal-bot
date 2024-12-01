import sqlite3
from config import DB_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """إنشاء جداول قاعدة البيانات إذا لم تكن موجودة"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                signal_type TEXT,
                entry_price_min REAL,
                entry_price_max REAL,
                stop_loss REAL,
                tp_levels TEXT,
                currency_pair TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_signal(self, message_id, signal_type, entry_price_min, entry_price_max, 
                   stop_loss, tp_levels, currency_pair, status='open'):
        """حفظ إشارة جديدة في قاعدة البيانات"""
        self.cursor.execute('''
            INSERT INTO signals (
                message_id, signal_type, entry_price_min, entry_price_max,
                stop_loss, tp_levels, currency_pair, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, signal_type, entry_price_min, entry_price_max,
              stop_loss, ",".join(map(str, tp_levels)), currency_pair, status))
        self.conn.commit()

    def update_signal_status(self, message_id, status):
        """تحديث حالة الإشارة"""
        self.cursor.execute('''
            UPDATE signals 
            SET status = ? 
            WHERE message_id = ?
        ''', (status, message_id))
        self.conn.commit()

    def get_open_signals(self):
        """استرجاع جميع الإشارات المفتوحة"""
        self.cursor.execute('SELECT * FROM signals WHERE status = "open"')
        return self.cursor.fetchall()

    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        self.conn.close()
