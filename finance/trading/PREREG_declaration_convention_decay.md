# Pré-enregistrement — la convention est-elle **en train de mourir** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #491.

## Le constat à éprouver

Le **#486** a daté la convention d'auto-déclaration : **premier `PREREG_`
déclaré le 13/08/2026**, aucun des **380** antérieurs. Mais il a aussi observé
une décroissance apparente :

> **33** déclarés apparus le 13/08, puis **0** sur les 5 derniers.

Il l'a inscrite comme question ouverte. **Ce cycle la tranche.**

## Le soupçon qui motive ce cycle, dit d'avance

La règle du #483 cherche `Cycle de **X**` — **le mot seul en gras**. Une variante
de mise en forme, `**Cycle de X**` — **la phrase entière en gras** — ne serait
pas reconnue, alors qu'elle **déclare exactement la même chose**.

**Si les cycles récents ont glissé vers cette variante, la « mort » de la
convention serait un artefact du détecteur, pas un fait du dépôt.** C'est une
hypothèse commode pour moi, puisque j'écris ces cycles : elle doit rester
réfutable, et la mesure doit pouvoir la démentir.

## Le protocole

Population : **tous** les `PREREG_*.md`, datés par leur commit d'introduction
(`git log --diff-filter=A --reverse`), **même méthode qu'au #486**.

Deux règles appliquées à l'identique sur les **douze premières lignes** :

```python
LITTERALE = r"Cycle d[e'’]\s*\*\*([^*]+)\*\*"        # celle du #483
TOLERANTE = r"\*\*Cycle d[e'’]\s*([^*]+)\*\*|Cycle d[e'’]\s*\*\*([^*]+)\*\*"
```

La tolérante accepte **les deux mises en forme** et rien d'autre : elle
n'élargit pas la notion de déclaration, seulement son typographie.

## Les trois lectures — toutes publiables

- **A. Déclin réel** — les **deux** règles montrent une baisse sur la période
  récente : la convention est effectivement abandonnée.
- **B. Artefact de format** — la règle **tolérante** ne montre **pas** de baisse
  là où la littérale en montre une : c'est le détecteur qui décroche, pas la
  pratique.
- **C. Ni l'un ni l'autre** — les deux règles donnent le même compte, et la
  baisse persiste sans explication typographique.

## Le critère qui départage — fixé ici

Soit `L` et `T` les parts de déclarés parmi les **20 `PREREG_` les plus
récents**, sous chaque règle.

- **B** si `T − L ≥ 30 points` ;
- **A** si `T < 30 %` **et** `T − L < 30 points` ;
- **C** sinon.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **deux règles citées verbatim**, et leurs comptes publiés **côte à côte**
   sur toute la population.
2. La **chronologie par tranches** publiée **sous les deux règles**.
3. **Une** des trois lectures nommée par le critère chiffré.
4. Si **B** : le constat du #486 **explicitement nuancé**, sans que son entrée
   soit réécrite.
5. Les cycles **#487 à #491** — les miens, les plus récents — **nommés
   individuellement** avec leur détection sous chaque règle.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. La lecture **B** est retenue.
2. Les cycles **#487 à #491** sont **tous** détectés par la tolérante et
   **aucun** par la littérale.
3. Le compte total de déclarés **augmente d'au moins 5** en passant à la
   tolérante.

Si la lecture **A** sort, la convention est réellement abandonnée — **par moi,
puisque c'est moi qui écris ces cycles** — et je devrai l'écrire sans chercher
d'excuse typographique.

## Ce que ce cycle ne fait pas

- Il ne **modifie** aucun `PREREG_` pour le rendre détectable.
- Il n'**exécute** aucun script du dépôt : lecture de `git log` et du disque.
- Il ne **réécrit** ni le #483 ni le #486 — une nuance s'ajoute, elle n'efface
  pas.
- Il ne **change pas** la règle du #483 dans les autres cycles : la tolérante
  n'existe que dans ce rapport.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que j'ai abandonné la
   convention.
2. Règles, population et seuils **inchangés** après mesure.
3. Les deux comptes publiés **côte à côte**, jamais le seul favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
