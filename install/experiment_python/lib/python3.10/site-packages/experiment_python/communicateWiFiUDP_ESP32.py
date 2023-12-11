import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
from std_msgs.msg import UInt8 # state用
from std_msgs.msg import String
import json # jsonを使うため
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor
import playsound
import asyncio
import time
motor_speed=[0,0,0,0]
reception_json = {}
joy_pub = ""
serial_reception_text = [""]

state = 0

import socket

# ESP32のIPアドレスとポート番号
esp32_ip = "192.168.160.78"
esp32_port = 12345

# UDPソケットの作成
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ローカルポート番号
local_port = 12346

# ローカルUDPソケットの作成
local_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_udp_socket.bind(('0.0.0.0', local_port))

local_udp_socket.settimeout(1.0)  # タイムアウトを1秒に設定

# try:
print(f"Listening for UDP packets on 0.0.0.0:{local_port}", flush=True)

def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(udp_reception)
        executor.submit(battery_alert)
        executor.submit(auto_driving_feedback)
        future = executor.submit(ros)
        future.result()         # 全てのタスクが終了するまで待つ

def udp_reception():
    global local_udp_socket
    global reception_json
    global battery_alert_music
    while True:
        try:
            # データを受信
            data, addr = local_udp_socket.recvfrom(1024)
            # print(f"Received {addr}: {data.decode('utf-8')}",flush=True)
            reception_json_temp = json.loads(data.decode('utf-8'))
            reception_json.update(reception_json_temp)

            # 角度を取得する
            # 距離を取得する
        except Exception as e:
            print("ESP32から受信に失敗",flush=True)
            reception_json["battery_voltage"] = 0

def auto_driving_feedback():
    global reception_json
    # while True:


def battery_alert():
    global reception_json
    temp = 0
    while True:
        if "battery_voltage" in reception_json and reception_json["battery_voltage"] < 10 and reception_json["battery_voltage"] > 5:
            temp+=1
            if temp > 3:
                playsound.playsound("battery_alert.mp3")
        else:
            temp = 0
        time.sleep(0.2) # 無駄にCPUを使わないようにする

def ros(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()

class MinimalSubscriber(Node):
    motor1_speed = 0
    motor2_speed = 0
    motor3_speed = 0
    motor4_speed = 0
    state = 1

    def __init__(self):
        global reception_json
        print("Subscriber",flush=True)
        super().__init__('command_subscriber')
        self.publisher_ESP32_to_Webserver = self.create_publisher(String, 'ESP32_to_Webserver', 10)
        self.publisher_state = self.create_publisher(UInt8, 'state', 10)
        self.subscription = self.create_subscription(
            Int16MultiArray,
            "Drive_Controller_Node",
            self.Drive_listener_callback,
            10)
        self.subscription = self.create_subscription(
            Int16MultiArray,
            "Collect_Controller_Node",
            self.Collect_listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.01  # seconds 0.01
        # 0.001でも試す！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        global motor_speed
        global reception_json

        msg = UInt8()
        msg.data = self.state
        self.publisher_state.publish(msg)

        serialCommand = f"{{'motor1':{{'speed':{self.motor1_speed}}},'motor2':{{'speed':{self.motor2_speed}}},'motor3':{{'speed':{self.motor3_speed}}},'motor4':{{'speed':{self.motor4_speed}}}}}\n"

        serialCommand = serialCommand.encode()

        # データをESP32に送信
        udp_socket.sendto(serialCommand, (esp32_ip, esp32_port))
        # print(f"Sent {esp32_ip}:{esp32_port} {serialCommand}",flush=True)

        msg = String()
        msg.data = json.dumps(reception_json)
        self.publisher_ESP32_to_Webserver.publish(msg)



    def Drive_listener_callback(self, msg):
        # self.get_logger().info('Received: {}'.format(msg.data))
        self.motor1_speed = msg.data[0]
        self.motor2_speed = msg.data[1]
        self.motor3_speed = msg.data[2]
        self.motor4_speed = msg.data[3]

    def Collect_listener_callback(self, msg):
        # self.get_logger().info('Received: {}'.format(msg.data))
        self.motor3_speed = msg.data[0]
        self.motor4_speed = msg.data[1]

if __name__ == '__main__':
    main()