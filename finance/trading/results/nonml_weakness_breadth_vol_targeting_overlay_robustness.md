# Robustesse — Overlay vol-targeting gaté par la breadth de faiblesse (grilles CAP et fenêtre, PAS un retuning de la porte)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j. **Attendu (cf. audit) : la porte brute n'est active que 5 jours sur 1385 (0,36%) -- cette grille confirme donc la triviality du résultat plutôt qu'un vrai plateau d'edge.**

## Grille CAP (fenêtre fixée à 20j)

| CAP | PASS (Sharpe ET rendement > BH) |
|---|---|
| 1.5x | OUI |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | OUI |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | PASS (Sharpe ET rendement > BH) |
|---|---|
| 15j | OUI |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | OUI |
| 30j | OUI |

**Lecture honnête** : la stabilité de ce "plateau" ne reflète pas un edge robuste, mais le fait que la porte est presque toujours inactive quels que soient CAP/fenêtre — voir l'avertissement du backtest et de l'audit.
