# Les **sections qui ne paraissent que sous condition** (pré-enregistré)

Le **#475** a montré qu'une section entière — **titre compris** — pouvait
être sous garde (`if perdus:`), et que **trois cycles** (#469, #472,
#475) y avaient usé leur budget. Ce cycle mesure si le motif est courant.

## Ce que ce chiffre est, et ce qu'il n'est pas

**Il mesure une prévalence, pas une culpabilité.** Une section
conditionnelle est souvent le bon choix : « Les défauts trouvés » suivie
d'un `if not fautifs: "Aucun."` **paraît toujours** — c'est son *contenu*
qui varie, pas son existence.

Le cas du #475 est plus étroit : **le titre lui-même est sous garde**, la
section **disparaît entièrement**, et deux exécutions produisent des
rapports dont on ne peut plus aligner les sections. **Ma règle ne
distingue pas une garde qui peut être fausse d'une garde toujours vraie**
— d'où l'examen à la main de cinq scripts.

## La population

- rapports de `results/` : **1074**
- avec script producteur sous la convention : **766**
- **hors convention** *(comptés à part, jamais fautifs — #464)* : **308**
- **scripts producteurs distincts** analysés : **766**

La règle, par **arbre syntaxique** — un titre est conditionnel s'il a au
moins un `If`/`For`/`While`/`Try` englobant :

```python
GARDES = (ast.If, ast.For, ast.While, ast.Try)
ECRIVENT = ("append", "write", "print", "write_text")
```

## La prévalence

- titres de section écrits, tous scripts confondus : **989**
- dont **sous au moins une garde** : **58** (**5,9 %**)
- scripts portant **au moins un** titre conditionnel : **31 / 766** (**4,0 %**)
- **médiane** par script affecté : **2,0**
- maximum sur un seul script : **3**

## L'examen individuel — les **5** plus chargés

Échantillon **fixé avant de regarder** : les 5 scripts portant le plus de
titres conditionnels, ex æquo par ordre alphabétique.

### `nonml_prereg_convention_coverage_backtest.py` — **3** titres conditionnels

```python
l.174  ### Les seuls cas sans aucun fichier
        gardé par : if (l.151) → if (l.173)
l.182  ### Ceux dont le rapport existe autrement *(extrait de 10)*
        gardé par : if (l.151) → if (l.181)
l.193  ## Entrées citant plusieurs `PREREG_`
        gardé par : if (l.192)
```

**Verdict : **la section PEUT DISPARAÎTRE** *(forme #475)***

Gardes : `if not sans_rapport:`, `if aucun_fichier:`, `if autre_nom:`, `if plusieurs:`. **Toutes peuvent être fausses** — au #474 la population `aucun_fichier` valait 10, elle pourrait valoir 0 demain et la sous-section s'effacerait. **Atténuation, et elle est réelle** : les effectifs (`10`, `104`, `9`…) sont publiés **sans garde** dans le tableau qui précède. Un lecteur voit donc *pourquoi* une section manque.

### `nonml_repo_magnitudes_recount_backtest.py` — **3** titres conditionnels

```python
l.192  ### Le seul recomptage qui mord — et il confirme le #457
        gardé par : if (l.191)
l.220  ### Les « écarts » — et pourquoi aucun n'en est un
        gardé par : if (l.219)
l.248  ### Les concordances *(publiées aussi — critère 2)*
        gardé par : if (l.247)
```

**Verdict : **la section PEUT DISPARAÎTRE** *(forme #475)***

Gardes : `if discordants:`, `if concordants:`, et surtout `if 456 in par_num and 457 in par_num and (ap - av) == 29:` — **une garde sur des valeurs de données**, pas sur une liste. Si un jour l'écart ne vaut plus exactement 29, la section « le seul recomptage qui mord » **disparaît sans que rien ne la remplace**. C'est la forme la plus proche du #475 de tout l'échantillon.

### `nonml_reproducibility_campaign_v2_backtest.py` — **3** titres conditionnels

```python
l.145  ### Divergents
        gardé par : if (l.144)
l.166  ### Non concluants
        gardé par : if (l.165)
l.174  ### Identiques
        gardé par : if (l.173)
```

**Verdict : **la section PEUT DISPARAÎTRE** *(forme #475)***

Gardes : `if divergent:`, `if inconclusive:`, `if identical:` — les trois issues d'un même partitionnement. **Au moins une est vide dans presque toute exécution**, donc au moins une section manque toujours. Atténuation : les trois effectifs sont publiés **sans garde** juste au-dessus.

### `nonml_reproducibility_sample_backtest.py` — **3** titres conditionnels

```python
l.127  ### Identiques
        gardé par : if (l.126)
l.136  ### Divergents — le rapport publié ne correspond plus à son code
        gardé par : if (l.135)
l.148  ### Non concluants
        gardé par : if (l.147)
```

**Verdict : **la section PEUT DISPARAÎTRE** *(forme #475)***

Même motif à trois branches. Vérifié ligne à ligne : `| rapports **divergents** | **{len(divergent)}** |` est écrit **hors de toute garde** avant les sections. **La disparition est donc signalée**, ce qui est exactement ce qui manquait au #475.

### `nonml_reproducibility_sample_lot2_backtest.py` — **3** titres conditionnels

```python
l.117  ### Divergents — le rapport publié ne correspond plus à son code
        gardé par : if (l.116)
l.139  ### Non concluants
        gardé par : if (l.138)
l.148  ### Identiques
        gardé par : if (l.147)
```

**Verdict : **la section PEUT DISPARAÎTRE** *(forme #475)***

Même motif que le précédent, même atténuation. Sa présence ici tient à l'ex æquo alphabétique, pas à une charge supérieure : **quatre des cinq scripts de l'échantillon portent trois titres conditionnels**, et l'ordre alphabétique a tranché.

- **sections pouvant disparaître entièrement** : **5 / 5**

> **Ce `5` ne se généralise pas aux 31 scripts
> affectés.** L'échantillon a été choisi pour sa **charge maximale**,
> c'est-à-dire là où le motif avait le plus de chances de se voir. **Un
> taux mesuré sur les cas les plus chargés ne s'extrapole pas au reste.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 40 scripts avec un titre conditionnel | ≥ 40 | 31 | **réfutée** |
| médiane ≤ 2 par script affecté | ≤ 2 | 2,0 | **vérifiée** |
| ≥ 3 des 5 peuvent disparaître | ≥ 3 | 5 | **vérifiée** |

**La prédiction 1 est réfutée** : j'annonçais ≥ 40 scripts
affectés, il y en a **31** sur **766**, soit
**4,0 %**. Le motif est donc **moins répandu** que je ne le
pensais — la plupart des rapports de ce dépôt écrivent leurs sections
de bout en bout et font varier le **contenu**, pas la **structure**.

**La prédiction 3 est vérifiée : les cinq gardes peuvent être
fausses.** Mais l'examen a trouvé ce que ma règle ne pouvait pas
voir, et c'est le vrai résultat du cycle.

> **Dans quatre cas sur cinq, l'effectif est publié *sans garde* juste
> avant la section gardée.** Le lecteur voit « divergents : **0** »,
> puis pas de section « Divergents » — et comprend pourquoi. **La
> disparition est signalée.**

C'est précisément ce qui manquait au **#475** : là, la section
`if perdus:` portait **l'unique** mention de son sujet. Rien, dans le
rapport, ne disait qu'une section aurait pu exister — d'où trois
cycles dépensés à chercher un encart « perdu » qui n'avait jamais été
écrit.

**La ligne de partage n'est donc pas « section conditionnelle ou
non », mais « la garde a-t-elle un témoin inconditionnel ».** Ma règle
ne mesure pas cela, et je ne peux pas l'extrapoler aux 31 scripts
affectés : **seuls les cinq lus le sont**.

Le cas le plus proche du #475 dans l'échantillon est
`repo_magnitudes_recount`, dont une garde porte sur des **valeurs de
données** (`(ap - av) == 29`) et non sur une liste : si l'écart change,
la section s'efface **sans qu'aucun compte ne le signale**.

## Critères de succès

1. Population énumérée, hors convention comptés à part — **OUI**.
2. **766/766** scripts producteurs classés — **OUI**.
3. **5** scripts examinés individuellement — **OUI**.
4. Aucun total présenté comme un compte de fautes — **OUI**, dit à
   l'endroit du chiffre et non en note.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).