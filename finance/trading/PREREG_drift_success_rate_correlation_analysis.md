# Pré-enregistrement — Le Sharpe Buy&Hold d'un marché prédit-il son taux de succès dans la lignée de portes/estimateurs #215-243 ?

**Committé AVANT tout calcul.** Cycle #246 du backlog non-ML. Reprend la
3e des 3 pistes proposées à la clôture du #245 (diagnostic DAX).

## Nature du cycle

**Analyse informative, PAS un nouveau backtest** — même famille que
#116/#150/#155/#245. Aucune nouvelle donnée de marché ni nouveau
mécanisme testé : agrège des résultats DÉJÀ committés pour généraliser
(ou réfuter) au-delà du seul cas DAX l'hypothèse de travail posée au
#245 (« un drift Buy&Hold plus faible rend l'amplification vol-targeting
structurellement moins rentable »).

## Question posée (déclarée à l'avance)

Sur les 5 marchés standards du backlog, le taux de succès (%
d'hypothèses PASSant les deux jambes Sharpe ET rendement) de la famille
homogène d'estimateurs/portes #215-243 (même mécanisme #46 sous-jacent,
même table de résultats à 5 marchés) corrèle-t-il avec le Sharpe
Buy&Hold annualisé de chaque marché (déjà mesuré au #245) ?

## Méthode et périmètre (déclarés avant calcul, pas de sélection après résultat)

- **Périmètre exact** : les 16 cycles de la famille #215-243 testés sur
  les 5 marchés standards avec la table de résultats homogène (`|
  Marché | ... | Sharpe>BH | Rdt>BH |`) : #215/#216/#217/#218/#219/#220/
  #221/#222/#223/#231/#233/#236/#237/#239/#240/#242. **Exclu explicitement**
  : #234 (GJR-forecast-gate, testé sur NDX seul par construction, pas
  comparable) et toute la famille calendrier/macro antérieure (#47-#206,
  univers/formats hétérogènes, hors scope de cette question qui porte
  spécifiquement sur la famille #215-243 identifiée au #244/#245).
- Pour chaque cycle, un marché est compté PASS si ses deux colonnes
  `Sharpe>BH` ET `Rdt>BH` valent `OUI` dans le fichier `results/nonml_
  <nom>_vol_targeting_overlay_result.md` déjà committé — extraction
  automatique par script (regex sur les lignes de tableau), pas de
  saisie manuelle.
- Taux de succès par marché = (nb de PASS) / 16.
- Corrélation de Spearman (rangs) entre le taux de succès et le Sharpe
  Buy&Hold annualisé déjà calculé au #245 — Spearman choisi à l'avance
  car robuste à la relation non nécessairement linéaire et à l'échantillon
  minuscule (5 points).

## Ce que ce cycle NE fait PAS (déclaré à l'avance)

- Ne recalcule AUCUN backtest existant.
- Ne teste PAS de nouvelle stratégie.
- N'ajuste PAS le mécanisme #46 pour DAX ou tout autre marché.
- Un résultat de corrélation faible ou nul serait rapporté tel quel — ce
  cycle ne cherche pas à confirmer l'hypothèse du #245, seulement à la
  tester avec plus de puissance (16 observations au lieu d'1 cas isolé).

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_drift_success_rate_correlation_analysis.py`. Pas de
vérification anti-cheat automatisée applicable (pas de backtest, même
convention que #116/#150/#155/#245).
