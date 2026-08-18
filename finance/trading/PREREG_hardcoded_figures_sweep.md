# Pré-enregistrement — les **chiffres publiés sans code qui les produise**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #475.

## D'où vient la question

Le **#473** a établi que le « **1** » du #451 — trois cycles avaient cherché à
le reproduire — était une **chaîne écrite à la main** dans le code qui rédige le
rapport :

```python
105:    L.append("| rapport qui **cite** l'encart sans le porter | **1** |")
```

Aucune variable ne le portait, aucun calcul ne le produisait. La leçon inscrite
était : **« ce que coûte un nombre publié sans le code qui le produit »**. Reste
à savoir si le cas est **isolé ou courant**. Ce cycle le mesure.

## La population

Tout rapport de `results/` ayant un script producteur sous la convention de
nommage : `_result.md` → `_backtest.py`, `_audit.md` → `_audit.py`,
`_robustness.md` → `_robustness.py`. Les rapports **hors convention** sont
comptés à part et **jamais** présentés comme fautifs — leçon du #464.

## La règle — celle du #473, reprise telle quelle

Dans chaque script producteur, on retient les lignes qui **écrivent un chiffre
en gras** au sens de la convention du dépôt (`**42**`, `**42,3 %**`), et on les
classe :

- **CALCULÉ** si la ligne interpole — `f"`, `.format(`, `%`, `{…}`,
  concaténation, `str(` ;
- **LITTÉRAL** sinon : le nombre est écrit en toutes lettres dans une chaîne
  simple.

```python
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
```

C'est **exactement** le test du #473, réemployé sans modification.

## Ce qu'un littéral n'est PAS

**Un chiffre littéral n'est pas automatiquement une faute**, et ce cycle ne
publiera **aucun total présenté comme un compte de fautes**. Sont parfaitement
légitimes :

- un **seuil pré-enregistré** rappelé dans le rapport (« critère : **25 %** ») ;
- un **chiffre cité d'un cycle antérieur** (« le #451 comptait **1** ») ;
- une **constante de protocole** (« **5 bps** aller-retour », « `n_trials = 1` »).

La faute du #473 est plus étroite : un littéral **présenté comme le résultat
mesuré par ce cycle-là**. **Ma règle mécanique ne sait pas faire cette
différence** — elle mesure une **prévalence**, pas une culpabilité. Le rapport
devra le dire à l'endroit du chiffre, pas seulement en note.

## L'examen individuel — échantillon fixé avant de regarder

Le comptage seul reproduirait la faute des #462, #464 et #465 : accuser la trace
du dépôt sur la foi d'un total. Donc :

**Les 5 scripts portant le plus de littéraux** — ex æquo départagés par ordre
alphabétique — sont **examinés un par un**, et pour chacun le rapport publie :

1. la ligne **verbatim** ;
2. un verdict : **« présenté comme mesure de ce cycle »** (défaut de type #473)
   ou **« légitime »** avec sa raison.

Un littéral non examiné ne sera **jamais** qualifié de défaut.

## Critère de succès — chiffré, il porte sur le procédé

1. Population énumérée, effectif publié, rapports **hors convention** comptés à
   part.
2. **100 %** des rapports de la population classés.
3. Les **5** de l'échantillon examinés individuellement, ligne verbatim et
   verdict publiés pour chacun.
4. Aucun total présenté comme un compte de fautes — la distinction
   prévalence / culpabilité **écrite à l'endroit du chiffre**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 50** rapports de la population contiennent **au moins un** chiffre
   littéral. *(Fondement : la convention du dépôt met en gras presque tous les
   nombres, et les rappels de seuils sont systématiques.)*
2. Sur les **5** examinés, **≥ 1** littéral est **présenté comme une mesure du
   cycle** — donc un défaut de type #473, prouvant que le #451 n'était pas
   isolé.
3. La **médiane** du nombre de littéraux par rapport affecté est **≤ 3** : le
   phénomène est **diffus**, pas concentré sur quelques scripts.

Si la prédiction 2 est réfutée — **aucun** des cinq n'est un défaut — alors le
cas du #451 est **isolé** parmi les plus chargés, et je devrai l'écrire : la
leçon du #473 vaudrait comme avertissement, pas comme constat de dette. **Ce
serait le résultat favorable, et le plus suspect** : cinq scripts choisis pour
leur charge maximale sont l'endroit où un défaut devrait se voir.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script ni aucun rapport.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **réécrit** aucun verdict passé, et ne rouvre pas la question du #451,
  close au #473.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le #451 était isolé.
2. Population, règle et taille d'échantillon **inchangées** après mesure.
3. **Aucun total présenté comme un compte de fautes** — engagement pris contre
   la faute répétée des #462, #464, #465, et évitée de justesse au #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
