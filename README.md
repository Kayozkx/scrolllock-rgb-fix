# Scrolllock RGB Fix

Fixes the RGB lighting behavior of generic gaming keyboards that use the **Scroll Lock LED** as a firmware trigger on systems running **GNOME/Wayland**. It provides a permanent solution for recent Ubuntu releases (26.04+) where GNOME has completely removed support for Xorg sessions.

---

## Documentation and Learning Resources

In addition to the required files, this repository includes **RGB_ScrollLock_Ubuntu_EN.pdf**, a complete technical guide and development journal containing:

- A detailed, line-by-line explanation of how the Python script interacts with the hardware.
- A complete breakdown of how the `systemd` service works.
- A step-by-step history of the 22 terminal commands used to diagnose the issue and validate the solution.

If you want to understand how the solution was built or adapt it to another Linux distribution, the PDF is the best place to start.

---

## About the Project

The idea for creating a Python script to solve this RGB issue came from me. However, since I didn't yet have enough Python knowledge to implement it from scratch, the code was developed through **vibe coding** with the assistance of Anthropic's Claude AI.

The AI served as a development tool to transform the concept into a working implementation, while the overall idea, testing, debugging, and validation of the solution were carried out by me.

---

## The Problem

Many low-cost gaming keyboards do not provide official software support for Linux. On these keyboards, the RGB lighting is controlled internally by the firmware, which uses the **Scroll Lock LED** state as its trigger.

This works perfectly on Windows and also in Linux virtual consoles (TTY).

However, when running **GNOME on Wayland**, changes to the Scroll Lock LED state are no longer synchronized with the physical keyboard. Since GNOME 49+ removed support for Xorg sessions, simply switching display servers is no longer a viable workaround.

---

## The Solution

This project implements a lightweight Python service that runs in the background and communicates directly with the Linux kernel.

Features include:

- **Dynamic Device Detection:** Automatically locates the correct keyboard and Scroll Lock LED under `/sys/class/leds/` and `/dev/input/`, even if device indexes change after reboot.
- **Real-Time Event Monitoring:** Uses the `evdev` library to monitor keyboard events.
- **Direct Kernel Control:** Writes directly to the LED's `brightness` file whenever Scroll Lock is pressed, triggering the keyboard's RGB firmware.
- **Conflict Recovery:** Detects when GNOME changes the LED state (for example after pressing Caps Lock or Num Lock) and immediately restores the correct value.
- **Automatic Startup:** Runs silently as a `systemd` service and starts automatically during system boot.

---

## Requirements

- Ubuntu with GNOME running on Wayland (tested on Ubuntu 26.04 LTS)
- `python3-evdev`
- A keyboard whose RGB controller depends on the physical Scroll Lock LED state

---

## Installation

Follow the steps below to install the service.

### 1. Clone the repository and install dependencies

```bash
# Clone the repository
git clone https://github.com/Kayozkx/scrolllock-rgb-fix.git

# Enter the project directory
cd scrolllock-rgb-fix

# Install the required Python library
sudo apt install python3-evdev
```

### 2. Copy the files

```bash
# Copy the Python script
sudo cp scrolllock-rgb.py /usr/local/bin/scrolllock-rgb.py
sudo chmod +x /usr/local/bin/scrolllock-rgb.py

# Copy the systemd service
sudo cp scrolllock-rgb.service /etc/systemd/system/scrolllock-rgb.service
```

### 3. Enable and start the service

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable the service at boot and start it immediately
sudo systemctl enable --now scrolllock-rgb.service
```

---

## Verifying the Installation

After installation, press the **Scroll Lock** key to verify that the RGB lighting turns on and off correctly.

To confirm that the service is running:

```bash
systemctl status scrolllock-rgb.service --no-pager
```

To monitor the service logs:

```bash
journalctl -u scrolllock-rgb.service --no-pager
```

You can also repeatedly press **Caps Lock** and **Num Lock** to verify that GNOME no longer interferes with the RGB state.

---

## How It Works

The Linux kernel exposes the Scroll Lock LED through the following file:

```text
/sys/class/leds/<device>::scrolllock/brightness
```

Writing the value `1` turns the LED on, while writing `0` turns it off. Since many keyboards internally use this LED as the trigger for their RGB controller, changing this file also controls the keyboard lighting.

The script continuously listens for keyboard events using the **evdev** library and writes directly to this file whenever necessary. By interacting directly with the kernel through **sysfs**, it bypasses the limitations imposed by Wayland without requiring Xorg or any graphical workarounds.

---
