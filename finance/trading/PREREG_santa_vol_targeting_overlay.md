# Pré-enregistrement — Overlay vol-targeting gaté par la fenêtre Santa Claus Rally

**Committé AVANT tout calcul.** Cycle #72 du backlog non-ML. Remplace la
porte calendaire du #54 (union ToM∪Halloween) par la fenêtre Santa Claus
Rally (#64, PASS 4/5 en overlay binaire, la fenêtre calendaire la plus
étroite testée du backlog, ~2,8% du temps) — teste si le mécanisme
hiérarchique vol-targeting se généralise aussi à une porte calendaire
TRÈS resserrée, et pas seulement aux fenêtres larges déjà testées
(ToM∪Halloween ~30-45% du temps, breadth ~27-38%, tendance ~50-75%).

## Hypothèse

Le mécanisme hiérarchique (porte + vol-targeting) a jusqu'ici toujours
été testé sur des portes actives une fraction substantielle du temps
(≥27%). La fenêtre Santa Claus Rally (#64) n'est active que ~2,8% du
temps (7 séances/an), un régime radicalement plus rare. Si le mécanisme
se généralise, moduler l'amplification par la vol réalisée UNIQUEMENT
pendant cette fenêtre étroite devrait au moins égaler le CAP fixe du
#64 (PASS 4/5) tout en préservant mieux le MDD, comme observé
systématiquement pour les autres types de porte (#47, #54, #57, #68).

## Définition (fixée ici, avant tout résultat)

- Porte = fenêtre Santa Claus Rally (identique au #64 : 5 dernières
  séances de décembre + 2 premières de janvier, `DEC_TAIL=5`,
  `JAN_HEAD=2`).
- Quand la porte est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au
  #46/#47/#54/#57/#68, aucun retuning).
- Quand la porte est inactive : position = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (tous les paramètres repris à l'identique des
cycles #46/#64 déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_santa_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py santa_vol_targeting_overlay`.
