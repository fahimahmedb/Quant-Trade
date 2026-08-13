# La phrase figée du balayage — remplacée par une énumération calculée (pré-enregistré)

**Cycle de MODIFICATION**, second après le #445, même discipline : régime
annoncé ligne à ligne, effet déclaré, critère qui peut échouer.

## Le résultat qui prime sur la correction de prose

Le pré-enregistrement annonçait : *si l'un de ces PASS est une **stratégie**
et non un script d'inventaire, cela signifierait que des candidats PASS ne
sont pas contrôlés contre les doublons, et serait publié en tête.*

**C'est le cas de 1 sur 4 :**

- **`tom_decomposition_overlay`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**

`tom_decomposition_overlay` est une décomposition du turn-of-month dont la
**variante A (fin de mois seule) est PASS**. Or le #8 (ToM complet) est PASS
lui aussi et **possède** son `.npz`. Si les deux séries étaient très proches,
le décompte d'hypothèses indépendantes serait gonflé — c'est précisément ce
que le balayage existe pour détecter, et il ne peut pas le faire ici.

**Ce cycle ne le résout pas** : produire un `.npz` pour cette stratégie est
une modification hors du bloc annoncé. **Inscrit en tête de file.**

**Ma prédiction est donc partiellement réfutée.** J'attendais que les
nouveaux venus soient des scripts d'inventaire ; trois le sont, un ne l'est
pas. C'est la prédiction qui avait tort, pas la mesure.

## Le défaut corrigé

Le rapport publiait :

> **4** PASS sont **les deux** candidats écartés au #427 avec leur raison publiée

Le compte était **calculé**, la prose **figée**. La phrase était fausse deux
fois : le nombre ne concordait pas, et l'**identité** affirmée ne pouvait pas
couvrir des scripts apparus depuis. Même genre de défaut que le `284 − 208` du
#428 — une affirmation non mesurée enchâssée dans une phrase d'allure factuelle.

Le bloc **nomme désormais ce qu'il compte**, et ne peut plus se périmer.

## Critère 1 — le diff est-il confiné au bloc annoncé ?

- insertions : **23** — suppressions : **2**
- hunks du diff : **1**
  - `-194,2 +194,23`

Les 2 lignes annoncées (194-195) sont remplacées ; l'énumération est insérée à
leur place. **Un seul hunk** : aucune autre partie du balayage n'est touchée.

Le calcul des noms est fait **dans le bloc lui-même**, et non dans la boucle de
comptage : y toucher aurait été sortir de l'intervalle annoncé. C'est un peu
redondant, et c'est le prix du régime déclaré.

## Critère 3 — idempotence

Le balayage est exécuté **deux fois de suite** et les deux rapports comparés
octet par octet.

**Identiques : OUI.** Une phrase calculée qui
varierait d'une exécution à l'autre n'aurait rien réglé.

## Critère 4 — attribution de chaque différence

- lignes avant : **92** — après : **99**
- lignes réellement ajoutées ou retirées : **21** — dont **11** au bloc, **10** à la dérive du dépôt

| Sens | Cause | Ligne |
|---|---|---|
| retirée | dérive | `| scripts de backtest non-ML du dépôt | **298** |` |
| retirée | dérive | `| **couverture non-ML** | **69.8 %** |` |
| ajoutée | dérive | `| scripts de backtest non-ML du dépôt | **299** |` |
| ajoutée | dérive | `| **couverture non-ML** | **69.6 %** |` |
| retirée | dérive | `**La soustraction 298 − 208 ne compte rien de réel** : les deux` |
| ajoutée | dérive | `**La soustraction 299 − 208 ne compte rien de réel** : les deux` |
| retirée | dérive | `> **113** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
| ajoutée | dérive | `> **114** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
| retirée | dérive | `| sans rapport | **1** |` |
| ajoutée | dérive | `| sans rapport | **2** |` |
| retirée | **bloc** | `**4** PASS sont les deux candidats écartés au #427 avec leur raison` |
| retirée | **bloc** | `publiée (variantes multiples, et un diagnostic qui n'est pas une stratégie).` |
| ajoutée | **bloc** | `Les **4** PASS sans `.npz` sont nommés ici plutôt` |
| ajoutée | **bloc** | `qu'affirmés — la version précédente les disait « les deux candidats écartés` |
| ajoutée | **bloc** | `au #427 », phrase figée qu'un compte calculé a fini par démentir (#446) :` |
| ajoutée | **bloc** | `` |
| ajoutée | **bloc** | `- `capitulation_gate_floor_sweep`` |
| ajoutée | **bloc** | `- `npz_report_consistency_baskets`` |
| ajoutée | **bloc** | `- `protocol_inventory`` |
| ajoutée | **bloc** | `- `tom_decomposition_overlay`` |
| ajoutée | **bloc** | `` |

