import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import json # jsonを使うため
from concurrent.futures import ThreadPoolExecutor # threadPoolExecutor
import playsound # バッテリー低電圧保護ブザー用
import subprocess # SSID取得用
import time
import ipget
import socket
motor_speed=[0,0,0,0]
reception_json = {
    "raw_distance":0,
    "raw_angle":-179,
    "battery_voltage":0,
    "wifi_signal_strength":0
    }

# ESP32のIPアドレスとポート番号
esp32_ip = "192.168.20.78"
esp32_port = 12345

# UDPソケットの作成
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sp_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sp_udp_socket.bind(('127.0.0.1', 5002))
sp_udp_socket.settimeout(1.0)  # タイムアウトを1秒に設定

local_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_udp_socket.bind(('0.0.0.0', 12346))
local_udp_socket.settimeout(1.0)  # タイムアウトを1秒に設定

try:
    result = subprocess.check_output(['iwgetid', '-r'], universal_newlines=True)
    wifi_ssid=result.strip()
    # wifi_ssid= bytes(result.strip(), 'utf-8').decode('unicode-escape')
except subprocess.CalledProcessError:
    wifi_ssid="エラー"

def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(sp_udp_reception)
        # executor.submit(udp_reception)
        executor.submit(battery_alert)
        future = executor.submit(ros)
        future.result()         # 全てのタスクが終了するまで待つ

def sp_udp_reception():
    global sp_udp_socket
    global reception_json
    while True:
        try :
            message, cli_addr = sp_udp_socket.recvfrom(1024)
            # print(f"Received message : {message.decode('utf-8')}",flush=True)
            reception_json_temp = json.loads(message.decode('utf-8'))
            reception_json.update(reception_json_temp)
        except Exception as e:
            print(f"スマホから受信に失敗: {e}", flush=True)

