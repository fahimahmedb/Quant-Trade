# Pré-enregistrement — l'idempotence des rapports

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, deuxième piste de la file ouverte au #461.

## Pourquoi ce cycle existe

Le contrôle D du #461 a trouvé **un** rapport qui changeait d'une exécution à
l'autre : les variantes typographiques étaient stockées dans un `set`, et
l'étiquette affichée suivait l'ordre d'itération, donc la graine de hachage.
La classification était stable, le texte publié ne l'était pas.

**Il a été trouvé par accident**, en vérifiant autre chose — comme les quatre
faux du backlog. La question que ce cycle pose est simple : **combien d'autres ?**

Un rapport non idempotent est un défaut réel : deux lecteurs qui rejouent le
même script obtiennent deux textes différents, et un cycle ultérieur qui compare
un rapport à sa régénération voit une dérive qui n'en est pas une (c'est
exactement le piège des #449/#450).

## L'univers — 18 scripts, et je dis ce que ce choix coûte

Les backtests des entrées **#443 à #460** — **le même univers figé que les #461
et #462**, pour que les trois cycles se comparent.

**Ce n'est pas tout le dépôt.** Il compte **314** `nonml_*_backtest.py` ; j'en
éprouve **18**, soit **5,7 %**. Deux raisons, dites avant de mesurer :

1. rejouer 314 scripts deux fois est hors de portée d'un cycle ;
2. c'est **dans cette famille** — les scripts qui lisent le dépôt plutôt que des
   données de marché — que le défaut connu est apparu.

**Le résultat ne se généralisera donc pas** aux 314, et je ne l'écrirai pas.

## Le protocole

Pour chaque script : exécution **deux fois de suite**, empreinte SHA-256 du
rapport produit comparée entre les deux passages.

- **budget déclaré : 300 s par exécution.** Au-delà, le script est classé
  « budget dépassé » et **listé**, pas silencieusement omis.
- un script qui échoue est classé « erreur » avec son code de sortie.
- un script dont le rapport n'existe pas après exécution est classé
  « sans rapport identifiable ».

## L'effet de bord, et comment il est annulé

Rejouer ces scripts **réécrit leurs rapports sur le disque**. Le #450 a montré
ce que coûte une régénération non maîtrisée : quatre marqueurs effacés, non
restaurés.

**Donc** : après la mesure, l'arbre de travail est restauré
(`git checkout -- finance/trading/results/`), et ce cycle ne committe **que son
propre rapport**. Toute autre modification sous `results/` serait un échec du
cycle, et le rapport la publierait.

## Critère de succès — chiffré, il porte sur le procédé

1. **18/18** scripts traités ou classés **avec leur raison**.
2. Pour chaque script éprouvé, les **deux empreintes** publiées.
3. Tout rapport non idempotent publié avec **le diff qui le prouve** — pas
   seulement le constat.
4. L'arbre de travail **vérifié propre** sous `results/` après restauration,
   hors le rapport de ce cycle.

> **PASS** = les quatre points. **FAIL** = un seul manque.

Un cycle qui ne trouve aucun rapport non idempotent et le montre proprement
**réussit**.

## Prédictions — falsifiables

1. **Au moins un** script autre que celui du #461 est non idempotent.
   Fondement : le défaut du #461 vient d'un `set` de chaînes, et cette
   construction est banale dans ces scripts.
2. **Au moins 12** des 18 tiennent dans le budget de 300 s.
3. Les scripts non idempotents le sont sur **l'étiquetage**, pas sur les
   **compteurs** — comme au #461, où la classification était stable.

Si la prédiction 1 est réfutée, je ne dois **pas** conclure que le dépôt est
idempotent : **je n'en éprouve que 5,7 %**, et deux exécutions consécutives dans
le même processus ne sondent qu'une partie des sources de non-déterminisme.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script non idempotent : le défaut est publié et
  inscrit, pas réparé au passage — engagement tenu depuis le #450.
- Il ne **committe** aucun rapport régénéré.
- Il ne juge **aucune stratégie**.

## Engagements

1. Résultat rapporté tel quel, y compris s'il ne trouve rien, et y compris un
   **FAIL** de mon procédé.
2. Univers, budget et protocole **inchangés** après mesure.
3. La proportion **5,7 %** est rappelée dans le rapport final, pas seulement
   ici — c'est la limite qui décide de ce qu'on a le droit d'en conclure.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
