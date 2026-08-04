# Pré-enregistrement — Renversement à horizon 1 AN au niveau INDICE, overlay levé

**Committé AVANT tout calcul.** Cycle #183 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Horizon intermédiaire jamais testé à ce niveau d'agrégation : le #177
(FAIL) a testé le renversement à 3 ANS au niveau INDICE (De Bondt &
Thaler, tercile bas → poursuite de crise plutôt que rebond, MDD dégradé
-90,0% vs -82,9%). Le #73 (PASS) a testé le MOMENTUM 12-1 mois — mais au
niveau TITRE (stock-level, sélection cross-sectionnelle), un mécanisme
économique différent (sélection relative entre titres, pas timing de
l'indice entier). Ce cycle teste le RENVERSEMENT à 1 AN (12 mois) au
niveau INDICE — même mécanisme structurel que le #177 (tercile bas =
renversement attendu), mais horizon 4x plus court, pour voir si le
problème identifié au #177 (le tercile bas capture surtout la
POURSUITE d'une crise) est spécifique à l'horizon long ou général à
toute construction de renversement au niveau indice.

## 2. Marché testé (figé, identique au #177)

**NDX (40 ans) uniquement** — même raisonnement qu'au #177 (seul
historique suffisamment long pour ce type de signal avec suffisamment
de cycles indépendants ; Composite trop court). n_trials=1, un seul
marché.

## 3. Mécanisme (figé, réutilisation stricte Règle 7 de la structure du #177)

- Signal : `retour_1an(t) = close(t-1)/close(t-1-252) - 1` (252 séances
  ≈ 1 an de bourse, alignement causal `t-1`).
- Seuil : **percentile EXPANDING 33,33** (tercile inférieur), même
  technique que les #169/#177.
- **BURN_IN = 252 séances supplémentaires** après le premier signal
  disponible avant de commencer à trader (même convention que le #177).
- `position(t) = 2.0x` si `retour_1an(t) ≤ seuil_expanding(t)`, `1.0x`
  sinon. CAP=2.0x réutilisé tel quel. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — identique au #177)

> **PASS si et seulement si** `Sharpe(overlay) > Sharpe(Buy&Hold)`
> **ET** `rendement total(overlay) > rendement total(Buy&Hold)`, net de
> coûts 5 bps.

**n_trials = 1** (un marché, un horizon fixé avant calcul, un seuil de
tercile expanding sans paramètre libre, un critère).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme au #177, le mécanisme de renversement au niveau indice pourrait
   systématiquement capturer la poursuite de régimes baissiers/volatils
   plutôt qu'un rebond — si c'est le cas à 1 an aussi, cela confirmerait
   que le problème est général à cette construction, pas spécifique à
   l'horizon 3 ans.
2. Un horizon plus court (1 an vs 3 ans) pourrait au contraire capter un
   rebond tactique plus rapide (moins de temps pour qu'une crise se
   prolonge structurellement) — c'est l'hypothèse alternative testée
   ici, pas présumée vraie à l'avance.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
