# Pré-enregistrement — Porte de profondeur de drawdown glissante pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #250 du backlog non-ML. Backlog "à
faire" épuisé après le #249 (correction mécanique mitigée) ; ce cycle
reprend la 3e des 3 pistes proposées à sa clôture.

## Hypothèse et distinction explicite avec le #38/#161-164 (déjà testés)

`prediction.py::build_features` calcule déjà `drawdown_60 = close/
roll_max(60) - 1` (Étape B), jamais réutilisé dans le backlog non-ML
comme porte du mécanisme hiérarchique #46. **Distinction méthodologique
explicite avec le #38** (momentum, Sharpe brut record, ré-évalué #161-164
avec correction du biais du survivant) : le #38 utilisait la proximité
au plus-haut comme **remplacement direct de l'exposition** via un
**seuil FIXE et absolu** (`≥95% du plus-haut` double l'exposition) — un
mécanisme identifié comme la cause de son échec de crise (double
l'exposition exactement dans la configuration de février 2020, #163).
Ce cycle utilise au contraire le mécanisme #46 **INCHANGÉ** (vol
réalisée comme dénominateur) et une porte **relative et adaptative**
(comparaison à sa propre médiane glissante), exactement la même
convention que TOUTES les autres portes déjà testées (VR #217, kurtosis
#219, vol-de-la-vol #220, clustering ARCH #223/#242, ν Student-t #237)
— pas un seuil absolu fixé arbitrairement comme le #38.

**Direction déclarée à l'avance (Règle 2)** : porte active quand
`drawdown_60(t) >= médiane glissante 252j de drawdown_60`, c'est-à-dire
un drawdown MOINS profond que la norme récente (plus proche des plus
hauts que d'habitude) = régime sain = amplifier — même logique
"calme=amplifier" que toute la lignée de portes.

## Définitions et alignement causal (déclarées avant calcul)

- `drawdown_60(t) = close(t)/rolling_max_60j(close)(t) - 1` (fenêtre de
  60j réutilisée à l'identique de `build_features`, Règle 7), décalé
  d'un jour (`np.roll(...,1)`) pour n'utiliser que l'information connue
  à la clôture de `t-1`, comme toute la lignée de portes.
- `MEDIAN_WINDOW=252` réutilisé à l'identique de toute la lignée #78-
  #249 (Règle 7).
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  CAP=2.0, COST_BPS=5 bps, Règle 7). **Aucun doublement de seuil fixe
  comme le #38** — la porte ne fait qu'autoriser/interdire
  l'amplification déjà bornée à 2,0x par le mécanisme #46.
- Échantillon testable à partir de la 312e séance (60j amorçage + 252j
  médiane).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que toute la lignée de portes #47-#249.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#249).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Bien que la construction diffère du #38 (porte relative vs seuil
   fixe, mécanisme #46 inchangé vs remplacement d'exposition), le
   thème sous-jacent (proximité aux plus-hauts) reste apparenté — si le
   contrôle de crise échoue pour la même raison économique que le #38
   (amplifier près des plus-hauts est risqué juste avant un choc), ce
   serait cohérent et informatif plutôt que surprenant.
2. Le drawdown 60j est très lentement variable (mémoire longue,
   similaire aux estimateurs à mémoire longue déjà en échec : ATR #233,
   HAR-P #236) — risque de turnover/réactivité insuffisante.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_drawdown_depth_vol_targeting_overlay_backtest.py`
(nouveau) et
`scripts/nonml_drawdown_depth_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
drawdown_depth_vol_targeting_overlay`.
