# Robustesse — breadth de faiblesse, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `INDEX_LOOKBACK` (252), les seuils de proximité (0,95 / 1,05)
et le **seuil de porte (50 %)** définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

**Lecture obligatoire avant les tableaux** : le verdict de ce candidat est
étiqueté **NON INFORMATIF** (porte brute active 0,45 % du temps), et l'audit a
établi que l'exposition ne dépasse jamais 1,0×. Toutes les cellules ci-dessous
sont donc mécaniquement identiques à Buy & Hold, quel que soit le CAP : faire
varier un plafond que la stratégie n'atteint jamais ne teste rien. Cette grille
est exécutée pour le montrer, pas pour valider un plateau.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.76 | +597.8% |
| 2.0× ← pré-enregistré | OUI | +0.76 | +597.8% |
| 2.5× | OUI | +0.76 | +597.8% |
| 3.0× | OUI | +0.76 | +597.8% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | OUI | +0.76 | +597.8% |
| 20 j ← pré-enregistré | OUI | +0.76 | +597.8% |
| 25 j | OUI | +0.76 | +597.8% |
| 30 j | OUI | +0.76 | +597.8% |

**4/4 cellules PASS sur la grille CAP, 4/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Le cycle d'origine (univers biaisé par le survivant) sert de point de
comparaison ; son rapport de robustesse est dans
`results/nonml_weakness_breadth_vol_targeting_overlay_robustness.md`.
