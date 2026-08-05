# Pré-enregistrement — Porte d'autocorrélation à un seul retard (ACF lag-1) pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #248 du backlog non-ML. Reprend la
1ère des pistes proposées à la clôture du #247, après vérification
préalable de redondance déclarée ci-dessous.

## Vérification préalable de redondance (déclarée avant le backtest, Règle 2)

Avant d'engager ce cycle, une vérification rapide (pas un backtest, pas
committée comme résultat séparé) a été faite : corrélation entre le VR(5)
glissant (#217, `lo_mackinlay_vr`) et l'ACF(1) glissante sur NDX, fenêtres
252j échantillonnées tous les 21j (n=472) : **ρ=0,87**. Une corrélation
élevée était attendue (VR(5) est par construction une somme pondérée des
ACF aux retards 1 à 4, avec le poids le plus élevé sur le retard 1), mais
**pas parfaite** — 24% de variance non expliquée. Ce cycle teste malgré
cette corrélation connue si l'ACF(1) seule (statistique plus simple,
poids concentré sur un seul retard plutôt que dilué sur 4) produit un
profil qualitativement différent du #217 (PASS 4/5 niveau 1, mais
Règle 9 seulement 1/5, la porte la plus rare de la lignée). **Risque
explicitement assumé** : un résultat quasi identique au #217 est
plausible et serait rapporté comme tel, sans forcer une distinction
artificielle.

## Hypothèse

`diagnostics.py::acf` (Étape A, jamais réutilisé comme signal tradable)
calcule l'autocorrélation à un ou plusieurs retards. Ce cycle construit
une porte à partir du SEUL retard 1 (persistance immédiate d'un jour sur
l'autre), par opposition au VR(5) déjà testé qui agrège les retards 1 à 4.

**Direction déclarée à l'avance (Règle 2)** : porte active quand
`ACF(1)(t) >= médiane glissante 252j`, c'est-à-dire une persistance
immédiate plus forte que la norme récente = régime tendanciel = amplifier
— même logique que le VR(5) du #217 (VR≥1 = persistance = amplifier,
cohérent avec la lignée tendance #47/#68 déjà validée).

## Définitions et alignement causal (déclarées avant calcul)

- `ACF(1)(t)` = autocorrélation à retard 1 calculée sur `r[t-ACF_WINDOW:t]`
  (fenêtre STRICTEMENT antérieure à `t`, donc causale) : `Σ(r_i-μ)(r_{i-1}-μ)
  / Σ(r_i-μ)²` sur la fenêtre.
- `ACF_WINDOW=252` réutilisé de la convention du VR(5) (`lo_mackinlay_vr`
  utilisé avec une fenêtre glissante 252j au #217, Règle 7).
- `MEDIAN_WINDOW=252` réutilisé à l'identique de toute la lignée #78-
  #247 (Règle 7).
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  CAP=2.0, COST_BPS=5 bps, Règle 7).
- Échantillon testable à partir de la 504e séance (252j fenêtre + 252j
  médiane), même ordre de grandeur que le #217.

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que le #217.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#247).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La corrélation ρ=0,87 avec le VR(5) rend un résultat quasi identique
   au #217 (PASS 4/5, DAX seul échoue, Règle 9 1/5) le scénario le plus
   probable — pas une découverte réellement nouvelle, à documenter
   honnêtement si c'est le cas.
2. Une statistique à un seul retard, plus bruitée qu'une agrégation sur
   4 retards, pourrait être moins stable que le VR(5) plutôt
   qu'équivalente — un résultat DÉGRADÉ par rapport au #217 est tout
   aussi plausible qu'un résultat identique.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_acf_lag1_vol_targeting_overlay_backtest.py` (nouveau) et
`scripts/nonml_acf_lag1_vol_targeting_overlay_audit.py`. Vérification
via `nonml_anti_cheat_check.py acf_lag1_vol_targeting_overlay`.
