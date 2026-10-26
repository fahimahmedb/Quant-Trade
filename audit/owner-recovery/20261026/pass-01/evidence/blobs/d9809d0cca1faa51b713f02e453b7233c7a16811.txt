# Décision Owner — Weather V4 A2, lot 2 : autorisation technique groupée

## PROJET FINALISÉ — en attente de ratification explicite

Date de rédaction : 2026-10-07. Dépôt : `fahimahmedb/Quant-Trade`.

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
MISSION_CLASS = OWNER_CONSOLIDATED_TECHNICAL_AUTHORIZATION_FOR_A2_LOT2_PREPARATION_ONLY
EFFECT_BEFORE_RATIFICATION = NONE
```

La publication et la finalisation de ce projet n'autorisent aucune action technique. Owner doit ratifier explicitement cette version, identifiée par son chemin, son commit complet et son blob. Le commit et le blob de publication sont enregistrés dans le retour de publication, pas dans le fichier qui les détermine. Toute modification ultérieure du projet change la version présentée à ratification.

Les clauses « autorisé » ci-dessous prennent effet seulement après cette ratification, pour les actions dont les prérequis propres sont satisfaits. Aucune signature d'Astra, constat CLEAR, qualification de contrôle, identité dérivée, activation ou exécution n'est produit par le présent texte.

## 0. Références exactes et priorité documentaire

| Alias | Commit exact | Chemin et portée | Blob |
|---|---|---|---|
| A1 | `728cf23e7d69a373306f3c1a3fb5d11240210cda` | `research/weather_forward/v4/owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md`, notamment §§3 et 5 | `483907e4f719ec8bcb3851af0f184690cea96279` |
| O | `08fe3a1d9e0ab27c3e6cdf8fa717dd58ae2a334d` | `research/weather_forward/v4/owner/OWNER_V4_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`, §§2, 4, 5, 8–11 | `8530a0d344f6dd18993cce5b4f48c887b20dada8` |
| O12 | `3ed9607add11618862043e707c687053d208dff6` | Même fichier, §12 : désignation du moyen de contrôle des ressources | `3c67f6b3b33ab76d1ebd1ecf3b11c1591023f751` |
| D | `49d3d0033dd5088ebe6ed93937d283b0a5b83a63` | `research/weather_forward/v4/blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md`, §§14.2, 14.7–14.11, 14.14.5–14.14.6, 14.15 | `c3271812aa7ad67747916afa0c64344aec36590d` |
| H | `78d537de681363ed83a6c7787aba4319f3c73c4d` | Sources du harnais énumérées ci-dessous | Voir table suivante |
| C | `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` | `research/weather_forward/v4/owner/OWNER_V4_A2_DEDICATED_HARNESS_BUILDER_DECISION_2026-10-04.md` : autorité de construction historique conservée dans les bindings | `81d2ad4dac7ed50173442448437c9a23cc1ef51e` |
| TST | `45f5c940140788bb96c7b6da8581d9aa7c627dfa` | `research/weather_forward/v4/owner/OWNER_V4_A2_BOUNDED_OFFLINE_HARNESS_TEST_AUTHORITY_2026-10-05.md` : précédent de forme et règle des objets synthétiques | `2201905c60b19c915cc9ae4ef655ff7c48fa16ec` |
| L1-TARGET | `77766db60eaca40f0cd9b1531cb65df3e080f2e5` | Dossier Blue, §§14.1–14.14 uniquement ; §14.15 exclu de la revue lot 1 | `c764f3999c6734ecd51822f7cd22eb011a76872c` |
| L1 | À venir ; aucune identité inventée | Constat Astra sur L1-TARGET, dans `research/weather_forward/v4/audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_<date>.md`, puis décision Owner qui l'adopte et dispose les points prévus en L2-C/L2-D | Commit, chemin et blob exacts à enregistrer lorsqu'ils existent |

Les références C et TST ne réactivent aucune permission historique. La présente décision ratifiée doit fournir les permissions nouvelles. Le constat Astra reste une preuve indépendante, jamais une permission de construction, d'activation ou d'exécution.

| Fichier de production à H | Blob exact, également présent à D |
|---|---|
| `research/weather_forward/v4/a2_harness/contract.py` | `f6f94a4a472e3f6652a1502f6afb5825721364d0` |
| `research/weather_forward/v4/a2_harness/harness.py` | `00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4` |
| `research/weather_forward/v4/a2_harness/trusted_root.py` | `9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94` |
| `research/weather_forward/v4/a2_harness/__init__.py` | `bf9a2bdba7658454ea10009a28c975024365cfe1` |

La concordance de ces blobs à D et H est une preuve d'identité des fichiers du dépôt, pas une preuve d'intégrité du code chargé sur la VM.

La branche documentaire proposée est `owner/weather-v4-a2-lot2-technical-authorization-2026-10-07`, issue exactement de D. Elle contient uniquement le présent nouveau projet. Les contenus O et O12 sont référencés à leurs commits ; leur présence sur cette branche n'est pas présumée. Une future consignation Owner dans le document de configuration existant part de sa propre base O12, sans écraser §12 ni substituer D à cette base.

Les valeurs ratifiées d'O prévalent sur une illustration. Les chaînes canoniques de D §14.2 sont reproduites exactement, sauf changement explicitement prévu et ratifié en L2-C/L2-D. Une déclaration, une preuve, un contrôle implémenté et une autorisation effective restent quatre états distincts.

Après ratification, cette décision adopte O12 §§12.4 et 12.6 dans les limites de L2-A. Elle ne déclare aucun contrôle vérifié.

## 1. Objet et limites du lot

Une seule décision couvre les actions L2-A à L2-J, chacune avec son périmètre et ses prérequis. Le lot prépare le candidat et les preuves pour la revue technique indépendante du lot 3. L'activation et l'opération bornée relèvent du lot 4.

```text
LOT2_COMPLETE != CONTROL_EFFECTIVENESS_FULLY_VERIFIED
LOT2_COMPLETE != TRUSTED_ROOT_ACTIVATED
LOT2_COMPLETE != A2_EXECUTION_PERFORMED
ASTRA_LOT3_PASS != ACTIVATION_AUTHORIZATION
ASTRA_LOT3_PASS != RELEASE_APPROVAL
```

Le mode immédiat demeure `DOCUMENTATION_ONLY_NO_FIXTURE`. Les futurs appels évaluent des déclarations, bindings et autorisations ; ils ne lisent pas le document référencé, ne qualifient aucun payload et ne réalisent aucun export. Le futur script peut conserver une représentation structurelle des résultats seulement sous la portée explicite d'E et de la décision lot 4. Aucune preuve d'opération réelle n'est créée dans le lot 2.

Le lot 2 peut se conclure par un dossier complet avec des actions localement bloquées. La complétude des recettes ne vaut pas matérialisation du candidat ni readiness d'exécution.

## 2. Acteurs et accès technique à l'hôte

| Acteur | Fonction dans le lot 2 | Restriction |
|---|---|---|
| PROJECT_OWNER | Opérateur de l'hôte ; ratifie les contenus figés ; émet E en L2-G | Seul à exécuter des commandes sur la VM |
| Builder | Session désignée par Owner, distincte d'Astra | Construit, transcrit, calcule et teste dans le périmètre défini ; aucune action sur la VM |
| Astra | Aucune construction ni exécution dans le lot 2 | Revue lot 1 indépendante, puis revue lot 3 ; éventuelle approbation de release distincte ; ne sert pas de Builder |

La désignation de la session Builder est consignée par Owner sans inventer une identité technique authentifiée. Les tokens documentaires de Blue, Astra et Owner restent ceux de D §14.2D. La vérification de l'origine des autorisations et de la correspondance des sessions demeure un prérequis externe d'une future opération.

Après ratification, l'accès SSH existant de l'opérateur et l'usage de son sudo existant sont permis uniquement pour L2-A. Cette exception technique permet le constat initial de l'hôte ; elle ne dépend pas circulairement d'un constat qui exigerait déjà cet accès. Elle n'autorise ni collecte de secrets, ni usage d'un credential opérationnel A2, ni accès à la console ou aux clés Oracle Cloud. L'accès SSH du lot 4 devra être couvert par la décision lot 4.

L'absence de données réelles et de credentials opérationnels est examinée dans les limites du constat autorisé : déclaration Owner, inventaire des emplacements et services et vérification de ce qui est exposé à l'unité, sans ouvrir de payload ni de secret. Une absence exhaustive ne peut être inférée d'un inventaire partiel. Une présence ou une inconnue matérielle bloque la qualification et l'opération ; aucun contenu trouvé n'est inspecté, copié ou publié pour poursuivre.

## 3. Branches, snapshots et mutations

Les branches techniques partent du commit documentaire exact ratifié de la présente décision. Elles ne partent pas d'une référence mouvante ni d'un projet non ratifié.

| Branche | Contenu | Règle |
|---|---|---|
| `builder/weather-v4-a2-lot2-tooling-<date>` | Nouveaux fichiers sous `research/weather_forward/v4/a2_operation/` : `qualification/`, `identity/`, `frozen/`, `verification/`, `operation/`, `evidence/` | Aucun fichier de production du harnais modifié |
| `builder/weather-v4-a2-doc-integration-root-candidate-<date>` | Un seul commit modifiant uniquement `research/weather_forward/v4/a2_harness/trusted_root.py` | Diff limité à O §8.8 et L2-H |

Aucun merge, force-push ou effacement de branche. Le dossier relève les bases, parents, commits et blobs exacts. Les recettes et fichiers provisoires sont distingués des valeurs finales ; aucun placeholder n'est soumis au harnais comme identité résolue.

L2-I assemble les snapshots d'outillage et du candidat dans un répertoire de travail isolé. Les anciens tests et runners sont matérialisés à leurs blobs H, sans modification. Cet assemblage n'est ni un merge ni une activation sur l'hôte.

Le chargement de la root candidate dans un processus de vérification bornée est autorisé seulement par L2-I. Il est distinct de l'activation d'une root utilisable pour une opération réelle sur la VM.

## 4. Actions, conditions et livrables

Une action n'est permise que si la décision est ratifiée, son autorité applicable est résolue, ses prérequis sont satisfaits et ses contrôles propres sont disponibles. L'absence d'un grant de release ne bloque pas la qualification des ressources, l'outillage ou un calcul d'identité déjà autorisé.

### L2-A — Qualification des contrôles de ressources

**Conditions :** ratification de cette décision ; terminal disponible ; accès sudo existant constaté. Indépendante du constat Astra lot 1.

**L2-A0, Builder :** construit les scripts factices, le superviseur de qualification et la procédure O12 §12.6 sous `a2_operation/qualification/`. Les scripts ne chargent pas le harnais et ne représentent aucune fixture de recherche.

**Opérateur :** exécute la procédure sur l'hôte existant désigné par O12. Les commandes, versions et effets sont consignés. Les plafonds ratifiés demeurent 60 s écoulées, 5 s CPU cumulées, un processus sans enfant, 128 MiB de mémoire réelle du cgroup sans swap, 1 MiB d'artefacts temporaires inclus et 64 KiB de sorties cumulées. Les contraintes du traitement contrôlé ne sont pas appliquées par défaut au terminal administratif qui le supervise ; cette séparation est documentée.

**Mutations d'hôte permises :**

- Création de l'utilisateur et groupe dédiés `a2runner`, sans sudo, ni accès supplémentaire à des services. UID et GID réellement attribués sont relevés, jamais supposés.
- Création de `/opt/a2`, dont le code est détenu par l'opérateur et non inscriptible par `a2runner`. Hors unité contrainte, réception fichier par fichier ou checkout partiel restreint des seuls fichiers nécessaires, à leurs chemins relatifs. Chaque fichier est vérifié par `git hash-object` contre son blob épinglé avant usage. Aucun clone ou checkout complet. Pour la qualification : scripts factices ; pour le constat facultatif O12 §12.6.5 : les quatre fichiers H, jamais importés sur l'hôte dans le lot 2.
- Création et montage d'un tmpfs dédié `/srv/a2out`, de taille maximale 1 MiB, mode `0700`, UID/GID numériques de `a2runner`, `nosuid,nodev,noexec`. Il est l'unique emplacement d'artefacts inscriptible du traitement. Les chemins `/tmp`, `/var/tmp` et `/dev/shm` sont rendus inaccessibles ou en lecture seule. Le moyen exact est qualifié et consigné.
- Configuration transitoire de l'unité et des protections existantes nécessaires au plan O12 : temps, CPU, tâches, mémoire, swap, écritures, réseau et absence de core dump. Aucun service permanent, modification de démarrage ou modification de `/etc/fstab` n'est implicitement permis.

Un utilisateur ou chemin déjà présent n'est pas supprimé ou remplacé automatiquement. Une installation de paquet, mise à niveau du noyau, nouvelle infrastructure ou mutation non listée impose STOP sur cette action et une décision Owner.

**Constats :** Ubuntu, systemd, noyau, architecture, cgroup v2 et Python ≥ 3.10 ; statut borné des données et credentials ; séparation effective de `a2runner`. « Il ne lit pas les autres répertoires » signifie ici refus des répertoires étrangers au traitement, avec une allowlist explicite pour `/opt/a2`, l'interpréteur, sa bibliothèque standard, les bibliothèques système et interfaces minimales requises. Aucune preuve d'isolation absolue n'est déduite de la seule création du compte.

**Mémoire :** lire `MemoryPeak` si disponible, sinon `memory.peak` avant disparition du cgroup. Capturer les mesures avant toute collecte/suppression de l'unité. Si aucune mesure admissible n'est disponible : `MEMORY_CONTROL = NOT_VERIFIED`, blocage local et décision Owner.

**Tests :** attente factice de 120 s, boucle CPU, allocation de 200 MiB, création d'enfant, tentative de réseau, écriture de 2 MiB, sortie de 100 KiB, puis témoin positif conforme. Les tentatives d'enfant et de réseau sont des probes explicitement autorisés dont le résultat attendu est un refus ; aucune connexion à une source ou endpoint opérationnel n'est permise. Les scripts, namespaces et protections doivent empêcher toute communication réelle avant cette tentative.

Chaque probe doit atteindre le contrôle visé. Si un autre plafond l'arrête avant, il ne démontre pas la barrière revendiquée. Des variantes factices peuvent être utilisées pour éviter ce masquage ; aucune limite de la future opération n'est relevée et toute variante de qualification est enregistrée.

Pour chaque limite, distinguer `PREVENTED_OR_STOPPED`, `DETECTED_AFTER_BREACH`, `NOT_VERIFIED`. Une mesure après l'arrêt ne prouve pas une prévention à la limite. Le contrôle de sortie qualifie le même chemin borné d'écriture que le futur script, pas seulement un constat a posteriori de taille. Un hook Python ou `PrivateNetwork` déclaré ne constitue pas, seul, la preuve de zéro communication. Les réglages disponibles de l'hôte doivent être éprouvés. Toute relaxation nécessaire des plafonds ratifiés relève d'Owner.

**Livrable :** procédures, profils exacts, commandes et transcripts factices, mesures, liste des mutations et limites. Publication sur la branche d'outillage, sans IP, nom d'hôte public, chemin de secret ou secret. La perte du tmpfs au redémarrage est consignée. Aucune preuve d'opération A2 n'est publiée.

**Effet :** `CONTROL_VERIFIED` par limite seulement si le constat démontre la sémantique requise ; sinon action localement bloquée. Un dépassement admis ne devient pas un succès parce qu'il a été détecté.

### L2-B — Outillage hors production

**Condition :** ratification. Aucun accès Builder à la VM.

1. **Voie H de dérivation :** les fonctions exactes `input_manifest_identity`, `output_manifest_identity`, `harness_policy_identity` de H. Les imports nécessaires de `__init__.py`, `contract.py`, `harness.py` et `trusted_root.py` à H sont permis dans le contexte de calcul. Le module de root H reste deny-all ; aucun appel `evaluate_*` n'est nécessaire pour dériver une identité.
2. **Voie indépendante :** bibliothèque standard `json` + `hashlib`, directement à partir des contenus JSON figés. Cette voie ne réutilise pas les helpers de canonicalisation ni les objets reconstruits par la voie H. Exactement les discriminants, 17/13/12 champs, valeurs d'enum, tris prescrits sans déduplication et chaînes de H ; `ensure_ascii=True`, clés triées, séparateurs `(',', ':')`, UTF-8, SHA-256 et préfixe `sha256:`. Une conversion de transport JSON n'autorise aucune normalisation canonique.
3. **Étalonnage synthétique :** OutputManifest aux treize valeurs exactes du setup de `test_bounded_runtime.py` à H, attendu `sha256:54bfcafcca4d87b9771b905efe9fb12023fdce061fbccda155bcecb3a62253bf`. Référence : `D5_TYPE_REPAIR_CONFIRMED_INITIAL_TEST_OUTPUT_2026-10-05.txt` à H, blob `c334e2e7aa2a8385b426ba5292ece6a3e57a0b63`, ligne 295. Il s'agit d'une valeur déjà publiée dans un transcript initial, pas d'un nouveau digest calculé ici ni d'un PASS de ce transcript. Les deux voies sont étalonnées et tous leurs résultats futurs comparés. L'accord sur un vecteur ne prouve pas à lui seul toute la couverture canonique.
4. **Runner et vérification :** nouveaux fichiers sous `a2_operation/verification/`, lancés avec `-I -S -B`, sources locales épinglées, refus du réseau, des sous-processus, des écritures du processus de test et des lectures non permises. Les imports de bibliothèque standard nécessaires sont explicitement permis ; les caches `.pyc` sont refusés au profit des sources autorisées. Les compteurs distinguent violations, lectures permises et refus attendus de caches. Le hook est un contrôle d'audit du processus, pas une isolation système démontrée.
5. **Script d'opération futur :** sous `a2_operation/operation/`, avec les exigences ci-dessous. Aucun lancement sur la configuration réelle dans le lot 2.

**Script d'opération :**

- Lancement prévu : `python3 -I -S -B -X pycache_prefix=/nonexistent`. Ajout explicite de `/opt/a2` à `sys.path`, sans découverte de modules tiers ni lecture d'un dépôt complet.
- Avant tout import du harnais : vérification des quatre blobs de production contre les épingles exactes finalisées en L2-I, dont le blob candidat de `trusted_root.py` ; refus des caches locaux et de toute lecture hors allowlist. Le code du script, les fichiers de contexte et les épingles sont eux-mêmes identifiés et vérifiés extérieurement à leurs blobs approuvés. Une épingle lue dans un fichier non authentifié ne prouve rien.
- Les fichiers de contexte ne comportent que valeurs figées, références d'E, contrôles et preuves documentaires admissibles. L'artefact d'approbation de release, inexistant avant lot 3, n'est pas simulé ou remplacé par un booléen choisi par Builder. Le script possède dès lot 2 un chemin explicite « preuve absente : aucun second appel » ; le contexte final du lot 4 pourra apporter les références réelles dans le schéma déjà revu, sans mutation implicite des manifests/policy.
- Construction exacte de `AuthorityBinding`, `HarnessPolicy`, `A2Harness`, journal initial, déclarations de rôles, autorisation READ_INPUT et contexte de journal. Aucun droit n'est déduit d'un token de rôle. Un objet RELEASE_OUTPUT AUTHORIZED est construit seulement lorsque les conditions externes d'E sont satisfaites, notamment l'approbation attribuable d'Astra. D2 n'en dispose pas.
- Un seul `evaluate_input_read`. Prédicat conforme à D §14.9D rectifié par §14.14.5 : type attendu, VALID, PERMIT, quarantaine CLEAR, **release BLOCKED**, COMPLETED, aucun stop_reason, code fixe approuvé, acquittement exactement `True`, enregistrement unique et contexte exact. Les sept champs de décision sont vérifiés séparément ; seuls les trois états partagés sont comparés au record. Le record n'est pas un objet égal à la décision entière.
- Puis, uniquement si ce prédicat et tous les prérequis propres à la release sont satisfaits : un `evaluate_output_release`, avec `first_result.log`, un ID distinct et vérification du prédicat output complet de D. Pas de retry. Un défaut exclusivement lié à une release non autorisée n'invalide pas rétroactivement un input valide.
- Sérialisation déterministe limitée aux quinze éléments exacts de D §14.2B, sans champ supplémentaire, mesure de ressource, traceback, texte libre ou code hors périmètre accepté. Nom final unique fixé dans E, sous `/srv/a2out`. UTF-8 ; au plus 65 536 octets pour l'ensemble des résultats, journal, vérifications et diagnostics. La sortie est validée en mémoire avant écriture ; l'écriture est bornée, n'écrase aucun résultat préexistant et ne laisse pas un fichier partiel présentable comme résultat final.
- Hook d'opération distinct du hook de test : il permet seulement l'écriture bornée du résultat autorisé, et les éventuelles opérations temporaires explicitement prévues, dans le plafond total de 1 MiB. Il ne reprend pas une règle générale « toute écriture interdite » qui empêcherait ce résultat.
- Aucune sortie de contenu sur stdout/stderr. L'unité future supprime ces deux canaux dès le démarrage, ainsi que les core dumps : le gestionnaire d'exceptions du script ne couvre pas une erreur de démarrage, d'import initial ou un arrêt par signal. Aucun traceback n'est conservé dans le journal hôte comme preuve A2.

| Code prévu | Signification après vérification interne |
|---|---|
| `0` | Fin normale après input valide et omission de release faute de prérequis propres à celle-ci |
| `10` | Second appel terminé avec release AUTHORIZED et liaison vérifiée ; pas, à lui seul, une permission d'ouvrir le fichier |
| `30` | STOP : prédicat, contexte, liaison ou code inattendu |
| `40` | Exception capturable ; aucune sortie de contenu |
| `50` | Résultat au-delà de 64 KiB ; aucune écriture de résultat final |

Un signal, timeout, OOM, code non prévu ou erreur de lancement n'est pas remappé artificiellement en fin normale. Un défaut de contrôle interdit l'ouverture ou le transfert, même avec un résultat du script apparemment positif. Les effets et révélations de ces codes sont traités en §6.

La logique de séquence, de sérialisation, d'absence d'approbation, d'écriture bornée et de sortie est testée uniquement sur des objets synthétiques aux identifiants manifestement synthétiques. Les imports, constructions d'objets et calculs synthétiques nécessaires à L2-B sont explicitement permis après ratification ; la computation des identités réelles reste conditionnée à L2-E/L2-F. L'égalité des valeurs réelles transcrites avec les contenus ratifiés et E est vérifiée sans exécuter cette opération.

Les objets de contrôle sont déterministes, non économiques, non calibrés sur données ou information d'efficacité réelles et jamais promus en fixture ou preuve de recherche. Les objets structurels des anciens tests, y compris leur provenance factice, restent soumis aux règles TST et à ce périmètre nouveau ; ils ne sont pas des fixtures A2.

### L2-C — Gel du contenu input

**Conditions :** L1 publié et adopté par Owner avec `INPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED` ; disposition Owner des limites O §8.7 qui affectent le contenu input.

Builder transcrit les dix-sept valeurs de D §14.2A dans un JSON sous `a2_operation/frozen/`. Seul `efficacy_leakage_assessment` devient `CLEAR`, sur la base du constat. Owner ratifie le fichier à son commit et blob exacts ; cet acte constitue le gel. Une simple transcription ou ratification de la méthode ne vaut pas gel permissif.

Si la condition manque, aucun gel input permissif. La source H refuse un input dont le leakage n'est pas CLEAR (`harness.py`, lignes 457–458). Un calcul éventuel sur UNRESOLVED ne contournerait pas ce refus et n'est pas substitué au présent chemin.

### L2-D — Gel du contenu output et choix D1/D2

**Conditions communes :** L1 publié et adopté ; disposition Owner des limites O §8.7 concernant l'output, notamment accès/custody, compatibilité du texte canonique de rétention avec les capacités disponibles et disponibilité ou limite expressément acceptée du mécanisme d'incident. La rétention de résultats non lus doit être explicitement compatible avec O §8.4 ou sa disposition ratifiée, sans prétendre avoir qualifié une suppression historique complète.

| Chemin | Disponible seulement si | Contenu figé |
|---|---|---|
| D1 — chemin complet candidat | `OUTPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED`, `CUMULATIVE_DISCLOSURE_FINDING = CLEAR_SUPPORTED`, `QUARANTINE_RECOMMENDATION = LIFT_RECOMMENDED_FOR_OWNER_DECISION`, diagnostics explicitement acceptés et levée expresse de la quarantaine par Owner | Treize champs de D §14.2B ; leakage, cumul et quarantaine deviennent CLEAR ; tout éventuel nouveau texte canonique relève de la disposition explicite ci-dessous |
| D2 — évaluation input seule candidate | Les conditions communes sont remplies mais D1 ne l'est pas ; choix explicite Owner | Valeurs de D §14.2B conservées, sauf éventuel nouveau texte canonique expressément ratifié ci-dessous ; états non permissifs inchangés : leakage et cumul UNRESOLVED, quarantaine BLOCKED_PENDING_OWNER_REVIEW |

La seule absence d'une mention `NOT_ACCEPTED` n'est pas une acceptation des diagnostics. Un constat absent, ambigu ou UNRESOLVED bloque D1. Il ne bloque pas les travaux indépendants.

Builder transcrit ; Owner ratifie le JSON exact et le chemin choisi. Tout nouveau texte de rétention/incident doit être ratifié avant ce gel et traité comme changement canonique. Les chaînes `exact_metric_or_artifact` et `granularity` demeurent exactement celles de D, sauf décision matérielle explicite ; aucune synthèse conceptuelle ne les remplace.

Le texte actuel de `retention_rule` nomme la destination documentaire O §8.4. Une garde locale non lue avant release n'est donc pas substituée silencieusement à cette destination. Owner dispose expressément sa compatibilité comme retenue préalable ; si un changement du texte canonique est nécessaire pour D2 ou D1, il est ratifié avant gel puis couvert par la nouvelle identité output. Le choix D2 seul ne résout pas cette compatibilité.

Sur D2, l'identité output est nécessaire pour compléter la policy, mais elle ne rend pas la sortie libérable. Le résultat input fait partie du rapport structurel : aucun destinataire ne peut en lire le contenu sans une release autorisée. La garde non lue par Owner n'est pas une release. La preuve observable D2 est limitée au canal de contrôle accepté, aux contrôles et à l'intégrité des sources ; elle ne fournit pas une observation humaine des décisions ou du journal retenus.

Passer ultérieurement de D2 à D1 impose les nouveaux gels/identités/bindings, E, candidat et revue rendus nécessaires par ce changement. Ce n'est pas un déblocage automatique du fichier D2 déjà retenu ; toute éventuelle release de ce fichier exige une portée et des preuves propres.

Les ratifications L2-C et L2-D et les dispositions liées à L1 peuvent être consignées dans un même acte Owner nommant chaque fichier exact. Aucun nouveau cycle de ratification des valeurs déjà ratifiées n'est créé.

### L2-E — Calcul des identités input et output

Chaque calcul dépend de **son propre gel** ratifié, de la méthode L2-B vérifiée et des sources H exactes. Il peut avancer sans attendre l'autre gel. L2-F attend en revanche les deux identités.

Les deux voies doivent donner le même résultat pour chaque manifest. Enregistrer contenu canonique, méthode, source, environnement et résultat ; un écart ou étalonnage manqué impose STOP sur le calcul et les bindings dépendants. Aucun digest n'est choisi par Owner.

Imports transitifs des quatre modules H autorisés uniquement pour cette dérivation. Aucune root candidate importée, injectée, instanciée ou activée dans ce contexte ; aucun appel `evaluate_*`.

### L2-F — Complétion, gel et calcul de la policy

**Condition :** deux identités L2-E vérifiées.

Builder transcrit les dix valeurs non dérivées de D §14.2C et les deux identités. Owner ratifie les douze champs exacts à leur commit/blob : c'est le gel de policy. Les deux voies calculent ensuite `harness_policy_identity` et doivent concorder.

C reste `expected_owner_authority_sha`. Le nouveau grant Builder n'efface pas cette autorité de construction historique. Aucun workflow, contrôle externe ou rôle n'est ajouté aux douze champs. Une insertion conforme à la recette approuvée n'est pas une mutation arbitraire ; tout autre changement matériel exige revalidation et re-gel.

### L2-G — Configuration finale et autorité d'exécution E

**Condition :** L2-F terminé et vérifié.

Owner ratifie la configuration finale et ses trois identités, puis publie et ratifie E selon l'annexe A. Cette décision lot 2 ne se substitue pas à E. L'émission d'E et la ratification finale peuvent être consignées ensemble, à leurs identités exactes.

Le SHA définitif d'E est nécessaire avant construction du candidat : `execution_policy_authority_sha` dans la root et `authority_sha` dans les ActionAuthorization doivent concorder. E n'inscrit pas son propre SHA dans son propre contenu. Builder attend E pour matérialiser la root ; les actions indépendantes continuent.

E définit une autorité conditionnelle future : sa publication ne rend pas ses conditions vraies et ne permet aucun appel réel dans le lot 2. Le harnais ne vérifie pas les conditions suspensives de l'annexe A ; leur prise d'effet relève des contrôles externes.

### L2-H — Construction du candidat trusted root

**Conditions :** E définitive et ratifiée ; identités vérifiées ; base et session Builder exactes.

Un seul commit sur la branche candidate, ne modifiant que `trusted_root.py` :

- `CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY` reçoit le SHA exact d'E.
- `CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT` reçoit un `TrustedExecutionPolicyRoot` construit par arguments nommés.
- Le résolveur, qui renvoie actuellement le littéral `None`, renvoie la constante de root.
- Annotations et docstrings de ce fichier sont mises en cohérence.

| Champ de root | Valeur |
|---|---|
| `execution_policy_authority_sha` | SHA exact d'E |
| `expected_construction_authority_sha` | `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` |
| `expected_harness_identity` | `research/weather_forward/v4/a2_harness` |
| `expected_harness_version_or_commit_identity` | `weather-v4-a2-doc-integration-v1` |
| `expected_policy_identity` | Identité finale L2-F |

Aucun setter, surcharge par environnement/configuration, repli permissif ou promotion de root de test. Le token n'est pas un commit et ne prouve pas le code chargé. `__init__.py` et `README.md` conservent leurs passages historiques décrivant la root absente ; cette discordance documentaire est explicitement relevée dans le dossier de transition, sans modifier ces fichiers hors périmètre.

Existence du candidat, import de vérification et PASS indépendant ne constituent pas une activation sur la VM.

### L2-I — Vérifications ciblées du candidat

**Conditions :** candidat construit ; sources et outillage épinglés. Exécution Builder hors ligne, limite externe de 600 s par lancement, distincte des plafonds de la future opération. Les réparations des nouveaux fichiers d'outillage et leurs reruns sont permises dans ce périmètre ; cela n'autorise aucun retry d'opération réelle ni correction de production hors L2-H.

**Anciennes suites :** aucune modification ou omission. Identités à H :

| Fichier | Blob |
|---|---|
| `test_bounded_runtime.py` | `aa0159c2a470da034c6611e207687997294fb236` |
| `test_d5_public_state_types.py` | `52bb94ed7fa497bb9756afe02052b855dcd3d9f5` |
| `run_bounded_runtime_tests.py` | `25b7d3bde54e412a51df45059a65283479420725` |
| `run_d5_type_regression_tests.py` | `f660a24d969e50db62ed6165c15272d90cb86b4b` |

Les anciens runners s'arrêtent avant les tests sur `PRODUCTION_TRUSTED_ROOT_MODIFIED` avec leur option de réparation, ou `AUDITED_SOURCE_BYTES_MISMATCH` sans elle. Consigner ces refus attendus ; aucun drapeau ne les contourne et aucun runner ancien n'est réécrit.

Le nouveau runner exécute les 279 tests anciens (145 + 134). Prévision statique des trois incompatibilités avec une root candidate présente :

| Identifiant complet, préfixe `research.weather_forward.v4.a2_harness.test_bounded_runtime.` | Signature prévue |
|---|---|
| `TrustedRootTests.test_production_root_absent_denies_all_authority_bearing_paths` | Assertion d'absence de la constante, ligne 198 |
| `TrustedRootTests.test_coordinated_caller_substitution_cannot_create_production_root` | Refus toujours DENY/BLOCKED/non-VALID ; motif EXECUTION_POLICY_ROOT_MISMATCH au lieu de MISSING_EXECUTION_POLICY_ROOT, assertion ligne 179 appelée ligne 212 |
| `TrustedRootTests.test_test_only_root_exercises_positive_paths_and_is_restored` | Assertion d'absence après restauration de la root de test, ligne 227 |

Ces trois résultats sont une **prévision de source**, pas des observations. Un simple accord sur trois identifiants ne suffit pas : vérifier type, assertion, motif, contexte/restauration et invariants associés. Toute autre signature, erreur, skip ou changement de collecte est un échec de vérification. Les nouvelles assertions sur la root remplacent la couverture devenue inapplicable, pas les tests anciens eux-mêmes.

Le sous-ensemble ancien est conforme au critère prévu seulement si 279 tests sont collectés/exécutés, 276 réussissent, exactement ces trois différences motivées existent, zéro erreur/skip/expectedFailure/unexpectedSuccess et zéro tentative réseau, sous-processus ou fichier interdit. Les lectures autorisées et refus attendus de caches peuvent être non nuls ; ce ne sont pas des violations à exiger à zéro. Le verdict est `LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED`, jamais « 279 tests verts ».

**Nouveaux tests et séparation des contextes :**

1. Vérifier que constantes, résolveur et tuple de la root réelle sont exactement ceux de L2-H. Les refus de construction, composant, version ou policy discordants sont exercés sur cette root, avec le seul écart annoncé.
2. Pour les cas d'acteur/autorité : les déclarations opérationnelles réelles peuvent servir de référence, mais aucune ActionAuthorization AUTHORIZED citant E n'est utilisée avec la root réelle et les manifests/policy réels pour un appel `evaluate_*`. Les cas autorisés sont des contextes volontairement non autorisés ou discordants, dont le refus est atteint avant toute permission. Tout appel sur le tuple réel complet autorisé est interdit.
3. Les barrières tardives — quarantaine, leakage/disclosure, ledger, défaut de journal/acquittement et séquence positive — utilisent exclusivement root et objets synthétiques, aux identifiants synthétiques et sans autorité E. Leur preuve est une preuve de sémantique, pas une preuve d'exécution permissive de la configuration réelle.
4. Sur D2, la root réelle ne peut pas atteindre `OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE` sans franchir l'autorisation de release, vérifiée auparavant par H. Le lot 2 **ne franchit pas cette autorisation** : constat statique du blocage canonique D2 et test synthétique de la barrière de quarantaine. Un refus plus précoce sur la root réelle ne certifie pas la quarantaine ; aucune barrière suivante n'est déclarée couverte par lui.
5. Tester la logique et les codes du script d'opération sur objets synthétiques, y compris succès input avec release BLOCKED, absence de grant/proof de release, préservation du premier record, second ID distinct, codes inattendus, exceptions et limites de sortie. Le profil réel d'écriture et d'absence de stdout/stderr est qualifié sur scripts factices en L2-A.

Les mocks sont limités aux dépendances synthétiques explicitement testées ; ils ne remplacent pas la barrière de production revendiquée. Tout test négatif identifie sa barrière, ses prérequis, l'écart unique et le refus observé. Si elle n'est pas atteinte, la couverture reste NON_DÉMONTRÉE. Un PERMIT sur la configuration réelle est un STOP ; un PERMIT sur un témoin synthétique autorisé n'est pas une opération A2.

Le verdict du nouveau runner distingue le sous-ensemble ancien et les nouveaux tests, qui doivent tous réussir, sans erreur ou skip ni violation d'audit. Un code de runner `0` signifie conformité à ce critère composé, pas succès de toutes les assertions anciennes.

Comparer Python et architecture Builder/hôte. Un écart non testé est consigné comme limite pour le lot 3 et peut bloquer l'exécution ; il n'est pas accepté implicitement. Aucun replay sur la VM n'est autorisé par L2-I.

### L2-J — Dossier de preuves et remise

Remise à Owner, puis à Astra pour lot 3, de : branches/bases/parents/commits/diffs exacts ; blobs avant/après ; snapshots assemblés ; contenus figés et ratifications ; trois identités par les deux méthodes et étalonnage ; E ; commandes numérotées ; versions Python/système/architecture ; résultats anciens avec leurs trois différences ; tous nouveaux tests et couverture atteinte/non atteinte ; compteurs d'audit détaillés ; constats/transcripts/mutations de L2-A ; épingles finales du script et du contexte ; limites de visibilité, custody, rétention et identité chargée.

Les preuves de qualification factice et de tests synthétiques peuvent être publiées sur la branche d'outillage après retrait des secrets et identifiants d'hôte. Ce sont des preuves techniques du lot 2, pas des preuves d'une opération réelle. Les contenus réels figés de configuration sont documentaires, pas des payloads.

Le dossier complet peut mentionner un candidat ou une action non matérialisé. Il sépare `LOT2_PREPARATION_COMPLETE_WITH_LOCAL_BLOCKERS` de `LOT2_CANDIDATE_AND_EVIDENCE_READY_FOR_ASTRA_LOT3`. Le second exige candidat, ratifications, identités et vérifications requises réellement disponibles. Aucun PASS Astra n'est écrit par Builder.

## 5. Fichiers modifiables et artefacts Owner

| Chemin | Branche | Actions |
|---|---|---|
| `research/weather_forward/v4/a2_harness/trusted_root.py` | Candidate, un seul commit | L2-H |
| `research/weather_forward/v4/a2_operation/` (nouveau) | Outillage | L2-A0, L2-B, transcriptions L2-C/L2-D, L2-E/L2-F, L2-I/L2-J |

Builder ne modifie pas `contract.py`, `harness.py`, `__init__.py`, `README.md`, anciens tests/runners, autres fichiers de `a2_harness/`, `src/`, Gate-B, fixtures ou artefacts Owner/Blue/Astra.

Owner consigne les ratifications, dispositions L1 et E dans ses propres artefacts de gouvernance. Cette compétence Owner ne devient pas une permission Builder de signer, ratifier ou modifier ces fichiers. Les snapshots de calcul et vérification restent exacts malgré des commits documentaires situés sur d'autres branches.

## 6. Visibilité, custody et effets des codes

Owner est opérateur, custodian et unique destinataire, avec des droits administrateur. La retenue du contenu envers lui est **procédurale**, pas une ACL qui l'empêcherait techniquement de lire. Cette limite est soumise à Astra lot 3 et à la décision d'activation ; aucune suppression ou protection parfaite n'est revendiquée.

Avant release, seules les informations de contrôle explicitement admises sont présentées : code de sortie et mesures de contrôle. Le fichier résultat, sa représentation, son empreinte SHA-256 et ses traces ne sont pas affichés ou transmis avant release. L'empreinte peut permettre des inférences lorsque le contenu appartient à un ensemble prévisible ; elle n'est pas traitée comme automatiquement sûre.

Astra lot 3 évalue le canal de contrôle complet : codes `0/10/30/40/50`, signaux/erreurs d'unité, existence ou absence de résultat et mesures de contrôle visibles. Ce canal n'est pas résumé à « un bit ». Ses éléments restent séparés des quinze champs du rapport. Un élément non admis est supprimé du canal ou bloque l'opération ; il n'est pas réputé accepté par le seul constat L1.

- **D1 :** ouverture seulement après code `10`, vérification interne des deux liaisons, fin normale de l'unité, contrôles post-opération conformes, approbation Astra attribuable, prise d'effet complète d'E et autorité d'activation/opération lot 4. Ensuite seulement, transfert par Owner selon E vers la destination O §8.4. Le code `10` seul ne suffit pas.
- **D2, ou D1 sans prérequis de release :** aucun contenu ouvert ou transféré. Garde non lue sur l'hôte, au plus 30 jours calendaires après clôture, sans extension automatique, selon la disposition de custody ratifiée avant gel. Perte au redémarrage du tmpfs consignée ; elle ne démontre pas une purge contrôlée. Toute lecture ou communication ultérieure exige une portée de release propre. La rétention et suppression du fichier local ne démontrent aucune suppression de versions historiques dans une destination documentaire.
- **STOP/exception/limite dépassée :** pas d'ouverture du contenu, ni de traceback divulgué. Seulement classe/référence d'incident sûre et contrôles admis selon O §8.5 et E ; aucune investigation de payload ni reprise automatique.

Les résultats retenus restent des preuves d'exécution non consultées. Un succès de vérification interne n'est pas transformé en inspection indépendante de leur contenu par Owner ou Astra. Cette limitation demeure explicite au lot 3 et dans le compte rendu lot 4.

## 7. Interdits du lot 2

Activation sur la VM ; appels sur le tuple réel complet autorisé ; lancement du script avec la configuration réelle ; fixture de recherche ou payload ; données ou métadonnées opérationnelles réelles ; endpoint ou credential opérationnel ; réseau d'un processus de calcul/test/A2 ; dépendance hors bibliothèque standard ; nouvelle dépense ; merge, force-push ou suppression de branche ; publication GitHub de preuves d'opération A2, dont aucune n'est produite ici.

Les probes factices L2-A refusés, accès administratif SSH précisément autorisé et transferts de seuls fichiers de gouvernance/code hors unité sont les exceptions techniques énumérées, pas une permission opérationnelle générale.

## 8. Blocages locaux et STOP

Blocage de l'action et de ses dépendants en cas d'autorité absente/ambiguë, valeur à inventer, freeze manquant, divergence de calcul, étalonnage échoué, contrôle indisponible/non démontré, test masqué, résultat ou contexte inattendu, versions non réconciliées, mutation d'hôte non listée ou besoin de paquet/infrastructure. Les travaux indépendants autorisés continuent.

Tout changement canonique invalide les identités et bindings affectés, impose re-gel et recalcul autorisés. Un changement de fichier épinglé invalide la preuve correspondante ; il ne reste pas couvert par une ancienne revue.

Un accès interdit, secret/donnée réelle apparu dans le traitement, mutation hors scope, approbation simulée ou PERMIT sur configuration réelle constitue une violation : arrêt du traitement concerné, conservation de références sûres seulement et rapport à Owner. Aucune poursuite qui réutiliserait le contexte compromis. Une ambiguïté de l'autorité gouvernante bloque toutes les actions qui en dépendent. Aucun contournement.

## 9. Statuts conditionnels et prochain travail

### Avant ratification du présent projet

```text
EFFECT_BEFORE_RATIFICATION = NONE
CONTROL_QUALIFICATION_AUTHORIZED = FALSE
BUILDER_AUTHORIZED = FALSE
IDENTITY_COMPUTATION_AUTHORIZED = FALSE
HARNESS_IMPORT_AUTHORIZED_BY_THIS_PROJECT = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
```

### Après ratification, sous les conditions de chaque action

```text
CONTROL_QUALIFICATION_AUTHORIZED = TRUE_FOR_L2_A_ONLY
O12_SECTIONS_12_4_AND_12_6_ADOPTED = TRUE_WITHIN_THIS_DECISION
BUILDER_AUTHORIZED = TRUE_FOR_L2_A0_B_C_D_TRANSCRIPTION_E_F_H_I_J_EXACT_SCOPE_ONLY
INPUT_FREEZE = OWNER_RATIFICATION_CONDITIONAL_ON_L1_INPUT_CLEAR_SUPPORTED_AND_O_8_7_DISPOSITION
OUTPUT_FREEZE = OWNER_RATIFICATION_CONDITIONAL_ON_L1_O_8_7_DISPOSITION_AND_D1_OR_D2_CHOICE
IDENTITY_COMPUTATION_AUTHORIZED = PER_IDENTITY_CONDITIONAL_ON_ITS_RATIFIED_FREEZE
HARNESS_IMPORT_AUTHORIZED = L2_B_SYNTHETIC_CALIBRATION_AND_TESTS_L2_E_F_DERIVATION_AND_L2_I_ONLY
TRUSTED_ROOT_CANDIDATE_AUTHORIZED = CONDITIONAL_ON_FINAL_RATIFIED_E_AND_VERIFIED_IDENTITIES
EXECUTION_AUTHORITY_E = TO_BE_ISSUED_AND_RATIFIED_BY_OWNER_AT_L2_G
RELEASE_APPROVAL = SEPARATE_ATTRIBUTABLE_ASTRA_ARTIFACT_REQUIRED_FOR_D1
CONTROL_VERIFIED = NOT_ESTABLISHED_BY_RATIFICATION
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED_BY_LOT2 = FALSE
A2_RESEARCH_FIXTURE_AUTHORIZED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
REAL_DATA_ACCESS_AUTHORIZED = FALSE
REAL_OPERATIONAL_METADATA_ACCESS_AUTHORIZED = FALSE
OPERATIONAL_ENDPOINT_ACCESS_AUTHORIZED = FALSE
OPERATIONAL_CREDENTIAL_USE_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

