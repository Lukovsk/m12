import serial
import threading
import tkinter as tk
from tkinter import ttk
import time

# ---------------------------
# CONFIGURAÇÃO DA SERIAL
# ---------------------------
PORTA = "~/dev/ttyACM0"
BAUD = 115200

ser = serial.Serial(PORTA, BAUD, timeout=0.1)
time.sleep(2)  # Pico reinicia quando conecta


# ---------------------------
# FUNÇÃO PARA ENVIAR COMANDOS
# ---------------------------
def send(cmd):
    ser.write((cmd + "\n").encode())


# ---------------------------
# GUI
# ---------------------------
root = tk.Tk()
root.title("Controle do Raspberry Pi Pico W")

led_states = [tk.IntVar() for _ in range(5)]

frame_leds = ttk.LabelFrame(root, text="LEDs")
frame_leds.pack(padx=10, pady=10, fill="x")

for i in range(5):
    cb = ttk.Checkbutton(frame_leds, text=f"LED {i}", variable=led_states[i], command=lambda i=i: send(f"LED{i}={led_states[i].get()}"))
    cb.pack(anchor="w")

ttk.Button(root, text="Ligar TODOS", command=lambda: send("ALL_ON")).pack(fill="x", padx=10)
ttk.Button(root, text="Desligar TODOS", command=lambda: send("ALL_OFF")).pack(fill="x", padx=10, pady=(0, 10))


# ---------------------------
# ÁREA DE EVENTOS DOS BOTÕES
# ---------------------------
frame_log = ttk.LabelFrame(root, text="Eventos de Botões do Pico")
frame_log.pack(padx=10, pady=10, fill="both", expand=True)

log = tk.Text(frame_log, height=10)
log.pack(fill="both", expand=True)


# ---------------------------
# THREAD PARA LER SERIAL
# ---------------------------
def serial_reader():
    while True:
        try:
            data = ser.readline().decode().strip()
            if data:
                log.insert("end", data + "\n")
                log.see("end")
        except:
            pass
        time.sleep(0.05)


thread = threading.Thread(target=serial_reader, daemon=True)
thread.start()


root.mainloop()
