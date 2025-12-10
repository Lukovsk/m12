import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import random


PORTA = "COM6"
BAUD = 9600


ROLES_DEF = ["VÍTIMA", "DETETIVE", "VÍTIMA", "ASSASSINO"]
CORES = ["AZUL", "AMARELO", "VERMELHO", "VERDE"]
LED_BRANCO = 4


class DetetiveGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Detetive - Controle Master")
        self.root.geometry("600x500")

        try:
            self.ser = serial.Serial(PORTA, BAUD, timeout=0.1)
            time.sleep(2)
            self.send("ALL_ON")
            time.sleep(0.5)
            self.send("ALL_OFF")
            print(f"Conectado na {PORTA}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar na {PORTA}\n{e}")
            self.root.destroy()
            return

        self.players = []
        self.actions_tonight = {}
        self.turn_queue = []
        self.current_player_idx = -1
        self.game_phase = "SETUP"
        self.witness_info = ["", "", "", ""]
        self.first_turn = True

        self.setup_gui()

        self.running = True
        self.thread = threading.Thread(target=self.serial_reader, daemon=True)
        self.thread.start()

    def send(self, cmd):
        if self.ser and self.ser.is_open:
            self.ser.write((cmd + "\n").encode())

    def serial_reader(self):
        while self.running:
            try:
                if self.ser and self.ser.is_open:
                    line = self.ser.readline().decode().strip()
                    if line == "BUTTON_PRESSED":

                        self.root.after(0, self.on_physical_button_pressed)
            except Exception as e:
                print("Erro Serial:", e)
            time.sleep(0.05)

    def start_game(self):

        shuffled_roles = list(ROLES_DEF)
        random.shuffle(shuffled_roles)

        self.players = []
        for i in range(4):
            self.players.append({"id": i, "color": CORES[i], "role": shuffled_roles[i], "alive": True})

            self.send(f"LED{i}=1")

        self.send(f"LED{LED_BRANCO}=0")
        self.lbl_status.config(text="JOGO INICIADO! A noite caiu.")
        self.start_night_phase()

    def start_night_phase(self):
        self.actions_tonight = {}
        self.witness_info = ["Nada aconteceu.", "Nada aconteceu.", "Nada aconteceu.", "Nada aconteceu."]

        self.turn_queue = [p for p in self.players if p["alive"]]
        self.next_turn()

    def next_turn(self):
        if len(self.turn_queue) == 0:
            self.process_night_results()
            return

        player = self.turn_queue.pop(0)
        self.current_player_idx = player["id"]

        self.game_phase = "WARNING"
        self.update_screen_warning(player)

    def on_physical_button_pressed(self):

        if self.game_phase == "WARNING":

            self.game_phase = "ACTION"
            self.update_screen_action()

        elif self.game_phase == "ACTION":

            self.next_turn()

        elif self.game_phase == "REVEAL_WARNING":
            self.game_phase = "REVEAL_CONTENT"
            self.update_screen_reveal_content()

        elif self.game_phase == "REVEAL_CONTENT":
            self.next_reveal()

        elif self.game_phase == "DAY":

            self.send(f"LED{LED_BRANCO}=0")
            self.start_night_phase()

    def setup_gui(self):
        style = ttk.Style()
        style.configure("Big.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Huge.TLabel", font=("Helvetica", 24, "bold"), foreground="red")

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        self.lbl_title = ttk.Label(self.main_frame, text="DETETIVE IOT", style="Big.TLabel")
        self.lbl_title.pack(pady=10)

        self.lbl_instruction = ttk.Label(self.main_frame, text="Pressione Iniciar", font=("Helvetica", 14), wraplength=550)
        self.lbl_instruction.pack(pady=20)

        self.btn_area = ttk.Frame(self.main_frame)
        self.btn_area.pack(pady=20)

        self.lbl_status = ttk.Label(self.main_frame, text="Aguardando...", foreground="gray")
        self.lbl_status.pack(side="bottom", pady=10)

        start_btn = ttk.Button(self.btn_area, text="INICIAR NOVO JOGO", command=self.start_game)
        start_btn.pack()

    def update_screen_warning(self, player):
        self.clear_buttons()
        p_name = f"PLAYER {player['id']+1} ({player['color']})"
        self.lbl_title.config(text=f"TURNO DO {p_name}")
        self.lbl_instruction.config(
            text=f"TODOS (menos {p_name}) VIREM DE COSTAS!\n\n{p_name}, quando estiver sozinho, pressione o botão no Hardware."
        )

    def update_screen_action(self):
        p = self.players[self.current_player_idx]
        role = p["role"]

        self.lbl_title.config(text=f"VOCÊ É: {role}")

        if self.first_turn is True:
            return

        if role == "ASSASSINO":
            self.lbl_instruction.config(text="Selecione quem você quer MATAR e depois aperte o botão físico.")
            self.create_target_buttons("MATAR")
        elif role == "DETETIVE":
            self.lbl_instruction.config(text="Selecione quem você quer INVESTIGAR/PRENDER e depois aperte o botão físico.")
            self.create_target_buttons("PRENDER")
        elif role == "VÍTIMA":
            self.lbl_instruction.config(text="Selecione quem você quer TESTEMUNHAR (Vigiar) e depois aperte o botão físico.")
            self.create_target_buttons("VIGIAR")

    def create_target_buttons(self, action_name):
        self.clear_buttons()

        for p in self.players:
            if p["alive"] and p["id"] != self.current_player_idx:
                btn = ttk.Button(
                    self.btn_area,
                    text=f"{action_name} P{p['id']+1} ({p['color']})",
                    command=lambda target=p["id"]: self.register_action(target),
                )
                btn.pack(side="left", padx=5)

        ttk.Button(self.btn_area, text="Não fazer nada", command=lambda: self.register_action(None)).pack(side="left", padx=5)

    def clear_buttons(self):
        for widget in self.btn_area.winfo_children():
            widget.destroy()

    def register_action(self, target_id):

        self.actions_tonight[self.current_player_idx] = target_id
        msg = "Nenhuma ação selecionada." if target_id is None else f"Alvo selecionado: P{target_id+1}"
        self.lbl_status.config(text=f"{msg} - AGORA APERTE O BOTÃO FÍSICO.")

    def process_night_results(self):
        self.lbl_title.config(text="PROCESSANDO A NOITE...")
        self.lbl_instruction.config(text="Calculando mortes e prisões...")
        self.clear_buttons()
        self.root.update()
        time.sleep(1)

        self.first_turn = False
        assassin_id = -1
        target_killed = -1
        detective_id = -1
        target_arrested = -1

        for p in self.players:
            if p["role"] == "ASSASSINO":
                assassin_id = p["id"]
            if p["role"] == "DETETIVE":
                detective_id = p["id"]

        target_killed = self.actions_tonight.get(assassin_id)
        target_arrested = self.actions_tonight.get(detective_id)

        game_over = False
        winner = ""

        if target_arrested is not None:
            if target_arrested == assassin_id:
                game_over = True
                winner = "DETETIVE (Prendeu o Assassino)"
            elif self.players[target_arrested]["role"] != "ASSASSINO":

                self.players[detective_id]["alive"] = False
                self.send(f"LED{detective_id}=0")
                self.witness_info[detective_id] = "Você prendeu um inocente e foi eliminado."

        if not game_over and target_killed is not None:
            if target_killed == detective_id:

                game_over = True
                winner = "ASSASSINO (Matou o Detetive)"
            else:
                self.players[target_killed]["alive"] = False
                self.send(f"LED{target_killed}=0")
                self.witness_info[target_killed] = f"Você foi assassinado esta noite."
                self.witness_info[assassin_id] = f"Você matou o Player {target_killed+1}."

        for p in self.players:
            if p["role"] == "VÍTIMA" and p["alive"]:
                target = self.actions_tonight.get(p["id"])
                if target is not None:
                    if target == assassin_id:
                        self.witness_info[p["id"]] = f"VOCÊ VIU O P{assassin_id+1} SAINDO PARA MATAR!"
                    elif target == target_killed:
                        self.witness_info[p["id"]] = f"Você viu o P{target+1} sendo morto pelo P{assassin_id+1}!"

        if game_over:
            self.end_game(winner)
        else:

            victims = [p for p in self.players if p["role"] == "VÍTIMA" and p["alive"]]
            if not victims:
                self.end_game("ASSASSINO (Todas vítimas mortas)")
            else:
                self.start_morning_reveal()

    def end_game(self, winner):
        self.send("DANCE")
        self.lbl_title.config(text="FIM DE JOGO")
        self.lbl_instruction.config(text=f"VENCEDOR: {winner}\n\nPressione o Botão para Reiniciar.")
        self.game_phase = "GAME_OVER"

    def start_morning_reveal(self):
        self.send(f"LED{LED_BRANCO}=1")
        self.turn_queue = [p for p in self.players]
        self.next_reveal()

    def next_reveal(self):
        if len(self.turn_queue) == 0:
            self.start_day_discussion()
            return

        player = self.turn_queue.pop(0)
        self.current_player_idx = player["id"]

        self.game_phase = "REVEAL_WARNING"
        p_name = f"PLAYER {player['id']+1} ({player['color']})"
        self.lbl_title.config(text=f"RELATÓRIO: {p_name}")
        self.lbl_instruction.config(text=f"Apenas {p_name} deve olhar.\nOutros virem de costas.\n\nAperte o botão quando pronto.")
        self.clear_buttons()

    def update_screen_reveal_content(self):
        idx = self.current_player_idx
        info = self.witness_info[idx]
        status = "VIVO" if self.players[idx]["alive"] else "MORTO"

        self.lbl_title.config(text=f"VOCÊ ESTÁ: {status}")
        self.lbl_instruction.config(text=f"{info}\n\nPressione o botão para o próximo.")

    def start_day_discussion(self):
        self.game_phase = "DAY"
        self.lbl_title.config(text="O SOL NASCEU")
        self.lbl_instruction.config(text="Discutam. Quem estiver com LED apagado morreu.\n\nQuando quiserem ir dormir, aperte o botão.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DetetiveGame(root)
    root.mainloop()
