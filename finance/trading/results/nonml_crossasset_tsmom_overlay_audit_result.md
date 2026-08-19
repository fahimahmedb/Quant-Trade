# Audit indépendant — #535, momentum cross-actifs (E3)

Route distincte : numpy pur (boucle explicite sur les indices), pas de `.diff()`/`.shift()` pandas comme le backtest.

## Recalcul indépendant vs backtest

- nombre de séances valides : recalcul **2233**, backtest **2233** — accord : **OUI**
- Sharpe overlay : recalcul +0.8331, backtest +0.8330 — accord (±0,01) : **OUI**
- Sharpe Buy&Hold : recalcul +0.9773, backtest +0.9773 — accord (±0,01) : **OUI**
- rendement total overlay : recalcul +65.97 %, cohérent avec le backtest (±0,5pt) : **OUI**

## Test anti-fuite

Perturbation ×5 du prix de clôture du **dernier** jour seulement : le signal `w` de tous les jours **précédents** doit rester strictement identique (il ne dépend que de clôtures antérieures).

- signal inchangé sur tous les jours sauf le dernier : **OUI**

**PASS** — la route indépendante (numpy pur, boucle explicite) reproduit les métriques du backtest et confirme l'absence de fuite (une perturbation du dernier jour n'affecte aucun signal antérieur).
