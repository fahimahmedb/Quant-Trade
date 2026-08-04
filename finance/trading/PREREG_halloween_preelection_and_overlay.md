# Pré-enregistrement — Intersection Halloween ET année pré-électorale, overlay levé

**Committé AVANT tout calcul.** Cycle #182 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Le #21 a déjà testé l'UNION de deux calendriers (ToM∪Halloween, PASS
4/5). Ce cycle teste l'INTERSECTION (AND) de deux calendriers de
fréquences complètement différentes — Halloween (cycle ANNUEL, nov-avril,
#17 PASS 4/5) ET l'année pré-électorale (cycle de 4 ANS, #30 PASS 5/5) —
jamais testé pour une paire purement calendaire dans ce backlog. Motivé
par le schéma déjà confirmé aux #81/#98 : combiner deux portes qui
fonctionnent CHACUNE séparément en AND préserve généralement l'edge
malgré la fenêtre plus restrictive (contrairement au #61 où l'une des
deux portes était un FAIL seul).

## 2. Marchés testés (figés, intersection des #17/#30)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — les deux
composantes ont chacune été testées sur les 5 marchés.

## 3. Mécanisme (figé, réutilisation stricte Règle 7)

- Halloween : `is_winter = (mois ≥ 11) OU (mois ≤ 4)`, formule copiée à
  l'identique du #17 (pas de fonction séparée à importer dans le script
  d'origine, logique reproduite ligne pour ligne).
- Pré-électorale : `preelection_mask` du #30 (`(année+1)%4==0`), importée
  directement.
- `position(t) = 2.0x` si `is_winter(t) ET preelection(t)` (les deux
  conditions simultanément), `1.0x` sinon. CAP=2.0x réutilisé tel quel
  (valeur commune aux #17/#30). Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #17/#30)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (combinaison AND de deux mécanismes déjà validés
séparément, aucun paramètre nouveau, un critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La fenêtre AND est nécessairement plus restrictive (~6/12 mois ×
   1/4 ans ≈ 12,5 % du temps attendu, contre ~50 % pour Halloween seul
   et ~25 % pour l'année pré-électorale seule) — moins de séances
   actives peut réduire la puissance statistique du signal et le rendre
   plus sensible aux coûts de transaction ou à un petit nombre
   d'observations chanceuses/malchanceuses.
2. Contrairement aux #81/#98 (deux portes de RÉGIME sur le même
   mécanisme sous-jacent), ici les deux calendriers n'ont aucune
   justification économique de RENFORCEMENT mutuel a priori — le succès
   du #81/#98 pourrait ne pas se généraliser à des portes de nature
   complètement différente (saisonnière vs électorale).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
