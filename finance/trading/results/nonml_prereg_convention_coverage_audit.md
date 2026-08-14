# Audit adversarial — couverture de la convention `PREREG_` (#464)

Le backtest découpe le backlog **ligne à ligne** ; l'audit le découpe par
une **expression régulière sur le texte entier**. Deux routes distinctes.

## A. Les trois catégories, recomptées

| Grandeur | Rapport | Audit |
|---|---|---|
| entrées | 284 | 284 |
| exactement un | 171 | 171 |
| aucun | 104 | 104 |
| plusieurs | 9 | 9 |

**CONCORDANT.**

## B. Les cas « aucun fichier » — vraiment aucun ?

- cas relus : **10**
- **contredits** (un fichier porte pourtant ce nom) : **0**

**CONCORDANT.**

## C. Les orphelins réels — le nom est-il vraiment absent ?

- orphelins relus : **15**
- **contredits** (le nom apparaît dans le backlog) : **0**

**CONCORDANT.**

## D. Idempotence de mon propre rapport

Le #463 a montré qu'un cycle qui mesure les autres doit commencer par
lui-même. Ce rapport ne compte **pas** de rapports — il compte des
**entrées de backlog** — donc l'auto-inclusion du #447 ne devrait pas
l'atteindre. À vérifier plutôt qu'à supposer.

- avant : `785a3903e3139f05`
- après : `785a3903e3139f05`

**CONCORDANT.**

## Ce que cet audit ne couvre pas

- Il **ne juge pas** si la convention *devrait* être suivie : il mesure
  une couverture, il ne prononce pas d'infraction.
- Il relit les cas **publiés** par le rapport, pas ceux que le rapport
  aurait omis de produire.

## Verdict — **CONCORDANT** (4/4)

Aucun écart par recomptage indépendant.