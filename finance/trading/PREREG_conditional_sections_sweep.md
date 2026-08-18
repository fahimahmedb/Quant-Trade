# Pré-enregistrement — les **sections qui ne paraissent que sous condition**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #477.

## D'où vient la question

Le **#475** a établi que la marque « Rapport dépendant du dépôt » manquait au
rapport de `six_reports_regeneration` **non pas par perte**, mais parce que la
ligne qui l'écrivait était sous une garde :

```python
231:    if perdus:
240:        L.append("> **Rapport dépendant du dépôt** — …")
```

Toute une **section** — titre compris — ne paraissait que si le script avait
trouvé quelque chose. Trois cycles (#469, #472, #475) ont dépensé leur budget
sur ce seul cas. La question ouverte : **est-ce courant ?**

## La population

Tout rapport de `results/` ayant un script producteur sous la convention de
nommage : `_result.md` → `_backtest.py`, `_audit.md` → `_audit.py`,
`_robustness.md` → `_robustness.py`. Les rapports **hors convention** sont
comptés à part et **jamais** présentés comme fautifs — leçon du #464.

## La règle — par arbre syntaxique, pas par indentation

Dans chaque script producteur, on repère les **titres de section** écrits dans
le rapport : un appel `append`/`write`/`print` dont l'argument est une chaîne
**simple** commençant par `## ` ou `### `.

Chacun est classé par sa position dans l'**arbre syntaxique** :

- **INCONDITIONNEL** — aucun `If` / `For` / `While` / `Try` englobant dans le
  corps de sa fonction ;
- **CONDITIONNEL** — au moins un.

L'AST est employé plutôt que l'indentation parce qu'il donne la structure
réelle. Le #475 avait établi les deux routes concordantes sur un cas ; ici c'est
l'AST seul, et l'audit recomptera par l'indentation.

## Ce qu'une section conditionnelle n'EST PAS

**Ce n'est pas une faute**, et ce cycle ne publiera **aucun total présenté comme
un compte de fautes**. Le motif est souvent le bon :

- une section « Les défauts trouvés » suivie d'un `if not fautifs: "Aucun."`
  **paraît toujours** — c'est son *contenu* qui varie, pas son existence ;
- une section légitimement absente quand son sujet l'est aussi.

Le cas du #475 est plus étroit : **le titre lui-même est sous garde**, donc la
section **disparaît entièrement**, et deux exécutions produisent des rapports
dont on ne peut plus aligner les sections. **Ma règle mécanique ne distingue pas
« garde qui peut être fausse » de « garde toujours vraie en pratique »** — elle
mesure une **prévalence**, pas une culpabilité. Le rapport devra le dire à
l'endroit du chiffre, pas en note.

## L'examen individuel — échantillon fixé avant de regarder

**Les 5 scripts portant le plus de titres conditionnels** — ex æquo départagés
par ordre alphabétique — sont **lus un par un**, et pour chacun le rapport
publie :

1. la garde **verbatim** ;
2. un verdict : **« la section peut disparaître entièrement »** (forme #475) ou
   **« garde structurellement toujours vraie »** avec sa raison.

Un titre conditionnel non examiné ne sera **jamais** qualifié de défaut.

## Critère de succès — chiffré, il porte sur le procédé

1. Population énumérée, effectif publié, hors convention comptés à part.
2. **100 %** des scripts de la population classés.
3. Les **5** de l'échantillon examinés individuellement, garde verbatim et
   verdict publiés.
4. Aucun total présenté comme un compte de fautes — la distinction
   prévalence / culpabilité **écrite à l'endroit du chiffre**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 40** scripts de la population écrivent **au moins un** titre de section
   sous condition. *(Fondement : le motif « section publiée seulement s'il y a
   quelque chose à montrer » est fréquent dans ces cycles.)*
2. La **médiane** de titres conditionnels par script affecté est **≤ 2** : le
   phénomène est **diffus**, pas concentré.
3. Sur les **5** examinés, **≥ 3** ont une garde qui **peut être fausse**, donc
   une section susceptible de disparaître entièrement — la forme exacte du #475.

Si la prédiction 3 est réfutée — **la plupart des gardes sont toujours vraies** —
alors le cas du #475 est **rare** et la piste ouverte au #477 se referme sur un
constat mince. **Ce serait le résultat favorable, et le plus suspect** : cinq
scripts choisis pour leur charge maximale sont l'endroit où le motif devrait se
voir.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script ni aucun rapport.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **réécrit** aucun verdict passé, et ne rouvre pas le cas du #475.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le cas du #475 est rare.
2. Population, règle et taille d'échantillon **inchangées** après mesure.
3. **Aucun total présenté comme un compte de fautes** — engagement pris contre
   la faute répétée des #462, #464, #465, et tenu aux #474 et #476.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
