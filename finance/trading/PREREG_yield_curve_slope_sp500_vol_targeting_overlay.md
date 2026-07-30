# Pré-enregistrement — Pente de la courbe des taux US (T10Y2Y) appliquée au S&P 500

**Committé AVANT tout calcul.** Cycle #126 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Le #114 (même mécanisme, gate T10Y2Y) a montré un profil intéressant
sur NDX (40 ans, SPA significatif pour la 1ère fois, p=0,043) mais
reste limité par la taille d'échantillon de la famille titre-par-titre
(~1385 séances) pour les AUTRES candidats de ce backlog. Ce cycle
n'ajoute PAS un nouveau signal — il ré-applique EXACTEMENT le mécanisme
déjà validé du #114 à un second marché INDÉPENDANT au sens de la Règle
3 de PROTOCOLE_ANTI_SNOOPING.md (S&P 500, marché large US distinct du
NASDAQ). Choix pré-enregistré AVANT tout calcul : **S&P 500** (parmi
Russell 2000/S&P 500/DAX autorisés par la Règle 3) — cohérence
économique directe avec le signal (courbe des taux US, marché actions
US large), pas un choix fait après avoir vu un résultat sur les 3.
Russell 2000 et DAX restent disponibles pour un futur cycle SÉPARÉ si
besoin, mais ne sont PAS testés ici (éviter la sélection post-hoc du
"meilleur des 3").

## Définition (fixée ici, avant tout résultat — IDENTIQUE au #114, seul
le marché piloté change)

- Signal : `data/t10y2y_daily.csv` (déjà en local, FRED T10Y2Y).
- Alignement causal : `Slope(t-1)` (veille de bourse), `MEDIAN_WINDOW =
  252` séances, porte active si `Slope(t-1) ≥` sa médiane glissante.
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x — mécanisme hiérarchique identique, AUCUN
  paramètre retuné.
- **Coûts** : 5 bps par unité de turnover.
- **Univers piloté** : S&P 500 (`sp500_daily.txt`, déjà en local).
- **Référence** : Buy & Hold sur S&P 500.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour CE marché précis (une
extension géographique du #114, pas une nouvelle construction).

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py yield_curve_slope_sp500_vol_
targeting_overlay`, n_trials=taille totale du backlog.

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j}.

## Anti-cheat

Ce fichier committé avant
`nonml_yield_curve_slope_sp500_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py yield_curve_slope_sp500_vol_targeting_overlay`.
