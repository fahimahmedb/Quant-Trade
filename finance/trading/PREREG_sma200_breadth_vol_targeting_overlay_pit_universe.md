# Pré-enregistrement — Porte breadth SMA200 (#96) sous univers point-in-time réel

**Committé AVANT tout calcul.** Cycle #271 du backlog non-ML.

## Contexte et motivation

Suite au #270 (porte dispersion cross-sectionnelle, #78, BASCULE EN FAIL
sous univers point-in-time réel — premier signal de régime agrégé
vérifié sous PIT). Ce cycle teste si ce résultat se généralise à un
**second signal de régime agrégé économiquement DISTINCT** : la breadth
SMA200 (#96, PASS, plateau parfait 8/8) — fraction des titres NDX-100
au-dessus de leur propre moyenne mobile 200j, mesure de la largeur de la
TENDANCE de moyen terme titre par titre, différente de la dispersion
(amplitude des écarts de rendement quotidiens) tant dans sa construction
que dans son interprétation économique.

## Hypothèse de sens (déclarée AVANT tout calcul, Règle 2)

**Aucune prédiction directionnelle a priori**, comme au #270 — le sens
du biais d'un panneau restreint aux survivants sur une statistique de
LARGEUR DE TENDANCE n'est pas évident (les survivants 2026 pourraient
être systématiquement plus souvent au-dessus de leur SMA200, biaisant la
breadth mesurée à la hausse, mais l'effet net sur la PORTE et sur l'edge
qui en résulte n'est pas prévisible sans calcul).

## Univers et données

`data/pead/prices_pit/*.json` (178 tickers, réutilisé sans modification
depuis les cycles #264-270, aucune nouvelle donnée). Composition
historique via `ndx100_membership.tickers_as_of_date`, couverture
2015-01-01+ (comme au #270). `data/nasdaq100_daily.txt` pour l'indice
(inchangé).

## Méthode (réutilisation stricte du #96, Règle 7)

Identique au #96 : `Breadth(t) = fraction des titres RÉELLEMENT membres
du NDX-100 au jour t (au lieu des 99 membres 2026) dont le prix est
au-dessus de leur propre SMA200`, `SMA_WINDOW=200`,
`BREADTH_THRESHOLD=0.50`, mécanisme vol-targeting identique
(`VOL_WINDOW=20`, `TARGET_VOL_ANNUAL=0.20`, `CAP=2.0`, `COST_BPS=5.0`).
Application du même garde-fou anti-contamination que le #270 (masquage
explicite des dates hors couverture de composition 2015+, éviter le
piège « comparaison avec NaN renvoie False » déjà rencontré).

## Référence et critère de succès (renforcé, identique au #96 original)

Référence = Buy&Hold NDX-100 (identique au #96 original).

## Risques déclarés à l'avance

1. Comme au #270, l'échantillon PIT (2015+) pourrait différer
   sensiblement en longueur de l'original (~2021-2026) — comparabilité
   directe limitée, signalé si observé.
2. Le calcul de la breadth au niveau du panneau ENTIER (pas seulement le
   sous-ensemble éligible à une date de rebalancement) sur un univers
   dont la taille change à chaque changement de composition — même
   limite reconnue qu'au #270, non corrigée si observée.
3. Ce cycle teste UN second signal de régime après le #270 — pas le
   début d'une recherche systématique sur les 6 formes de breadth ; si
   le schéma se généralise à 2/2, ce sera rapporté comme tel sans tester
   automatiquement les 4 autres.

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_sma200_breadth_vol_targeting_overlay_pit_universe_result.md`.
Script : `scripts/nonml_sma200_breadth_vol_targeting_overlay_pit_universe_backtest.py`.
