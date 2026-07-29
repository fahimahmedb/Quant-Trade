# Résultat — Overlay vol-targeting gaté par la breadth de faiblesse NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth de faiblesse(t) ≥50% (fraction des titres NDX-100 proches à ≤105% de leur plus bas 252j), sinon 1.0x. 1385 séances testables.

%j porte breadth de faiblesse active (position résultante >1x) : 0.0%
Porte BRUTE (breadth ≥ seuil, avant clip vol-targeting) active : 5 jour(s) sur 1385 (0.36%). Breadth de faiblesse max observée sur toute la période : 63.4% (moyenne 7.0%).
Position moyenne : 1.00x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting gaté breadth de faiblesse** | **+0.68** | **+101.7%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (techniquement, critère numérique atteint) — critère renforcé atteint.**

**⚠️ AVERTISSEMENT — PASS NON INFORMATIF.** Le seuil pré-enregistré (BREADTH_THRESHOLD=50%, repris tel quel du #77 par symétrie, sans retuning) n'est atteint que 5 jour(s) sur 1385 (0.36%) — la breadth de faiblesse ne dépasse quasiment jamais 50% sur cet échantillon (2021-2026, majoritairement haussier). Le résultat est donc quasi-identique à Buy&Hold (l'overlay ne s'active essentiellement jamais), et le "PASS" formel ne constitue PAS une validation économique de l'hypothèse de capitulation — il reflète l'absence quasi-totale d'activation de la porte, pas un edge démontré. Rapporté honnêtement plutôt que présenté comme un succès substantiel.
