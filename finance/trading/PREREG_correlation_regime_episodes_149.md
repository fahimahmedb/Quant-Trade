# Pré-enregistrement — comportement de #149 pendant les épisodes de corrélation actions/obligations élevée

**Committé AVANT tout calcul de performance.** Suite directe du monitoring
Voie A (`scripts/monitoring_correlation_kill_switches_149.py`) qui a détecté
un kill-switch corrélation actif (48j, dans la norme historique). Décision
utilisateur : analyser les épisodes historiques avant de choisir une
politique opérationnelle pour l'épisode courant.

## Définition des épisodes (fixée ici, calculée AVANT de regarder la performance)

Algorithme déterministe déjà appliqué (identique à
`monitoring_correlation_kill_switches_149.py`) : corrélation glissante 60j
entre rendements NDX et rendements du proxy obligataire DGS10 > 0,30,
maintenue en continu plus de 20 séances. 21 épisodes identifiés sur
1985-2026 (10184 séances), listés ci-dessous par ordre chronologique
(dates de début/fin FIXÉES, aucune sélection après coup) :

1985-12-30→1986-06-05, 1986-09-11→1986-12-08, 1986-12-16→1987-01-30,
1987-04-08→1987-08-12, 1987-08-31→1987-10-16, 1988-02-23→1988-04-12,
1988-04-14→1989-08-03, 1990-05-01→1991-01-04, 1991-02-14→1991-05-02,
1991-06-05→1991-07-15, 1993-07-01→1993-08-23, 1994-02-23→1994-07-18,
1994-08-11→1994-12-06, 1996-08-01→1996-11-08, 1997-08-22→1997-10-15,
1999-08-11→1999-11-22, 2021-03-03→2021-07-16, 2022-10-04→2022-11-03,
2022-11-10→2023-01-23, 2023-11-02→2023-12-26, 2026-05-04→2026-07-13
(épisode courant, en cours à la fin de l'historique disponible).

## Question posée (fixée ici)

Pendant CES fenêtres précises, #149 (overlay complet, tel que committé dans
`results/nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz`)
reste-t-il défensif (Sharpe ≥ BH, MDD pas pire que BH, comme le contrôle b
de la Règle 9 déjà appliqué aux 4 fenêtres de crise standard) ou devient-il
contre-productif (Sharpe < BH ou MDD pire que BH) quand sa propre hypothèse
de diversification est mécaniquement invalidée par la corrélation positive ?

## Métriques et critère (fixés ici)

Pour chaque épisode couvert par les données de #149 (démarrent après le
split design/test implicite du npz) : Sharpe annualisé, rendement total net
(`cumprod(1+r)-1`, convention du backlog), MDD — overlay vs BH, sur la
fenêtre exacte de l'épisode uniquement. Agrégat : nombre d'épisodes où
l'overlay MDD est pire que BH (devrait être proche de 0 si le mécanisme
"portage" protège même quand le "timing corrélation" échoue), et Sharpe
médian overlay vs BH sur l'ensemble des épisodes.

## Ce que cette analyse NE fait PAS

Ne change aucun verdict Règle 9 déjà rendu (SPA/DSR restent en échec à
n_trials=125). N'ajoute pas de nouveau paramètre au mécanisme #149. Sert
uniquement à décider la politique opérationnelle pendant un épisode de
kill-switch actif (§5 du document de déploiement).

## Anti-cheat

Ce fichier committé avant `nonml_correlation_regime_episodes_149.py`. La
liste d'épisodes ci-dessus est calculée par un algorithme déterministe déjà
exécuté et publié dans le commit précédent (monitoring), pas choisie à la
main après avoir vu la performance.
