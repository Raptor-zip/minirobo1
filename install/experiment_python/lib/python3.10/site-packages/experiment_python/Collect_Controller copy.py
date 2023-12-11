import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from sensor_msgs.msg import Joy
import time # sleep使うため


class MinimalSubscriber(Node):
    motor1_speed = 0
    motor2_speed = 0

    def __init__(self):
        super().__init__('minimal_subscriberer')
        self.publisher = self.create_publisher(Int16MultiArray, 'Collect_Controller_Node', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        timer_period = 0.02  # seconds 0.01
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Int16MultiArray()
        # msg.data = [self.motor1_speed, self.motor2_speed]
        # self.publisher.publish(msg)

    def joy_callback(self, joy_msg):
        if len(joy_msg.buttons) >= 8:
            button_7_state = joy_msg.buttons[7]  # ボタン7の状態を取得
            self.get_logger().info('Button 7 state: {}'.format(button_7_state))

            if button_7_state == 1:
                self.get_logger().info('Button 7 state: {}'.format(button_7_state))

    def listener_callback(self, joy):
        msg = Int16MultiArray()
        msg.data = [int(joy.buttons[7])]
        self.publisher.publish(msg)
        # self.get_logger().info(joy.buttons[7])
        # self.get_logger().info(int(joy.axes[3]))
        # if joy.buttons[7] == 1:
        #     self.motor1_speed = 255
        #     # time.sleep(1)
        #     self.motor1_speed= 0
        # msg = String()
        # msg.data = "{'motor1':{'speed': %d }}" % abs(int(joy.axes[3]*256))
        # self.get_logger().info('Publishing: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()