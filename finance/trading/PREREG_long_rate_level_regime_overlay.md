# Pré-enregistrement — Régime de NIVEAU du taux LONG (DGS10), overlay coupé/levé

**Committé AVANT tout calcul.** Cycle #186 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Même structure exacte que le #175 (DGS3MO, FAIL net, mécanisme
contre-productif : le plancher 0,5x sous-pondérait les phases de
croissance où les taux courts montent, et le plafond 2,0x amplifiait les
pertes dans les phases de baisse de taux liées à une crise déjà en
cours). Ce cycle teste **le même mécanisme structurel** mais sur le taux
LONG (DGS10) plutôt que le taux COURT (DGS3MO) — un signal
économiquement DIFFÉRENT : le taux long reflète surtout les anticipations
de croissance/inflation à long terme, pas directement la politique
monétaire à court terme de la Fed. Question testée : le problème
identifié au #175 est-il spécifique au taux court, ou se reproduit-il
avec le taux long ?

## 2. Marchés testés (figés, identiques au #175)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 3. Mécanisme (figé, réutilisation stricte Règle 7 de la structure du #175)

- Signal : `direction(t) = signe(DGS10(t-1) - DGS10(t-1-63))`, alignement
  causal `ffill+shift(1)` identique au #175, fenêtre N=63j identique.
- `position(t) = 0,5x` si `direction(t) > 0` (taux long en hausse),
  `2,0x` si en baisse, `1,0x` si égal. CUT=0,5x et CAP=2,0x réutilisés
  tels quels (mêmes valeurs que le #175, aucun nouveau paramètre). Coûts
  5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #175)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (même structure que le #175, série de taux différente,
aucun paramètre nouveau, un critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le taux long pourrait souffrir du même problème structurel que le
   taux court au #175 (les phases de hausse de taux longs coïncident
   aussi souvent avec la croissance économique et les marchés haussiers ;
   les phases de baisse avec des paniques de type "flight to quality" —
   exactement le mécanisme contre-productif déjà identifié).
2. Alternativement, comme le taux long réagit davantage aux anticipations
   d'inflation/croissance qu'à la politique monétaire de court terme, le
   signal pourrait se comporter différemment — hypothèse testée, pas
   présumée.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
