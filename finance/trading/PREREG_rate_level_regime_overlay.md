# Pré-enregistrement — Régime de NIVEAU des taux courts (DGS3MO), overlay coupé/levé

**Committé AVANT tout calcul.** Cycle #175 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Anomalie "don't fight the Fed" : les actions performent structurellement
mieux en régime de BAISSE des taux courts (politique monétaire
accommodante) qu'en régime de HAUSSE (resserrement). Distinct de tous
les cycles DGS3MO déjà testés dans ce backlog, qui exploitaient soit la
PENTE de la courbe (taux courts vs taux longs, #44/#134/#149…) soit le
NIVEAU comme terme de portage (Règle 10, décompositions #142/#166) —
**jamais comme signal de régime DIRECTIONNEL sur le niveau lui-même**.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX). DGS3MO est un
proxy de coût de financement USD à portée globale (canal de financement
en dollars) — extension aux marchés non-américains testée comme au #30
(cycle électoral), avec la même prudence de non-indépendance implicite
(un seul cycle de taux Fed affecte simultanément tous les marchés testés
via la politique monétaire globale).

## 3. Mécanisme (figé, alignement causal explicite)

- Signal : `direction(t) = signe(taux(t-1) − taux(t-1−N))`, avec
  **N = 63 séances** (≈1 trimestre, fenêtre standard de ce backlog pour
  les signaux macro, ni trop bruitée à court terme ni trop lente pour
  capter un changement de régime). `taux(t-1)` = dernière valeur DGS3MO
  connue à la clôture du jour `t-1` (alignement causal `ffill` +
  `shift(1)`, même convention que la Règle 10 des #142/#166).
- `position(t) = 0.5x` si `direction(t) > 0` (taux en hausse sur les 63
  dernières séances), `2.0x` si `direction(t) < 0` (taux en baisse),
  `1.0x` si strictement égal (rare, cas de repli neutre). **FLOOR=0.5x**
  est une valeur NOUVELLE dans ce backlog (aucun cycle antérieur n'avait
  de plancher sous 1.0x autre que 0) — choisie symétriquement à
  CAP=2.0x autour de la position neutre 1.0x (0.5x = 1/2.0x), pas
  ajustée après résultat.
- Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que tous les cycles multi-marché)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une fenêtre N=63j fixée avant calcul par cohérence avec
les conventions macro du backlog, un plancher/plafond symétrique, un
critère multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le signal de niveau de taux peut être dominé par de longues
   tendances séculaires (ex. désinflation 1981-2020) plutôt que par des
   cycles de resserrement/assouplissement pertinents pour l'horizon de
   chaque marché testé — risque de sur-représentation d'une seule
   tendance longue plutôt que de plusieurs cycles indépendants.
2. Réduire l'exposition à 0.5x en régime de hausse pourrait coûter plus
   en manque à gagner (les actions montent souvent MALGRÉ des hausses de
   taux graduelles, ex. 2004-2006, 2015-2018) que ce que le régime de
   baisse ne rapporte en sur-exposition.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
