# Simulation — 300 EUR, overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Porte kurtosis (252j/252j) ET porte ν Student-t (252j, refit 21j, médiane 252j), vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay conjonction ET gaté** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte ET est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau correct mais pas parfait : grille CAP 3-4/5, grille fenêtre de vol 2-4/5, quasi identique à celui du #237 dont ce candidat hérite l'essentiel de la sensibilité).

**Coïncidence numérique expliquée** : ce résultat (353,65€, MDD -9,0%, Sharpe +2,63) est EXACTEMENT identique aux simulations 300€ déjà publiées pour le #219 (kurtosis seule) et le #237 (ν seul) sur cette même fenêtre. Vérifié : sur ces 63 séances, la porte ν est triviale (active 63/63, ν restant au-dessus de sa médiane en permanence — cohérent avec la fragilité documentée au #237, où ν peut diverger vers une valeur élevée stable) et la porte kurtosis est quasi triviale (62/63) ; la conjonction ET se réduit donc de facto à la contrainte de vol réalisée elle-même (`position>1,0x` ssi vol réalisée < cible 20%) sur cette fenêtre précise, indépendamment de laquelle des trois portes est utilisée. Ce n'est PAS un bug — juste une propriété de cette fenêtre illustrative courte, sans rapport avec le verdict statistique du backtest complet où les trois portes se différencient nettement (%j actif combiné 19,6-35% contre 26,8-55,8% pour les composantes individuelles, cf. `..._result.md`).