`A2_EXECUTION_AUTHORIZED_BY_LOT2 = FALSE` reste vrai après émission d'E : un éventuel droit conditionnel ultérieur est attribué à E et à la décision lot 4, jamais déduit de cette décision technique.

Après ratification : `NEXT_SAFE_ACTION = L2_A_QUALIFICATION_AND_L2_B_TOOLING_IN_PARALLEL_WITH_ASTRA_LOT1`.

## Annexe A — Autorité d'exécution E, à émettre en L2-G

E est un fichier Owner distinct, définitif et explicitement ratifié après calcul de la policy. L'artefact comporte les éléments suivants, sans références SHA inventées ou auto-référentielles.

1. **Objet et prise d'effet.** Autorité future conditionnelle pour le binding de root et une seule opération bornée, D1 ou D2. Elle ne prend effet qu'après satisfaction de toutes les conditions applicables ci-dessous et décision Owner lot 4. Le grant technique lot 2 n'active pas ces conditions. E ne contient pas son propre SHA ; son commit exact est enregistré extérieurement et incorporé au candidat.
2. **Identités.** Les trois identités finales, leurs fichiers/commits/blobs et gels ; C ; `research/weather_forward/v4/a2_harness` ; `weather-v4-a2-doc-integration-v1` ; `A2-DOC-INTEGRATION-MANIFEST-V1` ; choix D1/D2. Ne pas lier E à un futur commit candidat encore inconnu comme si son SHA existait ; celui-ci sera nommé par la décision d'activation après construction/revue.
3. **Actions.** READ_INPUT : `a2-doc-v1-read-input-blue`, acteur `blue.weather-v4.a2.doc-integration.v1`, rôle EXECUTOR, AUTHORIZED seulement à la prise d'effet pour l'opération unique. D1 seulement : RELEASE_OUTPUT, `a2-doc-v1-release-output-astra`, acteur `astra.weather-v4.a2.doc-integration.v1`, rôle RELEASE_APPROVER, AUTHORIZED seulement si sa preuve propre est disponible. Le destinataire est `project-owner.weather-v4.a2.doc-integration.v1`, RESEARCH_VIEWER, distinct d'Astra. D2 n'autorise aucun second appel.
4. **Contexte.** Journal initial vide ; INPUT_LOG_RECORD_ID fixé ; OUTPUT_LOG_RECORD_ID distinct fixé sur D1 ; contexte d'incident fixé sans inventer un incident survenu ; nom unique de résultat. Sur D1, les records de ledger doivent avoir une justification documentaire attribuable dans L1 pour le tuple exact. Si L1 fournit `LEDGER_RECORDS_SUPPORTED`, reproduire exactement ses champs `output_id`, `recipient_actor_id`, `recipient_role`, `cumulative_safety` et leur portée ; Owner attribue seulement les `disclosure_id`, uniques et liés. Un constat CLEAR sans records explicitement justifiés n'autorise pas Builder à créer une histoire. L'absence de records admissibles bloque D1 seulement. Ni histoire vide ni couverture inconnue matériellement pertinente ne sont converties en CLEAR.
5. **Conditions communes avant READ_INPUT.** PASS Astra lot 3 sur snapshots exacts candidat/outillage/contexte et limites ; contrôles L2-A réellement disponibles/conformes ; custody et rétention compatibles avec le chemin choisi ; mécanisme d'incident disponible ; origine des autorisations et correspondance de session vérifiées ; code chargé constaté sur l'hôte contre les blobs candidats/outillage approuvés ; dispositions applicables A1 §5 attestées, fixture-generation non applicable à ce mode et jamais implicitement autorisée ; canal de diagnostic/contrôle admis ; décision Owner d'activation/opération nommant candidat, blobs, contexte, profils et chemins exacts ; plafonds O §8.3 et visibilité §6 ; une opération sans retry. Les conditions de destination/release propres à D1 ne deviennent pas des prérequis READ_INPUT sur D2.
6. **Conditions additionnelles avant RELEASE_OUTPUT.** D1 ; output/ledger/quarantaine libérables ; approbation de release Astra dans un artefact distinct, publié après lot 3 et nommant identités output/policy, ledger exact, tuple, E et périmètre de divulgation ; accès, conservation/suppression et mécanisme d'incident nécessaires à la destination O §8.4 disponibles ; prédicat input et sa liaison exacte vérifiés. Aucun booléen ou rôle ne remplace l'artefact attribuable. Si une condition manque, omettre le second appel ; une fin input normale ne devient pas STOP pour cette seule absence.
7. **Portée d'écriture et transfert.** E autorise, à sa prise d'effet et sous décision lot 4, une écriture structurelle bornée sous `/srv/a2out` selon le script revu. Sur D1 seulement et après toutes les vérifications §6, transfert par Owner vers le fichier natif existant `OWNER_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`, identité `libfile_4f09286d65ac8191a6e343b85aff696e`, section `EVIDENCE_A2_DOC_INTEGRATION_V1`. Aucun autre partage/export/GitHub. Sur D2 : custody locale non lue uniquement, avec règle exacte de suppression, perte et incident ratifiée. La simple garde ne permet aucune consultation.
8. **Exclusions.** E n'active pas elle-même la root, ne vaut pas approbation de release, n'autorise aucune autre opération/cible, aucune fixture, donnée réelle, collecte, endpoint, credential opérationnel ou économie. Une nouvelle activation/target ou modification canonique n'est pas couverte silencieusement.

