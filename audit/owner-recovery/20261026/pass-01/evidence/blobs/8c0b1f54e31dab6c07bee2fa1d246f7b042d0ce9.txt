# Q14 — grille de triage adverse du rapport Astra lot 3

Date : 2026-10-08. Statut : `REVIEW_CHECKLIST_ONLY`. Objet : contrôler le rapport Astra dès sa publication sans refaire passer une conclusion narrative avant les preuves.

## A. Porte d’entrée

Noter le commit, le chemin et le blob complets du rapport ; vérifier l’indépendance annoncée, l’ancestry, les objets examinés et les sorties reproductibles. Si le rapport ou une référence obligatoire manque/diverge, classer `BLOCKED_INCOMPLETE_EVIDENCE` et arrêter tout triage positif. Aucun remède proposé par l’équipe ne modifie le rapport Astra original.

## B. Grille par constat

Pour chaque constat Astra, remplir une ligne :

`ID | sévérité Astra | objet exact | observation falsifiable | commande/preuve reproduite | résultat | impact sécurité/chaîne de garde | portée | remède minimal | propriétaire | preuve de fermeture exigée | nouvelle revue requise`

Appliquer les questions adverses suivantes :

1. Le constat est-il attaché à des octets exacts plutôt qu’à un nom de branche ?
2. La reproduction démontre-t-elle l’assertion, avec code retour et sortie, ou seulement l’absence d’échec ?
3. Un test synthétique est-il présenté à tort comme preuve sur configuration réelle, VM ou lot 4 ?
4. Le défaut peut-il produire un faux `LINKED`, `VALID`, `PERMIT`, `AUTHORIZED` ou une libération fail-open ?
5. Le remède ferme-t-il la cause racine sans élargir l’autorité ni changer silencieusement un objet gelé ?
6. La fermeture exige-t-elle correction, nouvelle preuve locale, requalification VM, nouvelle Astra, ou décision distincte ?

## C. Classes de triage

- `T0_BLOCKING_SAFETY_OR_AUTHORITY` : fail-open, faux permissif, substitution/identité, contenu gardé incomplet, chargement interdit, autorité indue. Action : arrêt ; correction bornée ; preuves neuves ; nouvelle revue indépendante.
- `T1_BLOCKING_EVIDENCE` : objet/référence/sortie/environnement requis absent ou non reproductible. Action : fournir l’objet manquant sans substitution ; reprendre Astra.
- `T2_NON_BLOCKING_BUT_REQUIRED_BEFORE_LOT4` : écart réel borné qui n’invalide pas le candidat mais conditionne VM, B.5 ou activation. Action : propriétaire et preuve de fermeture avant lot 4.
- `T3_NON_BLOCKING_JUSTIFIED` : écart reproduit, impact nul démontré et justification suffisante. Action : conserver la trace ; aucun crédit au-delà de la portée prouvée.
- `T4_EDITORIAL` : forme uniquement, sans effet sur reproductibilité, identité, garde ou verdict. Action : erratum traçable, sans réécrire l’historique.

En cas d’incertitude entre deux classes, retenir la plus restrictive. Une recommandation de remède n’est jamais une autorisation de l’exécuter.

## D. Contrôles obligatoires transversaux

| Axe | Test adverse | Condition acceptable |
|---|---|---|
| Inventaire | commits, chemins, blobs, arbres, base `276fd99`, candidat `73280c3…` | tous résolus et concordants |
| Baseline | 279 anciens tests | 276 PASS + exactement 3 écarts attendus, aucun autre |
| Nouveaux tests | 27 tests et 22 évaluations root réelle | 27 PASS ; 22 refus ; 0 PERMIT/AUTHORIZED |
| `validate_binding` réel | appel signalé en Q7 §7.2 | portée explicitement bornée : validation structurale seule, ni évaluation permissive, ni activation ; sinon T0/T1 |
| D2 | input, output, policy, root | liaisons exactes et fail-closed |
| Garde | tableau canonique | exactement 15 entrées, chacune sourcée et testée ; 14/16 = blocage |
| Statut structurel | valeurs hors domaine/absence/type faux | toujours refusées ; aucune coercition |
| Provenance | `1910994` autre session | octets et effet sur chaîne de garde classés avec preuve |
| Environnement | Python 3.13 local vs 3.12 initial | conclusions séparées ; aucune équivalence présumée |
| VM | L2-A non faite | reste non qualifiée ; aucune preuve locale substituée |
| Lot 4 | permissif sur configuration réelle | non exécuté, non anticipé |
| E B.5 | chaque condition et autorité propre | aucune satisfaction par présomption |

## E. Règles sur remèdes et écarts

Pour chaque remède, exiger : cause racine, changement minimal, fichiers autorisés, test régressif qui échoue avant/réussit après, objets à regeler, preuves invalidées, réviseur indépendant et critère de sortie. Refuser les remèdes qui assouplissent le test, changent l’attendu pour suivre le résultat, substituent un objet synthétique, ou regroupent plusieurs autorités.

Tenir séparément les trois écarts connus : auteur de `1910994`, VM non qualifiée, Python 3.13/3.12. Ajouter tout nouvel écart ; ne jamais compenser un écart par un succès ailleurs. Qualifier chacun `FERMÉ_PAR_PREUVE`, `OUVERT_NON_BLOQUANT`, `OUVERT_BLOQUANT` ou `NON_ÉVALUABLE`, avec propriétaire et prochaine preuve.

## F. Sortie du triage

Émettre une seule recommandation : `ACCEPT_REPORT_FOR_OWNER_LOT4_CONSIDERATION`, `RETURN_FOR_CORRECTION_AND_REVIEW`, ou `BLOCKED_PENDING_EXACT_EVIDENCE`. `ACCEPT_REPORT_FOR_OWNER_LOT4_CONSIDERATION` exige le verdict Astra correspondant, zéro T0/T1 ouvert, et une liste explicite de tous les T2 et écarts résiduels ; il ne vaut ni PASS lot 4 ni activation.

```text
VM_QUALIFIED = FALSE_UNLESS_SEPARATELY_PROVEN_BY_OWNER
REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4
E_EFFECTIVE = FALSE
A2_EXECUTION_AUTHORIZED_BY_TRIAGE = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED_BY_TRIAGE = FALSE
QUARANTINE_LIFTED_BY_TRIAGE = FALSE
ECONOMIC_AUTHORITY = 0
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
