from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# وظيفة للاتصال بقاعدة البيانات وجلب الإشارات
def get_signals():
    conn = sqlite3.connect('trading_signals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT signal_type, entry_price, tp_levels, stop_loss FROM signals WHERE status = 'open'")
    signals = cursor.fetchall()
    conn.close()
    
    signal_list = []
    for signal in signals:
        signal_dict = {
            'signal_type': signal[0],
            'entry_price': signal[1],
            'tp_levels': signal[2].split(','),  # تحويل TP levels من سلسلة إلى قائمة
            'stop_loss': signal[3]
        }
        signal_list.append(signal_dict)
    
    return signal_list

# API لإرجاع الإشارات بصيغة JSON
@app.route('/get_signals', methods=['GET'])
def get_signals_api():
    signals = get_signals()
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True)