def udp_reception():
    global local_udp_socket
    global reception_json
    while True:
        try:
            # データを受信
            data, addr = local_udp_socket.recvfrom(1024)
            # print(f"Received {addr}: {data.decode('utf-8')}",flush=True)
            reception_json_temp = json.loads(data.decode('utf-8'))
            reception_json.update(reception_json_temp)
        except Exception as e:
            print(f"ESP32から受信に失敗: {e}", flush=True)
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
    motor1_speed = 0
    motor2_speed = 0
    motor3_speed = 0
    normal_max_motor_speed = 230 # 自動運転時の最高速度

    distance_adjust = -8 # パラメーター調整必要
    current_distance =0
    angle_adjust = 0
    current_angle=0

    axes_1 = 0
    axes_3 = 0

    buttons_L=0
    buttons_R=0
    buttons_ZL =0
    buttons_ZR= 0
    buttons_home=0
    buttons_X=0
    buttons_A=0
    buttons_B=0
    buttons_Y=0
    buttons_up=0
    buttons_left =0
    buttons_down =0
    buttons_right = 0

    start_time=0

    def __init__(self):
        global reception_json
        print("Subscriber",flush=True)
        super().__init__('command_subscriber')
        self.publisher_ESP32_to_Webserver = self.create_publisher(String, 'ESP32_to_Webserver', 10)
        self.subscription = self.create_subscription(
            Joy,
            "joy1",
            self.joy1_listener_callback,
            10)
        self.subscription = self.create_subscription(
            Joy,
            "joy2",
            self.joy2_listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # 0.001でも試す！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.timer_0001 = self.create_timer(0.001, self.timer_callback_0001)
        self.timer_0016 = self.create_timer(0.016, self.timer_callback_0016)

    def timer_callback_0016(self):
        global wifi_ssid ,esp32_ip

        msg = String()
        send_json = {
            "state":self.state,
            "ubuntu_ssid":wifi_ssid,
            "ubuntu_ip":ipget.ipget().ipaddr("wlp2s0"),
            "esp32_ip":esp32_ip,
            "battery_voltage":reception_json["battery_voltage"],
            "wifi_signal_strength":reception_json["wifi_signal_strength"],
            "motor1_speed":self.motor1_speed,
            "motor2_speed":self.motor2_speed,
            "motor3_speed":self.motor3_speed,
            "distance":reception_json["raw_distance"]+ self.distance_adjust,
            # "angle":,
            "raw_angle":0,
            "start_time":self.start_time
        }
        msg.data = json.dumps(send_json)
        self.publisher_ESP32_to_Webserver.publish(msg)


    def turn(self, target_angle):
        # 0°に旋回
        # print("現在角度",self.current_angle,flush=True)
        # print(target_angle - self.current_angle,flush=True)
        if abs(self.current_angle - target_angle) < 2: # この判定ゆるくする！！！！！！！！！！！！！！！！
            # 止まる
            self.motor1_speed = 0
            self.motor2_speed = 0
            self.state = 0
        elif abs(target_angle - self.current_angle) > 180:
            # 右旋回
            # print("右旋回",flush=True)
            self.motor1_speed = (target_angle - self.current_angle) * -5
            self.motor2_speed = (target_angle - self.current_angle) * 5
            if self.motor1_speed < -1 * self.normal_max_motor_speed:
                self.motor1_speed = -1 * self.normal_max_motor_speed - self.axes_3 + self.axes_1
                if self.motor1_speed < -1* 255:
                    self.motor1_speed = -1 * 255
            elif self.motor1_speed > self.normal_max_motor_speed:
                self.motor1_speed = self.normal_max_motor_speed - self.axes_3 + self.axes_1
                if self.motor1_speed > 255:
                    self.motor1_speed = 255

            if self.motor2_speed > self.normal_max_motor_speed:
                self.motor2_speed = self.normal_max_motor_speed + self.axes_1 - self.axes_3
                if self.motor2_speed > 255:
                    self.motor2_speed = 255
            elif self.motor2_speed < -1 * self.normal_max_motor_speed:
                self.motor2_speed = -1 * self.normal_max_motor_speed + self.axes_1 - self.axes_3
                if self.motor2_speed < -1*255:
                    self.motor2_speed = -1*255

        else:
            # 左旋回
            # print("左旋回",flush=True)
            self.motor1_speed = (target_angle-self.current_angle) * 5
            self.motor2_speed = (target_angle-self.current_angle) * -5
            if self.motor1_speed > self.normal_max_motor_speed:
                self.motor1_speed = self.normal_max_motor_speed + self.axes_3 - self.axes_1
                if self.motor1_speed > 255:
                    self.motor1_speed = 255
            elif self.motor1_speed < -1*self.normal_max_motor_speed:
                self.motor1_speed = -1*self.normal_max_motor_speed + self.axes_3 - self.axes_1
                if self.motor1_speed < -1*255:
                    self.motor1_speed = -1*255

            if self.motor2_speed < -1*self.normal_max_motor_speed:
                self.motor2_speed = -1*self.normal_max_motor_speed - self.axes_1 + self.axes_3
                if self.motor2_speed < -1*255:
                    self.motor2_speed = -1*255
            elif self.motor2_speed > self.normal_max_motor_speed:
                self.motor2_speed = self.normal_max_motor_speed - self.axes_1 + self.axes_3
                if self.motor2_speed > 255:
                    self.motor2_speed = 255

    def straight(self, target_angle):
        if  self.current_distance > 30:
            distance = self.current_distance * 5
            if distance > self.normal_max_motor_speed:
                distance = self.normal_max_motor_speed

            distance_1 = distance -  self.axes_3
            if distance_1 > 255:
                distance_1 = 255
            self.motor1_speed = distance_1

            distance_2 =  distance - self.axes_1
            if distance_2 > 255:
                distance_2 = 255
            self.motor2_speed = distance_2

            target_plus_180 = target_angle + 180
            if target_plus_180 > 360:
                target_plus_180 = 360 - target_angle

            angle_difference =  abs(self.current_angle - target_angle)
            if angle_difference > 180:
                angle_difference = 360 - abs(self.current_angle-target_angle)

            if target_angle > 180:
                if target_plus_180 <= self.current_angle <= target_angle:
                    angle_difference =  angle_difference*-1
            else:
                if target_angle <= self.current_angle <= target_plus_180:
                    pass
                else:
                    angle_difference =  angle_difference*-1

            # print(angle_difference,flush=True)

            # モーターがマイナス言った場合の処理加える！！ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
            if abs(angle_difference) > 2: # 単位:° パラメーター調整必要
                # 壁と平行じゃないなら
                # if target_angle == 0:
                if angle_difference > 0:
                    # 右に傾いているなら
                    self.motor1_speed = self.motor1_speed - angle_difference * 2 # パラメーター調整必要
                else:
                    # 左に傾いているなら
                    self.motor2_speed = self.motor2_speed - abs(angle_difference * 2) # パラメーター調整必要

                # if target_angle == 90:
                #     if angle_difference > 0:
                #         # 右に傾いているなら
                #         self.motor1_speed = self.motor1_speed - angle_difference * 2 # パラメーター調整必要
                #     else:
                #         # 左に傾いているなら
                #         self.motor2_speed = self.motor2_speed - abs(angle_difference * 2) # パラメーター調整必要

                #     # if angle_difference > 0:
                #     #     if 270 > self.current_angle:
                #     #         self.motor1_speed = self.motor1_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                #     #     else:
                #     #         self.motor2_speed = self.motor2_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                #     # else:
                #     #     self.motor2_speed = self.motor2_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                # if target_angle == 180:
                #     if target_angle - self.current_angle < 0:
                #         self.motor1_speed = self.motor1_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                #     else:
                #         self.motor2_speed = self.motor2_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                # if target_angle == 270:
                #     if target_angle - self.current_angle < 0:
                #         self.motor1_speed = self.motor1_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                #     else:
                #         if 90 > self.current_angle:
                #             self.motor1_speed = self.motor1_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                #         else:
                #             self.motor2_speed = self.motor2_speed - target_angle - self.current_angle * 2 # パラメーター調整必要
                if self.motor1_speed > 255:
                    self.motor1_speed = 255
                elif self.motor1_speed < -1 * 255:
                    self.motor1_speed = -1 * 255
                if self.motor2_speed > 255:
                    self.motor2_speed = 255
                elif self.motor2_speed < -1 * 255:
                    self.motor2_speed = -1 * 255
        else:
            self.motor1_speed = 0
            self.motor2_speed = 0
            self.state = 0



    def timer_callback_0001(self):
        global motor_speed
        global reception_json
        # print(reception_json["raw_angle"],flush=True)
        self.current_angle = reception_json["raw_angle"] + self.angle_adjust
        if self.current_angle < 0:
            self.current_angle = 360 + self.current_angle

        # print(reception_json["raw_angle"],self.angle_adjust,self.current_angle,flush=True)

###################################################################################################
        # self.current_distance = reception_json["raw_distance"] - self.distance_adjust
        self.current_distance = 50
###################################################################################################


        if self.state == 1:
            self.turn(0)
        if self.state == 2:
            self.turn(90)
        if self.state == 3:
            self.turn(180)
        if self.state == 4:
            self.turn(270)
        if self.state == 5:
            self.straight(0)
        if self.state == 6:
            self.straight(90)
        if self.state == 7:
            self.straight(180)
        if self.state == 8:
            self.straight(270)

        print(self.state , self.motor1_speed, self.motor2_speed, self.motor3_speed,flush=True)
        # print("state  ",self.state,flush=True)
        # print("motor1 ",self.motor1_speed,flush=True)
        # print("motor2 ",self.motor2_speed,flush=True)
        # print("motor3 ",self.motor3_speed,flush=True)

        serialCommand = f"{{'motor1':{{'speed':{int(self.motor1_speed)}}},'motor2':{{'speed':{int(self.motor2_speed)}}},'motor3':{{'speed':{int(self.motor3_speed)}}}}}\n"

        serialCommand = serialCommand.encode()
        try:
            udp_socket.sendto(serialCommand, (esp32_ip, esp32_port))
        except Exception as e:
            print(f"UDP送信エラー: {e}", flush=True)
        # print(f"Sent {esp32_ip}:{esp32_port} {serialCommand}",flush=True)

    def joy1_listener_callback(self, joy):
        global reception_json
        self.axes_1 = int(joy.axes[1]*64)
        self.axes_3 = int(joy.axes[3]*64)

        if self.state == 0:
            # 走行補助がオフなら
            self.motor1_speed = int(joy.axes[1]*256)
            self.motor2_speed=int(joy.axes[3]*256)

        if joy.buttons[6] == 1:
            # 走行補助強制停止
            self.state = 0
            self.motor1_speed = 0
            self.motor2_speed =0
            self.motor3_speed=0

        if joy.buttons[7] == 1:
            # 走行補助強制停止
            self.state = 0
            self.motor1_speed = 0
            self.motor2_speed =0
            self.motor3_speed=0

        if self.buttons_X == 0 and joy.buttons[2] == 1:
            # 0°に旋回
            self.state = 1
        if self.buttons_A == 0 and joy.buttons[1] == 1:
            # 90°に旋回
            self.state = 2
        if self.buttons_B == 0 and joy.buttons[0] == 1:
            # 180°に旋回
            self.state = 3
        if self.buttons_Y == 0 and joy.buttons[3] == 1:
            # 270°に旋回
            self.state = 4
        if self.buttons_up == 0 and joy.buttons[13] == 1:
            # 0°で直進
            self.state = 5
        if self.buttons_right == 0 and joy.buttons[16] == 1:
            # 90°で直進
            self.state = 6
        if self.buttons_down == 0 and joy.buttons[14] == 1:
            # 180°で直進
            self.state = 7
        if self.buttons_left == 0 and joy.buttons[15] == 1:
            # 270°で直進
            self.state = 8

        if self.buttons_L == 1 and self.buttons_R == 1:
            # 角度リセット
            if reception_json["raw_angle"] < 0:
                # マイナスのとき
                self.angle_adjust = - 180 - reception_json["raw_angle"]
            else:
                self.angle_adjust = -1 * reception_json["raw_angle"]

        if self.buttons_home == 0 and joy.buttons[10] == 1:
            # タイマースタート
            self.start_time = time.time()

        self.buttons_L = joy.buttons[4]
        self.buttons_R= joy.buttons[5]
        self.buttons_ZL = joy.buttons[6]
        self.buttons_ZR= joy.buttons[7]
        self.buttons_home=joy.buttons[10]
        self.buttons_X=joy.buttons[2]
        self.buttons_A=joy.buttons[1]
        self.buttons_B=joy.buttons[0]
        self.buttons_Y=joy.buttons[3]
        self.buttons_up=joy.buttons[13]
        self.buttons_left = joy.buttons[16]
        self.buttons_down = joy.buttons[14]
        self.buttons_right = joy.buttons[15]

    def joy2_listener_callback(self, joy):
        # 回収機構のモーター
        self.motor3_speed=int(joy.axes[1]*256)

        if joy.buttons[6] == 1:
            # 走行補助強制停止
            self.state = 0
            self.motor1_speed = 0
            self.motor2_speed =0
            self.motor3_speed=0

        if joy.buttons[7] == 1:
            # 走行補助強制停止
            self.state = 0
            self.motor1_speed = 0
            self.motor2_speed =0
            self.motor3_speed=0


if __name__ == '__main__':
    main()