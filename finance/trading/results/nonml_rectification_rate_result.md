# Le **taux de rectification** : combien de cycles ont été corrigés ?

Le **#509** a clos la série des emprunts sur ce constat : *treize
détecteurs successifs et leurs limites*. Le dépôt affirme régulièrement
qu'un cycle en rectifie un autre — **le taux n'avait jamais été mesuré**.

## La règle, citée verbatim

> Un cycle `#NNN` est **rectifié** si une section **postérieure**
> contient `#NNN` avec, dans **±200 caractères** *(la fenêtre du
> #502, reprise sans modification)*, au moins un marqueur :
>
> ```
> réfut   rétract   corrig   invalid   fauss   faux   erron   sur-affirm   surestim   sur-estim   dissou   tombe
> ```
>
> **Auto-rectification exclue** : seul un successeur compte.

## Ce que cette mesure **ne** mesure **pas**

Elle compte **la fréquence à laquelle une rectification est écrite**,
pas celle à laquelle une erreur est commise.

> **Un dépôt qui n'avouerait jamais rien obtiendrait un taux de zéro.**
> Un taux élevé peut signaler beaucoup d'erreurs **ou** beaucoup de
> franchise, et **cette mesure ne les distingue pas**. Toute lecture qui
> l'oublierait serait fausse, y compris la mienne.

## Le recensement

- sections de backlog : **308**
- cycles **rectifiés** par au moins un successeur : **183**
- **taux global** : **59,4 %**
- taux sur les **30 derniers** : **96,7 %**
- délai médian avant première rectification : **1** cycles

## La tendance, par tranches

| Tranche | Cycles | Rectifiés | Part |
|---|---|---|---|
| #101–#210 | **38** | **17** | **44,7 %** |
| #211–#254 | **38** | **17** | **44,7 %** |
| #255–#292 | **38** | **27** | **71,1 %** |
| #293–#350 | **38** | **10** | **26,3 %** |
| #351–#393 | **38** | **12** | **31,6 %** |
| #394–#431 | **38** | **29** | **76,3 %** |
| #432–#469 | **38** | **32** | **84,2 %** |
| #470–#511 | **42** | **39** | **92,9 %** |

- de la première à la dernière tranche, le taux **monte** (**44,7 %** → **92,9 %**)

> **Le taux monte.** Les cycles récents se rectifient les uns les
> autres plus souvent que les anciens. **Cela ne dit pas qu'ils se
> trompent davantage** — seulement qu'ils l'écrivent davantage.

## La fragilité du détecteur, mesurée

Certains marqueurs sont des **mots courants** de ce registre. Une
fenêtre de ±200 caractères peut donc en attraper un qui appartient
à la **phrase voisine**. Deux mesures pour que le lecteur en juge :

| Marqueur | Déclenchements |
|---|---|
| `faux` | **741** |
| `corrig` | **459** |
| `rétract` | **329** |
| `fauss` | **119** |
| `réfut` | **113** |
| `tombe` | **61** |
| `invalid` | **34** |
| `surestim` | **30** |
| `dissou` | **22** |
| `erron` | **17** |
| `sur-affirm` | **14** |

- appariements où le marqueur est dans la **même phrase** que la
  référence : **583** sur **1389** (**42,0 %**)
- appariements où il n'est **que dans la fenêtre** : **806**

- cycles rectifiés **sous la règle stricte de la phrase** : **137** — taux **44,5 %**

> **La majorité des appariements ne tiennent qu'à la fenêtre.** Le
> taux de **59,4 %** annoncé plus haut est donc une **borne
> supérieure** ; la lecture stricte donne **44,5 %**.
> **La règle figée reste celle du pré-enregistrement** — je ne la
> remplace pas après coup — mais publier le seul chiffre large
> serait le présenter comme plus solide qu'il n'est.

## Les cycles les plus rectifiés

| Cycle | Rectifié par | Successeurs |
|---|---|---|
| `#453` | **53** | `#454`, `#455`, `#456`, `#457`, `#461`, `#462`, … (**47** autres) |
| `#460` | **48** | `#461`, `#462`, `#466`, `#467`, `#468`, `#469`, … (**42** autres) |
| `#465` | **46** | `#466`, `#467`, `#468`, `#469`, `#470`, `#471`, … (**40** autres) |
| `#459` | **40** | `#460`, `#461`, `#474`, `#475`, `#476`, `#477`, … (**34** autres) |
| `#471` | **40** | `#472`, `#473`, `#474`, `#475`, `#476`, `#477`, … (**34** autres) |
| `#474` | **32** | `#475`, `#477`, `#479`, `#480`, `#482`, `#483`, … (**26** autres) |
| `#469` | **26** | `#470`, `#472`, `#473`, `#474`, `#475`, `#476`, … (**20** autres) |
| `#485` | **26** | `#486`, `#487`, `#488`, `#489`, `#490`, `#491`, … (**20** autres) |
| `#487` | **24** | `#488`, `#489`, `#490`, `#491`, `#492`, `#493`, … (**18** autres) |
| `#483` | **23** | `#484`, `#485`, `#486`, `#487`, `#488`, `#489`, … (**17** autres) |

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| taux global ≤ 20 % | ≤ 20 % | 59,4 % | **réfutée** |
| taux des 30 derniers > taux global | > 59,4 % | 96,7 % | **vérifiée** |
| ≥ 10 cycles rectifiés | ≥ 10 | 183 | **vérifiée** |

## Auto-exclusion

**Ce cycle ne se compte pas** : sa propre section n'existera qu'après la
mesure. L'exclusion est **structurelle**, et elle était déclarée au
pré-enregistrement (règle du #447).

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Le découpage du registre est **importé** du backtest du #501.

## Critères de succès

1. Liste de **12** marqueurs et fenêtre citées verbatim — **OUI**.
2. Population (**308**), rectifiés (**183**) et taux publiés — **OUI**.
3. Taux par tranche publié (**8**) et tendance nommée — **OUI**.
4. Cycles les plus rectifiés nommés (**10**), délai médian (**1**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état du registre à la
> date de son exécution.
