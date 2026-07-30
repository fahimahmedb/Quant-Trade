# Pré-enregistrement — Ajouter S&P 500 et Russell 2000 au script Étape D v3

**Committé AVANT tout calcul.** Cycle #160 du backlog non-ML.
**Formalisation d'infrastructure (PAS un nouveau candidat indépendant,
pas de nouvelle batterie Règle 9)** — les généralisations cross-marché
du #134 (#136) et du #149 (#151) sont déjà validées dans le backlog
non-ML. Ce cycle les ajoute au script officiel
`run_etape_d_v3_bond_diversification.py` (créé au #144, étendu au #152),
en complétant la liste `DATASETS` déjà générique.

## Objet

Étendre `DATASETS` avec S&P 500 et Russell 2000 (mécanisme déjà
générique, aucune modification de `vol_target_position`/
`bond_return_proxy` nécessaire), pour que le rapport officiel Étape D
couvre les 4 marchés déjà validés dans le backlog non-ML (Composite,
NDX, S&P 500, Russell 2000).

## Définition (fixée ici, aucun nouveau paramètre)

- `DATASETS` étendu à 4 jeux de données : Composite (5 ans), NDX
  (40 ans), S&P 500, Russell 2000.
- Mêmes 4 variantes déjà en place (BuyHold, VolTarget-Défensif20,
  +Diversification20, +Diversification15).
- Aucun retuning : reproduit EXACTEMENT les paramètres déjà validés.

## Ce que ce cycle NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu. Le critère de succès
rapporté reste celui, déjà existant, de l'Étape D (MDD -25%/rendement
≥80%).

## Anti-cheat

Ce fichier committé avant la modification de
`run_etape_d_v3_bond_diversification.py`. Aucune nouvelle donnée,
aucun nouveau paramètre.
