# Pré-enregistrement — Overlay vol-targeting gaté par le clustering ARCH glissant

**Committé AVANT tout calcul.** Cycle #223 du backlog non-ML. Idée #223
proposée au cycle #221, dernière ligne "à faire" de la série
d'estimateurs range-based et de clustering de volatilité (#221 Rogers-
Satchell PASS, #222 Yang-Zhang PASS).

## Hypothèse

Le mécanisme #46 pilote l'exposition en supposant que la volatilité
réalisée récente (décalée d'un jour) prédit bien la volatilité proche
future — c'est l'hypothèse implicite de TOUT vol-targeting. Cette
hypothèse est d'autant plus fiable que l'effet ARCH (clustering de
volatilité, autocorrélation des rendements AU CARRÉ) est FORT : dans un
régime de clustering intense, la vol d'hier est un bon prédicteur de la
vol de demain. Quand l'effet ARCH est FAIBLE (vol plus erratique/
idiosyncratique localement), l'hypothèse implicite du mécanisme est moins
valide. Ce cycle teste l'intensité de l'effet ARCH lui-même comme porte
du mécanisme hiérarchique — distinct du VR (#217, qui porte sur
l'autocorrélation des rendements BRUTS, pas leurs carrés) et de la
vol-de-la-vol (#220, qui porte sur la variabilité du NIVEAU de vol, pas
sur sa prévisibilité/clustering).

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
autorisée) quand `ARCH_stat(t) >= médiane glissante 252j de ARCH_stat`,
c'est-à-dire un clustering de volatilité récent AU-DESSUS de sa norme
historique récente (l'hypothèse implicite du vol-targeting est alors plus
fiable). Technique auto-référencée identique aux #78/#216/#218/#219/#220.

## Définitions et alignement causal (déclarés avant calcul)

- `r²(i)` = rendement log quotidien au carré.
- `ARCH_stat(t)` = autocorrélation empirique à retard 1 de la série
  `r²` sur la fenêtre `r²[t-ARCH_WINDOW:t]` (ARCH_WINDOW=252 observations
  se terminant à `r²[t-1]`, donc EXCLUANT `r²[t]` lui-même, calculée comme
  `corr(window[:-1], window[1:])` sur cette fenêtre — même convention
  causale que les #217/#218/#219/#220).
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216/#218/
  #219/#220 (Règle 7). `ARCH_WINDOW=252` réutilisé de la même fenêtre
  dominante.
- Porte = `ARCH_stat(t) >= rolling_median_252j(ARCH_stat)(t)`.
  Alignement causal identique aux #217-#220 : `gate[k]` déjà causal par
  construction, appliqué directement à `r[k]`, sans décalage
  supplémentaire.

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80/#216-#220)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 254e séance (même convention que
les #217-#220).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — rendements
déjà disponibles, aucun nouveau fetch.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#222).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'autocorrélation des rendements au carré est un estimateur bruité
   sur des fenêtres de taille modérée (252 observations) — le signal
   pourrait être dominé par du bruit d'estimation, comme déjà anticipé
   pour le VR (#217) et la skewness (#218).
2. Cette porte pourrait être fortement corrélée à la vol-de-la-vol (#220,
   PASS) puisque les deux mesurent des propriétés de second ordre de la
   dynamique de volatilité — risque de redondance plutôt que
   d'information marginale nouvelle.
3. Le DSR est hors de portée pour les 223 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_arch_clustering_vol_targeting_overlay_backtest.py`
(nouveau). Vérification via `nonml_anti_cheat_check.py
arch_clustering_vol_targeting_overlay`.
