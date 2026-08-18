# Les **sans témoin non examinés** du #481 (pré-enregistré)

Le **#481** avait classé **14** titres de section *sans témoin*, n'en
avait lu que **5**, et avait écrit lui-même que son **2/5 ne
s'extrapolait pas**. **Ce cycle lit les restants** et rend le compte
**complet** — un dénombrement, plus un taux d'échantillon.

## La population, re-dérivée

| | #481 | Ici | Écart |
|---|---|---|---|
| sans témoin | 14 | **15** | **+1** |
| déjà examinés au #481 | 5 | **5** | — |
| **restants, examinés ici** | — | **10** | — |

**La règle du #481 est reprise sans modification**, y compris son défaut
connu : elle ne reconnaît pas l'exhaustivité d'un `if/else`. Le total de
**15** reste donc un **majorant**, et les branches d'alternative
sont **comptées à part** ci-dessous plutôt que corrigées.

## Les verdicts, un par un

**Écrits à la main après lecture du code autour de chaque garde.** Ordre
et règle binaire fixés dans le pré-enregistrement.

### `nonml_hardcoded_tables_repair_backtest.py` l.215 — anodin

Garde : `if zero:` — section : *## Ce que l'idempotence ne prouve pas*

**C'est mon propre cycle #482**, entré dans la population depuis le #481. Le témoin existe **sous un autre nom** : le tableau publié sans garde juste au-dessus porte une colonne « Lignes de diff » où **0** apparaît pour le script concerné. Un lecteur voyant ce zéro sait pourquoi la section existe. **Troisième occurrence du même angle mort — et je viens de le commettre moi-même, dans le cycle qui l'a nommé deux fois.**

### `nonml_net_pnl_correction_robustness.py` l.86 — anodin *(branche d'`if/else`)*

Garde : `if tous:` — section : *## La conclusion ne tient pas partout*

**Branche `else` de `if tous:`** — le pendant exact du cas l.76 déjà lu au #481. Les deux issues écrivent une section (« Plateau, pas pic » ou « La conclusion ne tient pas partout ») : **une section paraît toujours**.

### `nonml_prereg_convention_coverage_backtest.py` l.174 — anodin

Garde : `if aucun_fichier:` — section : *### Les seuls cas sans aucun fichier*

Le **bloc parent** publie, quatre lignes plus haut, `| **aucun** fichier ne porte ce <nom> | **{len(aucun_fichier)}** |`. Le compte est donc visible chaque fois que le bloc englobant s'exécute. **Ma règle ne cherchait le témoin qu'au niveau *non gardé*** — elle ignore un témoin situé dans un bloc parent.

### `nonml_prereg_convention_coverage_backtest.py` l.182 — anodin

Garde : `if autre_nom:` — section : *### Ceux dont le rapport existe autrement *(extrait de 10)**

Identique au précédent : `| le rapport **existe sous un autre nom** | **{len(autre_nom)}** |` est publié dans le bloc parent. Même angle mort de ma règle, même script, deux lignes.

### `nonml_self_inclusion_detector_backtest.py` l.106 — anodin

Garde : `if rates:` — section : *### Pourquoi il l'a manqué — diagnostic, sans toucher à la r*

Le témoin existe **sous un autre nom** : le tableau de calibration publie sans garde `| **rappel** (fautifs signalés) | 2 / 2 | **{len(rappel)} / 2** |`. Or `rates` est le **complément** de `rappel` — un lecteur voyant « 2 / 2 » sait qu'aucun cas n'a été manqué. **Ma règle cherche la variable de la garde, pas la grandeur qu'elle décrit.**

### `nonml_silent_skip_decision_backtest.py` l.119 — anodin *(branche d'`if/else`)*

Garde : `if not a_modifier:` — section : *### **Décision : on ne touche à rien.***

**Branche `if not a_modifier:` d'une alternative** dont l'`else` écrit « Décision : rendre l'écart visible dans N script(s) ». **Une décision est toujours publiée** ; seule laquelle varie.

### `nonml_six_reports_regeneration_backtest.py` l.232 — **MASQUANT**

Garde : `if perdus:` — section : *## Un effet de bord découvert — les marqueurs du #439 sont e*

**Le cas du #475 lui-même.** `perdus` n'apparaît nulle part hors de sa garde. La section porte l'unique mention de l'effet de bord découvert, et son effacement a envoyé **trois cycles** (#469, #472, #475) chercher un encart qui n'avait jamais été écrit. **Contrôle positif : une règle qui ne le classerait pas masquant serait à jeter.**

### `nonml_sweep_pass_prose_fix_backtest.py` l.134 — **MASQUANT**

Garde : `if strategies:` — section : *## Le résultat qui prime sur la correction de prose*

