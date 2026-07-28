# Pré-enregistrement — Winners momentum court terme + overlay levé proximité plus haut 52-semaines (indice)

**Committé AVANT tout calcul.** Cycle #42 du backlog non-ML. Le
portefeuille Winners (#14) affiche un Sharpe extrême (+2,35 à +3,75
selon variante) mais a été explicitement flaggé **prudence forte** :
probablement propre au marché haussier concentré IA/semiconducteurs
2021-2026, pas forcément généralisable. Un essai précédent de
combinaison (#18, Winners + overlay ToM) avait déjà **échoué** à
améliorer le résultat. Ce cycle teste si le MEILLEUR signal de tendance
du backlog (#37, proximité du plus haut 52-semaines indice, PASS
exceptionnel au #38 avec Leaders) réussit là où le calendrier (#18) a
échoué.

## Hypothèse

Le filtre de tendance 52w-high (#37) coupe l'exposition en régime
baissier de l'indice — appliqué au portefeuille Winners (dont le risque
principal est justement une inversion brutale de tendance en fin de
bull market), il pourrait réduire le risque du #14 sans détruire son
edge, contrairement à l'overlay calendaire (#18, FAIL).

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Winners momentum court terme, IDENTIQUE au
  cycle #14 (signal = rendement 5j, tercile supérieur, rebalancement
  hebdomadaire, univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) dont
  la clôture est **≥ 95%** de son plus haut glissant sur 252 séances
  (paramètres identiques au #37/#38/#39), appliqué comme régime GLOBAL
  au portefeuille (alignement causal par ffill, même méthode que
  #33/#38/#39).
- Overlay = position de base **× CAP=2.0x** durant les jours où le
  signal est actif, position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Winners 1.0x (cycle #14), PAS Buy&Hold —
  même convention que #11/#18/#23/#33/#38/#39.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Winners de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x, fenêtre 252j et seuil 95% cohérents
avec #37/#38/#39, aucune grille testée avant ce résultat). **Prudence
maintenue** : même en cas de PASS, le résultat hérite de la même mise en
garde que le #14 (généralisabilité incertaine hors du bull market
2021-2026 échantillonné).

## Anti-cheat

Ce fichier committé avant
`nonml_winners_index52w_high_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py winners_index52w_high_overlay`.
