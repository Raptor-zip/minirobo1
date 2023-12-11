import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
import serial # serial通信用
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor
from flask import Flask, render_template, request # Flaskを使うため
import json # jsonを使うため
import webbrowser # webbrowserを開くため
import ipget # ipアドレスを取得するため
import logging # Flaskのログを削除する
import time # sleep使うため
import cv2
import base64
cap = cv2.VideoCapture(0)
img_str = "data:image/jpeg;base64だよ"
from flask_socketio import SocketIO, emit, join_room, leave_room, \
      close_room, rooms, disconnect

ser = None

global_value = 100
joy_pub = ""
serial_reception_text = [""]

ip = ipget.ipget()
# print(ip, flush=True)
# print(ip.ipaddr('eth0'))    # 有線IP
# print(ip.ipaddr('wlan0'))    # 無線IP
url = f"http://{ip}:5000/"

# ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
# print(ip, flush=True)


l = logging.getLogger()
l.addHandler(logging.FileHandler("/dev/null"))
app = Flask(__name__,
            template_folder="../../../../../../src/experiment_python/experiment_python/flask/templates",
            static_folder="../../../../../../src/experiment_python/experiment_python/flask/static") #Flaskが実行されるディレクトリがきもい
app.config['SECRET_KEY'] = 'secret!'

# cors_allowed_originは本来適切に設定するべき
# socketio = SocketIO(app, cors_allowed_origins='*')
socketio = SocketIO(app, cors_allowed_origins='*') # , async_mode='eventlet'

# ユーザー数
user_count = 0
# 現在のテキスト
text = ""

# webbrowser.open(url, 0)# デフォルトブラウザでWebサイトを新しいタブで開く

##############################################################

def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        # executor.submit(camera_get)
        # executor.submit(publish)
        executor.submit(serial_reception)
        # executor.submit(flask_run)
        # executor.submit(flask_socketio_run)
        future = executor.submit(publish)
        future.result()         # 全てのタスクが終了するまで待つ
        future2 = executor.submit(flask_socketio_run)
        future2.result()         # 全てのタスクが終了するまで待つ

@socketio.event
def image_ud():
    global img_str
    try:
        emit('image_update', {'image': img_str}, broadcast=True)
        emit('count_update', {'user_count': 20}, broadcast=True)
    except Exception as e:
        print(f"67エラー:{e}", flush=True)

def camera_get():
    print("camera_get起動", flush=True)
    global img_str
    while True:
        ret, frame = cap.read()
        cv2.imshow('camera' , frame)
        _, encoded = cv2.imencode(".jpg", frame)
        img_str = base64.b64encode(encoded).decode("ascii")
        cv2.waitKey(1)

        print("0.5秒おき", flush=True)
        try:
            print("81", flush=True)
            # image_ud()
            # emit('count_update', {'user_count': 30}, broadcast=True)
        except Exception as e:
            print(f"84エラー:{e}", flush=True)
        # image_ud()
        # time.sleep(0.033) # これないとCPU使用率が増える
        # time.sleep(0.0166) # これないとCPU使用率が増える
        time.sleep(0.2) # これないとCPU使用率が増える


thread = None

def flask_socketio_run():
    print("flask_socketio_run起動", flush=True)
    # socketio.run(app, debug=True, host="0.0.0.0", port=5000use_reloader=False,  allow_unsafe_werkzeug=True)
    # 非同期処理に使用するライブラリの指定
    # `threading`, `eventlet`, `gevent`から選択可能
    socketio.run(app, host="0.0.0.0", port=5000,) # , threaded=Trueやると起動しない  async_mode="threading"

    # スレッドを格納するためのグローバル変数


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
            Int16MultiArray,
            "joy_pub",
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.01  # seconds 0.01
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        global ser
        global global_value
        global joy_pub
        # print("きてる",flush=False)
        # serialCommand = "{'states':1,'motor1':{'speed':100},'motor2':{'speed':100},'motor3':{'angle':95},'motor4':{'speed':100}}\n"
        # serialCommand = f"{{'motor1':{{'speed':{global_value}}}}}\n"
        serialCommand = f"{{'motor1':{{'speed':{joy_pub}}}}}\n"
        # serialCommand = joy_pub+ "\n"
        # print(serialCommand,flush=False)
        if ser != None: # 未接続でなければ
            ser.write(serialCommand.encode()) # 書き込む
            # print("書き込む完了",flush=False)
        else:
            print("ESP32未接続",flush=False)

    def listener_callback(self, msg):
        print("サブすくした",flush=False)
        global global_value
        global joy_pub
        joy_pub = msg.data[0]
        # self.get_logger().info('I heard: "%d"' % msg.data[0])


