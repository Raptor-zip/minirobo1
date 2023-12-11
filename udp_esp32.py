import socket

import time

# ESP32のIPアドレスとポート番号
esp32_ip = "192.168.160.241"
esp32_port = 12345

# UDPソケットの作成
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ローカルポート番号
local_port = 12346

# ローカルUDPソケットの作成
local_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_udp_socket.bind(('0.0.0.0', local_port))

# try:
print(f"Listening for UDP packets on 0.0.0.0:{local_port}")


while True:
    # 送信するデータ
    # data_to_send = b"Hello, ESP32!"

    data_to_send = b"{'motor1':{'speed':100},'motor2':{'speed':200},'motor3':{'speed':400},'motor4':{'speed':500}}"

    # data_to_send = b"{'motor1':{'speed':100},'motor2':{'speed':200},'motor3':{'speed':400},'motor4':{'speed':500}}{'motor1':{'speed':100},'motor2':{'speed':200},'motor3':{'speed':400},'motor4':{'speed':500}}{'motor1':{'speed':100},'motor2':{'speed':200},'motor3':{'speed':400},'motor4':{'speed':500}}{'motor1':{'speed':100},'motor2':{'speed':200},'motor3':{'speed':400},'motor"

    # データをESP32に送信
    udp_socket.sendto(data_to_send, (esp32_ip, esp32_port))
    # print(f"Data sent to {esp32_ip}:{esp32_port}")

    # データを受信
    data, addr = local_udp_socket.recvfrom(1024)
    time_sta = time.perf_counter()
    try:
        test = data.decode('utf-8')
        time_end = time.perf_counter()
        # 経過時間（秒）
        tim = time_end- time_sta
        print(tim)
        # print(f"Received data from {addr}: {data.decode('utf-8')}")
        time_sta = time.perf_counter()
        # ut = time.time()
        # print(ut)
    except Exception:
        print(f"Received data from {addr}: {data}")

# finally:
    # ソケットをクローズ
    # udp_socket.close()
    # local_udp_socket.close()
