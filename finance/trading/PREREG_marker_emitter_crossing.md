# Pré-enregistrement — séparer **porteurs** et **citeurs** par le script émetteur

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #468.

## La limite que ce cycle lève

Le **#465** voulait distinguer les rapports qui **portent** l'encart de
dépendance de ceux qui le **mentionnent**. Il a échoué, et a publié pourquoi :

> Un rapport qui **cite verbatim** la marque produit une ligne **textuellement
> identique** à celle d'un rapport qui la porte. Aucune règle de début de ligne
> ne les sépare.

Il notait aussi ce qui manquait : le **#451** pouvait trancher parce qu'il
savait **quel script émet** la marque. Le contrôle C du #465 a vérifié que cette
information **existe dans le dépôt** — donc que la limite tient à la méthode,
pas à une impossibilité.

**Ce cycle utilise cette information.**

## La règle — énoncée mot pour mot

Un rapport **contient** la marque si son texte comporte
`Rapport dépendant du dépôt`.

Pour chaque rapport qui la contient, on remonte à son **script producteur**,
par le nom :

| Rapport | Script producteur |
|---|---|
| `nonml_<nom>_result.md` | `nonml_<nom>_backtest.py` |
| `nonml_<nom>_audit.md` | `nonml_<nom>_audit.py` |
| `nonml_<nom>_robustness.md` | `nonml_<nom>_robustness.py` |

Puis :

- **PORTEUR** — le script producteur **émet** la marque, c'est-à-dire que son
  code source contient la chaîne ;
- **CITEUR** — le script producteur existe et **n'émet pas** la marque : le
  rapport en parle sans la porter ;
- **INDÉTERMINÉ** — aucun script producteur trouvé sous cette convention.

## Ce que cette règle ne peut pas faire, dit d'avance

- Un script peut **construire** la marque par concaténation ou par variable : il
  l'émettrait sans que la chaîne apparaisse telle quelle. Ces cas seraient
  classés **CITEUR à tort**. Le rapport devra donc examiner **chaque** citeur
  trouvé, pas seulement les compter.
- Le #464 a établi que la convention de nommage n'est pas universelle : les
  **indéterminés** ne sont pas des anomalies, seulement des rapports hors
  convention.

## Critère de succès — chiffré, il porte sur le procédé

1. **100 %** des rapports contenant la marque classés dans l'une des trois
   catégories.
2. **Tout** citeur publié **nominativement**, avec son script producteur.
3. Chaque citeur **examiné** — construction par variable écartée ou signalée.
4. Les indéterminés listés, **sans être présentés comme fautifs**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Au moins 1 citeur**, conformément au #451 qui en identifiait un.
2. Le nombre de **porteurs confirmés** est **strictement inférieur** au nombre
   de rapports contenant la marque — sinon la distinction n'existe pas et le
   #451 se serait trompé.
3. **Aucun** rapport dont le script émet la marque ne manque de la contenir —
   contrôle de cohérence : si un script l'émet, son rapport doit la porter.

Si la prédiction 1 est réfutée — **0 citeur** —, alors soit le citeur du #451 a
disparu du dépôt depuis, soit **ma règle le classe porteur à tort**, et je
devrai chercher lequel des deux avant de conclure.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun rapport ni aucun script.
- Il n'**exécute** rien : lecture seule, aucun effet de bord (#463, #468).
- Il ne **réécrit** aucun verdict.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que la distinction
   n'existe pas.
2. Règle **inchangée** après mesure.
3. **Chaque citeur est examiné individuellement**, jamais résumé en un compte —
   c'est la leçon des #462, #464 et #465, où trois de mes comptes ont accusé à
   tort la trace du dépôt.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