##############################################################

def serial_reception():
    global ser
    while True:
        try:
            ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=5)
            print("マイコンとSerial接続成功", flush=True)
            break  # Serialが正常に開かれた場合はループを抜ける
        except Exception as e:
            print(f"マイコンとSerial接続失敗: {e}", flush=True)
            time.sleep(1)  # 1秒待って再試行
            # 自動的に/dev/ttyUSB1につなげるようにするのもいいかも
    global serial_reception_text
    while True:
        try:
            line = ser.readline()
            # line = ser.readline().decode('utf-8')
            # print(line, flush=True)
            # \n消したほうがいい気が
        except UnicodeDecodeError as e:
            # print("エンコードエラー")
            # print(line)
            print(f"デコードエラー:{e}", flush=True)
        serial_reception_text.insert(0, line)
        if len(serial_reception_text) > 100:
            del serial_reception_text[-1]
        time.sleep(0.002) # これないとCPU使用率が増える

##############################################################

class Data: # クラスを作成する
    def __init__(self, motor_1, motor_2, motor_3):
        self.motor_1 = motor_1
        self.motor_2 = motor_2
        self.motor_3 = motor_3

@app.route("/")
def index():
    data = Data(motor_1='190', motor_2=180, motor_3=100) # インスタンスの作成
    return render_template('index.html', gafa=data) # インスタンスをテンプレートに渡す

# flaskからPOSTでうけとったデータをpublishする
@app.route("/data_call_from_ajax", methods = ["POST"])
def datacallfromajax():
    global global_value
    if request.method == "POST":
        # ここにPythonの処理を書く
        try:
            global_value = int(request.form["data"])
            print(global_value, flush=True)
            message = f"値更新OK"
        except Exception as e:
            message = str(e)
        dict = {"data": message}      # 辞書
    return json.dumps(dict)             # 辞書をJSONにして返す

# subscribeしたデータに合わせてflaskを更新する
# @app.route("/stream_call_from_ajax", methods = ["POST"])
# def streamcallfromajax():
#     global serial_reception_text
#     global img_str

#     if request.method == "POST":
#         # ここにPythonの処理を書く
#         try:
#             message = serial_reception_text
#             # message = "aiueo"
#         except Exception as e:
#             message = str(e)
#         dict = {
#             # "data": message,
#             "image": img_str
#                 }

        # いるかわからないけど
        # スマホが何台か増えたときに負担が増えすぎるから困る
        # serialCommand = f"{{'motor1':{{'speed':{global_value}}}}}+\n"
        # ser.write(serialCommand.encode())

    # return json.dumps(dict)             # 辞書をJSONにして返す]





# ユーザーが新しく接続すると実行
@socketio.on('connect')
def connect(auth):
    print("connctされた")
    global user_count, text, img_str
    user_count += 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)
    image_ud()
    # テキストエリアの更新
    # emit('text_update', {'text': text})/


# ユーザーの接続が切断すると実行
@socketio.on('disconnect')
def disconnect():
    global user_count
    user_count -= 1
    # 接続者数の更新（全員向け）
    emit('count_update', {'user_count': user_count}, broadcast=True)
    image_ud()



# テキストエリアが変更されたときに実行
@socketio.on('text_update_request')
def text_update_request(json):
    global text
    text = json["text"]
    # 変更をリクエストした人以外に向けて送信する
    # 全員向けに送信すると入力の途中でテキストエリアが変更されて日本語入力がうまくできない
    emit('text_update', {'text': text}, broadcast=True, include_self=False)
    image_ud()

##############################################################

# @socketio.on('connect', namespace='/test')
# def test_connect():
#     global thread
#     if thread is None:
#         thread = socketio.start_background_task(target=background_thread)
#     emit('my response', {'data': 'Connected', 'count': 0})

# @socketio.on('my event', namespace='/test')
# def test_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my response',
#          {'data': message['data'], 'count': session['receive_count']})

# @socketio.on('my broadcast event', namespace='/test')
# def test_broadcast_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)

# @socketio.on('my ping', namespace='/test')
# def ping_pong():
#     emit('my pong')
# thread = socketio.start_background_task(target=background_thread)

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         socketio.sleep(10)
#         count += 1
#         socketio.emit('my response',
#                       {'data': 'Server generated event', 'count': count},
#                       namespace='/test')

if __name__ == '__main__':
    main()


