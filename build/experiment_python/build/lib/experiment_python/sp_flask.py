import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import threading
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# cors_allowed_originは本来適切に設定するべき
socketio = SocketIO(app, cors_allowed_origins='*')

# ユーザー数
user_count = 0

def main():
    threading.Thread(target=flask_socketio_run).start()
    # threading.Thread(target=publish).start()
    # flask_socketio_run()
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     # executor.submit(publish)
    #     future = executor.submit(flask_socketio_run)
    #     future.result()         # 全てのタスクが終了するまで待つ

def flask_socketio_run():
    print("flask_socketio_run起動", flush=True)
    cert_path = '/cert.pem'
    key_path = '/key.pem'
    socketio.run(app,host='0.0.0.0', port=5001, debug=True,use_reloader=False,threaded=False,certfile=cert_path, keyfile=key_path)
#,ssl_context=(cert_path, key_path)

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
        self.publisher_sp_to_ubuntu = self.create_publisher(String, 'sp_to_ubuntu', 10)
        self.timer_0001 = self.create_timer(0.001, self.timer_callback_0001)

    def timer_callback_0001(self):
        print("kita",flush=True)

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

if __name__ == '__main__':
    main()