import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JoyFeedbackArray, JoyFeedback

class JoyFeedbackNode(Node):
    def __init__(self):
        super().__init__('joy_feedback_node')
        self.publisher_ = self.create_publisher(JoyFeedbackArray, '/joy_feedback', 10)

    def send_vibration_feedback(self, intensity, duration):
        feedback = JoyFeedback()
        feedback.type = JoyFeedback.TYPE_RUMBLE
        feedback.id = 0  # バイブレーションのID

        feedback.intensity = intensity  # バイブレーションの強度
        feedback.duration = duration  # バイブレーションの持続時間

        feedback_array = JoyFeedbackArray()
        feedback_array.array = [feedback]

        self.publisher_.publish(feedback_array)
        self.get_logger().info("Vibration feedback sent: Intensity={}, Duration={}".format(intensity, duration))

def main(args=None):
    rclpy.init(args=args)

    joy_feedback_node = JoyFeedbackNode()

    # 例として、強度 1.0 で 1 秒間のバイブレーションを送信
    joy_feedback_node.send_vibration_feedback(intensity=1.0, duration=1.0)

    rclpy.spin_once(joy_feedback_node, timeout_sec=1.0)

    joy_feedback_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
