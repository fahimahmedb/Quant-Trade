# Pré-enregistrement — Leaders 52-semaines + overlay levé union ToM∪Halloween

**Committé AVANT tout calcul.** Cycle #23 du backlog non-ML. 3e variante
de combinaison avec le portefeuille Leaders (#4, PASS) : après ToM seul
(#11, PASS) et Halloween seul (#20, FAIL), on teste ici l'overlay UNION
déjà validé sur Buy&Hold au cycle #21 (PASS 4/5).

## Hypothèse

Puisque l'overlay union ToM∪Halloween bat Buy&Hold (cycle #21) et que
l'overlay ToM seul bat déjà le portefeuille Leaders (cycle #11), la
question ouverte est si l'union apporte un gain supplémentaire par
rapport à ToM seul sur Leaders, ou si — comme au #20 (Halloween seul sur
Leaders, FAIL) — la composante Halloween dilue l'avantage une fois
combinée à la sélection de titres momentum.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4
  (tercile supérieur par ratio prix/plus-haut-annuel, rebalancement
  21j, univers NDX-100 dynamique par date de cotation).
- Overlay = position de base **× CAP=2.0x** durant les jours où la
  fenêtre ToM **OU** Halloween est active (union, définitions identiques
  aux cycles #8/#17/#21), position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#16/#18/#20.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), univers dynamique
(union des dates de cotation, cf. cycle #4).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant
`nonml_leaders_tom_halloween_union_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py leaders_tom_halloween_union_overlay`.
