# Pré-enregistrement — Overlay défensif combiné (moyenne de 2 moteurs de volatilité indépendants)

**Committé AVANT tout calcul.** Cycle #121 du backlog non-ML. Ce cycle
combine deux résultats DÉJÀ committés (#115 et l'overlay GJR-GARCH
corrigé du #118) — pas une nouvelle collecte de données, mais une
construction NOUVELLE (jamais testée : la moyenne simple des deux
expositions) constitue un n_trials=1 authentique pour CETTE combinaison
précise.

## Hypothèse

#113 (vote majoritaire entre gates titre-par-titre CORRÉLÉES, même
mécanisme, même source de données) n'a pas réduit le bruit qui fait
échouer SPA/DSR — les 5 membres partageaient la même source
d'information (prix titre-par-titre NDX-100), donc leurs erreurs de
timing étaient corrélées. Ce cycle teste une combinaison
QUALITATIVEMENT différente : #115 (vol réalisée 20j simple, indice
niveau) et l'overlay GJR-GARCH corrigé du #118 (modèle économétrique
walk-forward, ré-estimé tous les 21j) sont deux ESTIMATEURS INDÉPENDANTS
de la même quantité (volatilité future de NDX), avec des sources
d'erreur différentes (bruit d'échantillonnage court terme vs
mauvaise-spécification du modèle GARCH) — hypothèse : moyenner leurs
expositions réduit le bruit idiosyncratique de CHAQUE estimateur sans
perdre le signal commun (les deux détectent la même chose : les régimes
de vol élevée/basse), contrairement à #113 où les 5 membres n'étaient
pas des estimateurs indépendants d'une même quantité mais des SIGNAUX
différents.

## Définition (fixée ici, avant tout résultat)

- `Position_combinée(t) = (Position_#115(t) + Position_GARCH(t)) / 2`
  — moyenne simple, non pondérée (pas d'optimisation de poids après
  avoir vu les résultats). Les deux positions sont déjà committées
  telles quelles (`nonml_defensive_calmar_vol_targeting_overlay_pnl.npz`,
  `nonml_etape_d_garch_defensive_overlay_pnl.npz`), aucun paramètre des
  deux mécanismes sous-jacents ne change.
- Fenêtre commune : intersection des dates des deux artefacts (20/09/1988
  → 13/07/2026, 9522 séances communes — la fenêtre GARCH, plus courte
  car nécessite T0=750 obs initiales).
- **Coûts** : 5 bps par unité de turnover (identique aux deux composants,
  turnover recalculé sur la position COMBINÉE, pas la somme des
  turnovers individuels — évite de double-compter les coûts).
- **Référence** : Buy & Hold sur NDX, même fenêtre commune.

## Critère de succès (pré-enregistré, DEUX volets rapportés séparément)

1. Critère standard : Sharpe ET rendement > BH (n_trials=1 pour cette
   combinaison précise).
2. Critère Calmar (cohérence avec #115) : Calmar > BH.
Les deux sont rapportés, aucun n'est privilégié après coup.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py dual_engine_defensive_overlay`,
n_trials=taille totale du backlog (jamais 1, ni 2).

## Anti-cheat

Ce fichier committé avant
`nonml_dual_engine_defensive_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py dual_engine_defensive_overlay`.
