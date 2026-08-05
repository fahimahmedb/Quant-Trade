# Pré-enregistrement — Correction du bug d'exécution « même barre » sur les overlays SMA200 restants (#35, #74, #83)

**Committé AVANT toute exécution/calcul.** Cycle #257 du backlog non-ML.

## Contexte et motivation

Le balayage d'intégrité #252-255 (documenté dans
`results/nonml_synthese_backlog_consolidee_v5.md`, section D) avait couvert
les scripts stock-selection partageant le motif
`weights_X[t:end] = w` puis `pnl = weights_X[start:] * R[start:]` — mais
seulement pour les 8 scripts trouvés via un grep restreint aux motifs
`weights_leaders[...]` / `weights_lowvol[...]`. Un grep plus large
(`weights_[a-z_]+\[t:end\] = w` sur `scripts/*_backtest.py`) exécuté au
début de ce cycle révèle 29 scripts au total partageant ce motif.

Vérification par lecture directe de code de chacun (déclarée avant tout
calcul) :

- 7 étaient déjà corrigés (`def main(causal=...)` présent) :
  `nonml_january_effect_lowprice_overlay_backtest.py`,
  `nonml_low_vol_tilt_backtest.py`,
  `nonml_lowvol_index52w_high_overlay_backtest.py`,
  `nonml_momentum_52w_high_backtest.py`,
  `nonml_momentum_consistency_backtest.py`,
  `nonml_winners_index52w_high_overlay_backtest.py`,
  `nonml_winners_trend_vol_targeting_overlay_backtest.py`.
- 8 étaient déjà corrigés lors du balayage #252-255 (#14/#38/#33/#41/#48/#11/#23/#53).
- 12 sont des candidats déjà **FAIL** dans le backlog (#5, #16, #18, #20,
  #28, #45, #75, #79, #84, #85, #88, et #73 lui-même qui est PASS mais
  **déjà vérifié non affecté le 01/08/2026** — son signal SKIP=21j exclut
  explicitement close(t)). Ces candidats FAIL ne sont pas ré-exécutés
  (priorité basse, cohérent avec le traitement déjà appliqué à #75/#79/#84
  dans le backlog).
- **3 candidats sont PASS et n'ont JAMAIS été vérifiés pour ce bug** :
  - **#35** `nonml_lowvol_sma200_overlay_backtest.py` (Low-Vol #15 + overlay
    SMA200 #29) — PASS, Sharpe +0,54→+0,79.
  - **#74** `nonml_momentum12_1_sma200_overlay_backtest.py` (Momentum 12-1
    #73 + overlay SMA200 #29) — PASS, Sharpe +0,67→+0,92. Le signal
    momentum lui-même (#73) est déjà vérifié non affecté ; c'est le
    **filtre de tendance SMA200** qui est concerné, pas la sélection de
    titres.
  - **#83** `nonml_momentum_consistency_sma200_overlay_backtest.py`
    (Momentum de constance #82 + overlay SMA200 #29) — PASS, Sharpe
    +0,67→+0,90.

Lecture directe du code confirme que les trois scripts partagent
**exactement** la même construction que #33 (déjà corrigé, a survécu) :
`index_trend_series()` calcule `close > sma` où `sma[i]` inclut `close[i]`
(rolling mean incluant la barre courante) — un signal de tendance décidé à
la clôture du jour t, appliqué via `exposure[t]` à `weights_lev[t]`, lequel
est multiplié par `R[t]` (le rendement DÉJÀ réalisé pendant le jour t). Fuite
« même barre » d'un jour, identique à l'audit original
(`results/nonml_same_bar_execution_audit.md`) et au patch #166/#167/#253/
#254/#255.

## Hypothèse

Les trois overlays SMA200 restants (#35, #74, #83) perdent une partie de
leur edge une fois la fuite corrigée, par analogie avec #33 (a survécu,
marge réduite) mais aussi #11/#53 (ont basculé en FAIL) — **aucune
prédiction ex ante sur le sens du résultat**, cohérent avec la leçon du
balayage précédent (« aucun facteur simple ne prédit le résultat »).

## Méthode

Application stricte du patch déjà établi (`lag_one_day`, `causal=True` par
défaut, `causal=False` conservé pour la non-régression) à chacun des 3
scripts : décalage d'un jour de `weights_base` ET `weights_lev` juste après
leur construction, aucune autre modification. Vérification de
non-régression via `causal=False` reproduisant bit-identiquement les
chiffres actuellement committés, puis exécution en `causal=True` (défaut)
pour le chiffre corrigé.

## Critère de succès (inchangé, réutilisation du critère renforcé déjà en
vigueur pour #35/#74/#83)

Le PASS survit si, après correction : Sharpe overlay > Sharpe référence
1.0x ET rendement overlay > rendement référence 1.0x, sur le même
portefeuille de référence causal-cohérent.

## Risques déclarés à l'avance

- Le nombre exact de candidats qui basculent est inconnu avant calcul (0 à 3).
- Le numérateur « PASS niveau 1 » du backlog sera décrémenté d'exactement
  1 par candidat qui bascule en FAIL, jamais pour une simple
  re-vérification.
- Ce cycle clôt (sauf découverte contraire) le balayage élargi initié par
  le grep générique ci-dessus — les 29 scripts identifiés sont tous
  comptabilisés dans ce document.

## Anti-cheat

Ce fichier committé et poussé avant toute exécution des scripts modifiés.
Sorties attendues : `results/nonml_lowvol_sma200_overlay_result.md`,
`results/nonml_momentum12_1_sma200_overlay_result.md`,
`results/nonml_momentum_consistency_sma200_overlay_result.md` (mise à jour
en place), plus mise à jour du backlog (cycle #257).
