# Pré-enregistrement — Intersection Halloween × année post-électorale (PASS × FAIL), combinaison multiplicative

**Committé AVANT tout calcul.** Cycle #185 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Le #184 a combiné deux signaux CONFLICTUELS mais tous deux
individuellement PASS (Halloween lève et fonctionne seul, mid-term coupe
et fonctionne seul) — PASS malgré le conflit. Ce cycle teste le cas
inverse : combiner un signal calendaire qui FONCTIONNE seul (Halloween,
#17, PASS 4/5) avec un signal calendaire qui ÉCHOUE seul (année 1
post-électorale, #180, FAIL net 0/4) — mécanisme déjà documenté pour des
portes de régime au #61 (combiner un signal qui fonctionne avec un
signal qui échoue seul DILUE l'edge, contrairement aux #81/#98 où les
deux fonctionnaient). Question testée : ce schéma se généralise-t-il aux
paires purement calendaires ?

## 2. Règle de combinaison (figée AVANT tout calcul, identique au #184)

**Combinaison MULTIPLICATIVE**, même construction que le #184 :

```
position(t) = 1.0 × (2,0x si Halloween(t) sinon 1,0) × (0,5x si post-élection(t) sinon 1,0)
```

- Halloween SEUL : `2,0x`
- Post-élection SEUL : `0,5x`
- Les deux coïncident : `2,0 × 0,5 = 1,0x`
- Ni l'un ni l'autre : `1,0x`

Choix neutre par construction, identique au #184, pas retouché après
résultat.

## 3. Marchés testés (figés, intersection des #17/#180)

4 marchés : NDX, Russell 2000, S&P 500, DAX (Composite exclu, comme au
#180, historique insuffisant pour l'année post-électorale).

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #184)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (combinaison multiplicative de deux mécanismes déjà
évalués séparément, règle fixée avant calcul, un critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Par analogie avec le #61, le signal FAIL (post-élection) pourrait
   diluer l'edge du signal PASS (Halloween) sur la fraction de temps où
   ils coïncident, faisant échouer ce cycle malgré le succès du #184.
2. Alternativement, comme au #184, la fréquence d'occurrence bien plus
   élevée de Halloween (~50% du temps) par rapport à la post-élection
   (~25%) pourrait suffire à préserver un edge net positif malgré la
   dilution locale.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
