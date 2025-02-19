from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

start_time = None  # タイマー開始時間
results = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@socketio.on('start_timer')
def start_timer():
    global start_time, results
    start_time = time.time()  # タイマー開始時刻を記録
    results = {}  # リセット
    emit('timer_started', start_time, broadcast=True)

@socketio.on('submit_time')
def submit_time(data):
    user = data['user']
    press_time = data['time']

    # 小数点以下3桁にフォーマット
    formatted_time = float("{:.3f}".format(press_time))
    results[user] = formatted_time

    emit('update_results', results, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
