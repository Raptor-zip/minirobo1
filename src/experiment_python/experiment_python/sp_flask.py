from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# cors_allowed_originは本来適切に設定するべき
socketio = SocketIO(app, cors_allowed_origins='*')

# ユーザー数
user_count = 0
# 現在のテキスト
text = ""

@app.route('/')
def index():
    return render_template('sp.html')

# ユーザーが新しく接続すると実行
@socketio.on('connect')
def connect(auth):
    global user_count, text
    user_count += 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)

# ユーザーの接続が切断すると実行
@socketio.on('disconnect')
def disconnect():
    global user_count
    user_count -= 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)

@socketio.on('state')
def connect(json):
    global user_count, text
    print(json["angle"])
    # print(json["sp_battery_level"])

cert_path = '/cert.pem'
key_path = '/key.pem'

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', port=5001, debug=True,ssl_context=(cert_path, key_path))