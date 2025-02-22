from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import time
import eventlet

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
    start_time = time.time()  # サーバー開始時刻（秒単位）
    results = {}  # 結果をリセット
    emit('timer_started', start_time, broadcast=True)  # すべてのクライアントに送信

@socketio.on('submit_time')
def submit_time(data):
    global start_time
    user = data['user']
    user_elapsed = data['elapsed']  # ユーザーが計測した経過時間
    client_start_time = data['start_time']  # クライアントのタイマー開始時刻
    
    # サーバー開始時刻とクライアント開始時刻の差を補正
    corrected_time = user_elapsed + (start_time - client_start_time)
    
    # 結果を小数点以下3桁にフォーマットして保存
    results[user] = round(corrected_time, 4)  # 小数点以下4桁で保存
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
