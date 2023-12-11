import evdev
from evdev import ecodes, ff
import time

def vibrate(device, duration_ms):
    # バイブレーションエフェクトを定義
    rumble = ff.Rumble(strong_magnitude=0xffff, weak_magnitude=0x0000)
    effect = ff.Effect(
        ecodes.FF_RUMBLE, -1, 0,
        ff.Trigger(0, 0),
        ff.Replay(duration_ms, 0),
        ff.EffectType(ff_rumble_effect=rumble)
    )

    # エフェクトをデバイスにアップロード
    effect_id = device.upload_effect(effect)

    # エフェクトを再生
    device.write(ecodes.EV_FF, effect_id, 1)

    # 指定された時間だけ待機
    time.sleep(duration_ms / 1000)

    # エフェクトを停止し、メモリから削除
    device.erase_effect(effect_id)

if __name__ == "__main__":
    # デバイスファイルを指定してInputDeviceオブジェクトを作成
    device_path = '/dev/input/event12' # 12は変えてね！
    device = evdev.InputDevice(device_path)

    # バイブレーションを実行する
    duration_ms = 2000  # バイブレーションの持続時間（ミリ秒）
    vibrate(device, duration_ms)
