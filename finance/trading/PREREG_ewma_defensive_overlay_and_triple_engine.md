# Pré-enregistrement — Overlay défensif EWMA + ensemble à 3 moteurs (réalisé + GARCH + EWMA)

**Committé AVANT tout calcul.** Cycle #124 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

#121 (moyenne de 2 moteurs indépendants, réalisé-vol #115 + GJR-GARCH
#118) a amélioré l'edge brut et la robustesse SANS résoudre SPA/DSR.
Ce cycle teste un TROISIÈME estimateur indépendant de la volatilité
future de NDX : EWMA (RiskMetrics, `λ=0.94`, déjà implémenté et
utilisé en Étape C — `src/volatility.py::ewma_path`, jamais utilisé
dans ce backlog non-ML). Deux résultats rapportés séparément :
1. L'overlay défensif EWMA SEUL (même mécanisme que #115 : jamais de
   levier, critère Calmar), pour vérifier qu'il fonctionne en isolation
   avant de l'ajouter à l'ensemble.
2. L'ensemble à 3 moteurs (moyenne des 3 expositions #115+GARCH+EWMA),
   pour tester si un 3e estimateur indépendant réduit ENCORE le bruit
   résiduel, ou si le gain marginal du #121 (2 moteurs) s'épuise déjà
   (rendements décroissants).

## Définition (fixée ici, avant tout résultat)

- **Composant EWMA** : walk-forward, mêmes paramètres que l'usage déjà
  validé en Étape C (`run_etape_c.py`) : `T0=750`, `REFIT_EVERY=21j`
  (cadence NDX long historique), `λ=0.94` (défaut RiskMetrics, jamais
  retuné). À chaque refit `tr`, `mu_tr = r[:tr].mean()` (moyenne
  TRAIN-ONLY, cf. convention déjà validée), `s2 = ewma_path(r - mu_tr)`,
  seule la portion `[tr, tr+REFIT_EVERY)` de ce chemin est retenue
  (walk-forward strict, aucune mise à jour rétroactive).
  `Position(t) = clip(20% / sqrt(s2[t]*252), 0.0, 1.0x)` — mécanisme
  défensif identique au #115 (jamais de levier, floor 0.0x).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`), fenêtre
  OOS walk-forward (à partir de T0=750).
- **Ensemble à 3 moteurs** : `Position_combinée(t) = (Position_#115(t)
  + Position_GARCH#118(t) + Position_EWMA(t)) / 3`, sur l'intersection
  des 3 fenêtres (déjà committées pour #115/#118, nouvellement calculée
  pour EWMA).

## Critère de succès (deux volets, identiques à #115/#121)

1. Standard : Sharpe ET rendement > BH.
2. Calmar : Calmar > BH.
Rapportés séparément pour le composant EWMA seul ET pour l'ensemble à
3 moteurs. n_trials=1 pour chacune de ces deux constructions précises
(jamais testées).

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py` sur le meilleur des deux
(EWMA seul ou ensemble 3 moteurs), n_trials=taille totale du backlog.

## Anti-cheat

Ce fichier committé avant
`nonml_ewma_defensive_overlay_and_triple_engine_backtest.py`,
vérification via
`nonml_anti_cheat_check.py ewma_defensive_overlay_and_triple_engine`.
