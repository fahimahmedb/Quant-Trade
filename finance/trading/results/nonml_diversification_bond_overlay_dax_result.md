# Résultat — Diversification obligataire sur DAX, taux allemand (pré-enregistré, deux critères, LIMITE DONNÉES reconnue)

**Limite reconnue** : taux allemand (FRED IRLTLT01DEM156N) disponible seulement en fréquence MENSUELLE, forward-fillé au calendrier DAX -- résultat moins probant qu'une vraie série quotidienne comme DGS10 (#134/#136). Interprété avec cette réserve, PASS ou FAIL.

6756 séances (fenêtre commune DAX ∩ taux allemand disponible).

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (DAX 100%) | +0.24 | +116.5% | -72.7% | 1.603 |
| **Diversification obligataire (taux allemand)** | **+0.29** | **+152.6%** | -61.3% | 2.488 |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI
3. Critère standard (1 ET 2) : PASS
4. Critère Calmar (overlay > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9), ET fragilisé par la limite de données mensuelle ci-dessus. Doit encore passer `nonml_pass_validation_battery.py diversification_bond_overlay_dax`.**
