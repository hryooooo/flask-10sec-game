from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

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
    print("タイマー開始イベントを受信")
    start_time = int(time.time() * 1000)  # 秒→ミリ秒に変換
    results = {}  # リセット
    emit('timer_started', start_time, broadcast=True)  # ミリ秒単位で送信

@socketio.on('submit_time')
def submit_time(data):
    user = data['user']
    press_time = data['time']

    # 小数点以下3桁にフォーマット
    formatted_time = float("{:.3f}".format(press_time))
    results[user] = formatted_time

    # adminに結果を送信
    emit('update_results', results, room="admin_room")

# 管理者の接続を受け入れる
@socketio.on('connect')
def connect():
    if request.path == '/admin':
        # 管理者が接続した場合、admin_roomに参加
        join_room("admin_room")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