**Instrument corrigé avant publication** : la première version comparait les
rapports **par position**. Le bloc insérant des lignes, tout ce qui suivait
était décalé et compté comme « dérive » — 44 fausses divergences. Un vrai
diff (`SequenceMatcher`) ne compte que les lignes réellement ajoutées ou
retirées.

**Et corrigé une seconde fois** : l'attribution se faisait ligne à ligne, si
bien que les noms insérés et les lignes vides du bloc — qui ne portent aucun
mot-clé — tombaient en « dérive ». L'attribution se fait désormais par
**groupe de diff contigu**, ce qui est la bonne unité : un remplacement est
un bloc, pas une collection de lignes indépendantes.

Au #445, 9 des 10 lignes modifiées n'étaient pas de moi. Le contrôle est
reconduit pour la même raison : sans lui, l'effet réel se lit mal.

## Les noms désormais publiés

**4** scripts nommés par la phrase nouvelle :

- `capitulation_gate_floor_sweep`
- `npz_report_consistency_baskets`
- `protocol_inventory`
- `tom_decomposition_overlay`

Chacun est **vérifié indépendamment** dans
`nonml_sweep_pass_prose_fix_audit.md` (critère 2) : le verdict de ce cycle ne
peut pas s'auto-attester.

## Idempotence réelle — le piège de l'auto-inclusion

Le test ci-dessus est **trop faible** : ses deux exécutions ont eu lieu **avant**
que le rapport de ce cycle n'existe. Or ce rapport rejoint le vivier que le
balayage mesure — c'est le piège d'auto-inclusion des #434 et #438.

Mesure refaite **après** écriture du rapport de ce cycle :

- noms publiés avant auto-inclusion : **4** — `capitulation_gate_floor_sweep`, `npz_report_consistency_baskets`, `protocol_inventory`, `tom_decomposition_overlay`
- noms publiés après : **5** — `capitulation_gate_floor_sweep`, `npz_report_consistency_baskets`, `protocol_inventory`, `sweep_pass_prose_fix`, `tom_decomposition_overlay`

**NON stable.** Le rapport de ce cycle s'ajoute lui-même à la liste : `sweep_pass_prose_fix`.

### Le défaut que ma propre correction a mis au jour

Ce n'est pas un accident de nommage. Le balayage détecte un PASS par
`"**PASS" in t` — **n'importe où** dans le rapport. Le rapport de ce cycle
contient la phrase « stratégie portant un **PASS** » à propos d'un *autre*
candidat : il est donc compté comme un PASS.

**Le détecteur de verdict du balayage confond « porter un PASS » et
« parler d'un PASS ».** Tout rapport d'inventaire qui commente un PASS est
compté comme candidat PASS.

La correction de prose de ce cycle est correcte ; elle a rendu **visible**
un défaut plus profond, en nommant ce qui n'était jusque-là qu'un compte.
C'est l'argument même du cycle : nommer ce qu'on compte.

**Non corrigé ici** — hors du bloc annoncé. **Inscrit en tête de file.**

## Verdict

| | Critère | État |
|---|---|---|
| 1 | diff confiné au bloc annoncé | ✔ |
| 2 | chaque nom vérifié indépendamment | voir `..._audit.md` |
| 3 | rapport idempotent | **NON** |
| 4 | chaque différence attribuée | ✔ (après deux corrections d'instrument) |

### **FAIL**

Le critère 3 n'est **pas** tenu : le rapport n'est pas idempotent une fois
le rapport de ce cycle versé au vivier. Le pré-enregistrement en faisait un
critère d'échec, et il l'est.

**La correction de prose, elle, fonctionne** — mais un cycle ne se juge pas
sur la partie qui marche. Le FAIL est publié tel quel, et ce qu'il a révélé
vaut mieux qu'un PASS : le détecteur de verdict du balayage est faux depuis
le début, et personne ne l'avait vu parce que rien ne nommait ce qu'il
comptait.
