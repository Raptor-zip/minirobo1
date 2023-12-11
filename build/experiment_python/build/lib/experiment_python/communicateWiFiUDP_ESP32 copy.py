# 12/9動いた

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
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

import socket

# ESP32のIPアドレスとポート番号
esp32_ip = "192.168.160.78"
esp32_port = 12345

# UDPソケットの作成
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ローカルポート番号
local_port = 12346

battery_alert_music = False

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

            reception_json = json.loads(data.decode('utf-8'))
            # print(reception_json["wifi_signal_strength"],flush=True)
            if reception_json["battery_voltage"] < 10 and reception_json["battery_voltage"] > 5:
                battery_alert_music = True
            else:
                battery_alert_music = False
        except Exception as e:
            print("ESP32から受信に失敗",flush=True)
            battery_alert_music = False


def battery_alert():
    global battery_alert_music
    temp = 0
    while True:
        if battery_alert_music == True:
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

    def __init__(self):
        global reception_json
        print("Subscriber",flush=True)
        super().__init__('command_subscriber')
        self.publisher = self.create_publisher(String, 'ESP32_to_Webserver', 10)
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
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        global motor_speed
        global reception_json

        serialCommand = f"{{'motor1':{{'speed':{self.motor1_speed}}},'motor2':{{'speed':{self.motor2_speed}}},'motor3':{{'speed':{self.motor3_speed}}},'motor4':{{'speed':{self.motor4_speed}}}}}\n"

        serialCommand = serialCommand.encode()

        # データをESP32に送信
        udp_socket.sendto(serialCommand, (esp32_ip, esp32_port))
        # print(f"Sent {esp32_ip}:{esp32_port} {serialCommand}",flush=True)

        msg = String()
        msg.data = json.dumps(reception_json)
        self.publisher.publish(msg)

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