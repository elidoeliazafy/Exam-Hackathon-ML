-----

````markdown
# Projet Hackathon Machine Learning - ISPM S1

> **Équipe R&D EdTech** : Conception d'une IA de Morpion Adaptative.
> (https://ispm-edu.com/)

---

## Notre Groupe
* **Nom du groupe** : More Than Conqueror
* **Membres** :
    1. ELIAZAFY Jean Elido Clever N°19 (Chef de projet)
    2. Lezo Honoricia Muguette N°59 (Data Scientist)
    3. VOLAMAMY Brainda N°11 (ML Engineer)
    4. MBOLAMANA MORA GIOVANNI N°46 (Développeur Interface)
    5. BEDAITTE Arimine N°45 (Analyste QA)
    6. RAKOTONANDRASANA Jean Nathanael N°40 (Documentation/Vidéo)
    7. ANDRIAKOLONIAINA Mevasoa N°51 (DevOps/GitHub)

---

## Description du Projet
Ce projet a été réalisé dans le cadre d'un hackathon de 9 heures. L'objectif était de construire un pipeline complet de Machine Learning capable de jouer au Morpion. 
Le projet comprend :
1. La génération d'un dataset de ~2400 états de jeu via l'algorithme **Minimax**.
2. Une analyse exploratoire des données (EDA).
3. L'entraînement de modèles de classification (Baseline vs Modèles Avancés).
4. Le déploiement d'une interface de jeu proposant des modes Humain, IA (ML pur) et Hybride (Minimax + ML).

---

## Structure du Repository
```text
.
├── resources/
│   └── dataset.csv             # Dataset généré (18 features, 2 cibles)
├── models/
│   ├── model_x_wins.pkl        # Modèle XGBoost final pour la victoire
│   └── model_is_draw.pkl       # Modèle XGBoost final pour le nul
├── notebook.ipynb             # EDA, Baseline et Modèles Avancés
├── generator/
│   └── generator.py            # Script de génération Minimax Alpha-Beta
├── interface/
│   └── main.py                 # Interface jouable (Streamlit/Tkinter/Flask)
└── README.md                   # Ce rapport
└── README-jeu.md               # Le readme du jeu
````

-----

## Résultats Machine Learning

Nous avons comparé notre Baseline (Régression Logistique) avec des modèles d'ensemble (Random Forest & XGBoost).

| Modèle | Accuracy (x\_wins) | F1-Score (is\_draw) |
| :--- | :---: | :---: |
| **Régression Logistique** | 80.62% | 0.00 (Échec sur classe minoritaire) |
| **Random Forest** | 89.69% | 0.59 |
| **XGBoost (Choisi)** | **93.81%** | **0.77** |

**Conclusion** : XGBoost a été sélectionné pour l'interface finale en raison de sa capacité supérieure à détecter les matchs nuls.

-----

## Réponses aux Questions (Section 5)

### Q1 : Coefficients et Influence des Cases

Dans le modèle de Régression Logistique, la **case centrale (c4\_x)** possède l'un des coefficients les plus élevés. Cela est cohérent avec la stratégie humaine : contrôler le centre offre le plus grand nombre de combinaisons de victoires possibles (horizontales, verticales et diagonales).

### Q2 : Déséquilibre des classes

Le dataset est fortement déséquilibré :

  - **x\_wins** : \~79% de '1'.
  - **is\_draw** : \~17% de '1'.
    En conséquence, nous avons privilégié le **F1-Score** plutôt que l'Accuracy. L'Accuracy est trompeuse car un modèle prédisant "toujours 0" pour les nuls obtiendrait 83% de score tout en étant inutile.

### Q3 : Comparaison des deux modèles

Le classificateur `x_wins` obtient de meilleurs scores (F1=0.96) que `is_draw` (F1=0.77).
**Pourquoi ?** Prédire une victoire est une tâche "positive" liée à l'alignement de 3 pions. Prédire un match nul est plus complexe : c'est une tâche "négative" qui nécessite de vérifier que toutes les lignes de victoire des deux joueurs sont bloquées simultanément.

### Q4 : Mode Hybride

En mode **Hybride**, l'IA devient nettement plus redoutable. Alors que l'IA-ML pur peut parfois faire des erreurs de placement local, le mode Hybride utilise Minimax pour anticiper les coups à court terme (3 coups) et utilise nos modèles ML pour évaluer la qualité des positions futures. Cela permet d'éviter les pièges grossiers en fin de partie.

-----

## Présentation Vidéo

Retrouvez notre démonstration et l'explication de notre démarche ici :  
👉 [**Lien vers la vidéo de présentation**]

-----

*Fait avec ❤️ par l'équipe More Than Conqueror - ISPM 2026*
