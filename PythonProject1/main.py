import tkinter as tk # package python pour interface graphique
from tkinter import messagebox

# ----------- MENU PRINCIPAL ----------- #

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion")
        self.root.geometry("300x430")
        self.root.configure(bg="#1e1e2f")

        self.create_menu()

    def create_menu(self):
        title = tk.Label(self.root, text="MORPION",
                         font=("Arial", 24, "bold"),
                         bg="#1e1e2f", fg="#00aaff")
        title.pack(pady=30)

        btn_style = {
            "font": ("Arial", 14, "bold"),
            "bg": "#2c2c3e",
            "fg": "white",
            "relief": "flat",
            "width": 20,
            "height": 2,
            "cursor": "hand2"
        }
        # les boutons
        tk.Button(
            self.root,
            text=" Joueur 1  vs   Joueur 2",
            command=lambda: self.start_game("HUMAN"),
            **btn_style
        ).pack(pady=10)

        tk.Button(self.root, text="Joueur vs IA (ML)",
                  command=lambda: self.start_game("IA"),
                  **btn_style).pack(pady=10)

        tk.Button(self.root, text="Joueur vs IA (Hybride)",
                  command=lambda: self.start_game("HYBRID"),
                  **btn_style).pack(pady=10)

        # Style général pour les boutons
        btn_style = {
            "font": ("Arial", 14, "bold"),
            "bg": "#2c2c3e",
            "fg": "white",
            "activebackground": "#3e3e5e",
            "relief": "flat",
            "width": 20,
            "height": 2,
            "bd": 0,
            "cursor": "hand2"
        }

        # Bouton Exit
        exit_btn = tk.Button(
            self.root,
            text="Exit",
            font=btn_style["font"],
            bg="#ff4d4d",  # rouge pour Exit
            fg=btn_style["fg"],  # texte blanc
            activebackground="#ff6666",  # effet hover rouge clair
            activeforeground=btn_style["fg"],
            relief=btn_style["relief"],
            width=btn_style["width"],
            height=btn_style["height"],
            bd=btn_style["bd"],
            cursor=btn_style["cursor"],
            command=self.root.quit
        )
        exit_btn.pack(side="bottom", pady=20)


    def start_game(self, mode):
        self.root.destroy()
        launch_game(mode)


# ----------- LOGIQUE JEU ----------- #
#  les cases du morpion
def check_winner(board):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != 0:
            return board[a]
    return 0
#  Si tous les cases remplies
def is_full(board):
    return all(x != 0 for x in board)
# Algorithme mini max
def minimax(board, is_x_turn):
    winner = check_winner(board)
    if winner == 1:
        return 1
    elif winner == -1:
        return -1
    elif is_full(board):
        return 0

    if is_x_turn:
        best = -10
        for i in range(9):
            if board[i] == 0:
                board[i] = 1
                score = minimax(board, False)
                board[i] = 0
                best = max(best, score)
        return best
    else:
        best = 10
        for i in range(9):
            if board[i] == 0:
                board[i] = -1
                score = minimax(board, True)
                board[i] = 0
                best = min(best, score)
        return best
# Algorithme pour IA Hybride
def ai_move(board):
    best_score = -10
    move = -1
    for i in range(9):
        if board[i] == 0:
            board[i] = 1
            score = minimax(board, False)
            board[i] = 0
            if score > best_score:
                best_score = score
                move = i
    return move


# ----------- INTERFACE JEU ----------- #


