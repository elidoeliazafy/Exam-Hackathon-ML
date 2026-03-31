import tkinter as tk
from tkinter import messagebox
import pickle
import numpy as np

# ----------- CHARGEMENT DES MODÈLES ----------- #

try:
    with open('x_wins_model.pkl', 'rb') as f:
        model_wins = pickle.load(f)
    with open('is_draw_model.pkl', 'rb') as f:
        model_draw = pickle.load(f)
    MODELS_LOADED = True
except Exception as e:
    print(f"Erreur chargement modèles : {e}")
    MODELS_LOADED = False

# ----------- LOGIQUE IA & ML ----------- #

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != 0:
            return board[a]
    return 0

def is_full(board):
    return all(x != 0 for x in board)

def evaluate_ml(board):
    """ Utilise les modèles XGBoost pour évaluer la position actuelle """
    if not MODELS_LOADED:
        return 0
    
    # Préparation des données (XGBoost attend souvent un 2D array)
    # Note: Assurez-vous que l'encodage (1, -1, 0) correspond à votre entraînement
    data = np.array([board])
    
    # Proba que X gagne (on veut que ce soit bas pour l'IA qui est O)
    prob_x_wins = model_wins.predict_proba(data)[0][1]
    # Proba de match nul (valeur positive pour l'IA)
    prob_draw = model_draw.predict_proba(data)[0][1]
    
    # Score pour l'IA (Joueur -1) : 
    # Inverser la proba de X et ajouter un bonus pour le nul
    return (1.0 - prob_x_wins) + (0.5 * prob_draw)

def hybrid_minimax(board, depth, alpha, beta, is_maximizing):
    """ Minimax Alpha-Beta avec coupure à profondeur 3 et évaluation ML """
    winner = check_winner(board)
    if winner == -1: return 100   # IA gagne
    if winner == 1: return -100   # Humain gagne
    if is_full(board): return 0

    # LIMITE DE PROFONDEUR : On bascule sur le modèle ML
    if depth >= 3:
        return evaluate_ml(board) * 10

    if is_maximizing:
        best = -float('inf')
        for i in range(9):
            if board[i] == 0:
                board[i] = -1
                score = hybrid_minimax(board, depth + 1, alpha, beta, False)
                board[i] = 0
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha: break
        return best
    else:
        best = float('inf')
        for i in range(9):
            if board[i] == 0:
                board[i] = 1
                score = hybrid_minimax(board, depth + 1, alpha, beta, True)
                board[i] = 0
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha: break
        return best

# ----------- INTERFACE GRAPHIQUE ----------- #

