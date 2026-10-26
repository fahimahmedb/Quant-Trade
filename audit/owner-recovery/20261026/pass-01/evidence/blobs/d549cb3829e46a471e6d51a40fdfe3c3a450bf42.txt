# Projet Q13 — domaine fermé de `structural_linkage_status` et contenu sous garde — route D1 future

Date : 2026-10-08. Statut : `DRAFT_ONLY_NO_EFFECT`. Ce texte prépare Q10 ; il n’exprime aucune décision d’Owner, ne rouvre pas D1 et ne modifie ni D2, ni E, ni la quarantaine.

## A. Références et préconditions

- constat Astra lot 1 : `research/weather_forward/v4/audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_2026-10-07.md` @ `52e5ff2`, notamment §I.1–2 ;
- décision lot 2 et annexe A : `research/weather_forward/v4/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md` @ `276fd99` ;
- E D2 conditionnelle : `research/weather_forward/v4/owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_D2_2026-10-08.md` @ `6e0320f15d48a924cef9507af5641e47de9fe938` ;
- revue Astra lot 3 : `A_REMPLIR_APRES_PUBLICATION` (commit, chemin et blob exacts).

Avant toute décision Q10, recopier depuis le rapport Astra lot 3 sa liste canonique des quinze éléments gardés et résoudre chaque source à son commit, chemin et blob complets. Toute divergence, omission ou référence non résolue maintient `D1_ROUTE_STATUS = CLOSED`.

## B. Domaine fermé proposé

`structural_linkage_status` est obligatoire, sensible à la casse, sans alias ni coercition, et vaut exactement l’un des trois littéraux suivants :

1. `LINKED` — les quinze éléments gardés sont présents une fois chacun, leurs types et valeurs canoniques sont valides, et toutes les liaisons exigées entre input, output, policy et root sont démontrées sur les objets gelés exacts ;
2. `NOT_LINKED` — au moins une contradiction reproductible établit une absence, une substitution, un surnombre, un mismatch d’identité/valeur/type ou une liaison structurelle fausse ;
3. `INDETERMINATE` — aucune contradiction n’est établie, mais au moins une preuve, identité, source, règle de canonicalisation ou liaison requise manque, diverge ou ne peut être reproduite.

Tout champ absent, `null`, booléen, entier, casse différente, valeur inconnue ou valeur future non ratifiée est invalide et se traite comme `INDETERMINATE` au bord de décision, jamais comme `LINKED`. Seul `LINKED` peut satisfaire ce contrôle ; `NOT_LINKED`, `INDETERMINATE` et toute erreur provoquent un refus fail-closed. Le producteur ne peut pas auto-déclarer `LINKED` : le statut résulte du vérificateur sur les octets et règles gelés.

## C. Contenu exact proposé sous garde

L’unité de garde est un enregistrement canonique indivisible contenant exactement quinze entrées, ni plus ni moins. Leur liste normative sera le tableau G du rapport Astra lot 3, après contrôle adverse Q14 et consignation Q10. Pour chaque entrée, Q10 doit figer :

`ordinal | canonical_name | source_commit | source_path | source_blob | field_path | canonical_type | allowed_value_or_closed_domain | normalization_rule | identity_binding | missing_rule | duplicate_rule`

La garde couvre la paire `(nom canonique, valeur canonique)` de chacune des quinze entrées, leur ordre canonique, le nombre `15`, les identités Git des sources, les règles de type/normalisation et les liaisons input–output–policy–root. Elle exclut commentaires, horodatages d’observation, chemins de rapport et métadonnées de présentation, qui ne doivent ni influer sur l’identité gardée ni pouvoir remplacer un élément gardé.

Aucune entrée ne peut être ajoutée, retirée, renommée, réordonnée, normalisée autrement ou sourcée depuis un autre objet sans nouvelle décision Q10 et nouveau gel. Le digest éventuel est calculé seulement après ce gel ; aucun digest n’est proposé ici.

## D. Critères minimaux avant une future route D1

D1 reste fermée sauf si, cumulativement : domaine et quinze entrées ratifiés à des objets exacts ; sérialisation canonique déterministe ; tests négatifs pour chaque valeur hors domaine et pour absence/surnombre/substitution/mismatch ; preuve que seul `LINKED` atteint le bord permissif ; relecture indépendante ; qualification VM distincte ; conditions B.5 de E satisfaites selon leur autorité ; autorité d’activation distincte. Un PASS Astra lot 3 ne décide aucun de ces points.

```text
DOCUMENT_STATUS = DRAFT_ONLY_NO_EFFECT
Q10_OWNER_DECISION_EXPRESSED = FALSE
D1_ROUTE_STATUS = CLOSED
D2_CHANGED = FALSE
E_EFFECTIVE = FALSE
QUARANTINE_LIFTED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