class TicTacToe:
    # Initialisation de l'interface graphique
    def __init__(self, root, mode):
        self.root = root
        self.mode = mode
        self.root.title(f"Morpion - {mode}")
        self.root.configure(bg="#1e1e2f")

        self.board = [0]*9
        self.buttons = []
        self.current_player = 1

        # --- Score --- #
        self.score = {"Joueur 1": 0, "Joueur 2": 0, "IA": 0}

        self.score_frame = tk.Frame(self.root, bg="#2c2c3e", bd=2, relief="ridge")
        self.score_frame.grid(row=0, column=0, columnspan=3, pady=10, sticky="we", padx=5)

        self.j1_label = tk.Label(
            self.score_frame,
            text=f"Joueur 1: {self.score['Joueur 1']}",
            font=("Arial", 14, "bold"),
            fg="#00aaff",
            bg="#2c2c3e",
            padx=10, pady=5
        )
        self.j1_label.pack(side="left", expand=True, fill="both")

        opponent = "Joueur 2" if self.mode == "HUMAN" else "IA"
        self.j2_label = tk.Label(
            self.score_frame,
            text=f"{opponent}: {self.score[opponent]}",
            font=("Arial", 14, "bold"),
            fg="#ff4d4d",
            bg="#2c2c3e",
            padx=10, pady=5
        )
        self.j2_label.pack(side="right", expand=True, fill="both")

        self.create_ui()

    def create_ui(self):
        for i in range(9):
            btn = tk.Button(self.root, text="", font=("Arial", 24, "bold"),
                            width=5, height=2,
                            bg="#2c2c3e", fg="white",
                            relief="flat",
                            command=lambda i=i: self.play(i))
            btn.grid(row=(i//3)+1, column=i%3, padx=5, pady=5)  # +1 pour laisser place au score
            self.buttons.append(btn)
        #boutton retour
        back_btn = tk.Button(
            self.root,
            text=" Menu Principal",
            font=("Arial", 12, "bold"),
            bg="#ffaa00",
            fg="black",
            activebackground="#ffcc33",
            activeforeground="black",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.back_menu
        )

        back_btn.grid(row=4, column=0, columnspan=3, sticky="we", pady=10)

    def play(self, index):
        if self.board[index] != 0:
            return

        # Mode HUMAN (joueur 1 vs joueur 2)
        if self.mode == "HUMAN":
            self.make_move(index, self.current_player)
            self.current_player *= -1

        else:
            self.make_move(index, 1)

            if self.check_end():
                return

            move = ai_move(self.board)
            if move != -1:
                self.make_move(move, -1)

        self.check_end()

    def make_move(self, index, player):
        self.board[index] = player

        if player == 1:
            self.buttons[index].config(text="X", fg="#00aaff")
        else:
            self.buttons[index].config(text="O", fg="#ff4d4d")

    # Mise a jour du score
    def update_score(self):
        self.j1_label.config(text=f"Joueur 1: {self.score['Joueur 1']}")
        self.j2_label.config(
            text=f"{'Joueur 2' if self.mode=='HUMAN' else 'IA'}: {self.score['Joueur 2'] if self.mode=='HUMAN' else self.score['IA']}"
        )

    # recherche du vainqueur
    def check_end(self):
        winner = check_winner(self.board)
        #fenetre de fin de partie
        def show_end_game(message, color="#ffaa00"):
            popup = tk.Toplevel()
            popup.title("Fin de Partie")
            popup.geometry("250x120")
            popup.configure(bg="#1e1e2f")
            popup.resizable(False, False)

            label = tk.Label(
                popup,
                text=message,
                font=("Arial", 14, "bold"),
                fg=color,
                bg="#1e1e2f"
            )
            label.pack(pady=20)

            btn = tk.Button(
                popup,
                text="OK",
                font=("Arial", 12, "bold"),
                bg="#2c2c3e",
                fg="white",
                activebackground="#3e3e5e",
                relief="flat",
                width=10,
                height=1,
                cursor="hand2",
                command=popup.destroy
            )
            btn.pack(pady=5)

            popup.update_idletasks()
            w = popup.winfo_width()
            h = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (w // 2)
            y = (popup.winfo_screenheight() // 2) - (h // 2)
            popup.geometry(f"{w}x{h}+{x}+{y}")

            popup.grab_set()
            popup.focus_set()

        # condition s'il y a n vainqueur
        if winner != 0:
            if self.mode == "HUMAN":
                joueur = "Joueur 1" if winner == 1 else "Joueur 2"
            else:
                joueur = "Joueur 1" if winner == 1 else "IA"

            # --- Mise à jour le score --- #
            self.score[joueur] += 1
            self.update_score()

            show_end_game(f"{joueur} gagne !",
                          color="#00aaff" if winner == 1 else "#ff4d4d")
            self.reset()
            return True
        # condition si c'est macth nulle
        if is_full(self.board):
            show_end_game("Match nul !", color="white")
            self.reset()
            return True

        return False

    # reinitialisation
    def reset(self):
        self.board = [0]*9
        for btn in self.buttons:
            btn.config(text="")

    # retour vers menu principale
    def back_menu(self):
        self.root.destroy()
        main()
# ----------- LANCEMENT ----------- #

def launch_game(mode):
    root = tk.Tk()
    TicTacToe(root, mode)
    root.mainloop()

def main():
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()

# ----------- START ----------- #

main()