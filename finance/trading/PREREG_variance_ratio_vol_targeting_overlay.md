# Pré-enregistrement — Overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant

**Committé AVANT tout calcul.** Cycle #217 du backlog non-ML. Idée #217
proposée au cycle #215, première ligne "à faire" de ce cycle.

## Hypothèse

`diagnostics.py::lo_mackinlay_vr` (Étape A) est déjà implémenté et validé
(VR(5)=0,89, z\*=-2,68, p=0,007 sur NDX 40 ans, retour à la moyenne faible
mais détecté — voir CLAUDE.md) mais n'a jamais été exploité comme SIGNAL
TRADABLE dans ce backlog — seulement comme diagnostic statique sur
l'échantillon entier. Ce cycle teste le ratio de variance en fenêtre
GLISSANTE comme porte du mécanisme hiérarchique vol-targeting (#46),
un type de signal encore jamais testé (autocorrélation locale, distinct
de la tendance #47/#68, du calendrier #54, de la breadth #57, de la
dispersion #78, de l'annuel #80 et du risque de gap #216).

**Direction déclarée à l'avance (Règle 2)** : le mécanisme #46/#47/#68
amplifie déjà l'exposition selon une logique de PERSISTANCE directionnelle
(tendance haussière = amplifier). Par cohérence avec cette logique
existante, l'hypothèse retenue AVANT tout calcul est : `VR(q) >= 1`
(autocorrélation positive locale, momentum/persistance) = régime favorable
à l'amplification ; `VR(q) < 1` (autocorrélation négative locale, retour à
la moyenne/marché heurté) = régime défavorable, position 1,0x (pas de
levier supplémentaire, risque de faux signaux plus élevé dans un régime
de retournements fréquents). Cette direction n'est PAS choisie après avoir
vu un résultat — c'est la lecture la plus cohérente avec le reste de la
famille de portes hiérarchiques déjà validées sur cette logique.

## Définitions et alignement causal (déclarés avant calcul)

- `q=5` réutilisé à l'identique de la valeur vedette de l'Étape A pour
  NDX (Règle 7 — pas de nouveau réglage ; l'Étape A a aussi testé q=2 et
  q=10, mais q=5 est le résultat cité dans CLAUDE.md).
- `WINDOW=252` réutilisé à l'identique des fenêtres de régime déjà
  utilisées dans cette famille (#47 INDEX_LOOKBACK, #78/#100/#216
  MEDIAN_WINDOW).
- Pour chaque jour de décision `k` (indice sur `r`, rendements
  clôture-à-clôture, `r[k]=log(close[k+1]/close[k])`), la porte
  `gate[k] = VR(q) calculé sur la fenêtre r[k-WINDOW:k]` (WINDOW
  observations se terminant à `r[k-1]`, donc EXCLUANT `r[k]` lui-même,
  qui n'est réalisé qu'à la clôture du jour k+1 et n'est donc pas connu
  à la clôture du jour k, jour de décision). `gate[k] = (VR>=1.0)`.
- Robustesse numérique déclarée à l'avance : `lo_mackinlay_vr` contient
  un `assert` de cohérence interne (VR vs somme d'autocorrélations) qui
  peut ponctuellement échouer sur une fenêtre dégénérée (variance quasi
  nulle) — dans ce cas, la fenêtre est traitée comme porte INACTIVE par
  défaut (1,0x), jamais comme une exception qui interrompt le calcul.

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80/#216)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 254e séance (WINDOW=252 + décalage
d'une séance pour le premier rendement disponible).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — OHLC déjà en
local, aucun nouveau fetch. Fonction `lo_mackinlay_vr` déjà implémentée
et testée à l'Étape A (`diagnostics.py`), réutilisée sans modification.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#216).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le VR(q) glissant sur une fenêtre de 252 jours varie probablement
   assez lentement (comme un signal de tendance lente #68) — le #68 a
   obtenu le score Règle 9 le plus faible de la lignée à cause d'une
   réactivité insuffisante ; le VR pourrait souffrir du même problème
   en PASS niveau 1 déjà (pas seulement Règle 9).
2. Le lien entre VR(q)>=1 et une réelle persistance EXPLOITABLE (nette de
   coûts) n'est pas garanti même si statistiquement détecté à l'Étape A
   sur l'échantillon entier (diagnostic non conditionnel) — un régime
   local peut différer du diagnostic global.
3. Le coût de calcul (boucle sur ~10 000 fenêtres pour NDX) est assumé
   comme acceptable ; en cas de lenteur excessive, le script sera
   optimisé (vectorisation) SANS changer la formule ni le résultat,
   déclaré ici à l'avance pour ne pas être interprété comme un ajustement
   de spécification après résultat.
4. Le DSR est hors de portée pour les 217 hypothèses testées jusqu'ici
   sans aucune exception.
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_variance_ratio_vol_targeting_overlay_backtest.py`
(nouveau). Vérification via `nonml_anti_cheat_check.py
variance_ratio_vol_targeting_overlay`.
