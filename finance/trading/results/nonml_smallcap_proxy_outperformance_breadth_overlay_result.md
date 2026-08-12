# Résultat — Overlay vol-targeting gaté par la breadth de surperformance petites caps (proxy vol idiosyncratique) (pré-enregistré, règle renforcée niveau 1)

**Limite de données assumée** : aucune capitalisation boursière disponible ; "petite capitalisation" est un PROXY (moitié supérieure par volatilité idiosyncratique glissante 60j), pas une mesure directe.

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth_Small(t) (fraction du groupe proxy petite cap surperformant la médiane du marché sur 21j) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal titre-par-titre est disponible).

%j porte surperformance petites caps active : 28.3%
Position moyenne : 1.10x
Breadth surperformance moyenne (toute la période) : 50.9%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.56 | +101.6% | -39.1% |
| **Overlay vol-targeting gaté surperformance petites caps** | **+0.58** | **+116.9%** | -39.1% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py smallcap_proxy_outperformance_breadth_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
