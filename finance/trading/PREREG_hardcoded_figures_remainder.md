# Pré-enregistrement — les **30 rapports non examinés** du #476

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #478.

## Ce que le #476 a laissé

Le #476 a trouvé **35** rapports dont le script porte au moins un chiffre
**littéral**, puis n'en a examiné que **5** — les plus chargés — et a écrit
lui-même la limite :

> **Ce `3` ne se généralise pas aux 35 rapports affectés.** L'échantillon a été
> choisi pour sa **charge maximale**, c'est-à-dire là où un défaut avait le plus
> de chances de se voir.

**Ce cycle examine les 30 restants**, et rend ainsi le premier compte **complet**
de cette série — non plus un taux d'échantillon, mais un dénombrement.

## La population — re-dérivée, pas recopiée

Elle est reconstruite par la règle du #476, **reprise sans modification** :

```python
GRAS      = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
ECRIT     = re.compile(r"\.append\s*\(|\.write\s*\(|write_text\s*\(|print\s*\(")
```

Un chiffre est **LITTÉRAL** s'il est écrit en gras dans une chaîne simple passée
à une ligne d'écriture, **sans interpolation**.

**Sont retirés d'avance** : les **5** déjà examinés au #476
(`protocol_inventory_audit`, `marker_emitted_by_scripts`,
`repo_magnitudes_recount`, `citer_451_definition`,
`duplicate_sweep_coverage_audit`), et **ce cycle lui-même** — règle d'exclusion
de soi des #447/#463, appliquée avant mesure.

Si l'effectif a bougé depuis le #476, **le nouveau chiffre est publié tel quel**
et l'écart signalé : un compte de dépôt est daté (#436-#438).

## La règle de verdict — celle du #476, reprise telle quelle

Pour chaque littéral, un verdict **écrit à la main** après lecture :

- **DÉFAUT** — le littéral est **présenté comme le résultat mesuré par ce
  cycle-là** (forme du #451, établie au #473) ;
- **LÉGITIME** — citation d'un cycle antérieur, seuil pré-enregistré rappelé,
  constante de protocole, ou **étiquette de numérotation** (`**1**`, `**2**`…),
  ce dernier cas étant un **faux positif de la règle mécanique**, reconnu au
  #476.

**Aucun verdict n'est produit par une règle** : c'est précisément ce qu'une
règle ne sait pas faire, et c'est pourquoi ce cycle lit au lieu de compter.

## Critère de succès — chiffré, il porte sur le procédé

1. Population re-dérivée, effectif publié, écart au #476 **signalé**, les 5
   déjà examinés **déclarés et exclus**.
2. **100 %** des restants examinés — **ligne verbatim et verdict pour chacun**.
3. Le **total consolidé sur les 35** publié, la part venant du #476 **distinguée**
   de celle établie ici.
4. **Aucun défaut compté sans sa ligne publiée.**

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 3 défauts** parmi les 30 restants. *(Fondement : 2 défauts nets sur les 5
   plus chargés ; un taux plus faible est attendu sur les moins chargés, mais
   30 cas restent nombreux.)*
2. **≥ 20 sur 30** sont des **citations** — la forme légitime dominante.
3. Le total consolidé sur les 35 est **≤ 8 défauts**.

Si la prédiction 1 est réfutée — **zéro défaut sur les 30** — alors les défauts
se concentrent entièrement sur les scripts les plus chargés, et **la règle
« charge maximale » du #476 était un bon prédicteur** sans que rien ne l'ait
garanti d'avance. Je devrai l'écrire comme un fait, non comme un mérite.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script ni aucun rapport — la réparation, si elle a
  lieu, sera un cycle dédié, comme au #468.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **réexamine pas** les 5 du #476 et ne révise aucun de leurs verdicts.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il ne trouve aucun défaut.
2. Population et règle de verdict **inchangées** après mesure.
3. **Chaque littéral cité verbatim**, jamais seulement compté — leçon des #462,
   #464, #465, #469, #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
