# from launch import LaunchDescription
# from launch_ros.actions import Node
import launch_ros.actions
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription(
        [
            # Node(
            #     package="joy",
            #     namespace="robocon2023_b_dash",
            #     executable="joy_node",
            # ),
            # Node(
            #     package="experiment_python",
            #     executable="communicateWiFi_ESP32",
            #     output = "screen", # print wo hyouzi
            #     # prefix= "xterm -e",
            # ),
            Node(
                package="experiment_python",
                executable="communicateWiFiUDP_ESP32",
                output = "screen", # print wo hyouzi
                # prefix= "xterm -e",
            ),
            Node(
                package="joy",
                executable="joy_node",
                # output="screen",
                parameters=[{"device_id": 0}],
            ),
            # Node(
            #     package="experiment_python",
            #     executable="Drive_Controller",
            # ),
            # Node(
            #     package="experiment_python",
            #     executable="Collect_Controller",
            # ),
            # Node(
            #     package="experiment_python",
            #     executable="webserver",
            #     # output = "screen", # print wo hyouzi
            #     # prefix= "xterm -e",
            # ),
            # Node(
            #     package="robocon2023_b_dash",
            #     namespace="robocon2023_b_dash",
            #     executable="SerialKIMD",
            # ),
            # Node(
            #     package="fruit_detection",
            #     namespace="robocon2023_b_dash",
            #     executable="pubdetect",
            #     output = "screen", # print wo hyouzi
            #     prefix= "xterm -e",
            # ),
        ]
    )