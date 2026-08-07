# Pré-enregistrement — Sleeve dollar-neutre composite redimensionné par sa propre volatilité (Piste C)

**Committé AVANT tout calcul.** Cycle #350 du backlog non-ML.

## 1. Contexte et motivation (Piste C de `RECHERCHE_dsr_par_construction.md`, suite directe du #349)

Le #349 (sleeve L/S dollar-neutre composite #4+#73+#82+#15, univers
PIT) a produit un résultat proche du seuil mais FAIL : Sharpe annualisé
**+0,45** (positif, > référence), **t-stat +1,52** (< 2 requis). La
Piste C de `RECHERCHE_dsr_par_construction.md` §7, explicitement
désignée comme "variante de la piste A, à ne tester qu'après A, et à
compter comme un essai supplémentaire", propose le redimensionnement
du sleeve par sa PROPRE volatilité réalisée — mécanisme documenté par
Daniel & Moskowitz (*Momentum Crashes*, JFE) et Barroso & Santa-Clara :
le vol-targeting d'un portefeuille momentum long/short **double
approximativement son Sharpe** et supprime l'essentiel des "krachs"
(pertes extrêmes concentrées en régime de vol élevée), car il retire
la variance des périodes de crise du dénominateur du Sharpe sans
retirer la totalité du rendement moyen.

**Aucun nouveau signal, aucune nouvelle donnée** : ce cycle applique
mécaniquement l'overlay de vol-targeting DÉJÀ pré-enregistré et validé
(#46, `nonml_vol_targeting_overlay_backtest.py`) au flux de rendement
du sleeve du #349 (`pnl_sleeve_net`, déjà committé dans
`results/nonml_dollar_neutral_composite_pit_pnl.npz`) — zéro degré de
liberté ajouté sur le signal, zéro paramètre optimisé après résultat.

## 2. Mécanisme (réutilisation STRICTE du #46, Règle 7 — formule et constantes inchangées)

- `vol_target_position(r)` importée telle quelle de
  `nonml_vol_targeting_overlay_backtest.py` : `pos(t) = clip(TARGET_VOL_ANNUAL
  / vol_réalisée_20j(r, t-1), 0, CAP)`, avec `TARGET_VOL_ANNUAL=0,15`,
  `VOL_WINDOW=20`, `CAP=2,0` — **aucune de ces trois constantes n'est
  modifiée**.
- `r` = `pnl_sleeve_net` du #349 (rendement quotidien du sleeve,
  DÉJÀ net des coûts de rebalancement 21j du #349) — traité comme
  "l'actif sous-jacent" à redimensionner, exactement comme le #46
  traite le rendement log quotidien brut de l'indice.
- Coût SUPPLÉMENTAIRE (au-delà des coûts déjà inclus dans
  `pnl_sleeve_net`) pour l'ajustement quotidien du levier :
  `extra_cost(t) = |Δpos(t)| × COST_BPS/1e4` (`COST_BPS=5,0`,
  réutilisé, même convention que le #46).
- Rendement final : `r_vt(t) = pos(t) × pnl_sleeve_net(t) − extra_cost(t)`.
- Avant que la fenêtre de vol 20j soit définie (les 20 premières
  séances testables), `pos=1,0` (neutre, non testé, hors échantillon —
  même convention que #46).

## 3. Référence et critère de succès

**Identique au #349** (Règle 7, pas de nouveau critère inventé pour ce
cycle) : critère réutilisé du seul précédent dollar-neutre du repo
(PEAD) :

> **PASS niveau 1 si et seulement si, sur la période testable, net de
> tous les coûts : Sharpe annualisé > 0 ET t-stat (moyenne/écart-type
> × √n) > 2.**

**n_trials = 1** (un overlay figé, trois constantes déjà validées
ailleurs, aucun balayage).

## 4. Prédiction déclarée à l'avance (Règle 2)

**PASS anticipé, non garanti** : le t-stat du #349 (1,52) est à ~76 %
du seuil requis (2,0), et la littérature (Barroso & Santa-Clara)
documente un doublement approximatif du Sharpe par ce mécanisme sur
des portefeuilles momentum long/short comparables — si cet ordre de
grandeur se vérifie ici, le t-stat franchirait le seuil. Risque
explicitement reconnu : le sleeve du #349 n'est pas un momentum pur
(il combine 4 signaux dont 1 low-vol, dont la dynamique de "krachs"
peut différer de celle étudiée par Daniel-Moskowitz) — un doublement
exact n'est pas garanti. Résultat rapporté tel quel, sans retuning
après calcul.

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le vol-targeting réduit la variance mais aussi potentiellement le
   rendement moyen si les meilleurs rendements du sleeve coïncident
   avec ses périodes de vol élevée (contrairement au régime "krach"
   spécifique au momentum long/short pur étudié par Daniel-Moskowitz).
2. Le coût supplémentaire de rebalancement quotidien du levier
   (`extra_cost`) pourrait éroder le gain de Sharpe si le multiplicateur
   de levier est volatil séance après séance.
3. Historique testable du sleeve limité (2907 séances, 2015-2026,
   contrainte héritée du #349) — un mécanisme nécessitant plusieurs
   cycles de régime de vol pour s'exprimer pleinement pourrait manquer
   de puissance statistique sur cette fenêtre.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 6. Sortie

`scripts/nonml_dollar_neutral_composite_vol_targeted_backtest.py`,
`scripts/nonml_dollar_neutral_composite_vol_targeted_audit.py`,
`results/nonml_dollar_neutral_composite_vol_targeted_{result,audit,anti_cheat}.md`.
Si PASS : robustesse (grille ±20% sur `TARGET_VOL_ANNUAL`/`CAP`),
simulation 300€, batterie Règle 9 au cycle suivant.
