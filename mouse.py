import evdev

# デバイスの指定
DEVICE_PATH = "/dev/input/event3"


def main():
    device = evdev.InputDevice(DEVICE_PATH)

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_REL:
            # move, wheel
            if event.code == evdev.ecodes.REL_X:
                print(f"REL_X:{event.value}")
            elif event.code == evdev.ecodes.REL_Y:
                print(f"REL_Y:{event.value}")
            if event.code == evdev.ecodes.REL_WHEEL:
                print(f"REL_WHEEL:{event.value}")
    return


if __name__ == "__main__":
    main()
