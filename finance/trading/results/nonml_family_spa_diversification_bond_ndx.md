# Test SPA famille-entière — sous-famille NDX de la diversification obligataire (cycle #150)

PAS un nouveau backtest indépendant. Portée RÉDUITE à 5 membres NDX partageant un horizon commun (limite mécanique de `spa_test`, exige le même T pour tous les modèles) — les variantes cross-marché (#136 S&P 500/Russell 2000, #140 DAX, #143 Composite) et le #149 (base équity différente) sont EXCLUES, documenté explicitement dans le PREREG.

Fenêtre commune : 1988-09-20 → 2026-07-13 (9522 séances).

| Membre | t-stat (vs BuyHold) |
|---|---|
| 134_DGS10 | -0.134 |
| 141_3mo | -0.409 |
| 141_1an | -0.347 |
| 137_hebdo | +0.628 |
| 139_ensemble3 | +0.204 |

**Meilleur membre (t-stat max)** : 137_hebdo
**t_SPA = 0.628, p-value SPA = 0.3144**

**ÉCHEC — non significatif à 5% : même en ne gardant que 5 variantes NDX de la famille, le SPA famille ne rejette PAS H0.**

Cette portée réduite (5 membres, sélectionnés parce qu'ils sont NDX-compatibles, pas au hasard) reste plus généreuse pour la famille qu'un test à 11+ membres cross-marché aurait été (moins de correction pour comparaisons multiples) — un résultat non significatif ici est donc d'autant plus honnête. Ne change AUCUN verdict Règle 9 déjà rendu.
