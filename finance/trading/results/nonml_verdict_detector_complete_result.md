# La règle complète du détecteur de verdict (pré-enregistré)

**Cycle de MODIFICATION**, quatrième après les #445, #446 et #447.

## Ce qui change

Deux changements, tous deux déclarés **avant** d'écrire le code :

1. la **décoration Markdown** (titre, citation, puce, étiquette « Verdict : »)
   est retirée avant lecture — *un verdict énoncé en titre est un verdict* ;
2. le littéral `"PASS (niveau 1)"` devient **positionnel** comme le reste.

Précédence (PASS l'emporte) **inchangée**.

## Critère 1 — diff confiné aux deux régions annoncées

- hunks : **4**
  - `-52,0 +53,50`
  - `-164,2 +214`
  - `-167 +216`
  - `-216,2 +265`

Un hunk pour la fonction insérée avant `main()` (région **a**), les autres aux
deux occurrences remplacées par un appel (région **b**).

> **La règle est écrite en opérations de chaînes, sans `re`.** Le
> pré-enregistrement la montrait sous forme d'expressions régulières ; un
> `import re` en tête de fichier aurait ouvert une **troisième région**, non
> déclarée. Comme au #447, je me suis **conformé au régime plutôt que de le
> réinterpréter**. L'équivalence des deux écritures est vérifiée par l'audit,
> ligne à ligne, sur tous les rapports du dépôt — elle est **contrôlée, pas
> affirmée**.

## Critère 4 — les deux faux négatifs du #447 sont-ils récupérés ?

C'est la raison d'être du cycle. Le pré-enregistrement le disait : *s'ils ne
sont pas récupérés, il a échoué.*

| Rapport | Verdict réel | #447 | #448 |
|---|---|---|---|
| `third_npz_schema_handling` | FAIL | indéterminé | **FAIL** |
| `sweep_pass_prose_fix` | FAIL | indéterminé | **FAIL** |

**Récupérés.**

## Critère 2 — l'effet complet, avec la preuve de chaque reclassement

Rapports examinés (scripts non-ML sans `.npz`, rapport présent) : **114**

| Verdict | #447 | #448 | Δ |
|---|---|---|---|
| PASS | 2 | 1 | **-1** |
| FAIL | 90 | 93 | **+3** |
| indéterminé | 22 | 20 | **-2** |

**3** rapports changent de classe.

| Rapport | #447 | #448 | Ligne qui décide |
|---|---|---|---|
| `sweep_pass_prose_fix` | indéterminé | **FAIL** | `### **FAIL**` |
| `third_npz_schema_handling` | indéterminé | **FAIL** | `## Verdict : **FAIL**` |
| `verdict_detector_fix` | PASS | **FAIL** | `### **FAIL**` |

## Critère 3 — relecture de contrôle

Les reclassés sont **3** (≤ 15) : **tous** sont relus. La méthode
est volontairement **différente** de la règle testée — on localise le dernier
bloc « Verdict » du rapport et on lit ce qu'il annonce. Un contrôle qui
réappliquerait la règle ne contrôlerait rien.

| Rapport | Classé #448 | Verdict lu dans son bloc « Verdict » | Contredit ? |
|---|---|---|---|
| `sweep_pass_prose_fix` | FAIL | FAIL | non |
| `third_npz_schema_handling` | FAIL | FAIL | non |
| `verdict_detector_fix` | FAIL | FAIL | non |

**Contredits : 0.**

## Critère 5 — le défaut résiduel a-t-il disparu ?

Le #447 classait son propre rapport **PASS** alors que son verdict était FAIL,
parce qu'il **citait** le littéral `"PASS (niveau 1)"`. Le test se refait ici
sur ce rapport-ci, qui cite le même littéral.

- ce rapport cite le littéral : **oui**
- ce rapport est classé : **indéterminé**

La preuve la plus directe est ailleurs, dans le tableau des reclassés :
`verdict_detector_fix` — le rapport du #447 — passe de **PASS** à **FAIL**,
c'est-à-dire de la classe que le littéral lui imposait à celle qu'il porte
réellement. **Le défaut résiduel est corrigé, et il est corrigé sur le cas même
qui l'avait révélé.**

## Verdict

| | Critère | État |
|---|---|---|
| 1 | diff confiné aux deux régions annoncées | ✔ |
| 2 | chaque reclassement publié avec sa preuve | ✔ |
| 3 | aucune relecture ne contredit | ✔ |
| 4 | les 2 faux négatifs du #447 récupérés | ✔ |
| 5 | défaut résiduel disparu | ✔ |

### **PASS**

Le détecteur lit désormais le verdict qu'un rapport **porte**, qu'il soit
énoncé en tête de ligne ou en titre, et ne le lit plus dans les phrases qui
**parlent** d'un verdict.

**Ce n'est pas un résultat de stratégie.** Aucun edge n'est démontré : c'est
un instrument de comptage remis d'aplomb, après trois cycles où il a été
faux de trois façons différentes.

**Ce qui reste faux** : les **8 autres scripts** portant l'ancien motif
`"**PASS" in` ne sont **pas** touchés. Ce cycle n'a corrigé qu'un
consommateur, comme le #447 avant lui.
