import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
import json # jsonを使うため

import time # sleep使うため
import socket
sock = None

host = '192.168.160.78'
port = 80

ser = None

motor_speed=[0,0,0,0]
joy_pub = ""
serial_reception_text = [""]

def main(args=None):
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
        print("Subscriber",flush=False)
        super().__init__('command_subscriber')
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

        timer_period = 0.02  # seconds 0.01
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        global sock
        global motor_speed

        if sock is None:
            try:
                sock = socket.create_connection((host, port))
                sock.settimeout(10)
                print("Connected", flush=True)
            except (socket.error, socket.timeout) as e:
                print(f"Connection failed: {e}", flush=True)
                return

        serialCommand = f"{{'motor1':{{'speed':{self.motor1_speed}}},'motor2':{{'speed':{self.motor2_speed}}},'motor3':{{'speed':{self.motor3_speed}}},'motor4':{{'speed':{self.motor4_speed}}}}}\n"

        try:
            sock.sendall(serialCommand.encode('utf-8'))
            print(serialCommand, flush=True)
            # data = sock.recv(1024)
            # print('Received:', data.decode('utf-8'), flush=True)
        except (socket.error, socket.timeout) as e:
            print(f"Communication error: {e}", flush=True)
            sock.close()
            sock = None

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