# Résultat — Correction taux réaliste sur cash appliquée au #44 (vol-targeting défensif cible 15%, NDX) (pré-enregistré)

Position équity #44 STRICTEMENT INCHANGÉE (TARGET_VOL_ANNUAL=15%, CAP=1.0x) ; fraction (1-pos_eq) allouée au proxy obligataire DGS10 au lieu du cash à 0%. 10252 séances (fenêtre commune NDX ∩ DGS10).

Position équity moyenne : 0.76x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX 100%) | +0.53 | +6416.7% | -82.9% |
| **#44 + correction taux réaliste** | **+0.84** | **+10425.6%** | -37.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé (IDENTIQUE au #44 original) atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py cash_rate_correction_defensive_vol_targeting_44`.**
