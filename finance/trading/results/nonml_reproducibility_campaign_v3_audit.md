# Audit — campagne v3 : le test comportemental a rattrapé ce que le motif ratait

Recalcul **indépendant** : cet audit n'importe rien du script de mesure.

## Contrôle 1 — tirage reproductible depuis la graine

**Piège rencontré et corrigé avant commit** : ce cycle produit son propre
`_result.md`, ce qui l'ajoutait au vivier (289 → 290) et décalait tout le
tirage. C'est **exactement** le défaut identifié au #434 — je l'y avais corrigé
mais **je ne l'avais pas reporté** dans ce nouveau script. Le contrôle l'a
rattrapé en échouant, ce qui est son rôle.

- vivier recompté : **289**
- échantillon redérivé identique au publié : **oui** ✔

## Contrôle 2 — aucune sentinelle laissée derrière

Le test comportemental **écrit dans le dépôt**. Le pré-enregistrement en faisait
un risque assumé, avec suppression dans un `finally` et contrôle final.

- fichiers sentinelles sur disque : **0** ✔
- traces dans `git status` : **0** ✔

**Le dépôt est propre.** Le garde-fou a tenu, y compris sur le script
divergent où le test a effectivement été déclenché.

## Contrôle 3 — le test comportemental a-t-il apporté ce que le motif ne pouvait pas ?

C'est la question du cycle. Le #437 avait exclu les auto-référents par un
**motif de code** énumérant trois écritures ; il en avait **manqué deux**.

La divergence structurelle détectée est `empty_pass_basket_extension`.

| | |
|---|---|
| capturé par le critère **syntaxique** du #437 | **NON** |
| classé par le test **comportemental** du #438 | **oui, structurelle** |

**Le test attrape exactement ce que le motif ratait.** Ce script fait partie
des deux que le #437 avait manqués — il écrit son `glob` d'une manière que
mes trois littéraux ne couvraient pas.

Le changement de méthode n'est donc pas cosmétique : sans lui, ce tirage
aurait produit une **troisième** campagne annulée par une divergence que
j'aurais dû reclasser après coup.

**Nuance sur la prédiction.** Le pré-enregistrement attendait que le test classe
`pnl_duplicate_sweep` ou `empty_pass_requalification` comme structurels. **Ni
l'un ni l'autre n'a été tiré** : la prédiction n'a pas été mise à l'épreuve sur
les cas nommés, mais sur un troisième script de la même famille. Je le signale
plutôt que de compter la prédiction comme vérifiée.

## Contrôle 4 — la borne, recalculée

| | Valeur |
|---|---|
| identiques | 23 |
| structurelles (exclues du dénominateur) | 1 |
| substantielles | 0 |
| **dénominateur** | **23** |
| **borne à 95 %** | **12.2 %** |

La règle d'exclusion des structurelles était **fixée au pré-enregistrement**,
avant tout tirage — ce n'est pas une reclassification de circonstance.

## Ce que vaut cette borne — et pourquoi elle est plus faible qu'avant

| | Borne | Statut |
|---|---|---|
| #435 | 8,0 % | **caduque** (#436) |
| #437 | — | non publiée |
| **#438** | **12.2 %** | **publiée** |

C'est la **première borne publiable de la campagne**, et elle est **moins bonne**
que celle revendiquée au #435. Normal : elle repose sur **23** tirages au lieu
de 36, parce que les trois remises à zéro ont été assumées plutôt que contournées.

Sur un vivier de **289**, elle laisse encore place à **~35** divergences substantielles non détectées.
Elle ne dit pas que le dépôt est reproductible ; elle dit qu'un problème
**massif** de péremption est écarté, et rien de plus.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| 24 tirés et classés | 24 | 24 | ✔ |
| divergents classés par le test | tous | 1 | ✔ |
| sentinelles subsistantes | 0 | 0 | ✔ |
| borne publiée si k=0 substantielle | oui | **12.2 %** | ✔ |

**La campagne aboutit à sa troisième tentative.** Le changement de méthode —
tester la propriété au lieu de deviner son écriture — était le bon, et il a
servi dès ce tirage.

Ce qui a coûté trois cycles n'est pas la mesure, c'est d'avoir voulu deux
fois reconnaître un comportement par la forme du code qui le produit.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
