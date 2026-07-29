# Pré-enregistrement — Overlay vol-targeting gaté par vote majoritaire (ensemble de 5 gates déjà validées niveau 1)

**Committé AVANT tout calcul.** Cycle #113 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Après #111/#112 : aucune variante ISOLÉE de la famille vol-targeting
gatée par un signal cross-sectionnel n'a de chance réaliste de passer le
DSR à n_trials=110 (edge individuel trop petit face au bruit de
sélection). Hypothèse : agréger PLUSIEURS signaux imparfaitement
corrélés (chacun déjà PASS niveau 1, agreement rate mesuré entre 55% et
77% par paire dans les audits précédents — donc ni identiques ni
indépendants) par un vote majoritaire pourrait réduire le bruit de
timing individuel de chaque porte et produire un signal composite plus
stable, potentiellement plus proche de passer la batterie renforcée
qu'aucun des 5 composants pris isolément.

**Limite méthodologique assumée explicitement** : les 5 membres ne sont
PAS choisis à l'aveugle — ce sont les 5 gates DÉJÀ CONNUES comme PASS
niveau 1 dans ce backlog (#78, #89, #100, #104, #112), sélectionnées
après avoir vu leurs résultats individuels. Ce choix introduit un biais
de sélection que la Règle 9 (n_trials=110, pas remis à zéro pour cet
ensemble) est censée absorber en partie, mais qui reste un facteur
aggravant à interpréter avec prudence si le résultat est positif.

## Définition (fixée ici, avant tout résultat)

- Les 5 membres (constructions déjà committées, réimportées SANS
  modification) :
  1. `#78` dispersion cross-sectionnelle ≥ médiane 252j
     (`nonml_dispersion_vol_targeting_overlay_backtest.py`)
  2. `#89` weakness breadth (fraction proche du plus bas 252j) > 0
     (`nonml_weakness_breadth_vol_targeting_overlay_backtest.py` —
     porte continue dans l'original, seuillée ici à >0 pour un vote
     booléen, comportement identique à son usage original où
     `np.where` traite tout non-zéro comme actif)
  3. `#100` dispersion du momentum ≥ médiane 252j
     (`nonml_momentum_dispersion_vol_targeting_overlay_backtest.py`)
  4. `#104` position continue dans le range 252j ≥ médiane 252j
     (`nonml_range_position_vol_targeting_overlay_backtest.py`)
  5. `#112` spread décile de momentum ≥ médiane 252j
     (`nonml_momentum_decile_spread_vol_targeting_overlay_backtest.py`)
- `Vote(t)` = nombre de ces 5 portes actives au jour t (0 à 5).
- Porte ENSEMBLE active si `Vote(t) ≥ 3` (majorité stricte).
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  ensemble active, sinon 1.0x (mécanisme hiérarchique identique).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX.
- Échantillon restreint à la période où TOUS les 5 signaux sont
  disponibles simultanément (intersection des 5 fenêtres individuelles).

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour CETTE construction d'ensemble
(distincte des 5 essais individuels déjà comptés séparément dans le
backlog).

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

Identique aux cycles précédents : `nonml_pass_validation_battery.py
ensemble_vote_vol_targeting_overlay`, n_trials=taille totale du backlog
(PAS remis à 5 sous prétexte que c'est "un seul ensemble" — même
principe que la Règle 2 appliquée à un sous-ensemble).

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x},
fenêtre de vol ∈ {15j, 20j, 25j, 30j}, ET seuil de vote ∈ {2, 3, 4}
sur 5 (le seuil de majorité fait partie de la définition du mécanisme
d'agrégation, pas un signal brut retuné après résultat — grille
symétrique autour de 3, PAS choisie après avoir vu le résultat à 3).

## Anti-cheat

Ce fichier committé avant
`nonml_ensemble_vote_vol_targeting_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py ensemble_vote_vol_targeting_overlay`.
