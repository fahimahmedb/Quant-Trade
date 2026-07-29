# Pré-enregistrement — Verrou temporel : #115 sur les 12 derniers mois (OOS pur)

**Committé AVANT tout calcul.** Cycle #122 du backlog non-ML. Applique
pour la première fois dans ce backlog la **Règle 8** de
`PROTOCOLE_ANTI_SNOOPING.md` (verrou temporel + validation prospective) :
"Réserver une tranche de données jamais vue par aucun essai (les
derniers 6-12 mois), ouverte seulement après qu'un candidat ait déjà
passé les critères sur design/test."

## Hypothèse

Le mécanisme du #115 (vol-targeting défensif, jamais de levier,
`clip(20%/vol_réalisée_20j(t-1), 0.0, 1.0x)`, critère Calmar) a été
conçu et testé sur l'historique COMPLET NDX (40 ans), qui inclut
implicitement les 12 derniers mois. Ce cycle isole EXPLICITEMENT les 12
derniers mois comme fenêtre "jamais analysée séparément" et vérifie si
la conclusion (Calmar overlay > Calmar BH) tient sur cette
sous-période récente prise isolément — SANS retoucher un seul
paramètre du mécanisme déjà figé.

## Définition (fixée ici, avant tout résultat)

- Candidat : #115 (`nonml_defensive_calmar_vol_targeting_overlay`,
  résultat déjà committé, npz déjà sauvegardé). Aucun paramètre
  modifié (TARGET_VOL_ANNUAL=20%, VOL_WINDOW=20j, CAP=1.0x, floor=0.0x).
- Fenêtre OOS pure : les 252 dernières séances de bourse (~12 mois)
  de l'artefact déjà committé (`nonml_defensive_calmar_vol_targeting_
  overlay_pnl.npz`, NDX).
- **Coûts** : 5 bps (identiques).
- **Référence** : Buy & Hold sur NDX, même fenêtre de 252 séances.

## Critère de succès (identique à #115, pas retuné)

Calmar overlay > Calmar BH sur cette fenêtre isolée. Rapporté honnêtement
que le résultat tienne ou non — un échec sur cette fenêtre ne serait PAS
retouché ni representé comme un succès sous un autre angle.

## Ce que ce cycle NE fait PAS

Ne change aucun paramètre du #115. Ne cherche pas une fenêtre différente
si celle-ci déçoit (violerait la Règle 8 : "Si le prospectif déçoit : le
modèle est abandonné, jamais retouché puis re-testé sur la même
fenêtre"). N'affecte pas le verdict Règle 9 déjà rendu sur #115 (reste
FAIL sur cette barre) — ce cycle teste une dimension différente
(stabilité temporelle sur une fenêtre OOS pure explicitement isolée,
pas encore couverte par les folds de la Règle 9c qui utilisent 4 folds
égaux, pas une fenêtre "verrouillée" dédiée).

## Anti-cheat

Ce fichier committé avant `nonml_ndx_defensive_oos_lockbox_analysis.py`,
aucune donnée nouvelle, aucun paramètre retuné.
