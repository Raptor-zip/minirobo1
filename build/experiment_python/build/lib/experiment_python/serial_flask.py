import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
import serial # serial通信用
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor
import json # jsonを使うため

import time # sleep使うため
import cv2
import base64
cap = cv2.VideoCapture(0)
img_str = "data:image/jpeg;base64だよ"

ser = None

global_value = 100
joy_pub = ""
serial_reception_text = [""]
##############################################################

def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        # executor.submit(camera_get)
        # executor.submit(publish)
        executor.submit(serial_reception)
        future = executor.submit(publish)
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

if __name__ == '__main__':
    main()


