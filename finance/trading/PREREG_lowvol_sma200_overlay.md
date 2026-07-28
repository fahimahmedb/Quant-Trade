# Pré-enregistrement — Low-Volatility Tilt + overlay levé filtre de tendance SMA200

**Committé AVANT tout calcul.** Cycle #35 du backlog non-ML. Teste si le
filtre de tendance SMA200 (#29, meilleur PASS solo, et #33, meilleure
combinaison avec Leaders) aide aussi le portefeuille défensif low-vol
(#15) — question directement motivée par le contraste #28 (overlay
CALENDAIRE sur low-vol, FAIL, Sharpe dégradé) vs #33 (overlay TENDANCE
sur momentum, PASS très net) : le signal de tendance réussit-il là où le
signal calendaire a échoué ?

## Hypothèse

Contrairement à l'overlay calendaire (#28, qui ajoute du levier à des
moments fixes indépendamment du régime de marché), le filtre de tendance
SMA200 est justement conçu pour ÉVITER le levier en régime baissier —
il pourrait donc préserver l'avantage de MDD du portefeuille low-vol
tout en améliorant son rendement, là où le calendrier a échoué.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Low-Volatility Tilt, IDENTIQUE au cycle #15
  (tercile inférieur de volatilité réalisée 60j, rebalancement 21j,
  univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 au-dessus de sa SMA200 (identique
  au #29/#33), appliqué comme régime GLOBAL au portefeuille (alignement
  causal par ffill, même méthode qu'au #33).
- Overlay = position de base **× CAP=2.0x** durant les jours où l'indice
  NDX-100 est au-dessus de sa SMA200, position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold —
  même convention que #11/#23/#28/#33.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Low-Vol de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_lowvol_sma200_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py lowvol_sma200_overlay`.
