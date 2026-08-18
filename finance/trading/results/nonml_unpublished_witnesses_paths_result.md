# Les **témoins non publiés** : que faudrait-il ? (pré-enregistré)

Quatre cycles consécutifs — **#487, #489, #490, #491** — ont dû écrire la
même phrase : *« le témoin est dans le code, pas encore dans le
rapport »*. **Personne n'avait établi ce qu'il faudrait.**

## La population, dérivée par code

Un script est **porteur d'un témoin non publié** si son code contient un
des préfixes ci-dessous **et** que la chaîne est **absente** de son
rapport publié. Préfixes **figés par le pré-enregistrement** :

```
- rapports ayant **perdu** l'encart du #439
- PASS qui sont des **stratégies**
- rapports classés « indéterminé » par la règle unifiée
- incohérences prose/compte exposées par le rafraîchissement
```

- scripts **porteurs d'un témoin non publié** : **4**

## Les quatre mesures, script par script

| Script | Exécute un script tiers | Cibles d'écriture | Touche l'arbre git | Classe |
|---|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | **1** | `OUT` | **0** | **C** |
| `nonml_net_pnl_correction_backtest.py` | **0** | `OUT` | **0** | **A** |
| `nonml_six_reports_regeneration_backtest.py` | **1** | `OUT` | **0** | **C** |
| `nonml_sweep_pass_prose_fix_backtest.py` | **0** | `OUT` | **0** | **A** |

| Classe | Nombre |
|---|---|
| **A** — Exécutable sans danger | **2** |
| **B** — Exécutable avec effets à annuler | **0** |
| **C** — Non exécutable en l'état | **2** |

## Ce qu'il faudrait, pour chacun

### `nonml_battery_coverage_backtest.py` — classe **C**

Témoin absent de `nonml_battery_coverage_result.md` : « - rapports classés « indéterminé » par la règle unifiée… »

Il **exécute 1 script(s) tiers** du dépôt. Le relancer
déclencherait une **cascade** : ces scripts réécrivent à leur tour
leurs propres rapports, et certains en écrivent d'autres.

> **Il n'existe pas de geste borné qui publie ce témoin.** Le
> publier exigerait d'accepter une régénération en chaîne dont le
> périmètre n'est pas connu d'avance — exactement ce que le #450
> avait subi, et le #482 refusé.

### `nonml_net_pnl_correction_backtest.py` — classe **A**

Témoin absent de `nonml_net_pnl_correction_result.md` : « - incohérences prose/compte exposées par le rafraîchissement… »

**Il suffirait de l'exécuter**, puis de vérifier que le diff de son
rapport se réduit au témoin avant de le committer — la règle que le
**#489** avait déjà fixée, et qui l'a fait renoncer parce que le
diff était dominé par la dérive du dépôt.

> **Le blocage n'est donc pas technique, il est de méthode** : tant
> que le dépôt bouge entre deux exécutions, le diff ne se réduira
> jamais au seul témoin. **Il faudrait accepter de committer un
> rapport dont d'autres chiffres ont changé** — décision qui
> dépasse ce cycle.

### `nonml_six_reports_regeneration_backtest.py` — classe **C**

Témoin absent de `nonml_six_reports_regeneration_result.md` : « - rapports ayant **perdu** l'encart du #439… »

Il **exécute 1 script(s) tiers** du dépôt. Le relancer
déclencherait une **cascade** : ces scripts réécrivent à leur tour
leurs propres rapports, et certains en écrivent d'autres.

> **Il n'existe pas de geste borné qui publie ce témoin.** Le
> publier exigerait d'accepter une régénération en chaîne dont le
> périmètre n'est pas connu d'avance — exactement ce que le #450
> avait subi, et le #482 refusé.

### `nonml_sweep_pass_prose_fix_backtest.py` — classe **A**

Témoin absent de `nonml_sweep_pass_prose_fix_result.md` : « - PASS qui sont des **stratégies**… »

**Il suffirait de l'exécuter**, puis de vérifier que le diff de son
rapport se réduit au témoin avant de le committer — la règle que le
**#489** avait déjà fixée, et qui l'a fait renoncer parce que le
diff était dominé par la dérive du dépôt.

> **Le blocage n'est donc pas technique, il est de méthode** : tant
> que le dépôt bouge entre deux exécutions, le diff ne se réduira
> jamais au seul témoin. **Il faudrait accepter de committer un
> rapport dont d'autres chiffres ont changé** — décision qui
> dépasse ce cycle.

## Ce que les cycles précédents avaient invoqué

Le **#487** avait refusé d'exécuter deux scripts. **Ses motifs sont
confrontés à la mesure :**

| Script | Motif invoqué au #487 | Mesure d'ici |
|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` | exécute d'autres scripts du dépôt | exécute **1**, écrit **1** cible(s) (`OUT`) — **confirmé** |
| `nonml_sweep_pass_prose_fix_backtest.py` | écrit 2 fichiers, dont un qui n'est pas le sien | exécute **0**, écrit **1** cible(s) (`OUT`) — **FAUX** |

> **1 motif invoqué est faux.** `sweep_pass_prose_fix` appelle bien `write_text` **deux fois**,
> mais **les deux visent `OUT`** — son propre rapport. Les autres
> chemins qu'il manipule (`REL`, `SWEEP_REL`) ne servent qu'à
> `git show` et `git diff`, **en lecture seule**.

**Le #487 a compté des appels, pas des cibles.** Il a donc refusé
d'exécuter un script **de classe A**, sans danger — et quatre cycles
ont répété ce refus sans le vérifier.

> C'est **le troisième motif de cette série que la lecture du code
> contredit**, après ceux du #488 et du #493. Les trois fois, le
> verdict tenait ou non, **mais la raison écrite était fausse.**

## Existe-t-il une voie détournée ?

**Non, et il faut le dire explicitement.** Un rapport de ce dépôt est
**une sortie de programme**. Y écrire le témoin à la main le rendrait
indiscernable d'un rapport produit — et **c'est précisément le défaut**
que les #479 à #493 ont passé quinze cycles à dénombrer.

> **Publier un témoin en éditant le rapport serait fabriquer exactement
> ce que cette série reproche.** L'option est exclue, et le
> pré-enregistrement l'excluait d'avance.

## Ce qui n'est pas mesurable ici

**L'idempotence** de ces rapports — au sens du #463 — exigerait de les
exécuter **deux fois**. Ce cycle n'exécute rien : la question est
**déclarée hors de portée**, et non tranchée par supposition.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| la population compte 4 scripts | 4 | 4 | **vérifiée** |
| au moins 2 classes distinctes | ≥ 2 | 2 | **vérifiée** |
| aucune voie détournée honnête | 0 | 0 | **vérifiée** |

> **La prédiction 3 n'est pas une mesure.** Elle énonce qu'éditer un
> rapport à la main est exclu — ce qui relève d'une **règle**, pas d'un
> fait observé. Je la marque vérifiée parce qu'aucune voie n'a été
> trouvée, **mais elle ne pouvait pas être réfutée par la mesure**, et
> c'est une faiblesse de ma formulation.

## Aucune exécution, aucun rapport modifié

- fichiers modifiés hors ceux de ce cycle : **0**

**Aucun script du dépôt n'a été exécuté.**

## Critères de succès

1. Population dérivée par code (**4**), préfixes verbatim — **OUI**.
2. Les quatre mesures publiées par script — **OUI**.
3. Chacun rangé et « ce qu'il faudrait » énoncé — **OUI** (**2** classes).
4. Aucune exécution, aucun rapport modifié — **OUI**.
5. Idempotence déclarée hors de portée — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).