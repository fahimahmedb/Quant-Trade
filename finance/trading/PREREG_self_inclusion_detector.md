# Pré-enregistrement — détecter l'auto-inclusion **sans exécuter**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #465.

## Le problème

Le **#463** a éprouvé **18** scripts en les rejouant deux fois et en a trouvé
**2** non idempotents, par **auto-inclusion** : un rapport qui compte des
rapports se compte lui-même s'il ne s'exclut pas du corpus. C'est la règle que
le **#446** avait trouvée et que le **#447** avait énoncée — **jamais propagée**.

Le dépôt compte **318** `nonml_*_backtest.py`. Les rejouer deux fois chacun est
hors de portée d'un cycle : le #463 a mis plus de vingt minutes pour 18.

## Ce que ce cycle fait — et ce qu'il refuse de faire

Il construit un détecteur **statique** : il **lit le code**, il n'exécute rien.

**Il ne répare rien.** La file demandait aussi de « propager l'exclusion de soi
aux deux scripts identifiés ». **Je le reporte à un cycle déclaré**, et je dis
pourquoi : réparer ces scripts **régénère leurs rapports**, et le #450 a payé
cher le mélange d'une réparation et d'une mesure. Un cycle qui détecte et un
cycle qui répare sont deux cycles.

## Le détecteur — ses règles, énoncées mot pour mot

Un script est **exposé** s'il réunit les deux conditions :

1. il **écrit** un rapport sous `results/` — présence d'un `write_text(` sur une
   variable de sortie ;
2. il **énumère** des fichiers de `results/` — `RESULTS.glob(`, `.iterdir()`, ou
   un `ls-tree`/`ls-files` portant sur `results/`.

Un script exposé est **protégé** s'il porte l'un de ces trois signes :

- un `unlink(` sur sa variable de sortie *(la correction du #446)* ;
- une comparaison excluant son propre nom de fichier ;
- un filtre nommé sur son propre `<nom>` de cycle.

**Exposé et non protégé ⇒ signalé.**

## La calibration — le seul garde-fou contre un détecteur qui invente

Le #463 fournit une **vérité terrain** : sur ses 18 scripts, **2** sont non
idempotents et **16** ne le sont pas. Le détecteur est confronté à ces 18 :

- **rappel** : combien des **2** sont signalés ;
- **faux positifs** : combien des **16** sont signalés à tort.

> **Un détecteur statique se trompe par construction.** Il ne voit pas si le
> glob d'un script *rencontre réellement* son propre fichier, ni si une
> protection écrite autrement fonctionne. Le publier sans sa calibration
> reviendrait à présenter une heuristique pour une mesure — la faute que les
> #462, #464 et #465 ont commise trois fois de suite.

## Critère de succès — chiffré, il porte sur le procédé

1. **318/318** scripts classés, ou écartés **avec leur raison**.
2. La calibration sur les 18 du #463 publiée : **rappel** et **faux positifs**.
3. Les scripts signalés listés **nominativement**.
4. Aucun script modifié — **le dépôt est en lecture seule pour ce cycle**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

Un détecteur qui se révèle mauvais **et le montre proprement** fait un PASS : le
critère porte sur la méthode, pas sur la qualité de l'heuristique.

## Prédictions — falsifiables

1. **Rappel 2/2** : les deux cas connus du #463 sont signalés. Si le détecteur
   en manque un, il est **inutilisable** et je l'écrirai.
2. **Au moins 5** scripts hors des 18 sont signalés. Fondement : la règle du
   #447 n'a jamais été propagée, et 300 scripts n'ont jamais été regardés.
3. **Faux positifs ≤ 4** sur les 16 idempotents connus.

Si le rappel est de 2/2 **et** les faux positifs nuls, je dois me méfier : sur
un échantillon de 18, un détecteur parfait est plus souvent le signe d'une règle
taillée sur les cas connus que d'une bonne heuristique. **La règle ci-dessus est
écrite avant d'avoir regardé le code des deux fautifs autrement que par le
rapport du #463.**

## Ce que ce cycle ne fait pas

- Il ne **répare** aucun script.
- Il n'**exécute** aucun script : donc **aucun effet de bord** (#463).
- Il ne **réécrit** aucun verdict.
- Il ne prétend pas que « signalé » vaut « défectueux » : seule l'exécution le
  prouverait, et elle n'est pas faite ici.

## Engagements

1. Résultat rapporté tel quel, y compris si le détecteur rate un cas connu.
2. Règles du détecteur **inchangées** après mesure. Si elles se révèlent mal
   formées, le défaut est **publié**, et la correction refaite **sous une règle
   déclarée**, pas ajustée au résultat.
3. La calibration est publiée **même si elle est mauvaise**.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
