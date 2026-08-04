# Résultat — Rebalancement hebdomadaire du portefeuille volatility-managed GJR-t (#165, cycle #167)

Spécification figée dans `PREREG_gjr_vol_managed_weekly_rebalance.md` (committé avant ce script). n_trials = 1. Correction ciblée du contrôle (a) de la batterie Règle 9 du #165 (stress de coûts, ÉCHEC à 25 bps) -- ne corrige PAS les contrôles (d) SPA et (e) DSR, structurellement indépendants du turnover (déclaré au PREREG §1).

Marché : NDX (40 ans) (`data/nasdaq100_daily.txt`). Fenêtre OOS : 9522 séances, 20/09/1988 → 13/07/2026. Position quotidienne du #165 échantillonnée tous les 5 jours et maintenue constante entre deux rebalancements (`weekly_hold_position`, réutilisée à l'identique du #154).

**Turnover réduit de 46.1 %** (quotidien : 395.66 cumulé, hebdo : 213.44 cumulé).

## 1. Résultat à coût nominal (5 bps)

| | Sharpe ann. | Rendement total | MDD |
|---|---|---|---|
| Buy & Hold | +0.52 | +4555.6% | -82.9% |
| Overlay quotidien (#165, rappel) | +0.67 | +7178.8% | -59.9% |
| **Overlay hebdomadaire** | **+0.70** | **+9864.9%** | -58.5% |

- Sharpe hebdo > BH : OUI
- Rendement hebdo > BH : OUI

## 2. Stress de coûts à 25 bps (le contrôle qui échouait au #165)

| | Sharpe ann. | Rendement total |
|---|---|---|
| Buy & Hold | +0.52 | +4555.6% |
| Overlay quotidien (#165, ÉCHEC rappelé) | +0.56 | +3200.4% |
| **Overlay hebdomadaire** | **+0.64** | **+6402.7%** |

**Contrôle (a) à 25 bps avec la position hebdomadaire : OUI (corrigé).**

## 3. Verdict contre le critère pré-enregistré

**PASS** — contrôle (a) à 25 bps corrigé ET verdict de niveau 1 à 5 bps maintenu.

**Rappel honnête** : même en cas de PASS ici, les contrôles (d) SPA à 1 candidat (p=1,0000 au #165) et (e) DSR (n_trials=taille backlog, DSR≈0,0004 au #165) resteront en échec -- aucune réduction de turnover ne les affecte. Le score Règle 9 passera au mieux de 2/5 à 3/5, jamais à un PASS renforcé.
