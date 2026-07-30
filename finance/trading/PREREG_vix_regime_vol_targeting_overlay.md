# Pré-enregistrement — Overlay vol-targeting gaté par le régime VIX (signal externe)

**Committé AVANT tout calcul.** Cycle #130 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Rupture avec la famille des estimateurs de volatilité AUTO-RÉFÉRENTIELS
déjà testés (réalisé #115, GJR-GARCH #118, EWMA #124 — tous calculés à
partir des rendements de l'actif piloté lui-même). Le VIX (CBOE
Volatility Index, série FRED `VIXCLS`, gratuite, récupérée le
30/07/2026, 1990-01-02→2026-07-28, 9542 observations) est un signal
GENUINEMENT externe : dérivé des prix d'options sur S&P 500, pas des
rendements historiques de NDX. Hypothèse a priori, **direction choisie
pour cohérence avec le pattern déjà établi dans ce backlog** (gates de
stress/breadth #89/#99/#100/#104/#109/#111/#112 : régime de stress
ÉLEVÉ par rapport à son historique récent = contrarian, amplifie
l'exposition) : VIX élevé (au-dessus de sa médiane glissante récente)
signale une opportunité contrarian (peur excessive, retour à la
moyenne), régime propice à amplifier l'exposition via le mécanisme
hiérarchique déjà validé. Direction NON choisie après avoir vu un
résultat — cohérente avec la convention majoritaire déjà utilisée pour
tous les gates de "stress" de ce backlog.

## Définition (fixée ici, avant tout résultat)

- Signal : `data/vixcls_daily.csv` (FRED VIXCLS, quotidien).
- Alignement causal : `VIX(t-1)` (veille de bourse, jamais le jour
  même — même discipline que #110/#114).
- `MEDIAN_WINDOW = 252` séances (médiane glissante, convention
  identique à toute la famille).
- Porte active si `VIX(t-1) ≥` sa médiane glissante 252j.
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique à toute la
  famille — SEULE la porte change).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Univers : NDX (40 ans) — historique VIX (1990+) plus court que NDX
  (1985+), échantillon testable = intersection des dates disponibles.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1.

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py vix_regime_vol_targeting_
overlay`, n_trials=taille totale du backlog.

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — MEDIAN_WINDOW=252j n'est PAS
retuné.

## Anti-cheat

Ce fichier committé avant
`nonml_vix_regime_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py vix_regime_vol_targeting_overlay`. Fichier
de données `data/vixcls_daily.csv` committé en même temps que ce
PREREG.
