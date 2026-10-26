# ASTRA — Weather V4 A2 — Revue documentaire indépendante, lot 1 — 2026-10-07

```text
REVIEWER = astra.weather-v4.a2.doc-integration.v1
DESIGNATION = décision Owner §§8.1 et 8.6, commit 08fe3a1d9e0ab27c3e6cdf8fa717dd58ae2a334d
OBJET = dossier Blue §§14.1–14.14, commit 77766db60eaca40f0cd9b1531cb65df3e080f2e5
NATURE = constat documentaire ; ni approbation de release, ni autorisation, ni modification de manifest
```

## 0. Indépendance, méthode et actes effectués

Je n'ai participé ni à la préparation du dossier ni à la construction du harnais, et je ne serai pas Builder du lot 2. Les interprétations du préparateur, notamment celle du §14.5 sur le critère 3, sont traitées comme des propositions.

Actes effectués : résolution d'objets Git (commits, arbres, identités de blobs retournées par Git) ; lecture des textes ; comparaisons textuelles octet à octet ; extraction par recherche textuelle des littéraux de la source. Les copies de lecture ont été extraites hors du dépôt. Je n'ai rien écrit dans le dépôt.

Actes non effectués : aucun import, aucune exécution ni aucun test du harnais ; aucun calcul de digest de manifest ou de policy ; aucune fixture ni payload ; aucun accès à une source opérationnelle, à un endpoint, à un credential ou à la VM.

Textes lus :
- le dossier aux §§14.1–14.14, objet de la revue. J'ai aussi lu le §13, incorporé par O §8.7 ;
- la décision Owner A2 à `08fe3a1`, en entier. Les §§2 et 8–11 sont gouvernants ;
- la décision A1 à `728cf23`, en entier ;
- les quatre fichiers source à `78d537de` ;
- comme documents de gouvernance : le support de décision Phase Gate (en entier), les décisions OD01–OD03 et OD04–OD12, et l'addendum de conception.
- Le registre d'exposition a été lu pour ses champs de gouvernance : l'en-tête, `blue_access` et les champs de statut de `surfaces[]`. Dans `hypothesis_surface_records[]`, je n'ai relevé que les décomptes agrégés des valeurs `CLEANLINESS` et `OUTCOME_VIEWING`, sans lire les identifiants ni le contenu des hypothèses.

Corps non ouverts : la Gold Map, l'audit de surapprentissage, le ledger d'hypothèses et la table de puissance V2. Leur identité a été vérifiée uniquement dans les arbres Git. La section E explique pourquoi mes conclusions ne dépendent pas de leur contenu.

Hors périmètre, mentionnés sans évaluation : le §14.15 du dossier (commit `49d3d00`, enfant de `77766db`, qui ne modifie que le dossier) et le §12 Owner (commit `3ed9607`, enfant de `08fe3a1`, qui ne modifie que le fichier Owner). Aux deux commits, les quatre blobs source sont égaux à ceux de H.

Abréviations : O = décision Owner A2 à `08fe3a1` ; A1 = décision Phase Gate A1 à `728cf23` ; H = source de référence à `78d537de` ; B = dossier Blue à `92088b8` ; C = autorité de construction `37e3b25`.

## A. Références

| Référence | Commit | Chemin | Blob attendu | Blob retourné par Git | Statut |
|---|---|---|---|---|---|
| Dossier revu | `77766db60eaca40f0cd9b1531cb65df3e080f2e5` | `research/weather_forward/v4/blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md` | `c764f3999c6734ecd51822f7cd22eb011a76872c` | identique | RÉSOLU |
| Méthode et valeurs Owner | `08fe3a1d9e0ab27c3e6cdf8fa717dd58ae2a334d` | `research/weather_forward/v4/owner/OWNER_V4_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md` | `8530a0d344f6dd18993cce5b4f48c887b20dada8` | identique | RÉSOLU |
| Périmètre A1 | `728cf23e7d69a373306f3c1a3fb5d11240210cda` | `research/weather_forward/v4/owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md` | `483907e4f719ec8bcb3851af0f184690cea96279` | identique | RÉSOLU |
| Source `contract.py` | `78d537de681363ed83a6c7787aba4319f3c73c4d` | `research/weather_forward/v4/a2_harness/contract.py` | `f6f94a4a472e3f6652a1502f6afb5825721364d0` | identique | RÉSOLU |
| Source `harness.py` | idem | `…/a2_harness/harness.py` | `00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4` | identique | RÉSOLU |
| Source `trusted_root.py` | idem | `…/a2_harness/trusted_root.py` | `9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94` | identique | RÉSOLU |
| Source `__init__.py` | idem | `…/a2_harness/__init__.py` | `bf9a2bdba7658454ea10009a28c975024365cfe1` | identique | RÉSOLU |

Les références internes du dossier se résolvent toutes avec les blobs annoncés :
- au §14.1 : S8 `6bba1e2`, B `92088b8`, l'audit `3121591` et C `37e3b25` ;
- au §14.13.2 : `11b81f0`, `9c0edb5`, `7ea1aec`, `8ee801a` et `5f129ec` (blob `a89e1410…`) ;
- au §14.14.2 : les neuf artefacts. Chacun est aussi présent, avec le même blob, à `5f129ec` et à `77766db`.