Le commit d'E est inscrit dans la root et les autorisations qui l'utilisent. Ses conditions suspensives sont contrôlées extérieurement : le code H compare les identités et les états déclarés, il ne connaît pas les décisions Owner lot 3/lot 4 ou l'authenticité de leur origine.

## Note de vérification documentaire de cette version

Cette finalisation a relu les blobs référencés, les fonctions de dérivation et d'autorisation, les prédicats D, les suites/runners historiques et les chaînes ratifiées. Elle n'a importé ou exécuté aucun harnais/test, calculé aucun digest de manifest/policy, créé aucun objet runtime/fixture, accédé à l'hôte ou produit une signature Astra.

Les trois échecs prévus, l'efficacité des contrôles et la compatibilité d'exécution restent à démontrer sous les grants appropriés. Les hooks Python sont des moyens d'audit, pas une garantie d'isolation ; voir la [documentation Python `sys.addaudithook`](https://docs.python.org/3/library/sys.html#sys.addaudithook). Les propriétés système sont candidates à qualifier sur la version réelle de l'hôte ; voir les documentations de l'éditeur [systemd.exec](https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml) et [systemd.resource-control](https://github.com/systemd/systemd/blob/main/man/systemd.resource-control.xml).

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
EFFECT_BEFORE_RATIFICATION = NONE
TECHNICAL_ACTIONS_PERFORMED_DURING_DRAFT_FINALIZATION = NONE
NEXT_SAFE_ACTION = OWNER_REVIEW_AND_EXPLICIT_RATIFICATION_OF_THIS_EXACT_LOT2_DRAFT
```
