# Chronologie et réutilisation — état de traitement 2

Audit toujours incomplet. Ce relevé apporte des chaînes datées et des destinations vérifiées ; il ne clôt pas la lecture de toutes les versions ni le devenir de toutes les branches. Les heures ci-dessous sont UTC. Les dates de commit sont distinctes des événements GitHub et du déploiement.

## Évolution des décisions d'audit

| Quand : commit | Trace lue | Ce qui est consigné et son devenir |
|---|---|---|
| 19 octobre, 10:00:06 | racine `d95b52f…`, README/RESUME | Première sauvegarde annoncée locale, hors durabilité distante démontrée ; PR #1 incluse malgré son absence des pointes de branches. Le présent lot conserve de nouveau les objets accessibles, sans prétendre avoir retrouvé les anciens fichiers locaux. |
| 19 octobre, 11:55:58–12:12:11 | CP2–CP4 | OCI ancien divergé ; chemin moderne revu sans exécuteur interne ; protocole visant des workers externes. Ces constats sont datés et scoped, pas des descriptions définitives de tout Quant. |
| 19 octobre, 12:25:54 | CP5 | Collision ASML et absence du ledger dans l'arbre ; interprétation runtime trop générale. |
| 19 octobre, 12:28:05 | CP6 | Correction explicite : des CI matérialisent et vérifient le ledger épinglé. Le défaut du loader générique reste distinct de l'exécution dans ces CI. Réutiliser le bootstrap existant, sans reconstruire une mémoire à partir de l'absence du fichier committé. |
| 19 octobre, 13:03:25–13:06:21 | CP7–CP9 | Déduplication/corpus/readiness et exigences Oracle définis ; rails VM/OCI classés. CP8 est une matrice d'acceptation, pas un runner. |
| 20 octobre, 01:16:53 | CP10 | Réconciliation contre Oracle V1 : bootstrap, normalisation, écrans candidats, blocage des overlaps et runtime déclarés réparés dans le chemin qualifié. Les conclusions CP7–CP9 ne sont plus toutes des travaux à refaire. La couverture scientifique globale reste partielle. |
| 20 octobre, 01:29:44 puis 02:21:10 | CP11 puis CP12 | Le premier plan de réduction est remplacé par une réconciliation préalable des capacités, résultats et décisions. Le script destructif CP11 n'est pas une instruction courante. |
| 20 octobre, 11:25:35–13:20:50 | CP13–CP14 | V2 actif et qualification rapportés ; raccordement Site et reboot V2 distingués ; Capital Desk/Book décrits comme hérités, pas comme absents. Ce sont des observations historiques à confronter aux preuves exactes et à l'état actuel. |
| 20 octobre, 14:03:29 puis 14:20:47 | CP15 puis CP16 | Les spécifications d'approfondissement deviennent explicitement des hypothèses à challenger ; les chantiers fermeture et amélioration passent en parallèle puis convergent. L'ancien ordre strictement séquentiel n'est plus l'ordre enregistré. |

Les 15 premières publications CP2–CP16, leurs dates auteur/committer, acteurs Git et blobs lus sont dans `audit-decision-chronology.csv`. Ces dates prouvent l'enregistrement des documents dans Git ; elles n'authentifient pas seules les événements Owner ou VM rapportés à l'intérieur.

## Construction → intégration → descendants

| Construction | Intégration observée | Destination réutilisable et limite |
|---|---|---|
| Mega B | `42203de5…`, 21 octobre 19:19:51 | Deux modules Discovery et cinq modules de tests importés, parmi neuf fichiers modifiés. Le checkpoint déclare un port sémantique depuis `ba80b8cd…`, pas une fusion complète du rail source. |
| Mega D0 | `a0ba421c…`, 21 octobre 19:28:02 | Noyau dans `research/research_os/expansion/_economic_lifecycle_d0.py`, adaptateur public `economic_lifecycle.py`. Vérification directe : le noyau a exactement le blob `a56b042a…` du module source au SHA `84aa0f5f…`. L'adaptateur rebind l'identité de campagne ; il ne faut donc pas recopier sans adaptation le seul chemin public de l'ancien rail. |
| Mega C0 | `14926055…`, 21 octobre 19:36:43 | Module canonique `research/research_os/expansion/scientific_adjudication.py`, avec noyau historique conservé séparément. L'interface canonique a ensuite évolué ; sa simple présence ne clôt pas les défauts découverts plus tard. |
| Mega E | `8d7383be…`, 21 octobre 19:48:33 | Port limité à `deploy/oracle_live_projection.py` et un module de tests de reçus live. Ce commit ne crée pas un second scheduler ni un second Oracle. |
| Multi-Source | PR #30, #31 et #33, 21 octobre | Commits de fusion vérifiés ancêtres de Wave2. Conserver les ports/hardening ; l'écart de graphe avec la branche source ne signifie pas que toute la capacité manque. |