Lignée vérifiée :
- Chaque commit de la chaîne a un parent unique : H → `3121591` → B → `11b81f0` → `9c0edb5` → S8 → `7ea1aec` → O → `8ee801a` → `5f129ec` → `77766db`.
- A1 est ancêtre de C (6 commits), C est ancêtre de H (20 commits), et O est à 5 commits de B.
- Le dossier à O est identique octet pour octet à B (blob `44eff971…`).
- Les quatre blobs source à O et à `77766db` sont égaux à ceux de H.
- Le §8 de O est identique octet pour octet au §8 de S8.
- Les versions du dossier à B, `8ee801a` et `5f129ec` sont des préfixes exacts, octet pour octet, du dossier à `77766db`. L'addition est donc purement additive : les §§1–14.13 sont inchangés. `77766db` ne modifie que le dossier.

Chaînes canoniques : j'ai comparé octet pour octet les valeurs des §§14.2A–B à leurs sources ratifiées. Toutes sont identiques, et aucune ne contient de caractère non ASCII :
- les 20 champs interdits (O §2.2 = B §13.4 = §14.2A) ;
- `source_provenance_class`, `exact_metric_or_artifact` et `granularity` (égaux à B §§13.4–13.5) ;
- `retention_rule` (égal à O §8.4) ;
- `incident_if_unexpected_information_revealed` (égal à O §8.5).

Les plages de lignes de H citées au §14.5 correspondent à la source.

Écart : aucun.

## B. Tableau des six critères (O §8.6, appliqués sans modification)

| Critère | Référence vérifiée | Périmètre | Constat | Limitation | Statut |
|---|---|---|---|---|---|
| 1 — Input et provenance | §14.2A ; O §2.2 ; B §13.4 ; A1 `728cf23` / `483907e…` ; H `harness.py` 415–467, 620–668 | Déclaration InputManifest (17 champs), au niveau de la spécification | L'input autorise exactement quatre champs de référence. Les 20 champs interdits incluent `document_body`. La classe est `DOCUMENTATION_ONLY` et la provenance désigne exactement le commit, le chemin et le blob A1, qui se résolvent. J'ai lu A1 en entier : il ne contient que des périmètres, des interdictions et des références de gouvernance, sans observation, mesure, valeur d'efficacité, classement ni préférence. L'opération définie ne lit aucun document : les deux évaluations portent sur des déclarations, et la source ne fait aucune entrée/sortie. | Le constat porte sur la spécification, non sur son application : le harnais n'inspecte aucun payload. La provenance n'est pas authentifiée à l'exécution. La valeur de `authorized_documentary_scope_reference` n'est fixée nulle part (seul le nom du champ l'est) ; c'est sans effet ici, car cette valeur n'entre pas dans le contenu canonique et aucune lecture n'a lieu. Le contenu n'est pas figé. | SUPPORTED |
| 2 — Output, motifs et codes | §14.2B ; O §2.3 ; §14.5 ; H `harness.py` et `contract.py` | Les 15 éléments, `detail_code`, `stop_reason`, les états, et le contenu conservé sous garde | (i) Les 78 codes finaux du §14.5 sont exactement ceux qu'atteignent les deux appels pour la policy déclarée (voir F). Ce sont des littéraux fixes, sans interpolation, de nature structurelle. (ii) Les états et `StopReason` sont des enums fermés. (iii) Les références et les bindings sont déterminés par la configuration. (iv) En revanche, `structural_linkage_status` n'a de domaine de valeurs défini ni dans O, ni dans les §§13–14, ni dans la source. Sa valeur serait produite hors de la source revue, par le vérificateur externe. Il en va de même du contenu « vérification » compté au O §8.3 et conservé sous garde. | Aucun rapport ni sérialiseur n'existe, et aucune sortie réelle n'a été observée. Pour cet élément, l'exigence « pas de texte libre » et l'examen des codes « dans leur source exacte » ne peuvent pas être établis. | UNRESOLVED |
| 3 — Liaisons | §§14.2C–D, 14.7–14.9D, 14.14.5–6 ; O §§8.1–8.2, 8.7–8.8 ; H `harness.py` 307–412, 575–606, 834–931 | Liaison documentaire | Les éléments suivants sont explicites et cohérents entre eux : acteurs, rôles, actions, identifiants d'autorisation, paire destinataire, identifiants de manifests, token de version, recettes du binding, de la policy et de la root, et tables de contexte du LogRecord. Les libellés de recette ne sont pas des valeurs admissibles : `validate_policy` les refuserait (`…_NOT_SHA256`), et le dossier interdit de les soumettre. Les identités dérivées, l'autorité d'exécution et le journal restent futurs (section G). | Aucune liaison d'exécution n'existe ni n'est revendiquée. Les tokens d'acteurs ne sont pas authentifiés. La section H relève des dépendances de séquencement. | SUPPORTED (stade documentaire, selon l'interprétation retenue en G) |
| 4 — Inventaire borné | §14.4 ; §14.13, attribué par Owner en §14.14.1 ; §§14.14.2–14.14.3 ; registre d'exposition | Informations pertinentes déjà divulguées au destinataire | L'inventaire est borné et attribué à Owner. Il donne des références exactes, que j'ai vérifiées, une limite de couverture et des inconnues explicites. Aucun endpoint ni payload n'a été consulté. Owner déclare qu'un inventaire exhaustif est impossible : HISTORIQUE = PARTIEL, COUVERTURE = INCONNUE. | La réception n'est pas authentifiée et la couverture est inconnue. Le critère 4 exige un inventaire borné avec inconnues explicites, non sa complétude ; l'effet de l'incomplétude relève du critère 5. | SUPPORTED |
| 5 — Cumul pour le tuple exact | O §8.6.5 ; clarification Owner §14.14.4 ; H `contract.py` 300–351 | `A2-DOC-OUT-STRUCTURAL-REPORT-V1` / `project-owner.weather-v4.a2.doc-integration.v1` / `RESEARCH_VIEWER` | Pour tous les éléments déterminés par la configuration, la contribution d'efficacité est nulle quel que soit l'historique : les inconnues ne sont donc pas matérielles pour ces éléments (section E). Les documents examinés ne contiennent aucun BLOCKED. Mais le contenu de sortie n'est pas fermé (critère 2) : pour l'élément produit hors source, les inconnues d'historique restent potentiellement matérielles. | Aucun ledger n'existe, et la source ne prouve pas la complétude d'un historique. | UNRESOLVED |
| 6 — Documentation des conclusions | Le présent constat | Toutes les conclusions | Chaque conclusion indique critère, référence vérifiée, périmètre, constat et limitation. Aucune ratification n'est utilisée comme preuve. | L'attribution passe par l'identité de gouvernance et la publication, sans signature cryptographique. Les constats sont liés aux versions exactes. | SUPPORTED |

