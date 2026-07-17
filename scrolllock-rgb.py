#!/usr/bin/env python3
"""
scrolllock-rgb.py

Sincroniza o LED de Scroll Lock com o RGB de teclados gamer genéricos
que usam esse LED como gatilho de firmware, em sistemas GNOME/Wayland
onde o compositor não repassa o estado do LED para o hardware.

Descobre automaticamente o teclado e o caminho do LED em tempo de
execução, então continua funcionando mesmo que os índices de
/dev/input/eventX ou /sys/class/leds/inputX::scrolllock mudem entre
reinicializações.
"""

import evdev
from evdev import ecodes
import glob
import time


def find_led_path():
    """Procura o arquivo de brilho do LED de Scroll Lock em /sys/class/leds/."""
    matches = glob.glob("/sys/class/leds/*scrolllock*")
    if matches:
        return matches[0] + "/brightness"
    return None


def find_keyboard():
    """Procura, entre os dispositivos de entrada, o que é realmente o teclado
    (precisa suportar tanto Scroll Lock quanto a tecla A, para descartar
    dispositivos auxiliares como 'Consumer Control' ou 'System Control')."""
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
        # O systemd está configurado com Restart=always, então o serviço
        # tenta de novo automaticamente até o teclado estar disponível.
        raise SystemExit("Teclado ou LED de Scroll Lock não encontrado ainda")

    state = 0

    def set_led(value):
        with open(led_path, "w") as f:
            f.write(str(value))

    for event in device.read_loop():
        if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_SCROLLLOCK and event.value == 1:
            # Tecla Scroll Lock pressionada: inverte o estado do RGB.
            state = 1 - state
            set_led(state)
        elif event.type == ecodes.EV_LED:
            # O GNOME alterou algum LED (Caps/Num Lock) e pode ter
            # resetado o nosso Scroll Lock sem querer. Espera o GNOME
            # terminar de escrever e força o estado correto de volta.
            time.sleep(0.05)
            set_led(state)


if __name__ == "__main__":
    main()
