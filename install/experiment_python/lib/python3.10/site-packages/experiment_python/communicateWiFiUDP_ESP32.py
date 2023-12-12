import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
from std_msgs.msg import UInt8 # state用
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import json # jsonを使うため
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor
import playsound
import time
import datetime
motor_speed=[0,0,0,0]
reception_json = {
    "raw_distance":0,
    "raw_angle":999,
    "battery_voltage":0,
    "wifi_signal_strength":0
    }
joy_pub = ""
serial_reception_text = [""]

state = 0

raw_distance = 0
distance_deviation = 0
raw_angle = 999
angle_deviation = 0

import socket

# ESP32のIPアドレスとポート番号
esp32_ip = "192.168.20.241"
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


def battery_alert():
    global reception_json
    temp = 0
    while True:
        if reception_json["battery_voltage"] < 10 and reception_json["battery_voltage"] > 5:
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
    state = 0
    assist_enable = False
    collection_enabled = False
    motor1_speed = 0
    motor2_speed = 0
    motor3_speed = 0
    motor4_speed = 0

    distance = 400 #あとで0に変えておいて
    ultrasonic_sensor_right_front_adjust = -2.5 # パラメーター調整必要
    ultrasonic_sensor_right_back_adjust = -8 # パラメーター調整必要
    ultrasonic_sensor_left_back_adjust = -8 # パラメーター調整必要

    axes_1 = 0
    axes_3 = 0

    buttons_ZR = 0
    buttons_ZL= 0
    buttons_X=0
    buttons_left=0
    buttons_right=0

    state2_start_time = 0
    state3_start_time = 0

    # 15 従事左で左回転
