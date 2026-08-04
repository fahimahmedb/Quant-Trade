# Pré-enregistrement — Batterie Règle 9 sur le #193 (corrélation cross-marché NDX-DAX)

**Committé AVANT tout calcul de la batterie.** Cycle #194 du backlog
non-ML. Applique la même discipline que les #189/#190 (PREREG dédié
avant toute exécution de la batterie, corrigeant l'écart de procédure
initialement signalé au #188).

## Contexte et motivation

Le #193 (`PREREG_cross_market_correlation_ndx_dax_overlay.md`,
`results/nonml_cross_market_correlation_ndx_dax_overlay_result.md`) est
le PASS niveau 1 le plus récent du backlog — **le premier PASS de la
famille des signaux macro-externes purement défensifs**
(#175/#178/#186/#187/#191/#192/#193) à dépasser le seuil renforcé, après
6 échecs consécutifs dans cette même famille (taux niveau/pente/
volatilité/inversion, prime de risque de variance, force relative
small-cap). Jamais soumis à la batterie renforcée. Aucune nouvelle
donnée, aucun nouveau réglage : application mécanique de l'outil déjà
figé `nonml_pass_validation_battery.py` à un résultat déjà committé.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec le choix déjà fait pour tous les candidats
précédents (#38/#134/#149/#165/#176/#179/#182/#184/#30/#185 aux
#188-190). Note : la fenêtre disponible pour ce candidat est plus courte
que le calendrier NDX complet (la corrélation NDX-DAX n'est calculable
qu'à partir du début de l'historique DAX, ~6651 séances utiles sur les
10272 du calendrier NDX complet, cf. #193) — signalé ici avant calcul,
pas après avoir vu un résultat favorable ou défavorable.

## Modification technique requise (déclarée avant calcul)

`nonml_cross_market_correlation_ndx_dax_overlay_backtest.py` sera
étendu pour sauvegarder
`results/nonml_cross_market_correlation_ndx_dax_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#190)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt). Note : compte tenu de la fenêtre
   disponible plus courte (~6651 séances, débutant après le début de
   l'historique DAX), certaines fenêtres de crise anciennes (dot-com,
   partiellement 2008) pourraient ne pas être couvertes — signalé à
   l'avance comme limite possible, pas comme excuse post-hoc.
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le #193 a déjà une robustesse imparfaite (27/45, pas un plateau
   parfait, fenêtre 48j fragile) — attente raisonnable que son score
   Règle 9 reflète cette fragilité relative, par analogie avec le
   #185 (robustesse non parfaite → score Règle 9 le plus faible testé).
2. Le DSR est hors de portée pour les 194 hypothèses testées jusqu'ici
   sans aucune exception — aucune raison structurelle d'attendre que le
   #193 y échappe.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_cross_market_correlation_ndx_dax_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
cross_market_correlation_ndx_dax_overlay`.
