# Pré-enregistrement — Overlay vol-targeting gaté par le régime de corrélation moyenne

**Committé AVANT tout calcul.** Cycle #90 du backlog non-ML.

## Hypothèse

La littérature documente une hausse de la corrélation moyenne entre
titres en période de stress de marché (perte du bénéfice de
diversification, "tous les titres baissent ensemble"). C'est une
dimension DISTINCTE de la dispersion cross-sectionnelle du #78 (PASS) :
la dispersion mesure l'AMPLITUDE des écarts de rendement du jour entre
titres (peut être élevée même si les titres sont fortement corrélés, si
les bêtas diffèrent), la corrélation mesure leur CO-MOUVEMENT temporel.
Une corrélation moyenne BASSE (titres évoluant de façon plus
idiosyncratique) signale un régime plus "sain"/diversifié, analogue
conceptuellement au régime calme du #9 mais mesuré différemment ; une
corrélation ÉLEVÉE signale un régime de stress/risk-off où amplifier
l'exposition serait imprudent (cohérent avec le FAIL du #31, vol
élevée = phases de baisse). Le mécanisme teste donc : porte active
(amplification vol-targeting) quand la corrélation moyenne est SOUS sa
médiane glissante, 1.0x sinon — même structure que le #78 (comparaison
à une médiane glissante causale), direction de comparaison adaptée au
sens économique opposé de la corrélation vs la dispersion.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #78/#84/#89.
- Corrélation moyenne(t) = moyenne des corrélations par paires
  (triangle supérieur, hors diagonale) des rendements log quotidiens
  sur une fenêtre roulante `CORR_WINDOW=60` jours, calculée UNIQUEMENT
  sur les titres ayant un historique complet sur cette fenêtre au jour
  t (calcul causal, connu à la clôture de t).
- Médiane glissante `MEDIAN_WINDOW=252` jours de cette série de
  corrélation moyenne (identique au #78).
- Porte active si corrélation moyenne(t) ≤ médiane glissante(t)
  (régime de corrélation SOUS la médiane = plus diversifié/sain).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89.
- Échantillon restreint à la période où la corrélation est réellement
  calculable (leçon du #77, appliquée dès le départ).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (CORR_WINDOW=60j
et MEDIAN_WINDOW=252j fixés ici a priori — 60j par analogie avec le
Low-Vol tilt #15/#53, 252j identique au #78 —, CAP=2.0x et vol
cible/fenêtre identiques au #46/#47/#78, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol-targeting ∈ {15j, 20j, 25j, 30j} — identique au
#47/#57/#78. `CORR_WINDOW` et `MEDIAN_WINDOW` ne sont PAS perturbés
(au cœur de la construction du signal, pas des paramètres accessoires).

## Anti-cheat

Ce fichier committé avant
`nonml_correlation_regime_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
correlation_regime_vol_targeting_overlay`.