class TicTacToe:
    def __init__(self, root, mode):
        self.root = root
        self.mode = mode
        self.root.title(f"Morpion - {mode}")
        self.root.geometry("350x500")
        self.root.configure(bg="#1e1e2f")

        self.board = [0]*9
        self.buttons = []
        self.current_player = 1 # 1 = X (Humain), -1 = O (IA)
        self.scores = {"J1": 0, "Opponent": 0}

        self.setup_ui()

    def setup_ui(self):
        # Scoreboard
        self.score_frame = tk.Frame(self.root, bg="#2c2c3e", pady=10)
        self.score_frame.pack(fill="x")
        
        opp_name = "Joueur 2" if self.mode == "HUMAN" else "IA"
        self.lbl_j1 = tk.Label(self.score_frame, text="J1 (X): 0", fg="#00aaff", bg="#2c2c3e", font=("Arial", 12, "bold"))
        self.lbl_j1.pack(side="left", expand=True)
        self.lbl_opp = tk.Label(self.score_frame, text=f"{opp_name} (O): 0", fg="#ff4d4d", bg="#2c2c3e", font=("Arial", 12, "bold"))
        self.lbl_opp.pack(side="right", expand=True)

        # Grille de jeu
        grid_frame = tk.Frame(self.root, bg="#1e1e2f")
        grid_frame.pack(pady=20)

        for i in range(9):
            btn = tk.Button(grid_frame, text="", font=("Arial", 20, "bold"), width=4, height=2,
                            bg="#2c2c3e", fg="white", relief="flat", cursor="hand2",
                            command=lambda i=i: self.play(i))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        # Bouton Retour
        tk.Button(self.root, text="Menu Principal", bg="#ffaa00", font=("Arial", 10, "bold"),
                  command=self.back_menu).pack(side="bottom", fill="x", pady=10)

    def play(self, index):
        if self.board[index] != 0: return

        # --- Tour Humain ---
        self.make_move(index, 1)
        if self.check_end(): return

        # --- Tour IA / Adversaire ---
        if self.mode == "HUMAN":
            self.current_player = -1
            # Dans ce mode, on attend juste le prochain clic qui sera traité par play()
        else:
            self.root.update() # Refresh UI
            move = self.get_ai_move()
            if move != -1:
                self.make_move(move, -1)
                self.check_end()

    def get_ai_move(self):
        if self.mode == "IA": # Mode ML Pur
            best_s = -float('inf')
            move = -1
            for i in range(9):
                if self.board[i] == 0:
                    self.board[i] = -1
                    score = evaluate_ml(self.board)
                    self.board[i] = 0
                    if score > best_s:
                        best_s = score
                        move = i
            return move

        elif self.mode == "HYBRID": # Mode Hybride
            best_val = -float('inf')
            move = -1
            for i in range(9):
                if self.board[i] == 0:
                    self.board[i] = -1
                    val = hybrid_minimax(self.board, 0, -float('inf'), float('inf'), False)
                    self.board[i] = 0
                    if val > best_val:
                        best_val = val
                        move = i
            return move
        return -1

    def make_move(self, index, player):
        self.board[index] = player
        char, color = ("X", "#00aaff") if player == 1 else ("O", "#ff4d4d")
        self.buttons[index].config(text=char, fg=color)

    def check_end(self):
        winner = check_winner(self.board)
        if winner != 0 or is_full(self.board):
            if winner == 1:
                self.scores["J1"] += 1
                msg = "Victoire du Joueur 1 !"
            elif winner == -1:
                self.scores["Opponent"] += 1
                msg = "L'IA a gagné !" if self.mode != "HUMAN" else "Victoire du Joueur 2 !"
            else:
                msg = "Match nul !"
            
            self.lbl_j1.config(text=f"J1 (X): {self.scores['J1']}")
            self.lbl_opp.config(text=f"{'J2' if self.mode=='HUMAN' else 'IA'} (O): {self.scores['Opponent']}")
            messagebox.showinfo("Fin", msg)
            self.reset()
            return True
        return False

    def reset(self):
        self.board = [0]*9
        for btn in self.buttons: btn.config(text="")
        self.current_player = 1

    def back_menu(self):
        self.root.destroy()
        main()

# ----------- MENU PRINCIPAL ----------- #

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion AI v2")
        self.root.geometry("300x450")
        self.root.configure(bg="#1e1e2f")

        tk.Label(root, text="MORPION", font=("Arial", 24, "bold"), bg="#1e1e2f", fg="#00aaff").pack(pady=30)

        style = {"font": ("Arial", 12, "bold"), "bg": "#2c2c3e", "fg": "white", "width": 20, "height": 2, "bd": 0}

        tk.Button(root, text="Joueur vs Joueur", command=lambda: self.start("HUMAN"), **style).pack(pady=10)
        tk.Button(root, text="IA (ML Pur)", command=lambda: self.start("IA"), **style).pack(pady=10)
        tk.Button(root, text="IA (Hybride)", command=lambda: self.start("HYBRID"), **style).pack(pady=10)
        
        tk.Button(root, text="Quitter", bg="#ff4d4d", fg="white", font=("Arial", 10), command=root.quit).pack(side="bottom", pady=20)

    def start(self, mode):
        self.root.destroy()
        launch_game(mode)

def launch_game(mode):
    root = tk.Tk()
    TicTacToe(root, mode)
    root.mainloop()

def main():
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
