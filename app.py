from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

start_time = None  # タイマー開始時間
results = {}  # ユーザーの結果を保存

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@socketio.on('start_timer')
def start_timer():
    global start_time, results
    start_time = int(time.time() * 1000)  # ミリ秒単位
    results = {}  # 結果をリセット
    emit('timer_started', start_time, broadcast=True)  # すべてのクライアントに送信

@socketio.on('submit_time')
def submit_time(data):
    user = data['user']
    press_time = data['time']
    results[user] = round(press_time, 3)
    emit('update_results', results, room="admin_room")

@socketio.on('connect')
def handle_connect():
    join_room("admin_room")
    emit('update_results', results, room="admin_room")

@socketio.on('admin_start_timer')
def admin_start_timer():
    start_timer()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
