# Audit adversarial — les chiffres littéraux (#476)

**Recalcul par une route différente** : l'**arbre syntaxique** au lieu de
l'expression régulière sur le texte. `ast.Constant` exclut d'office les
f-strings (`ast.JoinedStr`) et les concaténations (`ast.BinOp`) — **la
distinction que le backtest doit reconstruire par regex est ici
structurelle**, donc plus sûre.

| Grandeur | Audit (AST) | Rapport (regex) | Verdict |
|---|---|---|---|
| population (rapports avec producteur) | **762** | 762 | **concordant** |
| rapports hors convention | **308** | 308 | **concordant** |
| scripts avec ≥ 1 littéral | **35** | 35 | **concordant** |
| médiane par rapport affecté | **2,0** | 2,0 | **concordant** |
| maximum sur un script | **7** | 7 | **concordant** |

## L'échantillon est-il bien le bon ?

La règle pré-enregistrée : **les 5 plus chargés**, ex æquo par ordre
alphabétique. Recalculée par l'AST :

- `nonml_protocol_inventory_audit.py` (**7**) — examiné dans le rapport : **oui**
- `nonml_marker_emitted_by_scripts_backtest.py` (**5**) — examiné dans le rapport : **oui**
- `nonml_repo_magnitudes_recount_backtest.py` (**5**) — examiné dans le rapport : **oui**
- `nonml_citer_451_definition_backtest.py` (**4**) — examiné dans le rapport : **oui**
- `nonml_duplicate_sweep_coverage_audit.py` (**4**) — examiné dans le rapport : **oui**

**Les cinq que l'AST désigne sont ceux que le rapport examine.**
La règle d'échantillonnage n'a pas dérivé entre les deux routes.

## Un contrôle que le backtest ne fait pas

Les littéraux sont-ils dans des **lignes de tableau** (`| … |`) ou dans
de la **prose** ? Un tableau porte plus souvent un résultat, la prose
plus souvent une citation. **Ce n'est pas un test de culpabilité** —
seulement un indice structurel, et il est publié comme tel.

- littéraux en **ligne de tableau** : **19**
- littéraux en **prose** : **68**

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**CONCORDANT** — **5/5** grandeurs se retrouvent par
une route indépendante.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).