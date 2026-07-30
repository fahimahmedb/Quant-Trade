# Pré-enregistrement — Ajouter le #149 comme 4e variante du script Étape D v3

**Committé AVANT tout calcul.** Cycle #152 du backlog non-ML.
**Formalisation d'infrastructure (PAS un nouveau candidat indépendant,
pas de nouvelle batterie Règle 9)** — le mécanisme du #149 a déjà été
validé (PASS niveau 1, 4/5 Règle 9, meilleur résultat brut du backlog)
dans `finance/trading/`. Ce cycle l'ajoute à
`scripts/run_etape_d_v3_bond_diversification.py` (créé au #144) comme
4e variante, aux côtés du #134.

## Objet

Étendre `run_etape_d_v3_bond_diversification.py` avec une 4e variante
"VolTarget-Défensif15+Diversification" (mécanisme du #149 :
`TARGET_VOL_ANNUAL=15%` au lieu de 20%, même proxy DGS10) pour
permettre une comparaison DIRECTE des deux meilleures constructions
défensives dans le même rapport officiel Étape D — sans retoucher les
3 variantes déjà présentes (BuyHold, VolTarget-Défensif 20%, +
Diversification 20%).

## Définition (fixée ici, aucun nouveau paramètre)

- Univers étendu à 4 variantes (N=4 pour le DSR, mise à jour de N=3 à
  N=4 — l'ajout d'une variante RECONNUE change mécaniquement N, pas un
  contournement) : BuyHold, VolTarget-Défensif(20%), VolTarget-
  Défensif(20%)+Diversification (#134), VolTarget-Défensif(15%)+
  Diversification (#149, nouvelle variante ajoutée ici).
- Jeux de données : Composite (5 ans) et NDX (40 ans), identiques au
  #144.
- Coûts : 5 bps aller-retour (identique).
- Aucun retuning : reproduit EXACTEMENT les paramètres déjà validés du
  #149 (`TARGET_VOL_ANNUAL=15%`, `VOL_WINDOW=20j`, `CAP=1.0`).

## Ce que ce cycle NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu sur le #134 ou le #149. Le
critère de succès rapporté reste celui, déjà existant, de l'Étape D
(MDD -25%/rendement ≥80%), pas la Règle 9 du backlog non-ML.

## Anti-cheat

Ce fichier committé avant la modification de
`run_etape_d_v3_bond_diversification.py`. Aucune nouvelle donnée,
aucun nouveau paramètre.
