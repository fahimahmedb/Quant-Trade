# Pré-enregistrement — Porte de clustering ARCH par statistique de Ljung-Box glissante

**Committé AVANT tout calcul.** Cycle #242 du backlog non-ML. Backlog "à
faire" épuisé après le #241 (batterie Règle 9 sur le #240) ; ce cycle
reprend la 1ère des 3 pistes proposées à la clôture du #241.

## Hypothèse

`diagnostics.py::ljung_box` (Étape A, lags=(5,10,22), déjà utilisé pour
diagnostiquer l'effet ARCH massif documenté à l'Étape A) n'a jamais été
réutilisé comme signal tradable — seule l'autocorrélation à UN SEUL
retard des rendements au carré a été testée (#223, clustering ARCH, PASS
4/5). Ce cycle construit un signal DISTINCT : la statistique de Ljung-Box
Q, un test omnibus qui agrège l'information de PLUSIEURS retards
(1 à 22 jours, portée mensuelle) en une seule statistique pondérée,
plutôt que la seule autocorrélation adjacente (lag 1) du #223 — capture
un clustering ARCH étalé sur plusieurs horizons plutôt qu'un
raccrochement immédiat d'un jour sur l'autre.

**Direction déclarée à l'avance (Règle 2)** : porte active quand
`Q_LjungBox_22j(t) <= médiane glissante 252j de Q`, c'est-à-dire un
clustering ARCH FAIBLE par rapport à la norme récente = calme = amplifier
(même logique "calme=amplifier" que #216/#219/#220/#223/#237).

## Définitions et alignement causal (déclarées avant calcul)

- `Q_LjungBox_22j(t)` = statistique de Ljung-Box calculée sur les
  rendements AU CARRÉ de la fenêtre `r[t-LB_WINDOW:t]` (STRICTEMENT
  antérieure à `t`, donc causale), retard maximal `h=22` (le plus long
  des trois retards déclarés à l'Étape A, `lags=(5,10,22)` — choix
  unique fixé à l'avance, pas de sélection parmi les trois après
  résultat) : `Q(h) = n(n+2) * Σ_{k=1}^{h} ρ_k² / (n-k)`, formule standard
  de Ljung-Box, implémentée directement pour l'usage glissant (même
  statistique que `diagnostics.py::ljung_box`, adaptation Règle 7 comme
  pour EWMA/HAR/ν Student-t précédemment dans ce backlog — `statsmodels.
  acorr_ljungbox` n'est pas conçu pour un usage glissant quotidien sur
  plusieurs milliers de fenêtres).
- `LB_WINDOW=252` réutilisé de la convention ARCH_WINDOW=252 du #223
  (Règle 7).
- `MEDIAN_WINDOW=252` réutilisé à l'identique de toute la lignée #78-
  #240 (Règle 7).
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  CAP=2.0, COST_BPS=5 bps, Règle 7).
- Échantillon testable à partir de la 504e séance (252j fenêtre + 252j
  médiane), même ordre de grandeur que les autres portes de moments/
  clustering (#218-#223, #237).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que #223 et #237.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#241).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Si le clustering ARCH capturé par Ljung-Box est fortement corrélé au
   clustering lag-1 déjà testé (#223, PASS 4/5), un résultat similaire ou
   légèrement dégradé est plausible (cf. le #240 où deux signaux corrélés
   n'ont produit ni amélioration ni dégradation nette).
2. L'agrégation sur 22 jours pourrait lisser excessivement le signal
   (mémoire plus longue que le lag 1 du #223), produisant un profil plus
   proche des estimateurs à mémoire longue déjà en échec dans ce backlog
   (ATR #233, HAR-P #236) que du #223 lui-même.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_ljung_box_clustering_vol_targeting_overlay_backtest.py`
(nouveau) et
`scripts/nonml_ljung_box_clustering_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
ljung_box_clustering_vol_targeting_overlay`.
