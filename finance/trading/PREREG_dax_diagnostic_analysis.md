# Pré-enregistrement — Diagnostic structurel : pourquoi DAX est-il systématiquement le marché le plus difficile ?

**Committé AVANT tout calcul.** Cycle #245 du backlog non-ML. Reprend la
1ère des 3 pistes proposées à la clôture du #244 (synthèse v4).

## Nature du cycle

**Analyse diagnostique/informative, PAS un backtest** — même famille que
les cycles #116 (analyse de sensibilité DSR), #150 (analyse
complémentaire), #155 (analyse informative). Aucun critère PASS/FAIL
numérique de trading : ce cycle ne teste aucune nouvelle stratégie, il
documente pourquoi DAX est en échec sur la majorité des portes testées
#216-242 (synthèse v4, section F) — un constat jusqu'ici purement
descriptif, sans explication causale.

## Question posée (déclarée à l'avance)

DAX diffère-t-il structurellement des 4 autres marchés (Composite, NDX,
Russell 2000, S&P 500) sur des propriétés statistiques DÉJÀ mesurées à
l'Étape A (`diagnostics.py`), d'une façon qui expliquerait pourquoi les
portes "calme=amplifier" (moments statistiques, clustering, vol-de-la-
vol) y échouent plus souvent qu'ailleurs ?

## Méthode (déclarée avant calcul, aucune sélection après résultat)

Calcul des diagnostics suivants, DÉJÀ implémentés à l'Étape A, sur les 5
marchés (comparaison, pas de nouveau paramètre) :
1. `summary_stats` (Sharpe buy&hold, vol annualisée, skew, kurtosis).
2. `lo_mackinlay_vr` (ratio de variance q=5, comme #217).
3. `ljung_box` sur les rendements au carré, lag=22 (comme #242).
4. `engle_arch_lm` (effet ARCH, nlags=10).
5. `fit_student_t` (ν non conditionnel, pleine période).
Tous calculés sur l'échantillon COMPLET de chaque marché (pas de fenêtre
glissante — diagnostic statique, pas un signal tradable). Comparaison
DAX vs les 4 autres marchés sur ces 5 diagnostics, sans hiérarchie
déclarée à l'avance entre eux (aucun n'est présupposé "the" explication).

## Ce que ce cycle NE fait PAS (déclaré à l'avance)

- Ne modifie AUCUN script de backtest existant.
- Ne relance AUCUNE des 12+ portes déjà testées sur DAX.
- Ne propose PAS de "correction" de DAX (retrait, pondération) — un
  résultat honnête peut très bien être "aucune explication structurelle
  claire trouvée, la différence est peut-être due au hasard sur un
  échantillon de 5 marchés".

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_dax_diagnostic_analysis.py`. Pas de vérification
anti-cheat automatisée applicable (pas de backtest de trading, même
convention que #116/#150/#155).
