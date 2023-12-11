import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from sensor_msgs.msg import Joy
import time # sleep使うため
import threading


class MinimalSubscriber(Node):
    motor1_speed = 0
    motor2_speed = 0

    def __init__(self):
        super().__init__('minimal_subscriberer')
        self.publisher = self.create_publisher(Int16MultiArray, 'Collect_Controller_Node', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.02  # seconds 0.01
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.delay_timer = None

    def timer_callback(self):
        msg = Int16MultiArray()
        msg.data = [self.motor1_speed, self.motor2_speed]
        self.publisher.publish(msg)

        if self.delay_timer is not None and self.delay_timer.is_alive():
            return

        if self.motor1_speed != 0:
            self.delay_timer = threading.Timer(1.0, self.reset_motor_speed)
            self.delay_timer.start()

    def joy_callback(self, joy_msg):
        if len(joy_msg.buttons) >= 8:
            button_7_state = joy_msg.buttons[7]
            # self.get_logger().info('Button 7 state: {}'.format(button_7_state))

            if button_7_state == 1:
                self.motor1_speed = 255

    def reset_motor_speed(self):
        self.motor1_speed = 0

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()