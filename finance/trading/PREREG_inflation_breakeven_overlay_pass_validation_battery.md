# Pré-enregistrement — Batterie Règle 9 sur le #200 (anticipations d'inflation implicites)

**Committé AVANT tout calcul de la batterie.** Cycle #201 du backlog
non-ML. Applique la même discipline que les #189/#190/#194 (PREREG
dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #200 (`PREREG_inflation_breakeven_overlay.md`,
`results/nonml_inflation_breakeven_overlay_result.md`) est le PASS
niveau 1 le plus récent et le plus solide du backlog — PASS net sur les
5 marchés, robustesse 15/15 (plateau parfait), le premier PASS propre
sur l'ensemble des 5 marchés depuis le #182, et le seul de toute la
famille macro-externe défensive à ne pas échouer sur la jambe rendement.
Explicitement identifié dans le résultat du #200 comme candidat naturel
pour cette batterie. Jamais soumis à la barre renforcée. Aucune nouvelle
donnée, aucun nouveau réglage : application mécanique de l'outil déjà
figé `nonml_pass_validation_battery.py`.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec le choix déjà fait pour tous les candidats
précédents. Note : la fenêtre disponible pour ce candidat est plus
courte que le calendrier NDX complet (T10YIE ne débute qu'en 2003,
~5917 séances utiles sur les 10272 du calendrier NDX complet, cf. #200)
— signalé ici avant calcul.

## Modification technique requise (déclarée avant calcul)

`nonml_inflation_breakeven_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_inflation_breakeven_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#199)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt). Note : compte tenu de la fenêtre
   disponible (2003+), le dot-com crash (2000-2002) ne sera probablement
   pas couvert — signalé à l'avance comme limite possible.
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le plateau de robustesse parfait (15/15) et le PASS net sur les 5
   marchés sont les signes les plus favorables observés dans la famille
   macro-externe à ce jour — attente raisonnable d'un meilleur score
   Règle 9 que les candidats précédents de cette même famille (#193,
   1/5 au #194), mais aucune garantie : le DSR reste hors de portée pour
   les 200 hypothèses testées jusqu'ici sans exception.
2. La couverture de crise incomplète (dot-com probablement non couvert,
   historique 2003+) pourrait limiter le score du contrôle (b) même si
   les fenêtres couvertes (2008, COVID, 2022) passent.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_inflation_breakeven_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification via
`nonml_anti_cheat_check.py inflation_breakeven_overlay`.
