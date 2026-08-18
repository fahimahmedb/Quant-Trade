# Audit adversarial — les rapports non examinés du #476 (#479)

**Recalcul par une route différente** : l'**AST** (`ast.Constant` contre
`ast.JoinedStr`) au lieu des trois expressions régulières du #476 — la
distinction littéral / interpolé y est **structurelle**. Les verdicts sont
relus **dans le rapport publié**, pas dans la table du script.

| Grandeur | Audit (AST) | Rapport (regex) | Verdict |
|---|---|---|---|
| scripts affectés (population) | **37** | 37 | **concordant** |
| restants examinés | **32** | 32 | **concordant** |
| défauts pleins | **11** | 11 | **concordant** |
| partiels | **4** | 4 | **concordant** |
| légitimes | **17** | 17 | **concordant** |

## Le contrôle central — critère 4 du pré-enregistrement

> *« Aucun défaut compté sans sa ligne publiée. »*

Un cycle qui accuse **doit montrer**. Vérifié sur le rapport lui-même :

- scripts restants recomptés par l'AST : **32**
- **sans section dédiée** dans le rapport : **0**
- sections **sans aucune ligne de code publiée** : **0**

> **Chaque script examiné a sa section, et chaque section porte ses
> lignes numérotées.** Le critère 4 est tenu — un lecteur peut
> contester n'importe lequel des verdicts sur pièce.

## Le cycle s'accuse-t-il lui-même ?

Un balayage dont l'auteur est dans la population a une raison de
s'épargner. Contrôle mécanique :

| Script issu de cette série de cycles | Verdict reçu |
|---|---|
| `nonml_citer_451_resolution_backtest.py` | légitime |
| `nonml_conditional_sections_sweep_backtest.py` | légitime |
| `nonml_hardcoded_figures_sweep_backtest.py` | légitime |
| `nonml_orphans_interrupted_or_lost_backtest.py` | **PARTIEL** |

> **1 script(s) de la série reçoit un verdict à charge**
> — dont `orphans_interrupted_or_lost`, le cycle **#474**. Le balayage
> ne s'épargne pas.

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**CONCORDANT** — **5/5** grandeurs se retrouvent par
une route indépendante.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).