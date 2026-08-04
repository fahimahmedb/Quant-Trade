# Pré-enregistrement — Intersection Halloween × année mid-term (signaux conflictuels), combinaison multiplicative

**Committé AVANT tout calcul.** Cycle #184 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Le #182 a combiné deux calendriers qui vont dans le MÊME sens
(Halloween lève, année pré-électorale lève) — AND strict, PASS 5/5. Ce
cycle combine deux calendriers **CONFLICTUELS** : Halloween (#17, lève à
2,0x) et l'année de mid-term (#176, coupe à 0,5x) — un cas jamais
rencontré dans ce backlog où deux signaux individuellement validés
pointent dans des directions OPPOSÉES. Question testée : quel signal
domine (ou s'annulent-ils) quand ils coïncident ?

## 2. Règle de combinaison (figée AVANT tout calcul, pour éviter tout choix arbitraire de priorité)

**Combinaison MULTIPLICATIVE des deux multiplicateurs**, pas un choix de
priorité arbitraire :

```
position(t) = 1.0 × (2,0x si Halloween(t) sinon 1,0) × (0,5x si mid-term(t) sinon 1,0)
```

Ce qui donne, par construction arithmétique (aucun cas particulier codé
à la main) :
- Halloween SEUL (hors mid-term) : `2,0x`
- Mid-term SEUL (hors Halloween) : `0,5x`
- **Les deux coïncident : `2,0 × 0,5 = 1,0x`** (les deux effets
  s'annulent exactement par construction multiplicative)
- Ni l'un ni l'autre : `1,0x`

Ce choix (multiplicatif plutôt qu'un ordre de priorité type "mid-term
prime sur Halloween") est neutre par construction — il ne favorise
aucun des deux signaux a priori, et ne sera pas changé après avoir vu un
résultat.

## 3. Marchés testés (figés, intersection des #17/#176)

4 marchés : NDX, Russell 2000, S&P 500, DAX (Composite exclu, comme au
#176, historique insuffisant pour l'année de mid-term).

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #176)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (combinaison multiplicative de deux mécanismes déjà
validés séparément, règle de combinaison fixée avant calcul, aucun
paramètre nouveau, un critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Si les deux effets ne sont pas de force comparable (le #176 avait un
   edge net plus modeste que le #17), l'annulation multiplicative
   pourrait masquer un déséquilibre réel — le "1,0x" au chevauchement
   pourrait en réalité être sous-optimal dans un sens ou dans l'autre,
   ce que ce test ne peut pas distinguer par construction (déclaré à
   l'avance, pas un prétexte pour retester avec une pondération
   différente dans ce cycle).
2. Contrairement au #182 (renforcement mutuel), un signal conflictuel
   pourrait simplement ajouter du bruit/turnover sans bénéfice net.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