`if strategies:` n'a **pas d'`else`**, et aucun compte de `strategies` n'est publié hors garde. Si aucun PASS n'était une stratégie, le lecteur **n'apprendrait jamais que le contrôle a eu lieu** — alors que la section annonce précisément *« le résultat qui prime sur la correction de prose »*. **Deuxième masquant établi de ce cycle.**

### `nonml_verdict_detector_complete_robustness.py` l.124 — anodin *(branche d'`if/else`)*

Garde : `if plateau:` — section : *### La question qu'il faut poser franchement*

**Branche `else` de `if plateau:`.** L'issue `if` écrit « **Plateau** : le résultat tient sur tout le voisinage » ; l'`else` écrit « Ce n'est pas un plateau, c'est un escalier ». **L'état est toujours énoncé**, seule sa valeur change. *(Ma règle a attribué la garde au `if` alors que le titre est dans l'`else` — l'attribution est grossière, mais sans conséquence ici.)*

### `nonml_verdict_detector_fix_backtest.py` l.248 — anodin *(branche d'`if/else`)*

Garde : `if idem:` — section : *### Ce n'est pas un défaut de la correction — c'est structur*

**Branche `else` de `if idem:`**, et le témoin existe en plus **sous un autre nom** : le tableau de verdict publie sans garde `| 4 | comptes idempotents | ✔ / **NON** |`, calculé depuis `ok4 = idem`. **Deux raisons indépendantes** de ne pas le compter masquant.

## Le compte

- **MASQUANTS** parmi les restants : **2 / 10**
- **branches d'`if/else`** *(anodines par exhaustivité, comptées à part)* : **4**

### Consolidé sur toute la population

| Origine | Masquants | Examinés |
|---|---|---|
| #481 *(les 5 premiers)* | 2 | 5 |
| **#484** *(le reste)* | **2** | **10** |
| **total** | **4** | **15** |

> **Toute la population a été lue.** Ce total ne demande aucune
> extrapolation — c'est le second dénombrement complet de cette série,
> après celui du #479.

## Trois angles morts de ma règle, tous trouvés par l'examen

Le #481 en connaissait **un**. L'examen des restants en révèle **deux
autres** — et aucun n'est corrigé ici :

| Angle mort | Cas concernés |
|---|---|
| branche d'`if/else` exhaustif *(connu au #481)* | **4** |
| témoin situé dans un **bloc parent** | **2** |
| témoin publié **sous un autre nom** | **4** |

*(Les causes **se recoupent** : 10 causes
pour 8 cas anodins, parce qu'un cas peut
en cumuler deux — `verdict_detector_fix` est à la fois une branche
d'alternative **et** doté d'un témoin sous un autre nom.)*

> **Ma règle cherchait la variable de la garde au seul niveau non gardé.**
> Elle manque donc un témoin dès qu'il est un peu plus haut, ou qu'il
> porte un autre nom — `rappel` pour `rates`, `ok4` pour `idem`.

**Aucun n'est corrigé.** Les corriger après mesure serait le retuning que
les #480, #481 et #483 ont refusé. Le majorant est publié **avec ses
trois causes**, ce qui permet à un lecteur de retrancher lui-même.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 2 masquants parmi les restants | ≥ 2 | 2 | **vérifiée** |
| total consolidé ≤ 7 masquants | ≤ 7 | 4 | **vérifiée** |
| ≥ 1 branche d'`if/else` | ≥ 1 | 4 | **vérifiée** |

**Les trois sont vérifiées, et c'est le résultat le moins intéressant
du cycle.** Elles étaient faibles : « ≥ 2 » quand le #481 en avait trouvé
2 sur 5, « ≤ 7 » sur 14, « ≥ 1 » alternative quand le #481 en signalait
déjà une. **Ce que le cycle apprend vraiment, il ne l'avait pas prédit** :
les **deux angles morts supplémentaires** de ma propre règle.

## Ce que devient la dette

- **4 sections masquantes** établies sur **15** sans
  témoin — **toutes lues**, plus aucune non jugée ;
- **11** anodines, dont les **8** lues ici
  le sont **toutes** pour une raison que ma règle ne sait pas voir ;
- **0** correction apportée : ni aux scripts, ni à la règle.

> **La forme qui a coûté trois cycles existe en 4 exemplaires**
> — sur les **766** scripts producteurs recensés au #481. Elle est réelle,
> nommée, et rare — les trois à la fois.

## Critères de succès

1. Population re-dérivée (**15**), écart au #481 (**+1**),
   les **5** du #481 déclarés et exclus — **OUI**.
2. **10/10** examinés avec
   garde verbatim et verdict — **OUI**.
3. Total consolidé publié, part du #481 distinguée — **OUI**.
4. Aucun masquant compté sans sa garde publiée — **OUI**.
5. Branches d'`if/else` comptées à part (**4**) — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).