# Audit — reproductibilité, lot 3 : une divergence, et elle est de mon fait

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## La divergence

Sur 24 tirages : **23 identiques**, **1 divergent** — `pnl_duplicate_sweep`, **8** lignes.

Le pré-enregistrement du #435 comme celui du #436 prévoyaient ce cas :

> « Si une divergence apparaît, la borne ne s'applique plus : le résultat
> principal du cycle devient la divergence elle-même. »

**La borne n'est donc pas publiée.** Ni celle de ~4,9 % qui était visée, ni une
borne recalculée sur 59 tirages « hors le cas gênant ».

## La cause — un chiffre que j'ai moi-même rendu instable au #428

Les lignes divergentes portent toutes sur le même décompte :

```
- | scripts de backtest non-ML du dépôt | **284** |
+ | scripts de backtest non-ML du dépôt | **289** |
- | **couverture non-ML** | **73.2 %** |
+ | **couverture non-ML** | **72.0 %** |
```

Le dépôt comptait **284** scripts de backtest au #428 ; il en compte **289**
aujourd'hui. Les cinq de plus sont **les miens** — ceux des cycles #431 à #436,
dont ce cycle lui-même.

**C'est le #428 qui a introduit ce chiffre dans le rapport du balayage.** J'y
avais ajouté la couverture non-ML précisément pour que le lecteur ne surestime
pas la portée du balayage. L'intention était bonne ; la conséquence ne l'est
pas : un rapport qui embarque un décompte du **dépôt** cesse d'être stable dès
que le dépôt bouge, c'est-à-dire à chaque cycle qui ajoute un script.

Ce rapport était donc **divergent par construction** depuis le #428, et aucun
des cycles suivants ne l'avait vu — y compris les deux lots de reproductibilité,
qui ne l'avaient simplement pas tiré.

## Combien d'autres rapports sont dans ce cas

Scripts dont le rapport embarque un décompte du dépôt (et non de ses seules
entrées) : **7**

- `capitulation_gate_floor_sweep`
- `pnl_duplicate_sweep`
- `protocol_inventory`
- `reproducibility_sample`
- `reproducibility_sample_lot2`
- `reproducibility_sample_lot3`
- `sameday_timestamp_resolution`

Tous sont des **diagnostics**, pas des stratégies — ce qui limite la portée du
problème : aucun verdict PASS/FAIL n'en dépend. Mais tous partagent la même
fragilité, et **je les ai presque tous écrits**.

## Ce que je refuse de faire ici

Il serait tentant de distinguer deux espèces de divergence :

- **structurelle** — le rapport embarque un compteur du dépôt, il bougera
  toujours ; ce n'est pas un résultat périmé ;
- **substantielle** — un résultat publié ne se reproduit plus, ce que la
  campagne cherchait.

La distinction est **juste**. Mais l'appliquer **maintenant**, pour écarter le
seul cas gênant et republier une borne de 4,9 %, serait exactement le geste que
tout ce protocole interdit : changer la règle après avoir vu le résultat.

> La distinction sera donc **pré-enregistrée dans un cycle ultérieur**, avec son
> critère mécanique fixé avant tout nouveau tirage — et la campagne repartira de
> là, sans réutiliser les 60 tirages actuels comme s'ils avaient été classés
> selon une règle qui n'existait pas quand ils ont été faits.

**État publié de la borne : caduque.** Le #434 (22,1 %) et le #435 (8,0 %)
restent vrais pour ce qu'ils mesuraient, mais la campagne ne peut pas prétendre
à 4,9 % en écartant après coup le tirage qui la contredit.

## Volet B — représentativité en âge : contrôle passé

Ce volet est **indépendant de la divergence** et son verdict tient.

- date de publication médiane — vivier : **2026-08-04**, testés : **2026-08-01**
- écart sur le tiers le plus ancien : **-3.2 points**, tolérance **±10** fixée avant mesure

**Tirage représentatif en âge.** Les rapports anciens — les plus exposés à la
dérive du code partagé — sont couverts à la même fréquence que les récents. Le
seuil n'a pas été ajusté après coup ; il n'a pas eu besoin de l'être.

Ce contrôle valait la peine d'être fait **avant** de connaître son résultat :
s'il avait échoué, il aurait invalidé la lecture des deux lots précédents.

## Régime — aucun rapport publié modifié

- rapports `*_result.md` modifiés hors artefacts de ce cycle : **0** ✔

Le rapport divergent `pnl_duplicate_sweep` a été **restauré à l'identique**. Le corriger
demanderait son propre pré-enregistrement et son propre régime déclaré, comme
aux #428, #429 et #430.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| 24 scripts tirés et classés | 24 | 24 | ✔ |
| divergence publiée avec son `diff` | si présente | **oui** | ✔ |
| rapports publiés modifiés | 0 | 0 | ✔ |
| borne cumulée | ~4,9 % | **non publiée — caduque** | — |
| représentativité en âge | publiée | **passée (−3,2 pts)** | ✔ |

**La campagne de reproductibilité a trouvé ce qu'elle cherchait, à sa troisième
tentative — et le défaut est de mon fait.** C'est le meilleur résultat que ces
trois cycles pouvaient produire : une borne rassurante de plus n'aurait rien
appris ; une divergence, si.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