# 16 従事右で右回転
# 7 ZRでまっすぐ 距離センサー監視しながら
# 6 ZLで、旋回中でも、前進中でも、とまる
# 2 Xで回収機構モーター回転のオンオフ切り替え

    def __init__(self):
        global reception_json
        print("Subscriber",flush=True)
        super().__init__('command_subscriber')
        self.publisher_ESP32_to_Webserver = self.create_publisher(String, 'ESP32_to_Webserver', 10)
        self.publisher_state_sensor = self.create_publisher(Int16MultiArray, 'state_sensor', 10)
        self.subscription = self.create_subscription(
            Joy,
            "joy",
            self.joy_listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.001  # seconds 0.01
        # 0.001でも試す！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        global motor_speed
        global reception_json

        msg = Int16MultiArray()
        msg.data = [self.state, reception_json["raw_distance"], reception_json["raw_angle"]]
        self.publisher_state_sensor.publish(msg)

        serialCommand = f"{{'motor1':{{'speed':{int(self.motor1_speed)}}},'motor2':{{'speed':{int(self.motor2_speed)}}},'motor3':{{'speed':{int(self.motor3_speed)}}}}}\n"

        serialCommand = serialCommand.encode()

        # データをESP32に送信
        udp_socket.sendto(serialCommand, (esp32_ip, esp32_port))
        print(f"Sent {esp32_ip}:{esp32_port} {serialCommand}",flush=True)

        msg = String()
        msg.data = json.dumps(reception_json)
        self.publisher_ESP32_to_Webserver.publish(msg)

        if self.state == 1:
            # 前進
            if self.distance > 45:
                distance = self.distance * 5
                if distance > 255:
                    distance = 255

                distance_1 = distance -  self.axes_3
                if distance_1 > 255:
                    distance_1 = 255
                self.motor1_speed = distance_1

                distance_2 =  distance - self.axes_1
                if distance_2 > 255:
                    distance_2 = 255
                self.motor2_speed = distance_2

                distance_difference = (reception_json["ultrasonic_sensor_right_front"]+self.ultrasonic_sensor_right_front_adjust) - (reception_json["ultrasonic_sensor_right_back"]+self.ultrasonic_sensor_right_back_adjust) # 前 - 後

                if distance_difference > 0.2: # パラメーター調整必要
                    # 壁と平行じゃないなら
                    if (distance_difference > 0):
                        # 前のほうが壁と遠いなら右を遅くする
                        self.motor2_speed = self.motor2_speed - distance_difference * 5 # パラメーター調整必要
                    else:
                        # 後ろのほうが壁と遠いなら左を遅くする
                        self.motor1_speed = self.motor1_speed - distance_difference * 5 # パラメーター調整必要

                if reception_json["ultrasonic_sensor_left_back"]+self.ultrasonic_sensor_left_back_adjust > 2.5: # パラメーター調整必要
                    # 左の壁と遠いなら、左を遅くする
                    self.motor1_speed = self.motor1_speed - 20 # パラメーター調整必要


            else:
                self.motor1_speed = 0
                self.motor2_speed = 0
                self.state = 0

        if self.state == 2:
            # 左旋回
            # if (reception_json["ultrasonic_sensor_right_front"]+self.ultrasonic_sensor_right_front_adjust) - (reception_json["ultrasonic_sensor_right_back"]+self.ultrasonic_sensor_right_back_adjust) > 0.2: # パラメーター調整必要
            if (time.time() - self.state2_start_time) < 1: # パラメーター調整必要
                self.motor1_speed = 255 -  self.axes_3
                if self.motor1_speed > 255:
                    self.motor1_speed = 255

                self.motor2_speed =  -255 + self.axes_1
                if self.motor2_speed < -255:
                    self.motor2_speed = -255
            else:
                self.motor1_speed = 0
                self.motor2_speed = 0
                self.state = 0

        if self.state == 3:
            # 右旋回
            # if (reception_json["ultrasonic_sensor_left_back"]+self.ultrasonic_sensor_left_back_adjust) > 2.5: # パラメーター調整必要
            if (time.time() - self.state3_start_time) < 1: # パラメーター調整必要
                self.motor1_speed = -255 + self.axes_3
                if self.motor1_speed < -255:
                    self.motor1_speed = -255

                self.motor2_speed =  255 - self.axes_1
                if self.motor2_speed > 255:
                    self.motor2_speed = 255
            else:
                self.motor1_speed = 0
                self.motor2_speed = 0
                self.state = 0

        # print("motor1 ",self.motor1_speed,flush=True)
        # print("motor2 ",self.motor2_speed,flush=True)
        # print("motor3 ",self.motor3_speed,flush=True)
        # print(self.state,flush=True)

    def joy_listener_callback(self, joy):
        self.axes_1 = int(joy.axes[1]*64)
        self.axes_3 = int(joy.axes[3]*64)

        if self.assist_enable == False:
            # 走行補助がオフなら
            self.motor1_speed = int(joy.axes[1]*256)
            self.motor2_speed=int(joy.axes[3]*256)


        if self.buttons_ZL == 0 and joy.buttons[6] == 1:
            # オフにするだけでよくない？オンにする必要ある？^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # assist_enableいらなくない？state=0でいい気がする
            # 走行補助強制停止のオンオフ切り替え
            self.state = 0
            self.motor1_speed = 0
            self.motor2_speed =0
            self.motor3_speed=0
            self.motor4_speed=0

            self.assist_enable = False

            # if self.assist_enable == True:
            #     self.assist_enable = False
            #     self.state = 0
            # else:
            #     self.assist_enable = True

        if self.buttons_ZR == 0 and joy.buttons[7] == 1:
            # 前進
            self.state = 1


        if self.buttons_left == 0 and joy.buttons[15] == 1:
            # 左旋回
            self.state = 2
            self.state2_start_time = time.time()

        if self.buttons_right == 0 and joy.buttons[16] == 1:
            # 右旋回
            self.state = 3
            self.state3_start_time = time.time()

        if self.buttons_X == 0 and joy.buttons[2] == 1:
            # 回収機構回転のオンオフ切り替え
            # オンオフだと詰まったときに困るからジョイスティック2台目にする？!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.collection_enabled == False:
                self.motor3_speed = 255
                self.collection_enabled = True
            else:
                self.motor3_speed = 0
                self.collection_enabled = False

        self.buttons_ZR = joy.buttons[7]
        self.buttons_ZL = joy.buttons[6]
        self.buttons_X= joy.buttons[2]
        self.buttons_left= joy.buttons[15]
        self.buttons_right=joy.buttons[16]


if __name__ == '__main__':
    main()