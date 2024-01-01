import math
import matplotlib.pyplot as plt


class Robot:
    def __init__(self, initial_x=0, initial_y=0, initial_theta=0):
        self.x = initial_x
        self.y = initial_y
        self.theta = initial_theta

    def update_position(self, delta_x, delta_y, delta_theta):
        # ロボットの座標を更新
        self.x += delta_x * math.cos(self.theta) - \
            delta_y * math.sin(self.theta)
        self.y += delta_x * math.sin(self.theta) + \
            delta_y * math.cos(self.theta)
        self.theta += delta_theta


# ロボットの初期化
robot = Robot()

# リアルタイムで与えられる移動データ（仮のデータ）
sensor_data = [
    {"x": 10, "y": 10, "theta": math.radians(30)},
    # {"x": -3, "y": 8, "theta": math.radians(315)},
    {"x": 20, "y": 20, "theta": math.radians(0)},
    # {"x": -3, "y": 8, "theta": math.radians(315)},
    # 他のデータを追加
]

# ロボットの移動と座標の更新
trajectory_x = [robot.x]
trajectory_y = [robot.y]

for data in sensor_data:
    robot.update_position(data["x"], data["y"], data["theta"])
    trajectory_x.append(robot.x)
    trajectory_y.append(robot.y)

# 軌跡の可視化
plt.figure()
plt.plot(trajectory_x, trajectory_y, marker='o', label='Robot Trajectory')
plt.scatter(trajectory_x[0], trajectory_y[0],
            color='green', marker='s', label='Start')
plt.scatter(trajectory_x[-1], trajectory_y[-1],
            color='red', marker='x', label='End')
plt.title('Robot Trajectory')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()
plt.grid(True)

# グラフの縦横比を同じにする
plt.axis('equal')

plt.show()
