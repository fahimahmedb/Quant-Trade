# Pré-enregistrement — **combien des défauts restants sont irréparables ?**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #484.

## La catégorie découverte au #482, jamais comptée

Le **#482** devait réparer deux chiffres tapés à la main. Il n'en a réparé aucun,
et a découvert en chemin une catégorie que le #479 n'avait pas prévue :

> **Une grandeur historique dont l'univers n'est plus reconstructible n'est pas
> réparable — seulement signalable.**

Le #479 avait dénombré **18** chiffres publiés sans code qui les produise ; le
#482 en a **rétracté un**, ramenant le compte à **17**. **Aucun n'a été classé
réparable ou non.** Ce cycle le fait.

## La population — re-dérivée, et corrigée de la rétractation

Reconstruite par la règle du #479, **reprise sans modification** :

```python
GRAS      = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
ECRIT     = re.compile(r"\.append\s*\(|\.write\s*\(|write_text\s*\(|print\s*\(")
```

Puis **restreinte aux scripts que les #476 et #479 ont jugés DÉFAUT ou
PARTIEL**, et **privée de `reproducibility_sample_lot3_audit`**, dont le #482 a
rétracté le verdict *(les lignes incriminées étaient une citation de diff)*.

Si l'effectif a bougé, **le nouveau chiffre est publié tel quel** et l'écart
signalé : un compte de dépôt est daté (#436-#438).

## La règle de verdict — écrite à la main, et déclarée ici

Chaque défaut est **lu**, et reçoit l'un de ces deux verdicts :

- **RÉPARABLE** — la grandeur est dérivable de ce que le script **a sous la
  main aujourd'hui** : ses propres variables, ses entrées, le dépôt qu'il lit
  déjà. Une interpolation suffirait.
- **IRRÉPARABLE** — la grandeur est **historique** : elle mesure un univers que
  le script ne construit pas et qu'aucun module n'expose. La recalculer
  produirait **un chiffre qui mesure autre chose** — le cas exact établi au
  #482 sur `pnl_persistence_exposed_pass_audit`.

**Aucun verdict « irréparable » ne sera écrit sans la raison qui le rend tel.**

## Le proxy mécanique — publié à côté, et déclaré faible d'avance

Un proxy est calculé pour chaque script : **compte-t-il au moins une collection**
dans la même fonction (compréhension, `glob`, `len(...)`) ? Si oui, la matière
première existe peut-être ; sinon, elle est certainement absente.

**Ce proxy ne décide rien.** Toutes les règles mécaniques de cette série ont eu
un angle mort — #469, #478, #480, #481, #483, #484 — et il n'y a aucune raison
que celle-ci fasse exception. Elle est publiée **à côté** du verdict à la main,
avec son **taux d'accord mesuré**, pour que le lecteur juge de sa valeur.

## Critère de succès — chiffré, il porte sur le procédé

1. Population re-dérivée, effectif publié, **écart signalé**, et la rétractation
   du #482 **prise en compte explicitement**.
2. **100 %** examinés à la main — **ligne verbatim, verdict et raison** pour
   chacun.
3. Le proxy mécanique publié **à côté** des verdicts, et son **taux d'accord**
   chiffré.
4. **Aucun « irréparable » sans sa raison.**

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 5** défauts sont **IRRÉPARABLES**.
2. **≥ 8** sont **RÉPARABLES**.
3. Le proxy mécanique s'accorde avec le verdict à la main dans **moins de 80 %**
   des cas — comme toutes les règles mécaniques de cette série, il aura un angle
   mort.

Si la prédiction 3 est réfutée et que le proxy s'accorde à plus de 80 %, **je ne
conclurai pas qu'il est bon** : dix-sept cas ne valident pas une règle, ils
échouent seulement à la prendre en défaut. Ce serait le résultat le plus
flatteur, et le moins instructif.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien — la réparation, si elle a lieu, sera un cycle dédié,
  et le #482 a montré qu'elle peut être **nuisible**.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **révise** aucun verdict des #476, #479 ou #482.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris si presque tout est irréparable — ce
   qui rendrait la dette du #479 largement inactionnable.
2. Population et règle de verdict **inchangées** après mesure.
3. **Chaque ligne citée verbatim**, jamais seulement comptée.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
