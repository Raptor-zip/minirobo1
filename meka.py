import math


class MecanumWheelController:
    def __init__(self):
        pass

    def control_mecanum_wheels(self, direction, speed):
        print(direction * 360)

        # ラジアンに変換
        angle = direction * 2.0 * math.pi

        # 回転数を255から-255の範囲に変換
        front_left = math.sin(angle + math.pi / 4.0) * 255
        front_right = math.cos(angle + math.pi / 4.0) * 255
        rear_left = math.cos(angle + math.pi / 4.0) * 255
        rear_right = math.sin(angle + math.pi / 4.0) * 255
        adjust = 255 / max([abs(front_left), abs(front_right),
                           abs(rear_left), abs(rear_right)])
        front_left = int(front_left * adjust * speed)
        front_right = int(front_right * adjust * speed)
        rear_left = int(rear_left * adjust * speed)
        rear_right = int(rear_right * adjust * speed)

        return front_left, front_right, rear_left, rear_right


def main():
    # メカナムホイールの制御クラスのインスタンス化
    controller = MecanumWheelController()

    # 方向と速さの設定
    direction = 0.725  # 0から1の範囲で指定（北を0、南を0.5として時計回りに）
    speed = 1      # 速さを指定

    # 制御関数の呼び出し
    front_left, front_right, rear_left, rear_right = controller.control_mecanum_wheels(
        direction, speed)

    # 結果の表示
    print("Front Left Speed :", front_left)
    print("Front Right Speed:", front_right)
    print("Rear Left Speed  :", rear_left)
    print("Rear Right Speed :", rear_right)


if __name__ == "__main__":
    main()
