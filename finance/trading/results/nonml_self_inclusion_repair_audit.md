# Audit adversarial — réparation de l'auto-inclusion (#468)

Un cycle de **réparation** se juge autrement qu'un cycle de mesure : le
risque n'est pas de mal compter, c'est d'avoir **changé le comportement
au-delà de ce qu'on annonçait**.

## A. La correction est-elle **minimale** ?

Le régime déclarait : **une expression par script**, des commentaires,
**aucun import**, aucune autre ligne.

| Script | Lignes + | Lignes − | Import ajouté ? | Instructions modifiées |
|---|---|---|---|---|
| `verdict_rule_propagation` | 6 | 1 | **non** | 1 |
| `six_reports_regeneration` | 6 | 1 | **non** | 2 |

**CONCORDANT** — aucun import ajouté, la correction tient en peu de lignes.

## B. Le correctif ne change-t-il **que** l'auto-inclusion ?

C'est le contrôle central. Si les deux versions différaient ailleurs que
sur des lignes où le script **se nomme lui-même**, la réparation aurait
changé autre chose que ce qu'elle annonçait.

| Script | Lignes de diff | Mentionnant son propre nom | Autres |
|---|---|---|---|
| `verdict_rule_propagation` | 5 en 3 blocs | 3 blocs liés | **0** |
| `six_reports_regeneration` | 30 en 3 blocs | 3 blocs liés | **0** |

**CONCORDANT** — le correctif ne touche que ce qu'il annonçait.

## C. Les rapports tiers sont-ils intacts ?

Le cycle promet de restaurer les **7** rapports que
`six_reports_regeneration` réécrit. On le vérifie **contre `HEAD`**,
octet pour octet.

- fichiers modifiés hors des 4 autorisés : **0**

**CONCORDANT.**

## D. Idempotence de mon propre rapport

- avant : `83c36b38427f2a1f`
- après : `83c36b38427f2a1f`

**CONCORDANT**

## Ce que cet audit ne couvre pas

- Il ne vérifie pas que les **autres** scripts du dépôt sont indemnes
  d'auto-inclusion : le #467 a clos la piste de la détection statique,
  et seule l'exécution tranche — **296 scripts** restent non éprouvés.
- Il ne rejoue les scripts que **deux** fois dans le contrôle B ; c'est
  le backtest qui en fait trois.

## Verdict — **CONCORDANT** (4/4)

La réparation fait ce qu'elle annonce, et rien de plus.