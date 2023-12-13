import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor

from flask import Flask, render_template, request # Flaskを使うため
import webbrowser # webbrowserを開くため
import ipget # ipアドレスを取得するため
import logging # Flaskのログを削除する
import json

from threading import Lock
import time
thread_lock = Lock()

from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

ip = ipget.ipget()
# print(ip, flush=True)
# print(ip.ipaddr('eth0'))    # 有線IP
# print(ip.ipaddr('wlan0'))    # 無線IP
url = f"http://{ip}:5000/"

# ユーザー数
user_count = 0
# 現在のテキスト
text = ""
serial_reception_text = [""]
img_str = "data:image/jpeg;base64だよ"

reception_json = {}

# webbrowser.open(url, 0)# デフォルトブラウザでWebサイトを新しいタブで開く

l = logging.getLogger()
l.addHandler(logging.FileHandler("/dev/null"))
app = Flask(__name__,
            template_folder="../../../../../../src/experiment_python/experiment_python/flask/templates",
            static_folder="../../../../../../src/experiment_python/experiment_python/flask/static") #Flaskが実行されるディレクトリがきもい
app.config['SECRET_KEY'] = 'secret!'

# cors_allowed_originは本来適切に設定するべき
# socketio = SocketIO(app, cors_allowed_origins='*')
socketio = SocketIO(app, cors_allowed_origins='*') # , async_mode='eventlet'


@socketio.event
def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        # executor.submit(publish)
        future = executor.submit(flask_socketio_run)
        future.result()         # 全てのタスクが終了するまで待つ

##############################################################

def publish(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


class MinimalSubscriber(Node):
    def __init__(self):
        print("Subscriber",flush=False)
        super().__init__('command_subscriber')
        self.subscription = self.create_subscription(
            String,
            "ESP32_to_Webserver",
            self.listener_callback,
            10)
        self.subscription = self.create_subscription(
            Joy,
            "joy1",
            self.joy_listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        global reception_json
        print("サブすくした",flush=True)
        reception_json = json.loads(msg.data)
        print(msg.data,flush=True)

    def joy_listener_callback(self, msg):
        print("女医北",flush=True)


#############################################################

def emit_data_periodically():
    global reception_json
    while True:
        print("99", flush=True)
        socketio.sleep(0.016)  # 0.016秒ごとに実行
        # time.sleep(0.016) # 無駄にCPUを使わないようにする
        # データをブロードキャスト
        with thread_lock:
            if user_count > 0:
                if hasattr(flask.request, 'namespace'):
                        namespace = Flask.request.namespace
                        print("106", flush=True)
                        emit('json', reception_json, namespace=namespace)
                        print("107", flush=True)
                # try:
                #     print("106", flush=True)
                #     emit('json', reception_json)
                #     print("107", flush=True)
                # except RuntimeError:
                #     # リクエストコンテキストが存在しない場合は無視
                #     pass



def flask_socketio_run():
    print("flask_socketio_run起動", flush=True)
    # socketio.run(app, debug=True, host="0.0.0.0", port=5000use_reloader=False,  allow_unsafe_werkzeug=True)
    # 非同期処理に使用するライブラリの指定
    # `threading`, `eventlet`, `gevent`から選択可能
    socketio.start_background_task(target=emit_data_periodically)
    socketio.run(app, host="0.0.0.0", port=5000,) # , threaded=Trueやると起動しない  async_mode="threading"

@app.route("/")
def index():
    # data = Data(motor_1='190', motor_2=180, motor_3=100) # インスタンスの作成
    return render_template('index.html') # インスタンスをテンプレートに渡す , gafa=data

# ユーザーが新しく接続すると実行
@socketio.on('connect')
def connect(auth):
    print("connctされた")
    global user_count, text, img_str
    user_count += 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)
    # テキストエリアの更新
    # emit('text_update', {'text': text})/


# ユーザーの接続が切断すると実行
@socketio.on('disconnect')
def disconnect():
    global user_count
    user_count -= 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)


@socketio.on("my ping")
def ping():
    emit('my pong', {})


if __name__ == '__main__':
    main()