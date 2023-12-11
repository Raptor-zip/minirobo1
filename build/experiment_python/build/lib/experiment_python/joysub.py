import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from sensor_msgs.msg import Joy

print('\033[1m\033[31m'+'赤色'+'\033[0m')


class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.publisher = self.create_publisher(Int16MultiArray, 'joy_pub', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, joy):
        # print("Listener callback",flush=False)

        msg = Int16MultiArray()
        msg.data = [int(joy.axes[1]*256),int(joy.axes[3]*256)]
        self.publisher.publish(msg)

        # msg = String()
        # msg.data = "{'motor1':{'speed': %d }}" % abs(int(joy.axes[3]*256))
        # self.get_logger().info('Publishing: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()