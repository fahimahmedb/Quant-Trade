# Pré-enregistrement — Overlay levé "expiration d'options mensuelle" (monthly opex)

**Committé AVANT tout calcul.** Cycle #277 du backlog non-ML.

## Hypothèse

L'expiration mensuelle des options sur indice/actions (3e vendredi de
CHAQUE mois, pas seulement les 4 vendredis trimestriels de "triple
witching" déjà testés au #26) est documentée séparément dans la
littérature de microstructure comme un événement à volume et volatilité
anormalement élevés ("pinning" des prix vers les strikes à fort intérêt
ouvert, activité de rééquilibrage de couverture des market-makers) —
un effet mensuel simple, sans rollover de futures ni rééquilibrage
indiciel trimestriel massif, donc potentiellement d'une nature
différente (plus pur, moins pollué par d'autres flux institutionnels
concomitants) du triple witching déjà FAIL (#26, 1/5).

## Définition (fixée ici, AVANT tout calcul — réutilisation directe de
la détection data-driven du #26, Règle 7)

Fenêtre = le 3e vendredi de bourse de CHAQUE mois calendaire (tous les
12 mois, pas de filtre `WITCHING_MONTHS`) + la séance suivante (2
séances/mois). Détection par rang de vendredi dans le mois
(`fri_rank == 3`), identique à `witching_mask()` du #26, sans la
restriction `.isin({3,6,9,12})`.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée nécessaire.

## Stratégies comparées

- **Monthly-opex overlay** : position 1,0x en permanence, CAP=2,0x
  (réutilisé du #26, Règle 7) le jour d'expiration mensuelle + le
  suivant. Coût 5 bps par transaction.
- **Référence** : Buy & Hold classique.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés**. n_trials=1 (aucune
grille sur la largeur de fenêtre ou le CAP à ce stade — réutilisation
stricte du #26).

## Risque déclaré à l'avance

Fenêtre active nettement plus large (~24 séances/an contre 8/an pour le
#26) — le levier est actif plus souvent, ce qui dilue potentiellement
l'effet de concentration du #26 déjà FAIL plutôt que de le renforcer ;
résultat rapporté tel quel, sans retuning si FAIL.

## Anti-cheat

Ce fichier committé avant `nonml_monthly_opex_overlay_backtest.py`.
Vérification prévue : recalcul indépendant du masque (vendredis civils
filtrés par les séances réellement tradées, même méthode que l'audit du
#26). Sortie : `results/nonml_monthly_opex_overlay_result.md`.
