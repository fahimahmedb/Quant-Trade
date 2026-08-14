# Les trois écarts silencieux du #444 : mesurer avant de décider (pré-enregistré)

**Cycle de décision.** Il pouvait se conclure par « on ne touche à rien » ;
la règle était fixée **avant** toute mesure.

## Ce que le #444 disait, et qu'il faut rappeler

Ces trois consommateurs **n'ont pas de défaut** : leur résultat reste juste.
Ils écartent le troisième schéma `.npz` sans le signaler — une **lacune de
couverture**. Un silence n'induit en erreur que si le rapport **affirme** une
couverture que ce silence contredit.

## Combien de fichiers sont écartés ?

`.npz` du **troisième schéma** (ni `pos`, ni clés de panier) : **2**

- `nonml_dollar_neutral_composite_pit_pnl.npz`
- `nonml_dollar_neutral_composite_vol_targeted_pnl.npz`

## Chaque rapport revendique-t-il une couverture ?

| Script | Ligne qui écarte | Revendique | Ligne citée | Décision |
|---|---|---|---|---|
| `nonml_empty_pass_requalification_backtest.py` | `if "pos" not in d.files or "r_asset" not in d.files: continue` | non | — aucune — | ne rien changer |
| `nonml_pnl_persistence_lot5_audit.py` | `if "pos" not in p.files: continue` | non | — aucune — | ne rien changer |
| `nonml_npz_report_consistency_backtest.py` | compte ces fichiers sous l'étiquette **fausse** « schéma panier » | non | — aucune — | ne rien changer (compte rendu d'un cycle passé) |

## La décision

Règle fixée avant mesure : *rendre l'écart visible si et seulement si*
`n_skip > 0` **et** *le rapport revendique une couverture que ce silence
contredit*.

### **Décision : on ne touche à rien.**

Aucun des trois rapports ne revendique une couverture exhaustive des
fichiers. Leur silence ne trompe donc personne : ils parlent de
**candidats**, pas de l'inventaire des `.npz` du dépôt.

**C'est la conclusion d'un cycle, pas son échec.** Un cycle qui mesure et
conclut qu'il n'y a rien à faire vaut mieux qu'un cycle qui modifie pour
justifier son existence — et la dette inscrite depuis le #444 se ferme
ici, par une mesure plutôt que par un abandon.

**Prédiction vérifiée** : je l'annonçais, en n'excluant pas l'inverse.

## La provision déclarée d'avance, et son application

`nonml_npz_report_consistency_backtest.py` produit le **compte rendu du
#442**. Le pré-enregistrement prévoyait de **ne pas y toucher**, quelle que
soit la mesure : le régénérer ferait re-raconter ce cycle avec un état du
dépôt qu'il n'a pas connu.

**Appliqué.** Le #449 avait rencontré ce cas de figure **sans l'avoir prévu**
et avait dû publier une entorse ; ici la provision était écrite avant, et il
n'y a pas d'entorse à signaler. C'est le seul progrès de méthode de ce cycle,
et il est mince.

## Ce que ce cycle ne permet pas de conclure

- Il ne dit **pas** que ces scripts couvrent tout le dépôt : ils n'en couvrent
  pas les **2** fichiers du troisième schéma. Il dit que **leur
  rapport ne prétend pas le contraire**.
- Il ne **recalcule** aucun verdict et ne régénère aucun rapport.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).