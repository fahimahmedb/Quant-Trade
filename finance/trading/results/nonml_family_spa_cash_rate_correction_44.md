# Test SPA famille — famille #149 (cycle #159, portée corrigée avant calcul)

PAS un nouveau backtest indépendant. Portée corrigée AVANT tout calcul : deux tests SPA séparés par marché (limite mécanique de `spa_test`, ne peut pas mélanger des benchmarks d'actifs différents — même limite déjà rencontrée au #150).

## Famille NDX (#149 quotidien + #154 hebdomadaire)

Fenêtre commune : 1985-10-30 → 2026-07-13 (10252 séances).

| Membre | t-stat (vs BuyHold) |
|---|---|
| quotidien | -0.497 |
| hebdomadaire | -0.417 |

**Meilleur membre** : hebdomadaire — t_SPA=0.000, p-value SPA = 1.0000

## Famille S&P 500 (#151 quotidien + #157 hebdomadaire)

Fenêtre commune : 1970-02-02 → 2026-07-13 (14231 séances).

| Membre | t-stat (vs BuyHold) |
|---|---|
| quotidien | -0.174 |
| hebdomadaire | +0.063 |

**Meilleur membre** : hebdomadaire — t_SPA=0.063, p-value SPA = 0.4854

## Conclusion

Famille NDX : NON significatif à 5% (p=1.0000). Famille S&P 500 : NON significatif à 5% (p=0.4854). Cohérent avec les DSR individuels déjà calculés (tous ≈0 à n_trials=backlog). Ne change AUCUN verdict Règle 9 déjà rendu.