## C. Résultat input (séparé)

**Réponse : oui.** La base documentaire permet de faire passer `InputManifest.efficacy_leakage_assessment` de `UNRESOLVED` à `CLEAR` pour le contenu déclaré au §14.2A à `77766db`. La condition est que les 16 autres valeurs canoniques restent inchangées octet pour octet.

Motivation. L'input n'admet que quatre références de gouvernance à la décision A1. Aucun contenu d'efficacité ne peut y entrer, pour quatre raisons :
- la liste des champs permis et celle des champs interdits l'excluent ;
- l'artefact référencé ne contient lui-même aucune information d'efficacité ;
- l'opération ne lit rien ;
- le lecteur désigné (`Role.EXECUTOR`, Blue, exécutant désigné d'A1 par A1 §12) détient déjà ces références.

La contribution de cet input à l'information d'efficacité d'un lecteur, quel qu'il soit, est donc nulle.

Application des critères à la conclusion input :

| Critère | S'applique ? | Motivation |
|---|---|---|
| 1 | Oui, intégralement | C'est le fondement direct de la conclusion. SUPPORTED. |
| 2 | Non, pour ce champ | Le critère 2 porte sur les 15 éléments de sortie. Les codes produits par l'appel input atteignent le destinataire par la voie de sortie ou de garde : ils sont évalués côté output (critères 2 et 5, section F). Cette séparation est celle qu'exige le « résultat input/output séparé » de O §8.6. |
| 3 | Oui, sous sa forme documentaire | Le constat est lié à un contenu exact (commit, blob, valeurs du §14.2A). Les liaisons input sont explicites : `input_id` ↔ `expected_input_manifest_id` ; token de version ↔ binding et policy ; `EXECUTOR` ↔ Blue ↔ `a2-doc-v1-read-input-blue`. L'identité input ne peut être dérivée qu'après la fixation de l'état CLEAR ; l'exiger avant serait circulaire (section G). SUPPORTED. |
| 4–5 | Non, en tant que tels | Ces critères sont définis pour le tuple de disclosure `output_id + recipient_actor_id + recipient_role`, et l'InputManifest n'a pas de destinataire. Même appliqués par analogie au lecteur, ils ne changeraient rien : une contribution nulle ne devient pas non nulle par combinaison avec un historique, y compris l'exposition enregistrée d'une session Blue. |
| 6 | Oui | SUPPORTED. |

Lecture alternative, que je n'adopte pas : si Owner lit « critères cumulatifs » comme conditionnant chaque résultat aux six critères, y compris les critères 2, 4 et 5 formulés pour l'output, l'input resterait UNRESOLVED jusqu'à la fermeture de l'output. Cette lecture priverait d'objet le résultat input séparé exigé par O §8.6. Par ailleurs, O §2.2 pose une condition propre à l'input : une justification documentée sur le périmètre figé. L'arbitrage revient à Owner.

Limites du constat input :
- Il ne modifie aucun manifest et ne fige rien.
- Il vaut pour le contenu figé seulement si ce contenu est identique octet pour octet au §14.2A, hors la transition revue `UNRESOLVED → CLEAR`.
- Tout changement des 16 autres valeurs l'invalide.
- Il ne certifie ni l'application des contrôles, ni l'authenticité de la provenance, ni une lecture effective.

## D. Résultat output (séparé)

**D.1 — `OutputManifest.efficacy_leakage_assessment` : UNRESOLVED.**
- Quatorze des quinze éléments ont un domaine fermé ou déterminé par la configuration : états, `StopReason`, codes finis, références, bindings, identifiants d'enregistrement fixés par l'autorité.
- `structural_linkage_status` n'a aucun domaine défini. Sa valeur serait produite hors de la source revue par un acteur, ce qui crée un canal potentiel de texte libre. Le registre d'exposition montre que le risque n'est pas théorique : il enregistre une exposition d'une session Blue à des résumés publiés.
- Il en va de même de la « vérification » comptée au O §8.3 et conservée sous garde.
- En dehors de ce point, je n'ai identifié aucun élément capable de porter une information d'efficacité.
- Fermeture minimale (section I, points 1 à 3) : Owner fixe un ensemble fermé de valeurs pour cet élément ainsi que le contenu exact conservé sous garde, puis Astra confirme de façon ciblée.

**D.2 — `cumulative_disclosure_risk` pour le tuple `A2-DOC-OUT-STRUCTURAL-REPORT-V1` / `project-owner.weather-v4.a2.doc-integration.v1` / `RESEARCH_VIEWER` : UNRESOLVED.** La cause est la même lacune. Pour les éléments déterminés par la configuration, les inconnues d'historique ne sont pas matérielles (section E) ; pour l'élément non fermé, elles le restent.

**D.3 — Quarantaine : MAINTAIN.** La levée reste une décision Owner. Une contrainte structurelle s'y attache. `quarantine_status` est un contenu canonique de l'output : il entre dans l'identité output, donc dans la policy et dans la root (H `harness.py` 184–202, 241–261 et 378–379). Une levée doit donc être enregistrée avant le gel de l'output. Une levée postérieure au gel impose un nouveau gel, un recalcul, une nouvelle policy et une nouvelle root (§14.14.6, point 2). Avec le harnais actuel, une levée a posteriori au sein de la même opération, après examen de l'évaluation input, n'est pas réalisable.

**D.4 — Enregistrements de ledger supportés : NONE.**
- Mon constat ne permet aucun enregistrement CLEAR pour le tuple exact.
- Pour ce tuple, il supporte au plus l'état UNRESOLVED. C'est aussi ce que la source retourne pour un ledger vide (`evaluate()` → `UNRESOLVED`, `contract.py` 305–306) : aucun enregistrement n'est nécessaire pour le représenter.
- Pour les autres tuples, mes constats n'exigent aucun enregistrement, ni BLOCKED ni UNRESOLVED. Je n'ai identifié aucun BLOCKED à reporter : le registre d'exposition n'en contient aucun, et `DISCOVERY_CONTAMINATED` relève d'une structure distincte que §14.14.4 interdit de convertir.
- Avertissement tiré de la source (`contract.py` 304–332) : dans `CumulativeDisclosureLedger.evaluate()`, tout enregistrement UNRESOLVED, et non seulement BLOCKED, ainsi que tout `recipient_actor_id` non résolu, où qu'il soit dans le ledger, prévaut sur un CLEAR du tuple exact. Un futur ledger ne doit donc contenir que des enregistrements supportés par un constat. Tout enregistrement portant sur un autre tuple conditionnerait la release du tuple Owner.

## E. Matérialité des inconnues

**Lemme de détermination**, fondement de l'analyse :
- (a) À H, les deux évaluations ne lisent ni fichier, ni réseau, ni horloge, ni source d'aléa, ni environnement. Les imports se limitent à `hashlib`, `json`, `re`, `dataclasses`, `enum` et `typing`. Tous les `detail_code` sont des littéraux fixes ; la seule chaîne formatée est le préfixe `sha256:` (`harness.py` 156).
- (b) Leurs entrées sont exclusivement des déclarations de gouvernance : les manifests (§§14.2A–B), la policy (§14.2C), les acteurs et autorisations (§14.2D), le ledger, les identifiants d'enregistrement et le contexte d'incident fixés par l'autorité de l'opération, et le SHA d'autorité d'exécution émis par Owner.
- (c) Chaque champ des décisions et des LogRecords est donc une fonction déterministe de déclarations que le destinataire a ratifiées ou émettra, et d'une source présente dans le dépôt. Si `Out = f(C)` et que C est connu du destinataire, l'information apportée par Out à la connaissance K du destinataire est nulle, quel que soit K : `I(Out ; E | K) ≤ H(Out | K) = 0`, où E désigne l'information d'efficacité.
- (d) Indépendamment de (c), C ne contient aucune valeur d'efficacité : j'y ai relevé uniquement des tokens, des SHA de gouvernance, des enums et des noms de catégories. Même pour un destinataire autre que celui désigné par le token, Out ne porte aucune information d'efficacité.

Le lemme ne couvre pas les éléments produits hors de la source par un humain ou un agent : `structural_linkage_status` tant qu'il n'est pas défini, un récit de vérification, un texte libre d'incident. Il ne couvre pas non plus les déviations, comme un code chargé différent de H ou le texte d'une exception ; celles-ci relèvent de la règle STOP sans diffusion.

| Inconnue (§14.13.4) | Matérialité | Justification |
|---|---|---|
| U1 — Autres informations reçues hors du contexte fourni | Non matérielle pour les éléments déterminés ; matérielle tant que les éléments non fermés subsistent | Lemme (c) : le résultat ne dépend pas de K. Un élément non fermé, en revanche, n'est pas déterminé par C. |
| U2 — Corps, annexes ou transcripts effectivement lus | Même statut que U1 | Le destinataire peut connaître le contenu des quatre corps non ouverts : la sortie n'y ajoute rien si elle est fermée. |
| U3 — Ordre, répétition et combinaison des expositions | Non matérielle | L'opération est unique, avec au plus deux évaluations et sans série. Les états ne dépendent d'aucun comportement de source ou de marché : l'avertissement du support Phase Gate §8 (des séquences d'états ou d'erreurs révélant latence ou prévalence) ne s'applique pas. Durées et décomptes sont exclus. Condition : pas de nouvelle opération sans nouvelle autorité. |
| U4 — Disclosures indirectes et BLOCKED globaux | Non matérielle pour le contenu informationnel ; matérielle pour la procédure | Tout BLOCKED ou UNRESOLVED présent dans le ledger applicable prévaut. Je n'en ai identifié aucun dans la gouvernance examinée, mais je ne peux pas certifier leur absence dans un ledger qui n'existe pas encore. |
| U5 — Attribution technique du destinataire | Non matérielle pour l'évaluation de leakage | Lemme (d). L'authentification reste un contrôle externe, NOT_VERIFIED, qui conditionne la release ou la garde effective, non le constat. |
| U6 — Périmètre futur des diagnostics | Matérielle par construction | Le constat est lié à la source H et à la liste du §14.5. Tout changement (logique chargée différente de H, nouveau code, nouveau domaine) exige une réévaluation. |

| Élément (§§14.14.2–14.14.3) | Matérialité | Justification |
|---|---|---|
| Registre d'exposition (lu) | Non matériel | C'est une amorce, non un historique reconstitué : `SURF_V2V3_HISTORY = UNKNOWN`, trois surfaces sont `DISCOVERY_CONTAMINATED`, aucune valeur n'est BLOCKED et aucun enregistrement ne concerne le destinataire ou A2. La sortie ne touche aucune surface. Les classifications restent régies par OD09, sans assainissement ni aggravation. |
| Gold Map, audit de surapprentissage, ledger d'hypothèses, table de puissance V2 (non ouverts) | Non matériels pour la contribution marginale | Ces documents sont présumés porteurs d'efficacité. La sortie est indépendante de leur contenu (lemme c et d), et elle ne contient aucun token qui permettrait de les indexer : aucun EDGE_ID, famille, ville, station, modèle, source, date ou mesure dans des domaines fermés. Les ouvrir serait nécessaire seulement si Owner voulait admettre un élément de sortie non fermé ; je ne le propose pas. |
| Support Phase Gate (lu en entier) | Non matériel | Spécification de gouvernance, sans valeur d'efficacité. |
| OD01–OD03, OD04–OD12 (lus) | Non matériels | Décisions structurelles, sans résultat d'efficacité. OD09 reste inchangée. |
| Addendum de conception (lu) | Non matériel | Règles de propreté par hypothèse. Il mentionne un nombre d'EDGE_ID, sans contenu. |
| Contamination préexistante | Non affectée | Cette évaluation ne la requalifie pas, et aucune conversion en état de ledger n'est faite. |

**Combinaison.** Une fois les domaines fermés et le contenu entièrement déterminé par la configuration, aucune combinaison d'informations antérieures avec les éléments de sortie ne peut révéler une information d'efficacité qui ne soit déjà déductible des seules informations antérieures. Dans l'état actuel, `structural_linkage_status` et le contenu de vérification ne sont pas fermés, et une telle combinaison ne peut pas être exclue en principe. C'est le motif de l'état UNRESOLVED, non une fuite identifiée.

## F. Diagnostics

**F.1 — Complétude pour les deux appels : oui, pour la configuration déclarée.**

J'ai comparé mécaniquement les 134 littéraux en majuscules de `harness.py` aux 78 codes du §14.5. Résultat :
- Chaque code final atteignable par `evaluate_input_read` et `evaluate_output_release` est listé, pour une policy dont `fixture_provenance_contract` vaut `None`.
- Aucun code listé n'est absent de la source. Les deux codes de succès sont les produits statiques du `.replace` appliqué aux codes `*_PENDING_REQUIRED_LOG` (ligne 911).

Les 58 littéraux non listés se répartissent ainsi :
- 7 codes positifs internes ;
- 2 fragments (`PENDING_REQUIRED_LOG`, `LOGGED_AND_COMPLETED`) et 2 codes de succès avant remplacement ;
- 4 tokens d'ambiguïté (`UNKNOWN`, `UNRESOLVED`, `AMBIGUOUS`, `NOT_ATTESTED`) ;
- 3 codes hors des deux appels (lignes 1020–1035) ;
- des codes de fixture, en deux groupes distincts que la justification du §14.5 regroupe :
  - (i) les 15 codes `FIXTURE_CONTRACT_*` et `FIXTURE_PROVENANCE_CONTRACT_VALID`. Ils restent atteignables par les deux appels via `validate_policy` (lignes 341–344) si la policy fournie portait un contrat non `None`. Or `validate_policy` s'exécute avant la comparaison d'identité de policy avec la root (lignes 375–379) : une telle policy produirait ces codes plutôt que `TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH`.
  - (ii) `NO_APPROVED_FIXTURE_PROVENANCE_CONTRACT`, `FIXTURE_METADATA_ADMISSION_ELIGIBLE_PENDING_REQUIRED_LOG`, et les 21 codes de refus et le code positif propres à `validate_fixture_provenance`. Ils ne sont atteignables que par `evaluate_fixture_metadata_admission`, qui n'est pas appelé.

L'exclusion est correcte pour la policy déclarée, et toute apparition de ces codes entraîne STOP.

Deux remarques :
- `RELEASE_APPROVAL_REQUIREMENT_NOT_RESOLVED` est en pratique inatteignable : UNRESOLVED est déjà refusé ligne 494, et `RequirementState` n'a que trois valeurs. Le conserver dans la liste est sans inconvénient.
- Les messages d'exception de `contract.py` (`INVALID_DECISION_STATE_TYPE…`, `FINAL_PERMISSIVE_…`, `EXACT_HARNESS_DECISION_REQUIRED`, etc.) ne sont pas des codes de détail. Ils sont à juste titre hors liste.

**F.2 — Acceptabilité de la divulgation au destinataire.** Chaque code est un littéral fixe qui nomme une catégorie de garde, d'état ou d'identité, sans interpolation. Sa valeur dépend uniquement de déclarations de gouvernance. Aucun code ne porte plus qu'un état structurel. Codes exclus : aucun.

Trois signalements, qui ne sont pas des exclusions :
- `INPUT_EFFICACY_LEAKAGE_NOT_CLEAR` et `OUTPUT_EFFICACY_LEAKAGE_NOT_CLEAR` sont émis avec `StopReason.UNEXPECTED_EFFICACY_LEAKAGE` et `QuarantineState.QUARANTINED` lorsque l'évaluation *déclarée* n'est pas CLEAR (lignes 457–458, 641–645, 795–800). Ils n'indiquent pas une fuite détectée. Owner devrait préciser que, dans cette opération, cette combinaison désigne un état de déclaration. Elle ne doit être ni rapportée ni traitée comme la révélation d'une information d'efficacité : elle arrête la séquence comme tout refus, sans inférence.
- `DISCLOSURE_LEDGER_NOT_CLEAR_FOR_EXACT_OUTPUT_RECIPIENT_ACTOR_ROLE` révèle l'état du ledger, y compris l'existence éventuelle d'un enregistrement non CLEAR ailleurs. Ce ledger est fourni par Owner : rien de nouveau pour Owner.
- `REQUIRED_LOG_RECORD_ID_ALREADY_EXISTS` révèle la présence d'un identifiant dans le journal fourni. C'est une information structurelle.

**F.3 — Traitement d'une exception ou d'un code inattendu.** La règle actuelle (§14.5 et texte d'incident de O §8.5 : STOP, aucune conversion automatique, aucune diffusion) suffit comme règle documentaire, sous quatre précisions à fixer avant toute exécution :
1. « Inattendu » signifie : un code absent de la liste figée, par égalité exacte de chaîne ; ou un `stop_reason` ou un état hors des enums fermés ; ou un type de résultat différent du type attendu. Je recommande une vérification supplémentaire peu coûteuse : la cohérence du triplet `detail_code` ↔ `stop_reason` ↔ `quarantine_state` avec la source H. Elle fournit une preuve de conformité de la logique chargée.
2. L'enregistrement d'incident porte une classe fixe, issue d'un vocabulaire fermé à fixer par Owner. Il ne porte jamais le message, le `repr` ou la trace d'une exception : les exceptions Python levées sur des objets malformés peuvent contenir des noms de types ou des valeurs, ce qui est du texte libre au sens du critère 2.
3. La trace et la sortie d'erreur ne sont ni conservées sous garde, ni comptées dans la sortie.
4. La capture et la rétention de la sortie du processus relèvent d'un contrôle externe, NOT_VERIFIED. La règle est suffisante sur le plan documentaire ; son application reste non vérifiée.

En cas d'exception lors du second appel, `first_result.log` est conservé, sans retry.

## G. Critère 3 et liaisons

**Interprétation du §14.5 : ACCEPTÉE**, avec précisions.

Motifs :
1. Toute lecture littérale qui exigerait les identités dérivées, l'autorité d'exécution ou le journal avant le CLEAR documentaire est circulaire. Les états de leakage, de disclosure et de quarantaine sont des champs canoniques des manifests (`harness.py` 159–202). Les identités des manifests entrent dans la policy, et l'identité de la policy entre dans la root. Le journal n'existe qu'après une exécution qui exige elle-même CLEAR. Satisfaire cette lecture imposerait des valeurs fabriquées, ce qui est interdit.
2. L'interprétation ne dispense pas du critère. Elle le scinde en un stade documentaire (maintenant) et un stade d'exécution, où le même critère est vérifié sur les objets réels.
3. Les libellés de recette ne sont pas des placeholders opérationnels : ce ne sont pas des valeurs admissibles, et le dossier interdit de les soumettre.

Précision de calendrier, qui affine le résumé « valeurs dérivées, autorité d'exécution et journal seulement au moment de l'exécution » :
- les identités dérivées existent au stade du calcul, après le gel, bien avant l'exécution, puisque la matérialisation de la root les exige ;
- l'autorité d'exécution existe dès qu'Owner émet l'artefact d'autorité de policy d'exécution, avant la matérialisation de la root ;
- seul le journal n'existe qu'à l'exécution.

Ce qui doit exister, et à quel moment, sans calcul ni enregistrement fabriqué :

| Moment | Ce qui doit exister |
|---|---|
| Maintenant | La liaison des constats au contenu et aux versions exacts, assurée par la présente revue. |
| Au gel | Un contenu figé identique octet pour octet aux valeurs revues du §14.2, à l'exception des transitions d'état explicitement revues, enregistré avec son commit et son blob. Cette vérification est une comparaison textuelle, sans calcul. |
| Avant exécution | Des choix d'Owner, non dérivés : l'artefact d'autorité d'exécution (couvrant READ_INPUT et, s'il est visé, RELEASE_OUTPUT ; voir H.4) ; les identifiants d'enregistrement, le journal initial et le contexte d'incident, dans des formats fixés. |
| Au calcul | Les identités dérivées selon la recette revue et vérifiées indépendamment. |
| À l'exécution | Les prédicats du §14.9D, appliqués aux objets réels. |

« Aucune différence matérielle non revue » implique que toute valeur fixée après la présente revue et qui entre dans la sortie ou sous garde ait un format ou une valeur revus. Sont concernés : les identifiants d'enregistrement, la classe d'incident, `structural_linkage_status` et le SHA d'exécution.

## H. Dépendances (§§14.7–14.11, 14.14.5–14.14.6)

**H.1 — Cohérence générale.** Sur les faits que j'ai vérifiés, les sections examinées sont conformes à la source :
- les nombres de champs : 17, 13, 12, 5, 4, 6, 18 et 7 ;
- la recette de canonicalisation ;
- l'ordre des gardes ;
- l'absence de champ de digest de policy et de champ d'enregistrement précédent dans le LogRecord ;
- la root deny-all à H, à O et à `77766db` ;
- les prédicats du §14.9D : release BLOCKED normale en cas de succès input, `cumulative_disclosure_state` à `None` pour l'input, concordance des trois états partagés.

Je n'ai trouvé aucune erreur factuelle affectant les conclusions, hormis le point H.2.

**H.2 — Précédence dans le ledger (exactitude).** Le dossier (§§14.4, 14.9C, 14.9D) et O §8.6.5 parlent de la précédence globale de BLOCKED. Or la source (`contract.py` 304–332) donne aussi une précédence globale à tout enregistrement UNRESOLVED et à tout `recipient_actor_id` non résolu. Ce point devrait être ajouté au cas « Global BLOCKED precedence » du §14.9C et au §14.9D.

**H.3 — Voie READ_INPUT seul.**
- (a) Elle est cohérente avec O §§2.1 et 8.3 (« au maximum ») lorsqu'aucune release n'est tentée.
- (b) Elle exige néanmoins une identité output calculée (§14.14.6, point 1), et donc un contenu output figé.
- (c) Une conséquence n'est pas tirée par le dossier. Si l'output est figé à l'état bloqué du §14.2B, une release ultérieure devient impossible dans la même opération. Le CLEAR ou la levée de quarantaine changent en effet l'identité output, donc la policy et la root. Une release sous une autre policy sortirait de l'opération définie, qui suppose une policy et une root figées uniques pour les deux évaluations (§14.9D). Elle ne pourrait pas être prouvée par le LogRecord, qui n'a pas de champ de policy. Elle exigerait de remplacer la root et, faute de retry, une nouvelle opération sous une nouvelle autorité. Owner doit donc choisir avant le gel de l'output entre deux voies : (i) une opération input seul, avec un output figé à l'état bloqué ; (ii) une opération capable de release, qui exige les constats CLEAR output et la levée de quarantaine avant le gel.
- (d) Une tension est à confirmer. O §2.5 range « l'absence d'approbation indépendante » parmi les conditions imposant refus et STOP, ce qui inclut une référence d'incident et le recours au mécanisme de quarantaine. Le §14.14.5 prévoit au contraire une fin normale, sans incident, en l'absence de RELEASE_OUTPUT. Les deux sont compatibles si O §2.5 vise une évaluation de release effectivement tentée. Owner devrait le confirmer dans le grant d'exécution.

**H.4 — Couplage identité output → policy → root.** Le §14.14.6, point 2, décrit correctement ce couplage. Deux dépendances manquent :
- (a) Les transitions CLEAR de l'output et la levée de quarantaine sont des décisions Owner antérieures au gel. Le graphe du §14.11 montre `D → OF`, mais pas « décision Owner sur les états canoniques de l'output → OF ».
- (b) La root ne contient qu'un seul champ `execution_policy_authority_sha`, et il doit être égal à l'`authority_sha` des deux ActionAuthorization (`harness.py` 594–595). Un grant RELEASE_OUTPUT émis plus tard dans un artefact distinct, avec son propre SHA, serait refusé (`ACTION_AUTHORIZATION_EXECUTION_POLICY_AUTHORITY_MISMATCH`), sauf reconstruction de la root. L'examen extérieur de « l'autorité … propre à RELEASE_OUTPUT » prévu au §14.14.5 n'est donc praticable que si l'artefact d'autorité lié par la root couvre déjà RELEASE_OUTPUT, de façon conditionnelle. Le dossier devrait l'expliciter.

**H.5 — Garde par Owner des preuves de lecture.** Je suis d'accord que cette garde n'est pas une release au sens du harnais. C'est pourtant une disclosure au même humain, qui est à la fois destinataire (`RESEARCH_VIEWER`), custodian et autorité d'incident. Le gate de l'OutputManifest et la quarantaine ne gouvernent pas ce canal, et aucun manifest n'en déclare le contenu. La clarification Owner du §14.14.4 pose la question en termes d'information disponible pour le destinataire. Le support Phase Gate §8 exige de lier ce que chaque humain a vu, pas seulement les exports.

En conséquence, le contenu conservé sous garde doit :
- (a) être déclaré exactement : les 7 champs de la décision, les 18 champs du LogRecord, `log_acknowledged`, et les résultats des prédicats dans un domaine fermé, sans trace ni récit ;
- (b) être inclus dans l'évaluation cumulative du tuple.

Une fois (a) déclaré, le lemme s'applique et la garde n'ajoute aucune information d'efficacité. Sans (a), la lacune est la même qu'en D.1. Les capacités de garde (ACL, suppression, retenue) restent NOT_VERIFIED ; elles relèvent du lot 2, non évalué ici.

**H.6 — Mineur.** Le graphe du §14.11 n'a pas de nœud pour l'artefact d'autorité d'exécution, qui alimente `RB` et les ActionAuthorization. Sans autre effet que celui décrit en H.4.

## I. Blocages restants

| # | Élément | Action bloquée | Résolution minimale | Responsable |
|---|---|---|---|---|
| 1 | Domaine de `structural_linkage_status` non défini, valeur produite hors source | CLEAR de leakage output ; CLEAR cumulatif ; enregistrements de ledger ; levée de quarantaine ; gel de l'output sous forme permettant la release | Fixer un ensemble fermé de valeurs, par exemple les issues des prédicats du §14.9D, comme contrainte documentaire ou dans le texte canonique avant le gel. Aucun calcul n'est requis. | Owner (rédaction possible par le préparateur) |
| 2 | Contenu conservé sous garde non déclaré (dont la « vérification ») ; canal de garde non couvert | CLEAR cumulatif ; garde des preuves input, y compris sur la voie input seul | Déclarer le contenu exact conservé sous garde (H.5) et l'inclure dans l'évaluation du tuple | Owner |
| 3 | Confirmation après les points 1 et 2 | Critères 2 et 5 ; D.1, D.2, D.4 | Revue Astra ciblée, limitée à l'acte de fermeture | Astra |
| 4 | Ordre entre les états canoniques de l'output, la levée de quarantaine et le gel ; choix entre les voies H.3 (i) et (ii) | Gel de l'output sous forme permettant la release | Décision Owner avant le gel | Owner |
| 5 | Autorité d'exécution unique pour les deux actions | RELEASE_OUTPUT sans reconstruction de la root | Rédiger l'artefact d'autorité d'exécution avec une couverture conditionnelle explicite de RELEASE_OUTPUT | Owner |
| 6 | Règle de composition du ledger (précédence globale d'UNRESOLVED et de BLOCKED) | Ledger étayé pour la release | Documenter la règle ; le ledger ne contient que des enregistrements supportés | Owner (documentation possible par le préparateur) |
| 7 | Formats fixes des identifiants d'enregistrement et d'incident ; vocabulaire fermé des classes d'incident ; note d'interprétation sur `*_EFFICACY_LEAKAGE_NOT_CLEAR` | Toute exécution (l'un ou l'autre appel) | Fixer ces éléments dans le grant d'exécution | Owner |
| 8 | Gel de l'input portant l'état CLEAR, si Owner retient C | Calcul de l'identité input ; policy | Autorité de gel de l'input | Owner |
| 9 | Chaîne technique (calculs, root, Builder, vérification, activation, intégration) et contrôles externes (ressources, ACL, garde, suppression, retenue, authentification, code chargé) | Selon §§14.6, 14.10–14.11 | Grants et preuves propres à chaque action | Owner (grants) ; Builder (candidat root sous grant) ; revue indépendante (vérification) |
| 10 | Articulation entre O §2.5 et §14.14.5 (H.3 d) | Fin normale de la voie input seul | Confirmation Owner | Owner |

Le §14.15 et le §12 Owner, qui portent sur le contrôle des ressources, relèvent du lot 2 et ne sont pas évalués ici.

## J. Conclusion

Un `CLEAR_SUPPORTED` signifie que la base documentaire justifie le passage à CLEAR. Il ne modifie aucun manifest et n'autorise rien.

```text
REVIEWED_COMMIT = 77766db60eaca40f0cd9b1531cb65df3e080f2e5
REVIEWED_SECTIONS = 14.1-14.14
INPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED
OUTPUT_LEAKAGE_FINDING = UNRESOLVED
CUMULATIVE_DISCLOSURE_FINDING = UNRESOLVED
LEDGER_RECORDS_SUPPORTED = NONE
QUARANTINE_RECOMMENDATION = MAINTAIN
DIAGNOSTIC_SCOPE_FINDING = ACCEPTED
DIAGNOSTIC_CODES_EXCLUDED = NONE
CRITERION_3_INTERPRETATION = ACCEPTED
HARNESS_IMPORTED = NO
TESTS_RUN = NO
DIGESTS_COMPUTED = NO
UNOPENED_BODIES_OPENED = NO
REVIEWER = astra.weather-v4.a2.doc-integration.v1
REVIEW_DATE = 2026-10-07T12:31:09+02:00 (Europe/Paris)
```
