# Pré-enregistrement — Overlay vol-targeting gaté par la breadth de drawdown PROFOND (seuil absolu)

**Committé AVANT tout calcul.** Cycle #111 du backlog non-ML. Premier
cycle sous la **Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` (batterie de
validation renforcée obligatoire avant toute déclaration de PASS final).

## Hypothèse

Distinct du #89 (breadth de faiblesse, proximité RELATIVE au minimum
glissant, ≤105% du plus bas 252j) : ce cycle teste un seuil de douleur
ABSOLU — la fraction de titres NDX-100 dont le prix est au moins 20% sous
leur plus haut glissant 252 jours (définition standard d'un "bear market"
individuel), indépendamment de la distance au plus bas. Hypothèse
contrarian : une fraction élevée de titres en drawdown profond simultané
signale une capitulation large du marché, régime historiquement suivi de
rebonds — porte du mécanisme hiérarchique déjà validé (vol-targeting
CAP=2.0x/20j/20% cible, floor 1.0x).

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 individuels, `data/pead/prices/*.json`
  (calendrier UNION des tickers, comme #78/#89/#94/etc.).
- `RollingHigh_252(t)` = maximum glissant du prix de clôture sur 252
  séances (fenêtre PLEINE requise, comme #89 : `has_full`).
- Titre en drawdown profond au jour t si `close(t) <= 0.80 *
  RollingHigh_252(t)` (seuil ABSOLU fixe -20%, PAS un multiple de la
  distribution observée).
- `Breadth_DD(t)` = fraction des titres COTÉS ce jour-là (prix du jour
  fini, dénominateur = tous les titres listés, PAS seulement ceux avec
  fenêtre 252j complète — même convention que #89/#94/#96/#97, cf. leçon
  documentée dans l'audit du 29/07/2026 sur ce point précis).
- Porte active si `Breadth_DD(t) ≥` sa médiane glissante 252j (même
  convention que #99/#100/#104/#109 : régime ÉLEVÉ par rapport à son
  historique récent, pas un seuil absolu sur la breadth elle-même).
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique à toute la
  famille, CAP=2.0x/VOL_WINDOW=20j/TARGET_VOL_ANNUAL=20%).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Échantillon restreint à la période où le signal titre-par-titre est
  disponible (leçon #77/#89), comme tous les membres de cette famille.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1 — inchangé)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour ce backtest individuel
(construction nouvelle, jamais testée).

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

Si le critère ci-dessus est atteint, ce résultat n'est PAS un verdict
final. `scripts/nonml_pass_validation_battery.py deep_drawdown_breadth_
vol_targeting_overlay` doit tourner et passer les 5 contrôles (stress
coûts 3x/5x, stress crise, stabilité temporelle par folds+embargo 5j,
SPA à 1 candidat, DSR à n_trials=taille totale du backlog) avant toute
notification ou déclaration de succès. Seulement si TOUS les contrôles
tiennent : notification Telegram, PUIS audit adversarial fin
supplémentaire (recalcul indépendant, anti-lookahead, calibration).

## Robustesse prévue (SI PASS niveau 1, en plus de la batterie Règle 9)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — le seuil de drawdown -20% et la
fenêtre 252j ne sont PAS retunés (paramètres de définition de
l'hypothèse, pas des hyperparamètres du mécanisme).

## Anti-cheat

Ce fichier committé avant
`nonml_deep_drawdown_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py deep_drawdown_breadth_vol_targeting_overlay`.
