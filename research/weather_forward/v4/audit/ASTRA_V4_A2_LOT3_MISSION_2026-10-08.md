# Mission Astra — Weather V4 A2 — lot 3 — revue indépendante du candidat root

Date : 2026-10-08. Branche Astra visée : `astra/weather-v4-a2-lot3-independent-review-2026-10-08`.

## A. Rôle et indépendance

Tu es une Astra neuve, extérieure à l’équipe A2. Tu n’as participé ni à la décision, ni à l’outillage, ni aux gels, ni aux vérifications, ni à la construction du candidat. Travaille uniquement à partir des objets Git publiés cités ci-dessous et des preuves qu’ils contiennent. Ne reçois pas les échanges internes de l’équipe. Toute assertion doit être reproduite ou classée non établie.

## B. Objet exact et autorité de la revue

Effectue la revue technique indépendante prévue au lot 3 par la décision lot 2 :

- décision et annexe A : `research/weather_forward/v4/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md` au commit `276fd99` ;
- constat indépendant du lot 1 : `research/weather_forward/v4/audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_2026-10-07.md` au commit `52e5ff2` ;
- autorité conditionnelle E, notamment B.5 : `research/weather_forward/v4/owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_D2_2026-10-08.md` au commit `6e0320f15d48a924cef9507af5641e47de9fe938` ;
- outillage L2-B : commit `1910994` ;
- candidat root : `research/weather_forward/v4/a2_harness/trusted_root.py` au commit `73280c3e9d8604b2f2d8e6d2d174aa940389a760`, objet Git exact `73280c3e9d8604b2f2d8e6d2d174aa940389a760:research/weather_forward/v4/a2_harness/trusted_root.py` ;
- vérifications L2-I : objets désignés par le dossier L2-J ci-dessous ;
- dossier de preuves L2-J : branche `builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08`, commit `5358c7ac582b46804be0008cffc78a043751d910`, chemin `research/weather_forward/v4/a2_operation/evidence/L2_J_EVIDENCE_DOSSIER_2026-10-08.md`, blob `51c6bf2b3ae324892777439a862e3d0345bcaaf8`.

La revue porte conjointement sur le candidat root, l’outillage et l’intégralité des preuves L2-I/L2-J, au regard de L2-I, L2-J et de l’annexe A de la décision lot 2. Résous et consigne dans ton rapport les blobs Git complets de chaque objet ci-dessus avant toute conclusion ; si un objet, un blob ou une référence L2-J manque ou diverge, conclus `BLOCKED_INCOMPLETE_EVIDENCE`, sans substitution.

## C. Interdits

Ne modifie aucun objet examiné ; ne corrige pas le candidat ; ne charge pas le candidat hors des opérations expressément autorisées par L2-I ; n’utilise aucun endpoint, donnée, credential, argent ou système réel ; n’agis pas sur la VM ; ne qualifie pas la VM ; n’active ni n’opère A2 ; ne lève aucune quarantaine ; n’émet aucune décision Owner ; ne transforme pas E en autorité effective ; ne déduis aucun PASS de tests synthétiques seuls. Aucune autorité économique, de capital réel, de fusion ou d’activation n’est créée.

## D. Méthode minimale et reproductible

1. Vérifie les commits, chemins, blobs, arbres, ancestry et absence de fichiers hors périmètre ; établis que le candidat ne modifie que `trusted_root.py` par rapport à sa base déclarée `276fd99`.
2. Relis les exigences L2-I/L2-J et chaque point de l’annexe A ; construis une matrice exigence → preuve → reproduction → résultat.
3. Rejoue les commandes du dossier L2-J dans l’environnement déclaré, sans réparer ni compléter silencieusement les preuves.
4. Rejoue les 279 anciens tests et confirme précisément les trois écarts attendus ; tout autre écart est un défaut ou un blocage à expliquer.
5. Rejoue tous les nouveaux tests du candidat et de l’outillage ; vérifie séparément les refus sur la root réelle et les cas positifs sur objets synthétiques.
6. Effectue des tests adversariaux indépendants ciblant au minimum : confusion d’identité, substitution d’objet, mismatch commit/blob, contenu absent ou surnuméraire, statut hors domaine, défaut de liaison structurelle, politique incomplète, fail-open et chargement non autorisé.
7. Distingue preuve statique, test synthétique, test sur configuration réelle et qualification d’environnement. Ne crédite jamais une catégorie à une autre.
8. Archive commandes, versions, sorties, codes retour et digests nécessaires à une reproduction indépendante.

## E. Canal de contrôle D2 et contenu gardé

