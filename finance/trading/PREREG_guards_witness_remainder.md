# Pré-enregistrement — les **9 sans témoin non examinés**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #483.

## Ce que le #481 a laissé

Le #481 a classé **14** titres de section **sans témoin inconditionnel** — des
sections qui s'effacent sans qu'aucun compte ne le signale — puis n'en a lu que
**5**, en écrivant lui-même la limite :

> **Les 9 autres sans témoin ne sont pas jugés.** Cinq ont été lus parce que
> cinq avaient été déclarés ; le 2/5 **ne s'extrapole pas**.

**Ce cycle lit les 9 restants**, et rend le compte **complet** — un
dénombrement, plus un taux d'échantillon. C'est la même démarche qu'au #479
pour les chiffres littéraux.

## La population — re-dérivée, pas recopiée

Reconstruite par la règle du #481, **reprise sans modification** : un titre de
section est *sans témoin* si sa garde la plus interne est de la forme
`if <var>:` / `if not <var>:` et qu'**aucune ligne d'écriture non gardée de la
même fonction** ne mentionne `<var>`.

**Sont retirés d'avance** : les **5** déjà examinés au #481
(`battery_coverage` l.159, `citer_451_resolution` l.187,
`marker_emitter_crossing` l.175, `net_pnl_correction` l.279,
`net_pnl_correction_robustness` l.76), et **ce cycle lui-même**.

Si l'effectif a bougé, **le nouveau chiffre est publié tel quel** et l'écart
signalé : un compte de dépôt est daté (#436-#438).

## Le défaut connu de cette règle, rappelé d'avance

Le #481 a établi que sa règle **ne reconnaît pas l'exhaustivité d'un `if/else`**
et compte les deux branches comme sans témoin, alors qu'**une section paraît
toujours**. Le total de 14 est donc un **majorant**.

**La règle n'est pas corrigée ici** — ce serait un retuning. Mais les cas qui
sont des branches d'alternative seront **signalés comme tels** dans leur
verdict, et comptés à part du total des masquants.

## La règle de verdict — celle du #481, reprise telle quelle

Chaque cas restant est **lu**, et reçoit un verdict **écrit à la main** :

- **MASQUANT** — la section gardée est la **seule** mention de son sujet ; son
  absence est indiscernable d'un sujet inexistant (forme du #475) ;
- **ANODIN** — le sujet est mentionné ailleurs, la section est un développement
  dont l'absence ne cache rien, **ou** c'est une branche d'`if/else` exhaustif.

**Aucun verdict n'est produit par une règle** : c'est ce qu'une règle ne sait
pas faire, et c'est pourquoi ce cycle lit.

## Critère de succès — chiffré, il porte sur le procédé

1. Population re-dérivée, effectif publié, **écart au #481 signalé**, les 5
   déjà examinés **déclarés et exclus**.
2. **100 %** des restants examinés — **garde verbatim et verdict pour chacun**.
3. Le **total consolidé sur les 14** publié, la part venant du #481
   **distinguée** de celle établie ici.
4. **Aucun masquant compté sans sa garde publiée.**
5. Les branches d'`if/else` **comptées à part**, et le total de masquants dit
   **hors** de ces cas.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 2 masquants** parmi les restants. *(Fondement : 2 sur 5 au #481.)*
2. Le total consolidé sur les 14 est **≤ 7 masquants**.
3. **≥ 1** des restants est une **branche d'`if/else`** — donc anodin par
   exhaustivité, et retranché du majorant.

Si la prédiction 1 est réfutée — **aucun masquant parmi les 9** — alors les deux
cas du #481 étaient les seuls, la forme qui a coûté trois cycles est **rare**, et
je devrai l'écrire sans chercher à la prolonger.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script ni aucun rapport, ni la règle du #481.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **révise** aucun des 5 verdicts du #481.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il ne trouve aucun masquant.
2. Population et règle de verdict **inchangées** après mesure.
3. **Chaque garde citée verbatim**, jamais seulement comptée — leçon des #462,
   #464, #465, #469, #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
