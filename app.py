from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import time
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

start_time = None  # タイマー開始時刻（ミリ秒）
results = {}  # 各ユーザーの結果
timer_running = False  # タイマーの実行状態

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@socketio.on('start_timer')
def start_timer():
    global start_time, results, timer_running
    start_time = int(time.time() * 1000)  # サーバー時刻（ミリ秒）
    results = {}  # 結果をリセット
    timer_running = True  # タイマー開始

    emit('timer_started', start_time, broadcast=True)  # クライアントに送信
    socketio.start_background_task(send_server_time)  # サーバー時刻の送信を開始

def send_server_time():
    while timer_running:
        try:
            current_time = int(time.time() * 1000)  # 現在時刻（ミリ秒）
            socketio.emit('server_time_update', current_time, broadcast=True)
            eventlet.sleep(0.1)  # 100msごとに更新
        except Exception as e:
            print(f"Error in send_server_time: {e}")
            break  # エラーが発生したらループを抜ける

@socketio.on('submit_time')
def submit_time(data):
    global timer_running
    user = data['user']
    press_time = int(time.time() * 1000)  # 押された時のサーバー時刻（ミリ秒）

    elapsed = (press_time - start_time) / 1000  # 経過時間（秒）
    results[user] = round(elapsed, 3)

    emit('update_results', results, broadcast=True)
    timer_running = False  # タイマー停止

@socketio.on('connect')
def handle_connect():
    join_room("admin_room")
    emit('update_results', results, room="admin_room")

@socketio.on('admin_start_timer')
def admin_start_timer():
    start_timer()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
