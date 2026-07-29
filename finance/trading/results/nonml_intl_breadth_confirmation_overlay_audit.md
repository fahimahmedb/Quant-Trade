# Audit adversarial — Overlay de confirmation multi-marché internationale NDX+DAX

Recalcul indépendant du signal NDX (boucle explicite) : 0 écarts. **OK.**

Test anti-lookahead signal NDX : OK — aucune fuite.
Test anti-lookahead signal DAX : OK — aucune fuite.

Delta de Sharpe non arrondi (overlay − BH) : 0.015143
Delta de MDD non arrondi (overlay − BH, en points de %) : 0.000000
**OK — le PASS tient sur la valeur exacte, pas un artefact arrondi.**

**Comparaison avec le #52 (NDX+Russell2000, domestique)** : la porte internationale (NDX+DAX) est plus sélective (27,0% du temps contre une porte domestique plus large au #52) et surtout préserve EXACTEMENT le MDD (delta ≈0, contre une dégradation de -82,9%→-83,8% au #52). Le delta de Sharpe reste néanmoins fin comme au #52 — la confirmation croisée, domestique ou internationale, n'apporte jamais un edge Sharpe massif par rapport au signal NDX seul (#37, Sharpe +0,51→+0,59), mais la variante internationale a le mérite de ne dégrader le profil de risque en AUCUNE mesure, contrairement à la variante domestique.
