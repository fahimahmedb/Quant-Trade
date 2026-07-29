# Pré-enregistrement — Overlay vol-targeting gaté par le January Barometer

**Committé AVANT tout calcul.** Cycle #80 du backlog non-ML. Remplace le
CAP fixe du #59 (January Barometer, PASS 5/5) par le mécanisme
hiérarchique vol-targeting déjà validé sur 6 autres types de porte
(tendance #47/#68, calendrier #54/#72, breadth #57/#77, dispersion
#78) — première porte de décision ANNUELLE (pas récurrente intra-mois)
combinée à ce mécanisme.

## Hypothèse

Le #59 a montré qu'un CAP fixe de 2,0x pendant févier-décembre, activé
si janvier a été positif, bat Buy&Hold (PASS 5/5). Moduler l'amplitude
du levier par la volatilité réalisée plutôt que d'utiliser un CAP fixe
pourrait, comme pour les autres types de porte déjà testés, mieux
préserver le MDD tout en conservant ou améliorant le couple
Sharpe/rendement.

## Définition (fixée ici, avant tout résultat)

- Porte annuelle = identique au #59 : rendement de janvier(Y)
  (déc(Y-1)→jan(Y)) positif → porte active de février à décembre de
  l'année Y. Janvier reste toujours à 1,0x (comme au #59, pas de pari
  sur janvier lui-même).
- Quand la porte est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au
  #46/#47/#57/#77/#78, aucun retuning).
- Quand la porte est inactive (ou en janvier) : position = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (tous les paramètres repris à l'identique des
cycles #46/#47/#59 déjà validés, aucune grille testée avant ce
résultat). Même prudence méthodologique que le #59 sur le faible nombre
d'observations annuelles pour le Composite et les marchés à historique
court.

## Anti-cheat

Ce fichier committé avant
`nonml_january_barometer_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py january_barometer_vol_targeting_overlay`.
