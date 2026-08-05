# Pré-enregistrement — Porte de largeur de bande de Bollinger pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #247 du backlog non-ML. Backlog "à
faire" épuisé après le #246 (analyse de corrélation) ; ce cycle reprend
la 1ère des 2 pistes proposées à la clôture du #245.

## Hypothèse

`prediction.py::build_features` (Étape B) calcule déjà `ma20`/`sd20`
(moyenne et écart-type glissants du PRIX sur 20 jours) pour produire
`bb_pctb` (position %B dans les bandes de Bollinger), mais jamais la
LARGEUR de bande elle-même — une mesure de dispersion du prix autour de
sa moyenne mobile, normalisée par le niveau de prix plutôt que par le
rendement. Distincte du dénominateur du mécanisme #46 (écart-type des
RENDEMENTS log annualisé) : la largeur de Bollinger est calculée sur le
PRIX brut (pas les rendements), rescalée par la moyenne mobile du prix
plutôt que par `sqrt(252)`. Ce cycle teste cette mesure comme porte du
mécanisme hiérarchique standard.

**Direction déclarée à l'avance (Règle 2)** : porte active quand
`largeur_Bollinger(t) <= médiane glissante 252j`, c'est-à-dire une bande
resserrée ("squeeze") par rapport à la norme récente = calme = amplifier
(même logique "calme=amplifier" que #216/#219/#220/#223/#237/#242).

## Définitions et alignement causal (déclarées avant calcul)

- `ma20(t)` = moyenne mobile 20j du close, `sd20(t)` = écart-type mobile
  20j du close (mêmes fenêtres et mêmes fonctions que `bb_pctb` à
  l'Étape B, Règle 7).
- `largeur_Bollinger(t) = 4 × sd20(t) / ma20(t)` (bande supérieure −
  bande inférieure, normalisée par la bande médiane) — décalée d'un jour
  (`np.roll(...,1)`) pour n'utiliser que l'information connue à la
  clôture de `t-1`, comme toute la lignée de portes.
- `MEDIAN_WINDOW=252` réutilisé à l'identique de toute la lignée #78-
  #242 (Règle 7).
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  CAP=2.0, COST_BPS=5 bps, Règle 7).
- Échantillon testable à partir de la 272e séance (20j amorçage + 252j
  médiane), même ordre de grandeur que les autres portes à fenêtre
  courte (#216-#220).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que toute la lignée de portes #47-#242.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#246).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La largeur de Bollinger est mathématiquement très proche d'une
   vol réalisée glissante 20j (même fenêtre, même écart-type sous-jacent,
   juste normalisée différemment) — risque de forte redondance avec le
   dénominateur du mécanisme #46 lui-même, pouvant produire un signal de
   porte quasi-constant ou peu informatif (porte souvent alignée avec
   l'état déjà capturé par `vol_réalisée_20j`).
2. La normalisation par le PRIX (moyenne mobile) plutôt que par le
   niveau de rendement peut introduire une dérive de longue durée (sur
   un marché tendanciel, `ma20` croît, ce qui comprime artificiellement
   la largeur relative même à volatilité de rendement inchangée) —
   distinct des estimateurs déjà testés, à documenter honnêtement si
   observé.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_bollinger_width_vol_targeting_overlay_backtest.py`
(nouveau) et
`scripts/nonml_bollinger_width_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
bollinger_width_vol_targeting_overlay`.
