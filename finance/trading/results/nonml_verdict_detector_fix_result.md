# Le détecteur de verdict — « porter » contre « mentionner » (pré-enregistré)

**Cycle de MODIFICATION**, troisième après les #445 et #446.

## La règle changée

Avant : `"**PASS" in t` — **n'importe où** dans le texte.
Après : le verdict se lit sur une **ligne qui commence** par le marqueur.

Précédence (PASS l'emporte) et littéral `"PASS (niveau 1)"` **inchangés** :
un seul changement à la fois, sans quoi l'effet ne serait pas attribuable.

La règle est écrite **en clair aux deux endroits** plutôt que factorisée dans
une fonction commune. Ce n'est pas un choix de style : une fonction aurait été
un ajout **hors des deux occurrences annoncées**, et le critère 1 en faisait un
échec. J'ai d'abord écrit la version factorisée, constaté qu'elle violait mon
propre régime, et **me suis conformé au critère plutôt que de le réinterpréter**.

## Critère 1 — diff confiné aux occurrences annoncées

- hunks : **3** — départs : 156, 158, 206
- occurrences annoncées : 156, 158, 206
- **confiné : OUI**

## Critère 2 — l'effet, avec la preuve de chaque reclassement

Rapports examinés (scripts non-ML sans `.npz`) : **115**

| Verdict | Avant | Après | Δ |
|---|---|---|---|
| PASS | 5 | 1 | **-4** |
| FAIL | 91 | 90 | **-1** |
| indéterminé | 17 | 22 | **+5** |
| sans rapport | 2 | 2 | **+0** |

**5** rapports changent de classe.

| Rapport | Avant | Après | Ligne qui décide (règle nouvelle) |
|---|---|---|---|
| `capitulation_gate_floor_sweep` | PASS | **indéterminé** | `— aucune ligne ne commence par un marqueur —` |
| `npz_report_consistency_baskets` | PASS | **indéterminé** | `— aucune ligne ne commence par un marqueur —` |
| `protocol_inventory` | PASS | **indéterminé** | `— aucune ligne ne commence par un marqueur —` |
| `sweep_pass_prose_fix` | PASS | **indéterminé** | `— aucune ligne ne commence par un marqueur —` |
| `third_npz_schema_handling` | FAIL | **indéterminé** | `— aucune ligne ne commence par un marqueur —` |

**Aucun reclassement sans sa preuve** : la ligne citée est celle que la règle
nouvelle lit — ou la mention de son absence.

### La prédiction du pré-enregistrement

La règle étant **strictement plus stricte**, les PASS ne pouvaient que baisser
et les indéterminés que monter. Un mouvement inverse aurait signalé un défaut
de ma mise en œuvre.

- PASS baisse ou stable : **OUI**
- indéterminé monte ou stable : **OUI**

## Critère 3 — relecture de contrôle

Les reclassés sont **5** (≤ 15) : **tous** sont relus, comme le
pré-enregistrement l'exigeait. On cherche si le rapport **porte vraiment** le
verdict que la règle nouvelle lui refuse — y compris énoncé dans un titre.

| Rapport | Avant | Après (règle) | Verdict réellement porté | Contredit ? |
|---|---|---|---|---|
| `capitulation_gate_floor_sweep` | PASS | indéterminé | **aucun** | non |
| `npz_report_consistency_baskets` | PASS | indéterminé | **aucun** | non |
| `protocol_inventory` | PASS | indéterminé | **aucun** | non |
| `sweep_pass_prose_fix` | PASS | indéterminé | FAIL | **OUI** |
| `third_npz_schema_handling` | FAIL | indéterminé | FAIL | **OUI** |

**2 relectures contredisent la règle nouvelle.**

La contrepartie annoncée au pré-enregistrement s'est produite, et elle est
plus grave qu'un cas de figure théorique : deux rapports **portent un FAIL
énoncé dans un titre** (`## Verdict : **FAIL**`, `### **FAIL**`) et la règle
nouvelle les déclare *indéterminés*.

Le bilan honnête de la règle nouvelle est donc **mixte** :

- elle **corrige** 3 faux positifs — des rapports
  d'inventaire qui ne portaient aucun verdict et étaient comptés PASS ;
- elle **introduit** 2 faux négatifs — des verdicts réels, énoncés
  en titre, qu'elle ne voit plus.

**Je ne la corrige pas ici.** L'engagement 4 du pré-enregistrement était
explicite : *aucun ajustement de la règle après avoir vu les comptes*. La
règle qui reconnaîtrait aussi les titres est évidente à écrire — et c'est
précisément pourquoi il faut la déclarer avant, dans son propre cycle,
plutôt que la glisser ici en la faisant passer pour la même.

## Critère 4 — idempotence avec auto-inclusion

Mesure refaite **après** écriture du rapport de ce cycle (leçon du #446) :

| Verdict | Avant auto-inclusion | Après |
|---|---|---|
| PASS | 1 | 2 |
| FAIL | 90 | 90 |
| indéterminé | 22 | 22 |
| sans rapport | 2 | 1 |

**NON identiques.**

### Ce n'est pas un défaut de la correction — c'est structurel

Le balayage compte les **scripts sans `.npz`**. Ce cycle en ajoute un, plus
son rapport : le vivier mesuré grandit d'une unité **du seul fait de la
mesure**.

> **Un rapport qui compte les rapports ne peut pas être idempotent, puisqu'il
> en est un.**

Le #446 avait rencontré le même mur et l'avait imputé au détecteur. La
correction du détecteur faite, le mur est toujours là : il ne venait donc pas
du détecteur. C'est un acquis du cycle, obtenu en échouant.

J'avais posé ce critère en croyant qu'il mesurait la stabilité de la règle ;
il mesurait en réalité une propriété du dispositif. **Le critère était mal
conçu**, et je le dis plutôt que de le réécrire après coup.

### Le défaut résiduel se démontre sur ce rapport même

Le tableau ci-dessus classe ce cycle **PASS**. Or son verdict est **FAIL**.

La cause n'est pas la règle nouvelle mais le **littéral historique**
`"PASS (niveau 1)"`, laissé intact par décision explicite (*un seul
changement à la fois*). Il est comparé **en sous-chaîne, n'importe où** — et
ce rapport contient la phrase qui *décrit* ce littéral. Il est donc compté
PASS **parce qu'il parle du détecteur**.

C'est exactement le défaut corrigé aux deux autres endroits, subsistant là
où je ne l'ai pas touché. Le choix de ne changer qu'une chose à la fois a
**isolé** le défaut résiduel au lieu de le masquer : il est maintenant
visible, nommé, et démontré par un cas réel plutôt que supposé.

**À traiter dans le cycle qui reprendra la règle**, avec les verdicts en
titre. Pas ici.

## Verdict

| | Critère | État |
|---|---|---|
| 1 | diff confiné aux occurrences annoncées | ✔ |
| 2 | chaque reclassement publié avec sa preuve | ✔ |
| 3 | aucune relecture ne contredit | **NON** |
| 4 | comptes idempotents | **NON** |

### **FAIL**

Deux critères sur quatre échouent, pour des raisons **différentes** :

- le **critère 3** échoue sur le fond : la règle nouvelle rate les verdicts
  énoncés en titre. Elle est meilleure que l'ancienne sans être juste.
- le **critère 4** échoue parce qu'il était **mal conçu** : il exigeait
  l'idempotence d'un rapport qui se compte lui-même.

**Le détecteur reste néanmoins amélioré** — 3 faux positifs corrigés contre
2 faux négatifs introduits — mais le cycle ne se déclare pas PASS pour
autant. La correction complète est inscrite à la file, à déclarer avant.
