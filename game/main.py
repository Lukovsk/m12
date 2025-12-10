import select
import sys
from machine import Pin
import time

# ---------------------------
# LEDs
# ---------------------------
led_pins = [2, 3, 4, 5, 6]
leds = [Pin(p, Pin.OUT) for p in led_pins]

# ---------------------------
# Botões
# ---------------------------
button_pin = Pin(10, Pin.IN, Pin.PULL_DOWN)

last_state = 0

print("PICO ONLINE. Aguardando comandos...")


# ---------------------------
# LOOP PRINCIPAL
# ---------------------------
while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()

        if line.startswith("LED"):
            parts = line.split("=")
            led_id = int(parts[0].replace("LED", ""))
            state = int(parts[1])
            leds[led_id].value(state)
            print(f"ACK: LED{led_id}={state}")

        elif line == "ALL_OFF":
            for l in leds:
                l.value(0)
            print("ACK: ALL_OFF")

        elif line == "ALL_ON":
            for l in leds:
                l.value(1)
            print("ACK: ALL_ON")

        elif line == "DANCE":
            for l in leds:
                for j in leds:
                    j.value(1)
                    time.sleep(0.1)
                    j.value(0)
                l.value(0)

        else:
            print("ERRO: comando desconhecido ->", line)

    current = button_pin.value()

    if current != last_state:
        last_state = current

        if current == 1:
            print("BUTTON_PRESSED")
            time.sleep(0.1)

    time.sleep(0.02)