Évalue explicitement la route D2 choisie et la fermeture de D1. Vérifie que le contrôle D2 est fail-closed, que la liaison entre input, output, policy et root est exacte, et que le contenu sous garde comprend exactement quinze éléments — ni quatorze, ni seize — tels que définis par la configuration finale ratifiée et l’annexe A. Dresse la liste canonique des 15 éléments dans le rapport, avec pour chacun : source gelée, champ/chemin, valeur ou domaine autorisé, identité, preuve L2-J et résultat adversarial. Toute impossibilité d’énumérer ou de relier les 15 éléments est bloquante.

## F. Écarts connus à traiter sans les banaliser

Évalue et classe séparément :

1. le commit d’outillage `1910994`, publié par une autre session que le Builder désigné ; vérifie ses octets et sa provenance, et dis si cet écart affecte l’indépendance, la chaîne de garde ou la validité technique ;
2. la qualification de la VM L2-A, reportée et non accomplie ; aucune preuve locale ne doit être présentée comme sa substitution ;
3. l’écart d’environnement : Python 3.13 local contre Python 3.12 lors de la première livraison ; reproduis ce qui est disponible, compare les résultats et borne toute conclusion non démontrée sur 3.12.

Un écart connu reste un écart : classe-le `NON_BLOCKING_JUSTIFIED`, `BLOCKING_DEFECT` ou `BLOCKED_MISSING_EVIDENCE`, avec preuve.

## G. Limite de l’évaluation permissive

La première évaluation permissive sur la configuration réelle n’aura lieu qu’au lot 4. Le lot 3 ne doit donc ni l’exécuter, ni l’anticiper, ni conclure qu’elle réussirait. Les refus sur root réelle et les succès sur objets synthétiques établissent seulement les propriétés exactes qu’ils testent. Toute conclusion positive du lot 3 doit porter la réserve explicite : `REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4`.

## H. Conditions d’effet d’E

Contrôle point par point les conditions d’effet du point B.5 de E, sans les déclarer satisfaites par présomption. En particulier, sépare : preuves L2-I/L2-J, avis indépendant du lot 3, qualification de la VM L2-A, et décision Owner d’activation/opération au lot 4. E demeure conditionnelle et sans effet tant que toutes ses conditions ne sont pas prouvées selon leur autorité propre. Le rapport doit afficher `E_EFFECTIVE = FALSE` sauf si B.5 autorise explicitement une autre valeur sur les objets examinés ; aucune conclusion Astra ne vaut activation.

## I. Livrable Astra — sections obligatoires A à J

Publie un unique rapport `research/weather_forward/v4/audit/ASTRA_V4_A2_LOT3_INDEPENDENT_REVIEW_2026-10-08.md` comprenant exactement les rubriques suivantes :

A. mandat, indépendance et conflits éventuels ;
B. inventaire exact des commits, chemins, blobs, arbres et environnements ;
C. verdict exécutif et portée exacte ;
D. matrice exhaustive L2-I / L2-J / annexe A ;
E. reproduction des 279 anciens tests, des trois écarts attendus et des nouveaux tests ;
F. tests adversariaux indépendants et résultats ;
G. revue du canal D2 et tableau des 15 éléments gardés ;
H. écarts connus : auteur de `1910994`, VM non qualifiée, Python 3.13 contre 3.12 ;
I. limite lot 4 et contrôle des conditions d’effet B.5 de E ;
J. constats numérotés, verdict final, conditions résiduelles et prochaine action.

Chaque constat indique sévérité, objet exact, observation, reproduction, conséquence et remède minimal. N’accepte ni preuve narrative sans sortie reproductible, ni absence d’échec comme preuve de succès.

## J. Verdict et statuts autorisés

Choisis un seul verdict : `PASS_FOR_OWNER_LOT4_CONSIDERATION`, `FAIL_BLOCKING_DEFECT`, ou `BLOCKED_INCOMPLETE_EVIDENCE`. Même en cas de PASS, conserve au minimum :

```text
VM_QUALIFIED = FALSE_UNLESS_SEPARATELY_PROVEN_BY_OWNER
REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4
E_EFFECTIVE = FALSE
A2_EXECUTION_AUTHORIZED_BY_ASTRA = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED_BY_ASTRA = FALSE
QUARANTINE_LIFTED_BY_ASTRA = FALSE
ECONOMIC_AUTHORITY = 0
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```

Termine par la prochaine action exacte : correction et nouvelle revue si défaut ; fourniture des preuves manquantes si blocage ; ou transmission à Owner pour les seules décisions/conditions restantes si PASS. Cite le commit et le blob complets du rapport Astra.
