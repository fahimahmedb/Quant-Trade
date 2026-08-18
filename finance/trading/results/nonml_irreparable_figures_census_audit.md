# Audit adversarial — le recensement des irréparables (#485)

**Un verdict « irréparable » est le plus commode qui soit** : il ferme une
dette sans travail. L'audit ne recompte donc pas — **il teste chaque
irréparable** par une route propre.

- verdicts relus dans le rapport : **17** (**5** irréparables, **12** réparables)

## Chaque irréparable — la grandeur est-elle hors de portée ?

Route indépendante : l'**AST** énumère les noms liés et les appels du
module. Un script qui n'importe rien du dépôt et n'énumère aucun corpus
hors de sa propre liste ne peut pas reconstruire un univers historique.

| Irréparable | Imports du dépôt | Énumère `results/` | Constantes en dur |
|---|---|---|---|
| `nonml_marker_emitted_by_scripts_backtest.py` | **aucun** | **non** | oui |
| `nonml_pnl_duplicate_sweep_audit.py` | **aucun** | oui | non |
| `nonml_pnl_persistence_exposed_pass_audit.py` | **aucun** | **non** | oui |
| `nonml_protocol_inventory_audit.py` | **aucun** | **non** | non |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | **aucun** | **non** | oui |

- irréparabilités **fondées** par cette route : **4 / 5**

> **1 irréparabilité(s) non fondée(s)** par cette
> route — publié tel quel, le verdict à la main peut rester juste pour
> une raison que l'AST ne voit pas, mais **le doute est inscrit**.

## Le cycle s'épargne-t-il ?

| Script de cette série | Verdict reçu |
|---|---|
| `nonml_orphans_interrupted_or_lost_backtest.py` | réparable |

> **Le cycle se donne le verdict le plus exigeant.** Classer son propre
> défaut « réparable » **maintient la dette ouverte contre soi** ;
> l'inverse l'aurait close gratuitement. Le rapport écrit *« rien ne
> l'excuse »*.

## Le proxy est-il vraiment sans pouvoir de séparation ?

Le rapport affirme que son proxy répond « oui » partout. **Contrôle sur un
échantillon témoin** : le même motif appliqué à des scripts **hors** de la
population des défauts.

- scripts témoins testés : **40**
- dont le proxy répond « oui » : **40**

> **Le proxy répond « oui » à 100 % des témoins aussi.** Il ne sépare
> donc rien, nulle part — **l'aveu du rapport est vérifié, pas cru**.
> Un motif qui teste `for … in` ou `len(…)` teste que le fichier est
> du Python.

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**RÉSERVES** — **4/5** irréparabilités fondées par une route
indépendante, et l'inutilité déclarée du proxy **vérifiée sur un
échantillon témoin**.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).