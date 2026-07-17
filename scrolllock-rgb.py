#!/usr/bin/env python3
"""
scrolllock-rgb.py

Synchronizes the Scroll Lock LED with the RGB lighting of generic gaming
keyboards that use this LED as a firmware trigger on GNOME/Wayland
systems, where the compositor does not propagate the LED state to the
physical hardware.

The script automatically discovers both the keyboard device and the LED
path at runtime, allowing it to continue working even if the
/dev/input/eventX or /sys/class/leds/inputX::scrolllock indexes change
between reboots.
"""

import evdev
from evdev import ecodes
import glob
import time


def find_led_path():
    """Locate the Scroll Lock LED brightness file under /sys/class/leds/."""
    matches = glob.glob("/sys/class/leds/*scrolllock*")
    if matches:
        return matches[0] + "/brightness"
    return None


def find_keyboard():
    """Find the actual keyboard among all input devices.

    The device must support both the Scroll Lock key and the A key in
    order to filter out auxiliary devices such as "Consumer Control"
    or "System Control".
    """
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities().get(ecodes.EV_KEY, [])
        if ecodes.KEY_SCROLLLOCK in caps and ecodes.KEY_A in caps:
            return dev
    return None


def main():
    led_path = find_led_path()
    device = find_keyboard()

    if led_path is None or device is None:
        # The systemd service is configured with Restart=always,
        # so it will automatically retry until the keyboard becomes
        # available during boot.
        raise SystemExit("Keyboard or Scroll Lock LED not found yet")

    state = 0

    def set_led(value):
        with open(led_path, "w") as f:
            f.write(str(value))

    for event in device.read_loop():
        if (
            event.type == ecodes.EV_KEY
            and event.code == ecodes.KEY_SCROLLLOCK
            and event.value == 1
        ):
            # Scroll Lock key pressed: toggle the RGB state.
            state = 1 - state
            set_led(state)

        elif event.type == ecodes.EV_LED:
            # GNOME changed one of the keyboard LEDs (Caps Lock or
            # Num Lock), which may unintentionally reset Scroll Lock.
            # Wait for GNOME to finish updating the LEDs, then restore
            # the desired Scroll Lock state.
            time.sleep(0.05)
            set_led(state)


if __name__ == "__main__":
    main()
