# Pré-enregistrement — Overlay vol-targeting gaté par le spread décile de momentum

**Committé AVANT tout calcul.** Cycle #112 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` : un PASS niveau 1 ici n'est
PAS un verdict final, voir section dédiée ci-dessous.

## Hypothèse

Distinct du #100 (dispersion = écart-type cross-sectionnel du momentum,
pondère TOUS les titres également) : ce cycle mesure spécifiquement
l'écart entre les EXTRÊMES de la distribution — le spread décile
supérieur (10% des titres au momentum le plus fort) moins décile
inférieur (10% des titres au momentum le plus faible). C'est une mesure
de QUEUE de distribution, insensible à ce qui se passe au centre
(titres avec momentum proche de zéro), contrairement à l'écart-type
global du #100. Hypothèse : un spread décile élevé (queues très
séparées, marché en réelle bifurcation gagnants/perdants) est un régime
distinct, potentiellement plus informatif qu'une dispersion globale
diluée par la masse centrale — porte du même mécanisme hiérarchique déjà
validé (vol-targeting CAP=2.0x/20j/20% cible, floor 1.0x).

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 individuels, `data/pead/prices/*.json`
  (calendrier UNION des tickers, mêmes conventions que #94/#100).
- Momentum 12-1 mois par titre : `close(t-21) / close(t-252) - 1`
  (SKIP=21j, LOOKBACK=252j, identique à #94/#100 — AUCUN retuning).
- Chaque jour avec ≥`MIN_LISTED=10` titres éligibles (momentum
  calculable) : trie les scores de momentum, `decile_size =
  max(1, round(n_eligible * 0.1))`. `Spread(t) = moyenne(decile_size
  titres les plus forts) - moyenne(decile_size titres les plus
  faibles)`. NaN si <10 titres éligibles.
- Porte active si `Spread(t) ≥` sa médiane glissante 252j (même
  convention que #99/#100/#104/#109/#111 : régime ÉLEVÉ par rapport à
  son historique récent).
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique à toute la
  famille).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Échantillon restreint à la période où le signal titre-par-titre est
  disponible (leçon #77/#89), comme tous les membres de cette famille.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour ce backtest individuel.

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

Si le critère ci-dessus est atteint, ce résultat n'est PAS un verdict
final. `scripts/nonml_pass_validation_battery.py momentum_decile_spread_
vol_targeting_overlay` doit tourner et passer les 5 contrôles (stress
coûts 3x/5x, stress crise, stabilité temporelle par folds+embargo 5j,
SPA à 1 candidat, DSR à n_trials=taille totale du backlog) avant toute
notification ou déclaration de succès. Seulement si TOUS les contrôles
tiennent : notification Telegram, PUIS audit adversarial fin
supplémentaire.

## Robustesse prévue (SI PASS niveau 1, en plus de la batterie Règle 9)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — le décile (10%) et les fenêtres
momentum (252j/21j) ne sont PAS retunés (paramètres de définition de
l'hypothèse, identiques à #94/#100).

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_decile_spread_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py momentum_decile_spread_vol_targeting_overlay`.