Les sept checkpoints de ports Wave2 ont été lus. Leurs PASS déclarés restent liés à leurs SHA et suites ; le lot 1 distingue le cumulatif Wave2 réussi, le gate Mega E échoué et le sceau final non émis.

Le fichier `capability-lineages.csv` suit 14 fichiers des quatre commits de port à travers cinq destinations, soit 70 lignes. Sur Wave2, one-shot, C0 réparé et WP2 : 13 fichiers gardent les mêmes octets, et le module C0 est modifié. Cela établit une conservation ciblée de sources et tests, pas une qualification fonctionnelle de ces quatre arbres. La branche PR #46 fondée sur la branche par défaut a un autre périmètre ; les chemins absents de son arbre ne prouvent pas la disparition des capacités dans le dépôt.

## One-shot et réparations ultérieures

Le 26 octobre à 22:38–22:51 UTC, la lignée ajoute CP01–CP06 : ancrage, gardes CP02, admission CP03, continuation CP04, trace UST CP05 et renouvellement CP06. Ces commit titles sont des traces de construction ; les conclusions fonctionnelles exigent leurs preuves.

Le 27 octobre à 01:47:45 UTC, `68f16c0f…` supprime les modules produit `continuation.py`, `ideation_intake.py`, `renewal_policy.py` et `idea_feed/`, en préservant les tests historiques sous des chemins de replay. Le document de réduction indique qu'ils ne sont pas nécessaires à la mission bornée. La comparaison directe Wave2 → gel produit one-shot laisse trois fichiers produit modifiés : `v2_core.py`, `v2_pipeline.py`, `v2_stage_executor.py`, plus des tests/fixture. Il n'est donc pas exact de traiter CP03/CP04/CP06 comme trois capacités actives automatiquement à réimporter.

À 01:53:02 puis 01:54:36 UTC, les commits candidat et attestation gardent explicitement `NOT_QUALIFIED`, avec un échec de comptage C0. À 02:02:33 UTC, `a8339a02…` modifie le comptage des confirmations. À 02:17:25 UTC, `5dba2d81…` traite la membrane de références, suivi du candidat `c028bc86…`. À 02:21:05 UTC, `13721384…` enregistre l'attestation. Le run final `40437918834` démarre à 02:21:08 UTC et termine en succès au SHA de cette attestation. Le verdict non qualifié du one-shot historique n'est pas réécrit en qualification de toute sa mission.

Le diff gel produit → C0 final comporte, pour `scientific_adjudication.py`, 48 ajouts et 3 suppressions. La portée exacte des réparations est ainsi localisable ; aucun déploiement ni promotion n'est déduit.

## Conservation et avancement

Les deux archives publiées à `ae26de2fa580516a54544bbbdacbab48763a1c5c` ont été retéléchargées par Git, réassemblées et vérifiées par SHA-256 dans un autre répertoire. Les 289 têtes sauvegardées sont ancêtres du commit d'archive. Un nouveau processus a récupéré `resume.json`, les 12 936 lignes documentaires, les 423 objets de discussion et les 275 branches. Cette vérification concerne la reprise de l'audit ; elle ne certifie pas l'autonomie de Quant.

Lecture complète consignée : 35 blobs documentaires ; 1 objet de discussion (le contrat de reconstruction). Les archives d'origine conservent l'état du premier lot ; `reads-overlay.json` et le compteur courant portent l'avancement ultérieur. Le code C0 affiché partiellement et les extraits de logs ne sont pas comptés comme lectures complètes.

Restent notamment : devenir des corrections horizontales/verticales hors fichiers déjà suivis, intégrations CP001–CP099 et Mega A/W1, corpus scientifique juillet–octobre, décisions Owner/commentaires, qualification des branches actuelles et carte finale d'import/rejet/conservation. Aucune décision finale de tronc ou de suppression n'est prise par ce relevé.
