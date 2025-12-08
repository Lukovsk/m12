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
button_pins = [10, 11, 12, 13, 14]
buttons = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in button_pins]

last_state = [0] * 5

print("PICO ONLINE. Aguardando comandos...")


# ---------------------------
# LOOP PRINCIPAL
# ---------------------------
while True:

    # --- Lê comandos vindos do PC ---
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()

        if line.startswith("LED"):
            # LED0, LED1, LED2...
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

        else:
            print("ERRO: comando desconhecido ->", line)

    # --- Verifica botões ---
    for i, btn in enumerate(buttons):
        current = btn.value()

        if current != last_state[i]:
            last_state[i] = current

            if current == 1:
                print(f"BTN={i}")  # envia para o PC
    time.sleep(0.02)
