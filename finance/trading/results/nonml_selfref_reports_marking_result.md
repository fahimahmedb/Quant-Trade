# Rapports dépendants du dépôt — signalés, non appauvris (pré-enregistré)

Cycle de **modification déclarée**, régime des #428-#430. Aucune stratégie
évaluée, aucun verdict recalculé, aucun paramètre de stratégie touché.

## Pourquoi signaler plutôt que stabiliser

Le #438 avait inscrit « rendre stables » ces rapports, en invoquant un
dénominateur de borne amputé. **Le calcul ne le justifie pas** :

- candidats dépendants du dépôt : **10**
- vivier : **291** → **3.4 %**
- perte moyenne sur un tirage de 24 : **0.8** tirage

« Rendre stable » signifierait **supprimer** de ces rapports les décomptes du
dépôt — exactement l'information que le #428 y avait ajoutée à dessein pour
empêcher un lecteur de surestimer la portée du balayage. J'appauvrirais un
diagnostic pour récupérer moins d'un tirage sur vingt-quatre.

**Un diagnostic qui décrit l'état du dépôt doit changer quand le dépôt change.**
Sa divergence est son fonctionnement ; le défaut serait qu'un lecteur la prenne
pour une péremption. D'où un marqueur, et non une amputation.

## Deux défauts de ce cycle, rencontrés en l'exécutant

### 1. Interférence de sentinelles

Une première exécution a dû être **interrompue**. Un candidat manipule lui-même
des fichiers portant **les mêmes noms de sentinelles** : lancé comme candidat, il
supprimait les miennes dans son propre `finally`, **vidant le test de son sens**.

- candidats **écartés pour interférence** : **1**

- `reproducibility_campaign_v3`

La raison est **mécanique et connaissable sans voir aucun résultat** — elle se lit
dans le code du candidat, pas dans son verdict.

### 2. Processus orphelins survivant au délai

Plus grave, et découvert en inspectant l'arbre après coup : `subprocess.run`
avec `timeout` ne tuait que l'**enfant direct**. Les candidats qui relancent
eux-mêmes des backtests laissaient des **petits-enfants orphelins** qui ont
continué de tourner et **réécrit un rapport après sa restauration** —
`nonml_reproducibility_sample_result.md` a été retrouvé modifié alors qu'il
n'était pas marqué.

Les orphelins ont été tués et le rapport restauré. Le script exécute désormais
chaque candidat dans un **groupe de processus isolé**, tué entier au délai.
**La garantie « aucun rapport publié modifié » ne tenait pas à ce moment-là**, et
je l'écris plutôt que de la présenter comme acquise depuis le début.

## Test comportemental — ce qui déclenche le marquage

Le #437 a échoué en identifiant ces scripts par la **forme de leur code**. Ici
chaque candidat est **testé** : exécution, sauvegarde, ajout de fichiers
sentinelles neutres, ré-exécution, comparaison.

| | Nombre |
|---|---|
| candidats repérés par la syntaxe | **10** |
| **confirmés** par le test | **6** |
| **infirmés** (faux positifs syntaxiques) | **1** |
| indéterminés | **3** |

### Infirmés — repérés par la syntaxe, mais le test les disculpe

| Script | Raison |
|---|---|
| `sameday_timestamp_resolution` | le rapport ne dépend pas du contenu du dépôt |

**Ils ne sont pas marqués.** Le test prime sur la syntaxe, comme le
pré-enregistrement l'exigeait.

### Indéterminés

| Script | Raison |
|---|---|
| `reproducibility_sample` | délai > 300 s |
| `reproducibility_sample_lot2` | délai > 300 s |
| `reproducibility_sample_lot3` | délai > 300 s |

Non marqués : le doute ne suffit pas à justifier une modification.

## Marquage

- rapports **marqués** par ce cycle : **0**
- déjà porteurs du marqueur : **6**

Texte ajouté, **fixé au pré-enregistrement** :

```
> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).
```

## Contrôle des sentinelles

- sentinelles subsistantes : **0** ✔
