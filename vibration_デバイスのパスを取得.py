import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(f"Device: {device.name}, Path: {device.path}")
    print('\033[1m\033[31m'+'赤色'+'\033[0m')