# Pré-enregistrement — Renversement à LONG terme au niveau INDICE (De Bondt & Thaler 1985), overlay levé

**Committé AVANT tout calcul.** Cycle #177 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

De Bondt & Thaler (1985, *Does the Stock Market Overreact?*) documentent
un effet de renversement à LONG terme (horizon 3-5 ans) : les titres/
indices ayant le PLUS sous-performé sur une longue fenêtre passée ont
tendance à SURPERFORMER sur la fenêtre suivante (surréaction corrigée).
**Distinct** du renversement COURT terme au niveau TITRE déjà testé
(#5, horizon 1 semaine, FAIL catastrophique -83,6%) et de tous les
signaux de momentum/tendance déjà couverts (#4/#37/#73/#82, horizons
1 mois à 1 an) — jamais testé à l'horizon LONG (années) ni au niveau
INDICE (agrégé) dans ce backlog.

## 2. Marché testé (figé)

**NDX (40 ans) uniquement** — seul marché avec un historique
suffisamment long (10273 séances) pour un horizon de 3 ans avec assez de
cycles indépendants. Le Composite (5 ans) est structurellement trop
court (moins de 2 fenêtres de 3 ans). Russell 2000/S&P 500/DAX seraient
éligibles en historique mais ne sont PAS testés ici (n_trials=1, un seul
marché, cohérent avec la façon dont le #165 a d'abord été testé sur NDX
seul avant généralisation) — une extension multi-marché serait un cycle
séparé, proposé après ce résultat si informatif.

## 3. Mécanisme (figé, aucun paramètre libre après ce document)

- Signal : `retour_3ans(t) = close(t-1)/close(t-1-756) - 1` (756 séances
  ≈ 3 ans de bourse, alignement causal `t-1` — décision à la clôture de
  la veille). LOOKBACK=756 fixé par la définition originale de De Bondt
  & Thaler (horizon 3 ans), pas ajusté après résultat.
- Seuil : **percentile EXPANDING 33,33** (tercile inférieur, même
  technique que le #169 — zéro paramètre de fenêtre supplémentaire à
  choisir) calculé sur tout l'historique de `retour_3ans` déjà connu au
  jour de la décision.
- **BURN_IN = 252 séances supplémentaires** après le premier signal
  disponible (à `t=756`) avant de commencer à trader, pour que
  l'estimation du tercile ne soit pas basée sur une poignée de points
  (même convention que le #169).
- `position(t) = 2.0x` si `retour_3ans(t) ≤ seuil_expanding(t)` (indice
  dans son tercile de performance 3 ans la plus faible — renversement
  attendu), `1.0x` sinon. CAP=2.0x réutilisé tel quel. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé)

> **PASS si et seulement si** `Sharpe(overlay) > Sharpe(Buy&Hold)`
> **ET** `rendement total(overlay) > rendement total(Buy&Hold)`, net de
> coûts 5 bps, sur le seul marché testé (NDX).

**n_trials = 1** (un marché, un horizon fixé par la littérature d'origine,
un seuil de tercile expanding sans paramètre libre, un critère).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'effet De Bondt & Thaler est documenté au niveau TITRE INDIVIDUEL
   (portefeuilles diversifiés de losers/winners) — au niveau INDICE
   AGRÉGÉ (déjà diversifié par construction), le mécanisme économique
   (surréaction spécifique à une entreprise, corrigée par une meilleure
   information) pourrait ne pas s'appliquer de la même façon.
2. Sur seulement 40 ans de données, il y a au plus ~13 fenêtres de 3 ans
   non chevauchantes indépendantes — puissance statistique limitée,
   risque qu'un seul épisode (ex. rebond post-2000-2002, post-2008,
   post-COVID) domine tout le résultat.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
