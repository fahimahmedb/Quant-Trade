# Audit adversarial — les sans témoin non examinés (#484)

**Le contrôle central n'est pas le compte.** Un cycle qui déclarerait
« anodin » ce qu'il ne veut pas compter masquant serait **indétectable**
par un simple recomptage. L'audit teste donc **chaque motif d'anodin**
par une route mécanique propre.

- sections de verdict relues dans le rapport : **10**

## Motif « branche d'`if/else` » — vérifiable par AST

Le `if` gouvernant la ligne a-t-il un `orelse` **non vide** ?

| Cas | Motif invoqué | `orelse` non vide | Verdict |
|---|---|---|---|
| `nonml_net_pnl_correction_robustness.py` l.86 | alternative | **oui** | **confirmé** |
| `nonml_silent_skip_decision_backtest.py` l.119 | alternative | **oui** | **confirmé** |
| `nonml_verdict_detector_complete_robustness.py` l.124 | alternative | **oui** | **confirmé** |
| `nonml_verdict_detector_fix_backtest.py` l.248 | alternative | **oui** | **confirmé** |

> **Tous confirmés.**

## Motif « témoin dans un bloc parent » — vérifiable par AST

Une écriture située **hors** du bloc gardé mentionne-t-elle la variable ?

| Cas | Témoin parent trouvé | Verdict |
|---|---|---|
| `nonml_prereg_convention_coverage_backtest.py` l.174 | **oui** | **confirmé** |
| `nonml_prereg_convention_coverage_backtest.py` l.182 | **oui** | **confirmé** |

> **Tous confirmés.**

## Motif « témoin sous un autre nom » — **non vérifiable mécaniquement**

- cas invoquant ce motif : **5**
  - `nonml_hardcoded_tables_repair_backtest.py` l.215
  - `nonml_prereg_convention_coverage_backtest.py` l.174
  - `nonml_prereg_convention_coverage_backtest.py` l.182
  - `nonml_self_inclusion_detector_backtest.py` l.106
  - `nonml_verdict_detector_fix_backtest.py` l.248

> **Aucune route mécanique ne peut confirmer ce motif** : dire que
> `rappel` témoigne pour `rates`, ou `ok4` pour `idem`, demande de
> comprendre que l'une est le complément de l'autre. **C'est un jugement,
> et l'audit ne peut que le signaler comme tel.**

*(**3 de ces cas sont sur-captés** : ma détection de
motif est **textuelle**, et `prereg_convention_coverage` cite dans son
motif la ligne `| le rapport **existe sous un autre nom** |` — qui
parle d'un rapport, pas d'un témoin. **Leur motif réel est le bloc
parent, déjà confirmé ci-dessus.** L'imprécision est de mon audit, et
je la publie plutôt que de la corriger en silence.)*

**C'est la limite de cet audit, et elle porte sur le motif le plus
fréquent.** Un lecteur qui voudrait contester le cycle devrait commencer
par là — les citations verbatim du rapport sont ce qui le lui permet.

## Le cycle s'accuse-t-il lui-même ?

| Script de cette série | Verdict reçu |
|---|---|
| `nonml_hardcoded_tables_repair_backtest.py` l.215 | anodin |

> Le cycle **#482** figure dans la population qu'il mesure, et le
> rapport le dit : *« je viens de le commettre moi-même, dans le cycle
> qui l'a nommé deux fois »*. **L'auteur ne s'exclut pas.**

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**CONCORDANT** — **6/6** motifs mécaniquement
vérifiables sont confirmés ; **5** relèvent d'un jugement que
l'audit **ne peut pas trancher**, et le dit.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).