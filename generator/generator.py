"""
generator.py
============
Génère un dataset complet des états de jeu de Morpion (Tic-Tac-Toe) où
c'est au tour de X de jouer, avec l'issue théorique calculée via Minimax
+ élagage Alpha-Bêta.

Colonnes du dataset :
  - c0_x .. c8_x  : 1 si X occupe la case i, sinon 0  (9 colonnes)
  - c0_o .. c8_o  : 1 si O occupe la case i, sinon 0  (9 colonnes)
  - x_wins        : 1 si X gagne en jeu parfait, sinon 0
  - is_draw       : 1 si match nul en jeu parfait, sinon 0

Usage :
  python generator.py
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
X, O, EMPTY = 1, -1, 0   # Représentation interne du plateau
OUTPUT_PATH = "ressources/dataset.csv"


# ---------------------------------------------------------------------------
# Utilitaires plateau
# ---------------------------------------------------------------------------

def check_winner(board: tuple) -> int:
    """
    Vérifie si un joueur a gagné.

    Parameters
    ----------
    board : tuple de 9 entiers (X=1, O=-1, EMPTY=0)

    Returns
    -------
    1  si X gagne
    -1 si O gagne
    0  sinon (partie non terminée ou nulle)
    """
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # lignes
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # colonnes
        (0, 4, 8), (2, 4, 6),               # diagonales
    ]
    for a, b, c in wins:
        s = board[a] + board[b] + board[c]
        if s == 3:
            return X
        if s == -3:
            return O
    return EMPTY


def is_terminal(board: tuple) -> bool:
    """Retourne True si la partie est terminée (victoire ou plateau plein)."""
    if check_winner(board) != EMPTY:
        return True
    return EMPTY not in board


def whose_turn(board: tuple) -> int:
    """
    Détermine à qui c'est le tour de jouer en comptant les pièces.
    Si #X == #O  → c'est le tour de X (X joue en premier).
    Si #X == #O + 1 → c'est le tour de O.
    """
    count_x = board.count(X)
    count_o = board.count(O)
    return X if count_x == count_o else O


# ---------------------------------------------------------------------------
# Minimax avec élagage Alpha-Bêta
# ---------------------------------------------------------------------------

# Cache pour éviter de recalculer les mêmes positions
_minimax_cache: dict = {}


def minimax(board: tuple, alpha: float, beta: float, maximizing: bool) -> int:
    """
    Algorithme Minimax avec élagage Alpha-Bêta.

    Convention de score :
      +1  → X gagne
      -1  → O gagne
       0  → Match nul

    Parameters
    ----------
    board      : état courant du plateau (tuple immuable de 9 entiers)
    alpha      : meilleur score que le maximiseur est sûr d'obtenir
    beta       : meilleur score que le minimiseur est sûr d'obtenir
    maximizing : True si c'est au tour du maximiseur (X), False pour O

    Returns
    -------
    Score optimal (int) pour le joueur courant.
    """
    # Clé de cache : plateau + joueur courant
    cache_key = (board, maximizing)
    if cache_key in _minimax_cache:
        return _minimax_cache[cache_key]

    winner = check_winner(board)
    if winner == X:
        return 1
    if winner == O:
        return -1
    if EMPTY not in board:   # Match nul
        return 0

    if maximizing:
        best = -2
        for i in range(9):
            if board[i] == EMPTY:
                new_board = board[:i] + (X,) + board[i+1:]
                score = minimax(new_board, alpha, beta, False)
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break   # Coupure bêta
    else:
        best = 2
        for i in range(9):
            if board[i] == EMPTY:
                new_board = board[:i] + (O,) + board[i+1:]
                score = minimax(new_board, alpha, beta, True)
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break   # Coupure alpha

    _minimax_cache[cache_key] = best
    return best


# ---------------------------------------------------------------------------
# Exploration récursive de tous les états valides
# ---------------------------------------------------------------------------

def explore(board: tuple, seen: set, records: list) -> None:
    """
    Parcourt récursivement tous les états de jeu accessibles depuis `board`.

    - Enregistre l'état uniquement quand c'est au tour de X de jouer
      et que la partie n'est pas encore terminée.
    - Utilise `seen` (set) pour éviter les doublons.

    Parameters
    ----------
    board   : état courant (tuple de 9 entiers)
    seen    : ensemble des états déjà visités
    records : liste des enregistrements à sauvegarder
    """
    if board in seen:
        return
    seen.add(board)

    # Si la partie est finie, on ne peut pas jouer → pas d'enregistrement
    if is_terminal(board):
        return

    current_player = whose_turn(board)

    # N'enregistrer que les états où c'est au tour de X
    if current_player == X:
        score = minimax(board, -2, 2, True)
        records.append({
            **_encode_features(board),
            "x_wins":  1 if score == 1 else 0,
            "is_draw": 1 if score == 0 else 0,
        })

    # Explorer les coups suivants pour les deux joueurs
    for i in range(9):
        if board[i] == EMPTY:
            new_board = board[:i] + (current_player,) + board[i+1:]
            explore(new_board, seen, records)


def _encode_features(board: tuple) -> dict:
    """
    Encode un plateau en 18 features binaires.

    Pour chaque case i (0..8) :
      ci_x = 1 si X occupe la case, sinon 0
      ci_o = 1 si O occupe la case, sinon 0

    Parameters
    ----------
    board : tuple de 9 entiers

    Returns
    -------
    dict avec 18 clés : c0_x, c0_o, c1_x, c1_o, ..., c8_x, c8_o
    """
    features = {}
    for i, cell in enumerate(board):
        features[f"c{i}_x"] = 1 if cell == X else 0
        features[f"c{i}_o"] = 1 if cell == O else 0
    return features


# ---------------------------------------------------------------------------
# Point d'entrée principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Génération du dataset Morpion (Tic-Tac-Toe)")
    print("=" * 55)

    seen    = set()
    records = []

    # Plateau vide : X joue en premier
    initial_board = (EMPTY,) * 9

    print("\n[1/3] Exploration de tous les états valides...")
    explore(initial_board, seen, records)
    print(f"      → {len(seen):,} états uniques explorés.")
    print(f"      → {len(records):,} états retenus (tour de X, partie non terminée).")

    print("\n[2/3] Construction du DataFrame pandas...")
    # Ordre des colonnes : c0_x, c0_o, c1_x, c1_o, ..., c8_x, c8_o, x_wins, is_draw
    feature_cols = [f"c{i}_{p}" for i in range(9) for p in ("x", "o")]
    label_cols   = ["x_wins", "is_draw"]
    df = pd.DataFrame(records, columns=feature_cols + label_cols)

    # Vérification de cohérence : x_wins et is_draw mutuellement exclusifs
    assert not ((df["x_wins"] == 1) & (df["is_draw"] == 1)).any(), \
        "Incohérence : un état ne peut pas être à la fois victoire ET nul !"

    print(f"      → Shape du dataset : {df.shape}")
    print(f"      → Distribution des labels :")
    print(f"         x_wins=1  : {df['x_wins'].sum():>5,} états")
    print(f"         is_draw=1 : {df['is_draw'].sum():>5,} états")
    print(f"         o_wins    : {(df['x_wins'] + df['is_draw'] == 0).sum():>5,} états")

    print(f"\n[3/3] Export CSV → {OUTPUT_PATH}")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"      → Fichier sauvegardé avec succès ✓")

    print("\n" + "=" * 55)
    print("  Dataset prêt pour le hackathon !")
    print("=" * 55)


if __name__ == "__main__":
    main()
