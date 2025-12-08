import random
from serial import Serial
import threading
import tkinter as tk
from tkinter import ttk
import time

# ---------------------------
# CONFIGURAÇÃO DA SERIAL
# ---------------------------
PORTA = "COM6"
BAUD = 9600

ser = Serial(PORTA, BAUD, timeout=0.1)
time.sleep(2)  # Pico reinicia quando conecta
MINUTE = 10
HALF_MINUTE = MINUTE / 2

root = tk.Tk()
root.title("Controle do Raspberry Pi Pico W")
led_states = [tk.IntVar() for _ in range(5)]
LEDS = {}

fRN = {0, 1, 2, 3}
deads = [0, 0, 0, 0]
period = 0
witness = False

# ---------------------------
# FUNÇÃO PARA ENVIAR COMANDOS
# ---------------------------
def send(cmd):
    ser.write((cmd + "\n").encode())

def setup():
    send("ALL_OFF")

    random.shuffle(fRN)

def kill(target: int):
    if (target == 1 or target == 3):
        deads[3] = 1
    else:
        deads[target] = 1

def secure(target: int):
    if target == 3:
        deads[3] = 1
    else:
        deads[1] = 1
    
def testify(target: int):
    if target in [0, 2]:
        witness = True

def dance():
    send("DANCE")

def restart():
    for i in range(4):
        deads[i] = 0
        fRN[i] = i
    period = 0
    witness = False
    setup()

# ---------------------------
# GUI
# ---------------------------


frame_leds = ttk.LabelFrame(root, text="LEDs")
frame_leds.pack(padx=10, pady=10, fill="x")

for i in range(5):
    cb = ttk.Checkbutton(frame_leds, text=f"LED {i+1}", variable=led_states[i], command=lambda i=i: send(f"LED{i}={led_states[i].get()}"))
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

                if data == "BUTTON_PRESSED":
                    send("LED4=1")

            time.sleep(0.2)
            period += 1
            print(period)


            if period % MINUTE == HALF_MINUTE:
                send("LED4=0")
                
                

        except:

            pass
        time.sleep(0.05)


thread = threading.Thread(target=serial_reader, daemon=True)
thread.start()


root.mainloop()
