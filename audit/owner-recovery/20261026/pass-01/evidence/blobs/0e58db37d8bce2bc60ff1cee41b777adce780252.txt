# Astra — Weather V4 A2, lot 3 : revue indépendante du candidat root, de l'outillage et des preuves L2-I/L2-J

Date : 2026-10-08. Dépôt : `fahimahmedb/Quant-Trade`. Branche : `astra/weather-v4-a2-lot3-independent-review-2026-10-08`, créée depuis `73280c3e9d8604b2f2d8e6d2d174aa940389a760`. Ce fichier est l'unique ajout de la branche.

```text
DOCUMENT_STATUS = ASTRA_LOT3_INDEPENDENT_TECHNICAL_REVIEW
VERDICT = BLOCKED_INCOMPLETE_EVIDENCE
CANDIDATE_ROOT_BLOCKING_DEFECT_FOUND = NONE
REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4
```

## A. Mandat, indépendance et conflits éventuels

**Mandat.** Revue technique indépendante prévue au lot 3 par la décision lot 2 (`276fd99`, L2-I, L2-J, annexe A), portant conjointement sur le candidat root, l'outillage L2-B et les preuves L2-I/L2-J, avec contrôle des conditions d'effet B.5 de E. Aucun pouvoir de décision, d'activation, de levée de quarantaine, de release ou de fusion.

**Indépendance.** Session Astra neuve. Je n'ai participé ni à la décision lot 2, ni à l'outillage, ni aux gels, ni à E, ni au candidat, ni à L2-I/L2-J. Sources utilisées : uniquement les objets Git publiés cités par la mission et les objets qu'ils référencent par hash (décision D `49d3d00`, H `78d537de`, actes de gel `245f193`/`79f6e92`, ratification `ccd4747`). **Non lus** : tout fichier sous `research/weather_forward/v4/team/`, la branche `team/weather-v4-a2-coordination-2026-10-08` (citée par le rapport L2-I comme « file d'équipe lue » par le Builder), les commentaires de PR (dont la PR #22 citée par L2-J pour l'identité du dossier). L'identité du dossier a été résolue par le commit donné dans la mission, sans recours à la PR.

**Conflits.** Aucun conflit connu. Le Builder L2-I déclare avoir lu une file d'équipe ; cela ne touche pas mon indépendance, mais signifie que certaines justifications L2-I peuvent dépendre d'échanges non publiés : je ne les ai crédités que lorsqu'une sortie reproductible les étaye.

**Exécution.** Toutes les reproductions ont eu lieu hors dépôt, dans le répertoire scratchpad de la session, sans réseau pour les processus testés (hook d'audit), sans VM, sans endpoint, sans credential, sans donnée réelle. Aucun objet examiné n'a été modifié. Aucune action n'a été refusée par le contrôle automatique pendant cette revue.

## B. Inventaire exact des commits, chemins, blobs, arbres et environnements

### B.1 Objets de la mission (tous résolus ; aucun manquant ni divergent)

| Objet | Commit complet | Chemin | Blob | Arbre du commit |
|---|---|---|---|---|
| Décision lot 2 + annexe A | `276fd995fe494e1734bba13827e6103864ce68da` | `research/weather_forward/v4/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md` | `d9809d0cca1faa51b713f02e453b7233c7a16811` | `abde41ff8c8445c581665078c2d453bc45ae2ade` |
| Ratification lot 2 | `ccd4747e4bb9e2a4d93c552ba10e081f254af1e7` | `…/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_RATIFICATION_2026-10-07.md` | `705040cba9b75b188309672b73e7a6da615a444a` | — |
| Constat Astra lot 1 | `52e5ff27583f3480ea443acdf6b358d3a44242f5` | `research/weather_forward/v4/audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_2026-10-07.md` | `e5bfce1bb255fa20e4d7314685286a822ae867fe` | `34162352d93ebfb765321bd782bde0c56bc9df68` |
| E (D2) | `6e0320f15d48a924cef9507af5641e47de9fe938` | `research/weather_forward/v4/owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_D2_2026-10-08.md` | `89890a4f224889bc1cc3606c62ea477bb1e7c6b3` | `bd1d76f02380429fc8b77b20f0408afaddd5e047` |
| Outillage L2-B | `1910994f3141d20b10547a0f35e73d012b011a38` (parent `112933c5bd2dc511f91bd5500850c5a084eb772e`) | `research/weather_forward/v4/a2_operation/` | voir B.3 | `7a8e3926c162954095724acd8889ec8f855a3401` |
| Tête outillage + gels | `51f49c81d843e57111135df283b06368cc1546bf` | idem | voir B.3 | — |
| Candidat root | `73280c3e9d8604b2f2d8e6d2d174aa940389a760` (parent unique `276fd995…`) | `research/weather_forward/v4/a2_harness/trusted_root.py` | `9704a844bae0ef54637c76dded5bb82d9f4c334f` (avant : `9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94` = H) | `b0ebe6e612429ff78ffb34572093bcc768d04d00` |
| Vérification L2-I | `5b381d34ccdfc938727ccecaf1d09447dcd29ab5` | `a2_operation/evidence/L2_I_VERIFICATION_2026-10-08.md` ; `…/L2_I_RUN_OUTPUT_2026-10-08.txt` ; `verification/run_l2i_candidate_verification.py` ; `verification/test_l2i_candidate.py` | `12432cbcfea67a01cc334085b30350ba0fef7dcf` ; `a6411537fa027a69a7806c82b2c580ded7af141c` ; `6dcc9fb2304588a1d3fac35e5ee217d1a88ccfa9` ; `291f7769f68ae5a817f521a5813e931d8bcf4a22` | — |
| Dossier L2-J | `5358c7ac582b46804be0008cffc78a043751d910` (parent `5b381d3`) | `research/weather_forward/v4/a2_operation/evidence/L2_J_EVIDENCE_DOSSIER_2026-10-08.md` | `51c6bf2b3ae324892777439a862e3d0345bcaaf8` (= mission) | `c17a3ef9994add9e80ad57da32e49a32e71d28ae` |
| Gels input/output | `245f193edb158a6cee653f176ae7b93cf2f3ae80` | acte Owner `…L2_C_L2_D_D2_CONTENT_FREEZES_2026-10-08.md` | gèle `f85205f3…` / `7651de7e…` | — |
| Gel policy | `79f6e9290121869cece6d23a259249883b32941a` | acte Owner `…L2_F_POLICY_CONTENT_FREEZE_2026-10-08.md` | gèle `6a1fa30f…` | — |
| H (sources harnais) | `78d537de681363ed83a6c7787aba4319f3c73c4d` | `__init__.py`, `contract.py`, `harness.py`, `trusted_root.py` | `bf9a2bdb…`, `f6f94a4a…`, `00ae81d2…`, `9d8adeca…` | — |
| C (construction) | `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` | — | — | — |

Toutes les références abrégées du dossier L2-J (blobs `f85205f3`, `7651de7e`, `6a1fa30f`, `72095daa`, `7ced3ce2`, `591ea4ce`, `9d8adeca`, `bf9a2bdb`, `f6f94a4a`, `00ae81d2`, commits `245f193`, `79f6e92`, `ccd4747`, `9d0698b`, `78d537de`, `37e3b25f`, `51f49c81`, `5b381d34`) se résolvent sans ambiguïté et concordent avec les objets ci-dessus.

### B.2 Ancestry et périmètre

```text
git diff --stat 276fd99 73280c3        -> 1 file changed, 24 insertions(+), 8 deletions(-) : a2_harness/trusted_root.py uniquement
git log --oneline 276fd99..73280c3     -> 73280c3 (un seul commit)
git merge-base --is-ancestor 276fd99 1910994   -> vrai
git merge-base --is-ancestor 276fd99 5358c7a   -> vrai ; chaîne 112933c → 1910994 → 13d9143 → 492bd05 → 1b6416b → 51f49c8 → 5b381d3 → 5358c7a
git merge-base --is-ancestor 73280c3 5358c7a   -> faux (branches distinctes, attendu : L2-I assemble sans merge)
git diff --name-only 276fd99 5358c7a | grep -v '^research/weather_forward/v4/a2_operation/'  -> vide
git diff --stat 1910994 51f49c8        -> 8 fichiers ajoutés (frozen/*, evidence L2-C/D/E/F, identity/build_policy…, transcribe…) ; aucun fichier de 1910994 modifié
git diff --stat 5b381d3 5358c7a        -> 1 fichier ajouté (dossier L2-J)
```

Le candidat ne modifie que `trusted_root.py` par rapport à `276fd99` ; aucun fichier hors `a2_operation/` sur la lignée outillage/L2-I/L2-J ; aucun fichier de production du harnais modifié par l'outillage.

### B.3 Blobs des sources d'opération (snapshot `51f49c8`, identiques dans l'assemblage L2-I)

| Fichier (`research/weather_forward/v4/a2_operation/`) | Blob |
|---|---|
| `__init__.py` | `7a660047ed0e2f871905f6313e411305ea9b5a0b` |
| `common/__init__.py` | `af0d1060459ed178c47fdbe76c68442adcd2f7ce` |
| `common/bounded_output.py` | `5734e9b175c28f3790caa1fab2682d08f0bd4528` |
| `common/a2_unit_profile.sh` | `ec58a081cfa1fee0a1dfbe51b9930ab65cd13cac` |
| `identity/__init__.py` | `ef09a31771f39da2298c72fa6d64c182e8456959` |
| `identity/identity_via_harness.py` | `7d37ff60c335307029f0f260be7e920c713023cc` |
| `identity/identity_stdlib.py` | `47b819d2e63df6733e444b595a0aebaa36c4cc86` |
| `operation/__init__.py` | `cae8c76795fe1a5e15e4ed8ada95e7cc188566cb` |
| `operation/a2_doc_integration_operation.py` | `8999ba9ddea527974b0e18d5094c8ee31e6776c0` |
| `frozen/input_manifest_d2_v1.json` | `f85205f33a232de6fabd83c17c52a25d4634e374` |
| `frozen/output_manifest_d2_v1.json` | `7651de7e718a276b596f2256aff0877e771e5d6d` |
| `frozen/harness_policy_d2_v1.json` | `6a1fa30fac327c0183b2931550bd4c730195529c` |
| `verification/test_tooling.py` | `bf108641b8ac8268d31b8602f89f7677baa51c1c` |
| `verification/run_tooling_tests.py` | `8621d5d22a9f396afedebf7da382a1bb05b0d1ab` |
| `verification/source_pins.json` (mode `L2_B_SYNTHETIC_ONLY`, épingle `trusted_root.py` = H `9d8adeca…`) | `cbad2196a07de0d06669c9a5a96cf09a859a9e7e` |

**Absent du dépôt (recherche `git ls-tree -r 5358c7a`)** : aucun fichier de contexte d'opération (`A2_DOC_INTEGRATION_OPERATION_CONTEXT_V1`), aucun fichier d'épingles finales d'opération incluant le blob candidat `9704a844…`, aucun constat/transcript L2-A.

### B.4 Environnements de reproduction

| Élément | Valeur |
|---|---|
| Hôte de revue | Linux 6.18.44-fc-v77, x86_64, glibc 2.39 (conteneur de session ; **pas** la VM) |
| Python principal | CPython 3.13.16 (GCC 13.3.0) |
| Python secondaire | CPython 3.12.3 (GCC 13.3.0) — la première livraison L2-B déclare 3.12.14 |
| Drapeaux | `-I -S -B` ; limite externe `timeout 600` |
| Assemblage L2-I | `git archive 51f49c81… research/weather_forward/v4/a2_harness research/weather_forward/v4/a2_operation \| tar x` ; `git show 73280c3e…:…/trusted_root.py` ; `git show 5b381d34…:…/run_l2i_candidate_verification.py` et `test_l2i_candidate.py` ; `git hash-object` → `9704a844…`, `6dcc9fb2…`, `291f7769…` |
| Assemblages outillage | `git archive 1910994 …` et `git archive 51f49c8 …` (root H deny-all) |

## C. Verdict exécutif et portée exacte

**Verdict : `BLOCKED_INCOMPLETE_EVIDENCE`.**

Ce qui est établi par reproduction :

1. Le candidat `73280c3` est conforme à L2-H : un seul fichier, tuple de root exact `(E, C, composant, version, policy)`, résolveur renvoyant la constante, aucun setter/surcharge/repli. Aucun défaut bloquant du candidat trouvé.
2. Les trois identités (input, output, policy) sont reproduites par trois voies : H, outillage stdlib, et une canonicalisation Astra écrite indépendamment ; elles égalent le tableau A de E et l'identité de policy de la root.
3. L2-I est reproduit à l'identique (modulo chemins, durées, noyau) en Python 3.13.16 et en 3.12.3 : 279 anciens tests, 276 réussis, exactement les trois écarts prévus ; 27 nouveaux tests réussis ; 0 PERMIT sur la root réelle.
4. L'outillage L2-B (`1910994` et `51f49c8`) passe en 3.12.3 et 3.13.16 : 279 tests H verts + 64 tests synthétiques.
5. 27 tests adversariaux indépendants (56 évaluations sur la root réelle, aucune AUTHORIZED, 0 PERMIT) et 6 lancements refusés du script d'opération sur contextes synthétiques : aucun fail-open trouvé.

Pourquoi le verdict n'est pas PASS : deux objets que L2-J exige et que le point B.5(a) de E place dans le périmètre de l'avis lot 3 n'existent pas.

- **Contexte d'opération final et épingles finales du script** (L2-J : « épingles finales du script et du contexte » ; E B.5(a) : PASS « sur les snapshots exacts du candidat, de l'outillage et du contexte »). Aucun fichier de contexte n'est publié ; le seul fichier d'épingles (`source_pins.json`) est en mode synthétique et épingle la root H. La liaison exacte input/output/policy/root ↔ contexte réel ne peut donc pas être revue sur l'objet qui sera exécuté (constat J-1).
- **Constats/transcripts/mutations L2-A** (L2-J), dont dépendent le profil réel d'unité, la suppression de stdout/stderr, les signaux/OOM/timeout du canal de contrôle (L2-I.5 renvoie explicitement à L2-A). Le dossier L2-J le reconnaît lui-même : `LOT2_CANDIDATE_AND_EVIDENCE_READY_FOR_ASTRA_LOT3 = NOT_CLAIMED` (constat J-2).

Portée : ce verdict porte sur les objets du §B.1 uniquement. Il ne qualifie pas la VM, n'évalue pas la configuration réelle de façon permissive, ne vaut ni activation, ni approbation de release, ni levée de quarantaine.

## D. Matrice exhaustive L2-I / L2-J / annexe A

Légende de catégorie : **ST** preuve statique (lecture de source/objets Git) ; **SY** test synthétique ; **RR** test sur configuration réelle limité aux refus (aucune AUTHORIZED) ; **QE** qualification d'environnement. Aucune catégorie n'est créditée à une autre.

### D.1 L2-I

| # | Exigence | Preuve publiée | Reproduction Astra | Cat. | Résultat |
|---|---|---|---|---|---|
| I-0 | Assemblage isolé, sans merge ; blobs épinglés vérifiés avant import | L2-I §2, `PINS_MISMATCH=[]` | Assemblage refait ; `git hash-object` ; sortie `PINS_MISMATCH=[]`, 11 blobs concordants | ST | CONFORME |
| I-1 | Anciennes suites aux blobs H, sans modification | L2-I §1 | `SOURCE_BLOBS` reproduits (`aa0159c2`, `52bb94ed`, `25b7d3bd`, `f660a24d`) | ST | CONFORME |
| I-2 | Anciens runners : refus `PRODUCTION_TRUSTED_ROOT_MODIFIED` (option) / `AUDITED_SOURCE_BYTES_MISMATCH` (sans) consignés | **NON_FAIT** par L2-I (« non relancés ») | Relancés par Astra, 2 runners × 2 options × 2 Python : 8 sorties rc=1 aux motifs exacts attendus (§E.2) | ST/RR | CONFORME APRÈS REPRODUCTION ASTRA (lacune L2-I, constat J-6) |
| I-3 | 279 tests (145+134), 276 réussis, exactement 3 écarts motivés, 0 erreur/skip/xfail/uxs, 0 réseau/sous-processus/fichier interdit | L2-I §3, sortie `a6411537…` | Rejoué 3.13 et 3.12 : identique (§E.1) | RR (root réelle chargée, aucune autorisation) | `LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED` reproduit |
| I-4 | Nouveaux tests 1 : constantes, résolveur, tuple exacts ; refus construction/composant/version/policy discordants | L2-I §4 | Rejoué (27/27) + Astra B/A (§F) | ST + RR | CONFORME |
| I-5 | Nouveaux tests 2 : aucune AUTHORIZED citant E avec tuple réel ; refus avant permission | L2-I §4 (garde `real_eval`, 22 évaluations, 0 PERMIT) | Rejoué ; Astra : 56 évaluations réelles, garde à 0 déclenchement, 0 PERMIT | RR | CONFORME |
| I-6 | Nouveaux tests 3 : barrières tardives sur synthétique seulement | L2-I §4 | Rejoué ; Astra F (root synthétique `"3"*40` ≠ E) | SY | CONFORME (sémantique seulement) |
| I-7 | Nouveaux tests 4 : quarantaine D2 — constat statique + test synthétique ; pas de couverture réelle revendiquée | L2-I §4 | Lecture `harness.py` + test L2-I rejoué | ST + SY | CONFORME ; couverture réelle **NON_DÉMONTRÉE** (correctement déclarée) |
| I-8 | Nouveaux tests 5 : logique/codes du script sur synthétique | L2-I §5 : **NON_FAIT** dans L2-I, renvoi à `test_tooling.py` (exécuté sur root H) | `test_tooling` rejoué (64/64) ; Astra F rejoue `finish/execute/build_result/guarded` **sur l'assemblage candidat** | SY | CONFORME APRÈS REPRODUCTION ASTRA ; profil réel → L2-A (J-2) |
| I-9 | Compteurs d'audit (lectures permises / refus de cache non nuls admis) | L2-I §3 : 88/52 | 3.13 : 88/52 ; 3.12 : 89/53 ; violations 0 | ST | CONFORME (écart de compteurs expliqué §H.3) |
| I-10 | Verdict composé ; code runner 0 ≠ « 279 verts » | L2-I en-tête | rc=0 aux deux versions, `L2_I_VERIFICATION_PASS` | — | CONFORME |
| I-11 | Comparer Python/architecture Builder/hôte | L2-I §2/§7 : hôte inconnu | 3.12/3.13 comparés ; hôte non accessible | QE | **NON ÉTABLI pour l'hôte** (J-4) |
| I-12 | Aucun replay VM | L2-I | Aucun accès VM | — | CONFORME |

### D.2 L2-J

| Élément exigé par L2-J | Présent ? | Référence | Résultat |
|---|---|---|---|
| Branches/bases/parents/commits/diffs exacts | Oui | Dossier §1 | Vérifiés (§B) |
| Blobs avant/après | Oui | Dossier §1 | Vérifiés |
| Snapshots assemblés | Oui (recette) | L2-I §2 | Reproduits |
| Contenus figés et ratifications | Oui | Gels `245f193`/`79f6e92`, E | Blobs concordants |
| Trois identités, deux méthodes, étalonnage | Oui | Dossier §2 | Reproduits (3 voies) ; étalonnage `sha256:54bfcafc…` reproduit via `run_tooling_tests` |
| E | Oui | `6e0320f` | Vérifié |
| Commandes numérotées | Oui | L2-I §2 | Rejouées |
| Versions Python/système/architecture | Oui (Builder) | L2-I §2 | Hôte : NON |
| Résultats anciens + trois différences | Oui | L2-I §3 | Reproduits |
| Tous nouveaux tests + couverture atteinte/non atteinte | Oui | L2-I §4–5 | Reproduits |
| Compteurs d'audit détaillés | Oui | L2-I §3 | Reproduits |
| **Constats/transcripts/mutations L2-A** | **Non** | Dossier §4.1 : NON_FAIT | **MANQUANT** (J-2) |
| **Épingles finales du script et du contexte** | **Non** | Aucun fichier de contexte ; `source_pins.json` synthétique (root H) | **MANQUANT** (J-1) |
| Limites visibilité/custody/rétention/identité chargée | Oui (déclarées) | Dossier §4.8 | Déclarées, non vérifiables avant lot 4 |
| Séparation `…WITH_LOCAL_BLOCKERS` / `…READY_FOR_ASTRA_LOT3` | Oui | Dossier en-tête : READY = NOT_CLAIMED | Conforme et cohérent avec ce verdict |

### D.3 Annexe A (et sa transposition dans E)

| Point | Exigence | Constat Astra | Cat. | Résultat |
|---|---|---|---|---|
| A.1 | E future, conditionnelle ; ne contient pas son SHA ; commit inscrit dans le candidat | E ne contient pas `6e0320f…` (vérifié par recherche) ; root, constante et docstring le portent | ST | CONFORME |
| A.2 | Identités, fichiers/commits/blobs, C, composant, version, `A2-DOC-INTEGRATION-MANIFEST-V1`, choix D1/D2 ; pas de commit candidat dans E | Tableau A de E = blobs/identités reproduits ; route D2 ; aucun commit candidat dans E | ST | CONFORME |
| A.3 | READ_INPUT `a2-doc-v1-read-input-blue`, acteur `blue…`, EXECUTOR ; D2 sans second appel | Script : D2 interdit `release`/`output_record_id` (contexte refusé rc=30) ; `release_prerequisites_present` exige D1 | ST + SY | CONFORME |
| A.4 | Journal vide, INPUT_LOG_RECORD_ID, incident, nom unique | Valeurs dans E B.4 ; **aucun contexte matérialisé** pour les porter | ST | NON VÉRIFIABLE sur objet réel (J-1) |
| A.5 | Conditions communes avant READ_INPUT | Voir §I | — | NON SATISFAITES (attendu à ce stade) |
| A.6 | Conditions RELEASE_OUTPUT (D1 seulement) | D1 fermée par E ; aucune release possible sur D2 | ST + SY | SANS OBJET sur D2 |
| A.7 | Écriture bornée `/srv/a2out`, pas de transfert sur D2 | Script : répertoire exact exigé, écriture uniquement du `.partial-` puis lien, refus d'écrasement, ≤ 65 536 o | ST + SY (écrivain mémoire) | CONFORME en sémantique ; profil réel → L2-A |
| A.8 | Exclusions | E B.8 conforme | ST | CONFORME |

## E. Reproduction des 279 anciens tests, des trois écarts attendus et des nouveaux tests

### E.1 Runner L2-I

Commande (depuis la racine de l'assemblage) :

```bash
timeout 600 python3.13 -I -S -B research/weather_forward/v4/a2_operation/verification/run_l2i_candidate_verification.py   # rc=0
timeout 600 python3.12 -I -S -B research/weather_forward/v4/a2_operation/verification/run_l2i_candidate_verification.py   # rc=0
```

| Mesure | Publié (L2-I, 3.13.16) | Astra 3.13.16 | Astra 3.12.3 |
|---|---|---|---|
| Code retour | 0 | 0 | 0 |
| Lignes de sortie | 383 | 383 | 371 (pas de soulignements `~~^^` de traceback en 3.12) |
| SHA-256 sortie | `660e6122…8c8f97` | `bc9a95c9…c4441` | `ef2b5c4e…347d6f` |
| Collecte anciens | 145 + 134 = 279, 0 erreur de chargeur | idem | idem |
| Anciens : réussis / échecs / erreurs / skips / xfail / uxs | 276 / 3 / 0 / 0 / 0 / 0 | idem | idem |
| Nouveaux : collectés / réussis / échecs / erreurs / skips | 27 / 27 / 0 / 0 / 0 | idem | idem |
| Réseau / sous-processus / fichiers interdits | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Lectures permises / refus de cache attendus | 88 / 52 | 88 / 52 | 89 / 53 |
| `real_tuple_evaluations` / `real_tuple_permits` / garde AUTHORIZED | 22 / 0 / 1 | 22 / 0 / 1 | 22 / 0 / 1 |
| Verdict | `L2_I_VERIFICATION_PASS` | idem | idem |

`diff` publié ↔ Astra 3.13 : seules différences = chemin du scratchpad dans les tracebacks, noyau `fc-v80`→`fc-v77`, durées. Aucune différence de résultat.

**Trois écarts (préfixe `research.weather_forward.v4.a2_harness.test_bounded_runtime.TrustedRootTests.`) — observés identiquement aux deux versions :**

| Test | Type | Ligne(s) | Motif observé | Prévision décision | Résultat |
|---|---|---|---|---|---|
| `test_production_root_absent_denies_all_authority_bearing_paths` | `AssertionError` | 198 | `assertIsNone(CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)` : root présente | l. 198 | CONCORDANT |
| `test_coordinated_caller_substitution_cannot_create_production_root` | `AssertionError` | 179 appelée en 212 | `EXECUTION_POLICY_ROOT_MISMATCH is not MISSING_EXECUTION_POLICY_ROOT` ; DENY/BLOCKED/non-VALID conservés | l. 179/212, motif ROOT_MISMATCH | CONCORDANT |
| `test_test_only_root_exercises_positive_paths_and_is_restored` | `AssertionError` | 227 | `assertIsNone(get_trusted_execution_policy_root())` après restauration ; chemins positifs patchés réussis avant | l. 227 | CONCORDANT |

Aucun autre écart, erreur, skip ou changement de collecte.

### E.2 Anciens runners (refus attendus — lacune L2-I comblée par reproduction)

```text
python3.1{3,2} -I -S -B a2_harness/run_bounded_runtime_tests.py                          rc=1  AUDITED_SOURCE_BYTES_MISMATCH: {"contract.py": "f6f94a4a…", "trusted_root.py": "9704a844…"}
python3.1{3,2} -I -S -B a2_harness/run_bounded_runtime_tests.py --allow-in-scope-repair  rc=1  PRODUCTION_TRUSTED_ROOT_MODIFIED
python3.1{3,2} -I -S -B a2_harness/run_d5_type_regression_tests.py                       rc=1  AUDITED_SOURCE_BYTES_MISMATCH: {idem}
python3.1{3,2} -I -S -B a2_harness/run_d5_type_regression_tests.py --allow-in-scope-repair rc=1 PRODUCTION_TRUSTED_ROOT_MODIFIED
```

Les deux refus arrivent avant tout test (contrôle des octets en tête de runner). `contract.py` apparaît aussi dans le mismatch sans option car l'ancien runner épingle un `contract.py` antérieur à la réparation D5 (`db978016…`) ; c'est historique et sans rapport avec le candidat.

### E.3 Outillage L2-B

```bash
timeout 600 python3.1x -I -S -B research/weather_forward/v4/a2_operation/verification/run_tooling_tests.py
```

| Snapshot | Python | rc | Verdict | Anciens | Nouveaux | SHA-256 sortie |
|---|---|---|---|---|---|---|
| `1910994` | 3.12.3 | 0 | `L2_B_SYNTHETIC_VERIFICATION_PASS` | `LEGACY_H_BASELINE_279_GREEN` | 64/64 | `860c5041…71b4d` |
| `1910994` | 3.13.16 | 0 | idem | idem | 64/64 | `8f41adde…41c441a` |
| `51f49c8` | 3.12.3 | 0 | idem | idem | 64/64 | `f7fba987…1b6c6b` |
| `51f49c8` | 3.13.16 | 0 | idem | idem | 64/64 | `b81bbe62…dc8a95` |

Ces 343 tests portent sur la root H deny-all et des objets synthétiques : ils ne testent pas le candidat (SY seulement).

### E.4 Séparation refus sur root réelle / succès synthétiques

- **Root réelle (RR)** : seulement des refus (DENY/BLOCKED/non-VALID) ; la seule réponse `VALID` observée est `validate_binding()` du binding réel (aucune autorisation, aucun journal, aucun `evaluate_*`, aucun PERMIT). Elle établit que la liaison statique binding↔policy↔root résout ; elle **n'établit pas** qu'une évaluation permissive réussirait (§G, §I).
- **Synthétique (SY)** : tous les PERMIT observés l'ont été sous une root synthétique d'autorité `"2"*40` (L2-I) ou `"3"*40` (Astra), jamais E, avec identifiants `TEST_ONLY_*`. La root réelle est rétablie et vérifiée après chaque test.

## F. Tests adversariaux indépendants et résultats

### F.1 Suite Astra (27 tests, écrite sans réutiliser les helpers L2-I)

Lancement : `timeout 600 python3.1x -I -S -B run_astra.py <assemblage L2-I> <répertoire des tests>`. Le lanceur installe un hook d'audit refusant réseau, sous-processus et toute ouverture en écriture. Toute évaluation sur la root réelle passe par une garde qui lève une exception si l'autorisation est AUTHORIZED.

| Version | rc | Exécutés | Échecs | Erreurs | Skips | Évaluations root réelle | PERMIT réels | Garde AUTHORIZED | Réseau / sous-proc. / écriture |
|---|---|---|---|---|---|---|---|---|---|
| 3.13.16 | 0 | 27 | 0 | 0 | 0 | 56 | 0 | 0 | 0 / 0 / 0 |
| 3.12.3 | 0 | 27 | 0 | 0 | 0 | 56 | 0 | 0 | 0 / 0 / 0 |

Digests : `test_astra_lot3_adversarial.py` SHA-256 `fce2d2974a210d70c3153e304d41e2d5503abddd802dcd2c2321e402f7a8baec` ; `run_astra.py` `fcf8e1f22c50c9699de321be418724e6eb70e5461597c32986e9ccaf346f6360` ; sorties 3.13 `0e05acd7…bf88acf1`, 3.12 `0908e962…25859971`. Les sources complètes sont en F.4 pour reproduction indépendante.

**Un premier lancement a donné 13 échecs, tous dus à mes tests**, et non au système :
1. j'avais exigé `completion_state ≠ COMPLETED` pour un refus, alors que H journalise et complète un refus (`COMPLETED` avec DENY/BLOCKED) ; l'assertion a été retirée (les autres assertions de refus sont conservées) ;
2. une mutation `incident_identifier` était, par construction, identique côté harnais et côté record attendu : ce n'est pas un défaut de liaison. Elle a été remplacée par une mutation de l'autorité de construction du binding.

Le compteur final dépendait de ces tests. Aucun objet examiné n'a été modifié.

| Catégorie | Tests | Cat. | Résultat |
|---|---|---|---|
| Identités | 3 voies (H, outillage stdlib, canonicalisation Astra indépendante) = tableau A de E ; root.policy = identité policy ; policy porte C et `A2-DOC-INTEGRATION-MANIFEST-V1` ; root `frozen` (affectation refusée) | ST/RR | PASS |
| Confusion d'identité | Autorité de construction du binding remplacée par E, commit candidat, arbre candidat, blob candidat, blob E, `1910994`, C en majuscules, C à un caractère près → `EXECUTION_POLICY_ROOT_MISMATCH` ; binding+policy déplacés ensemble vers E → `TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH` ; composant/version quasi identiques (slash final, majuscules, notation pointée, espace final, commit candidat, `-v2`) → ROOT_MISMATCH ; acteurs Astra/Owner en EXECUTOR, acteur Blue en RESEARCH_VIEWER/RELEASE_APPROVER → DENY | RR | PASS |
| Mismatch commit/blob | `authority_sha` = C, commit/arbre/blob candidat, blob E, blob H root, préfixe E + zéros, E majuscules (×UNRESOLVED/DENIED) → DENY ; `verify_harness_blobs` refuse root H prise pour candidat, permutation contract/harness, fichier manquant | RR + ST | PASS |
| Substitution d'objet | OutputManifest passé en input → refus ou exception, jamais PERMIT ; 6 mutations d'un champ de l'input (leakage UNRESOLVED, id, visibilité, champ permis ajouté/retiré, provenance à un caractère) → DENY ; identités input/output permutées dans la policy → ROOT_MISMATCH ; tuple synthétique complet + autorisation AUTHORIZED citant E contre la root réelle → `EXECUTION_POLICY_ROOT_MISMATCH` (refus à la root, avant toute permission ; tuple non réel) | RR | PASS |
| Politique incomplète | identité output vide/`UNRESOLVED`, `sha256:` nu, destinataires vides, classifications vides, version de manifest vide → refus ou exception, jamais PERMIT | RR | PASS |
| Fail-open | Getter de root patché : `None`, objet arbitraire, E majuscules, E+1 caractère, policy en majuscules, composant `*` → jamais PERMIT ; root réelle rétablie ; `guarded` : `10.0`, `True`, `99`, `None` → 30 ; `KeyboardInterrupt`, `SystemExit(0)`, `MemoryError` → 40 | RR + SY | PASS |
| Canal D2 (synthétique) | Séquence positive D2 → code 0, **un** écrit, exactement 15 clés, `INPUT_LINKED_RELEASE_NOT_ATTEMPTED`, `release_state=["BLOCKED"]`, ≤ 65 536 o ; D2 avec objets de release présents et AUTHORIZED → aucun appel `evaluate_output_release` (patch tripwire) ; mismatch d'autorité d'exécution du contexte, d'autorité de construction, codes acceptés hors scope → 30 sans écriture ; formes de séquence hors domaine (`(0,…,AND_RELEASE)`, `OTHER`, `(10,…,NOT_ATTEMPTED)`, 2 évaluations avec code 0, `True`, `None`) → 30 sans écriture ; `build_result` à 14 ou 16 éléments → `StopOperation` ; limite de sortie → 50 ; cible existante → 30 | SY | PASS |
| Contenu absent/surnuméraire | Les 15 éléments du script = liste ordonnée extraite du champ figé `exact_metric_or_artifact` (15 éléments distincts) ; contexte sans `log`, avec clé en trop, D2 avec section `release`, D2 avec `output_record_id`, répertoire `/srv/a2out/`, nom `../x`, branche `D3`, épingle supplémentaire, codes acceptés vides, E en majuscules → `ContextError` ; JSON figé avec champ retiré ou ajouté (×3 types) → rejet | ST + SY | PASS |
| Observation reproduite | `build_result` seul accepte `structural_linkage_status = "NOT_IN_DOMAIN"` ; `finish` est l'unique point de contrôle du domaine (testé ci-dessus) | SY | OBSERVATION (J-7) |

### F.2 Chargement non autorisé (script d'opération, contextes synthétiques)

```bash
python3.1x -I -S -B -X importtime a2_operation/operation/a2_doc_integration_operation.py --repo-root <assemblage> --context <ctx>.json
```

| Contexte synthétique | 3.13 rc | 3.12 rc | stdout | Modules `a2_harness` / `a2_operation` importés |
|---|---|---|---|---|
| Épingles valides de forme mais `trusted_root.py` = H `9d8adeca…` | 30 | 30 | 0 o | 0 / 0 |
| Clé supplémentaire | 30 | 30 | 0 o | 0 / 0 |
| D2 avec section `release` | 30 | 30 | 0 o | 0 / 0 |
| Sans `-X importtime`, mêmes contextes + sans argument | 30 | — | 0 o | stderr 0 o |

Le refus a lieu avant tout import du harnais et avant l'installation du hook ; aucun fichier n'est créé (`/srv/a2out` absent de l'hôte de revue). Ces contextes sont synthétiques (identifiants `TEST_ONLY`, autorisation DENIED) : ce n'est **pas** un lancement sur la configuration réelle.

### F.3 Ce que ces tests n'établissent pas

Aucune propriété du profil systemd réel, des limites cgroup, de la suppression de stdout/stderr par l'unité, des signaux/OOM/timeout, du tmpfs, de l'hôte, ni d'une évaluation permissive réelle. Le hook d'audit est un contrôle du processus, pas une isolation.

### F.4 Sources Astra pour reproduction

`run_astra.py` :

```python
import sys, json
WS = sys.argv[1]
CNT = {"network": 0, "subprocess": 0, "write": 0}
def hook(ev, args):
    if ev.startswith("socket."):
        CNT["network"] += 1; raise PermissionError("ASTRA_DENY_NETWORK")
    if ev in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork"):
        CNT["subprocess"] += 1; raise PermissionError("ASTRA_DENY_SUBPROCESS")
    if ev == "open" and isinstance(args[0], (str, bytes)):
        mode, flags = args[1], args[2]
        if (mode and any(c in str(mode) for c in "wax+")) or (flags and flags & (1 | 2 | 64 | 512 | 1024)):
            CNT["write"] += 1; raise PermissionError("ASTRA_DENY_WRITE")
sys.addaudithook(hook)
sys.path.insert(0, WS)
sys.path.insert(0, sys.argv[2])
import unittest, test_astra_lot3_adversarial as t
r = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(unittest.defaultTestLoader.loadTestsFromModule(t))
print("ASTRA_SUMMARY=" + json.dumps({"python": sys.version.split()[0], "run": r.testsRun, "failures": len(r.failures),
      "errors": len(r.errors), "skips": len(r.skipped), "counters": t.COUNT, "audit": CNT}, sort_keys=True))
sys.exit(0 if r.wasSuccessful() and t.COUNT["real_permits"] == 0 and not any(CNT.values()) else 1)
```

`test_astra_lot3_adversarial.py` :

```python
"""Astra lot 3 independent adversarial tests (not committed; reviewer evidence only).

Rules: real root + real frozen manifests/policy are only used through ``real_eval``,
which refuses any AUTHORIZED ActionAuthorization and asserts the result is not PERMIT.
Positive paths use exclusively TEST_ONLY synthetic objects under a patched synthetic
root whose authority is not E. No VM, no network, no operation launch on the real
configuration.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

WS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None

from research.weather_forward.v4 import a2_harness as api
from research.weather_forward.v4.a2_harness import harness as h
from research.weather_forward.v4.a2_harness import trusted_root as tr
from research.weather_forward.v4.a2_harness.test_bounded_runtime import TestContext
from research.weather_forward.v4.a2_operation.identity import identity_via_harness as via_h
from research.weather_forward.v4.a2_operation.identity import identity_stdlib as via_s
from research.weather_forward.v4.a2_operation.operation import a2_doc_integration_operation as op

V4 = Path(op.__file__).resolve().parents[2]
E = "6e0320f15d48a924cef9507af5641e47de9fe938"
C = "37e3b25f17a7c5d3b3bc8d37df730aa988585b6c"
CAND = "73280c3e9d8604b2f2d8e6d2d174aa940389a760"
CAND_TREE = "b0ebe6e612429ff78ffb34572093bcc768d04d00"
CAND_BLOB = "9704a844bae0ef54637c76dded5bb82d9f4c334f"
E_BLOB = "89890a4f224889bc1cc3606c62ea477bb1e7c6b3"
H_ROOT_BLOB = "9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94"
TOOLING_1910994 = "1910994f3141d20b10547a0f35e73d012b011a38"
IN_ID = "sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00"
OUT_ID = "sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976"
POL_ID = "sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60"
HID = "research/weather_forward/v4/a2_harness"
VER = "weather-v4-a2-doc-integration-v1"
MVER = "A2-DOC-INTEGRATION-MANIFEST-V1"
EXEC_ACTOR = "blue.weather-v4.a2.doc-integration.v1"

COUNT = {"real_evals": 0, "real_permits": 0, "authorized_blocked_by_guard": 0}


def frozen_text(name):
    return (V4 / "a2_operation/frozen" / name).read_text(encoding="utf-8")


def frozen(name):
    return via_h.build_object(api, via_h.load_document(frozen_text(name)))


class R:
    input = frozen("input_manifest_d2_v1.json")
    output = frozen("output_manifest_d2_v1.json")
    policy = frozen("harness_policy_d2_v1.json")
    binding = api.AuthorityBinding(C, HID, VER, MVER)
    executor = api.RoleDeclaration(EXEC_ACTOR, api.Role.EXECUTOR)

    @staticmethod
    def auth(**kw):
        base = dict(authorization_id="a2-doc-v1-read-input-blue", authority_sha=E,
                    actor_id=EXEC_ACTOR, declared_role=api.Role.EXECUTOR,
                    action=api.Action.READ_INPUT, state=api.AuthorizationState.UNRESOLVED)
        base.update(kw)
        return api.ActionAuthorization(**base)


def real_eval(auth, *, manifest=None, policy=None, binding=None, actor=None):
    if getattr(auth, "state", None) is api.AuthorizationState.AUTHORIZED:
        COUNT["authorized_blocked_by_guard"] += 1
        raise AssertionError("ASTRA_TRIPWIRE_AUTHORIZED_ON_REAL_ROOT")
    assert h.get_trusted_execution_policy_root() is tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
    COUNT["real_evals"] += 1
    res = api.A2Harness(binding or R.binding, policy or R.policy).evaluate_input_read(
        api.StructuredAuditLog(()), "ASTRA_TEST_ONLY_REAL_DENY", manifest or R.input,
        actor or R.executor, auth)
    if res.decision.permit_or_deny_state is api.PermitState.PERMIT:
        COUNT["real_permits"] += 1
    return res


def independent_digest(doc):
    """Astra's own stdlib canonicalisation, written from H's field list, not tooling code."""
    f = doc["fields"]
    if doc["kind"] == "InputManifest":
        p = dict(f, manifest_kind="InputManifest")
        for k in ("exact_permitted_fields", "exact_prohibited_fields", "permitted_reader_roles"):
            p[k] = sorted(p[k])
        assert len(f) == 17
    elif doc["kind"] == "OutputManifest":
        p = dict(f, manifest_kind="OutputManifest")
        p["permitted_recipients"] = sorted(p["permitted_recipients"])
        assert len(f) == 13
    else:
        p = dict(f, contract_kind="HarnessPolicy")
        for k in ("allowed_input_classifications", "prohibited_input_classifications"):
            p[k] = sorted(p[k])
        p["permitted_recipient_actor_roles"] = sorted([list(x) for x in p["permitted_recipient_actor_roles"]])
        assert len(f) == 12
    raw = json.dumps(p, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class Deny:
    def deny(self, res, reason=None, detail=None):
        d = res.decision
        self.assertIs(d.permit_or_deny_state, api.PermitState.DENY)
        self.assertIs(d.release_state, api.ReleaseState.BLOCKED)
        self.assertIsNot(d.validation_state, api.ValidationState.VALID)
        if reason is not None:
            self.assertIs(d.stop_reason, reason, d.detail_code)
        if detail is not None:
            self.assertEqual(d.detail_code, detail)


class A_Identities(unittest.TestCase):
    def test_three_routes_agree_with_E_table_and_root(self):
        for name, expected, obj, fn in (
            ("input_manifest_d2_v1.json", IN_ID, R.input, api.input_manifest_identity),
            ("output_manifest_d2_v1.json", OUT_ID, R.output, api.output_manifest_identity),
            ("harness_policy_d2_v1.json", POL_ID, R.policy, api.harness_policy_identity)):
            doc = json.loads(frozen_text(name))
            self.assertEqual(independent_digest(doc), expected, name)
            self.assertEqual(fn(obj), expected, name)
            self.assertEqual(via_s.identity(via_s.load_document(frozen_text(name))), expected, name)
        self.assertEqual(tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT.expected_policy_identity, POL_ID)
        self.assertEqual(R.policy.expected_manifest_version_identity, MVER)
        self.assertEqual(R.policy.expected_owner_authority_sha, C)

    def test_root_tuple_and_E_constant(self):
        root = tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
        self.assertEqual((root.execution_policy_authority_sha, root.expected_construction_authority_sha,
                          root.expected_harness_identity, root.expected_harness_version_or_commit_identity,
                          root.expected_policy_identity), (E, C, HID, VER, POL_ID))
        self.assertEqual(tr.CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY, E)
        with self.assertRaises(Exception):
            root.execution_policy_authority_sha = "0" * 40  # frozen dataclass

    def test_baseline_binding_valid_but_no_permit_without_authorized(self):
        res = api.A2Harness(R.binding, R.policy).validate_binding()
        self.assertIs(res.state, api.ValidationState.VALID)
        self.deny = Deny.deny.__get__(self)
        self.deny(real_eval(R.auth()), api.StopReason.UNAUTHORIZED_READER)
        self.deny(real_eval(R.auth(state=api.AuthorizationState.DENIED)), api.StopReason.UNAUTHORIZED_READER)


class B_IdentityConfusion(unittest.TestCase, Deny):
    def test_construction_and_execution_authority_swapped(self):
        for owner in (E, CAND, CAND_TREE, CAND_BLOB, E_BLOB, TOOLING_1910994, C.upper(), C[:-1] + "6"):
            r = real_eval(R.auth(), binding=replace(R.binding, owner_authority_sha=owner))
            self.deny(r, api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)

    def test_policy_and_binding_both_moved_to_E(self):
        pol = replace(R.policy, expected_owner_authority_sha=E)
        self.deny(real_eval(R.auth(), policy=pol, binding=replace(R.binding, owner_authority_sha=E)),
                  api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH, "TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH")

    def test_near_miss_component_and_version_strings(self):
        for kw in (dict(harness_identity=HID + "/"), dict(harness_identity=HID.upper()),
                   dict(harness_identity="research.weather_forward.v4.a2_harness"),
                   dict(harness_version_or_commit_identity=VER + " "),
                   dict(harness_version_or_commit_identity=CAND),
                   dict(harness_version_or_commit_identity="weather-v4-a2-doc-integration-v2")):
            self.deny(real_eval(R.auth(), binding=replace(R.binding, **kw)),
                      api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)

    def test_actor_role_confusion(self):
        for actor in (api.RoleDeclaration("astra.weather-v4.a2.doc-integration.v1", api.Role.EXECUTOR),
                      api.RoleDeclaration("project-owner.weather-v4.a2.doc-integration.v1", api.Role.EXECUTOR),
                      api.RoleDeclaration(EXEC_ACTOR, api.Role.RESEARCH_VIEWER),
                      api.RoleDeclaration(EXEC_ACTOR, api.Role.RELEASE_APPROVER)):
            self.deny(real_eval(R.auth(), actor=actor))

    def test_authority_sha_is_commit_blob_or_tree_not_E(self):
        for sha in (C, CAND, CAND_TREE, CAND_BLOB, E_BLOB, H_ROOT_BLOB, E[:7] + "0" * 33, E.upper()):
            for st in (api.AuthorizationState.UNRESOLVED, api.AuthorizationState.DENIED):
                self.deny(real_eval(R.auth(authority_sha=sha, state=st)))


class C_ObjectSubstitution(unittest.TestCase, Deny):
    def test_output_manifest_passed_as_input(self):
        try:
            r = real_eval(R.auth(), manifest=R.output)
        except Exception:
            return
        self.deny(r)

    def test_input_manifest_single_field_mutations(self):
        for kw in (dict(efficacy_leakage_assessment=api.LeakageAssessment.UNRESOLVED),
                   dict(input_id="A2-DOC-IN-OWNER-A1-V2"),
                   dict(raw_values_visible=api.VisibilityState.HIDDEN),
                   dict(exact_permitted_fields=R.input.exact_permitted_fields + ("document_body",)),
                   dict(exact_permitted_fields=R.input.exact_permitted_fields[:-1]),
                   dict(source_provenance_class=R.input.source_provenance_class.replace("483907e4", "483907e5"))):
            self.deny(real_eval(R.auth(), manifest=replace(R.input, **kw)))

    def test_policy_input_output_identities_swapped(self):
        pol = replace(R.policy, expected_input_manifest_identity=OUT_ID, expected_output_manifest_identity=IN_ID)
        self.deny(real_eval(R.auth(), policy=pol), api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)

    def test_test_only_synthetic_policy_on_real_root(self):
        t = TestContext()
        r = api.A2Harness(t.binding, t.policy).evaluate_input_read(
            api.StructuredAuditLog(()), "ASTRA_TEST_ONLY", t.input, t.reader,
            api.ActionAuthorization("TEST_ONLY_AUTH", E, t.reader.actor_id, api.Role.EXECUTOR,
                                    api.Action.READ_INPUT, api.AuthorizationState.AUTHORIZED))
        # synthetic tuple with AUTHORIZED citing E against the real root: must be refused at the root
        self.deny(r, api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)


class D_IncompletePolicy(unittest.TestCase, Deny):
    def test_incomplete_or_ambiguous_policy_fields(self):
        for kw in (dict(expected_output_manifest_identity=""),
                   dict(expected_output_manifest_identity="UNRESOLVED"),
                   dict(expected_input_manifest_identity="sha256:"),
                   dict(permitted_recipient_actor_roles=()),
                   dict(allowed_input_classifications=()),
                   dict(expected_manifest_version_identity="")):
            try:
                r = real_eval(R.auth(), policy=replace(R.policy, **kw))
            except Exception:
                continue
            self.deny(r)


class E_FailClosed(unittest.TestCase, Deny):
    def test_root_variants_never_permit(self):
        root = tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
        variants = [None, object(), replace(root, execution_policy_authority_sha=E.upper()),
                    replace(root, execution_policy_authority_sha=E + "0"),
                    replace(root, expected_policy_identity=POL_ID.upper()),
                    replace(root, expected_harness_identity="*")]
        for v in variants:
            with patch.object(h, "get_trusted_execution_policy_root", lambda v=v: v):
                try:
                    r = api.A2Harness(R.binding, R.policy).evaluate_input_read(
                        api.StructuredAuditLog(()), "ASTRA_TEST_ONLY", R.input, R.executor, R.auth())
                except Exception:
                    continue
                COUNT["real_evals"] += 1
                self.deny(r)
        self.assertIs(h.get_trusted_execution_policy_root(), tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)

    def test_guarded_maps_everything_to_known_codes(self):
        for fn, expected in ((lambda: 10.0, 30), (lambda: True, 30), (lambda: 99, 30), (lambda: None, 30),
                             (lambda: (_ for _ in ()).throw(KeyboardInterrupt()), 40),
                             (lambda: (_ for _ in ()).throw(SystemExit(0)), 40),
                             (lambda: (_ for _ in ()).throw(MemoryError()), 40),
                             (lambda: 0, 0), (lambda: 30, 30)):
            self.assertEqual(op.guarded(fn), expected)


# ---------------------------------------------------------------- synthetic-only

SYN_E = "3" * 40


def synthetic_objects(branch="D2"):
    t = TestContext()
    o = op.Objects()
    o.binding, o.input, o.output, o.policy = t.binding, t.input, t.output, t.policy
    o.executor, o.recipient, o.approver = t.reader, t.recipient, t.approver
    o.read_authorization = api.ActionAuthorization("TEST_ONLY_READ", SYN_E, t.reader.actor_id,
                                                   api.Role.EXECUTOR, api.Action.READ_INPUT,
                                                   api.AuthorizationState.AUTHORIZED)
    o.release_authorization = None
    o.ledger = None
    o.execution_authority_sha = SYN_E
    o.input_record_id, o.output_record_id, o.incident_identifier = "TEST_ONLY_IN", None, None
    o.accepted_codes = frozenset({op.INPUT_SUCCESS_CODE})
    o.branch, o.approval_artifact = branch, None
    return t, o


def synthetic_root(t):
    return api.TrustedExecutionPolicyRoot(
        execution_policy_authority_sha=SYN_E,
        expected_construction_authority_sha=t.binding.owner_authority_sha,
        expected_harness_identity=t.binding.harness_identity,
        expected_harness_version_or_commit_identity=t.binding.harness_version_or_commit_identity,
        expected_policy_identity=api.harness_policy_identity(t.policy))


class MemWriter:
    class OutputLimitExceeded(Exception): pass
    class OutputTargetExists(Exception): pass
    class InvalidOutputName(Exception): pass

    def __init__(self):
        self.writes = []
        from research.weather_forward.v4.a2_operation.common import bounded_output as bo
        self.encode_result = bo.encode_result

    def write_bounded(self, directory, name, payload):
        self.writes.append((directory, name, payload))


class F_SyntheticD2Channel(unittest.TestCase):
    def setUp(self):
        self.t, self.o = synthetic_objects()
        self.p = patch.object(h, "get_trusted_execution_policy_root", lambda: synthetic_root(self.t))
        self.p.start()

    def tearDown(self):
        self.p.stop()
        self.assertIs(h.get_trusted_execution_policy_root(), tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)

    def test_d2_positive_writes_exactly_fifteen_elements_code_0(self):
        w = MemWriter()
        self.assertEqual(op.finish(api, self.o, w, "/srv/a2out", "x.json"), 0)
        self.assertEqual(len(w.writes), 1)
        result = json.loads(w.writes[0][2].decode("utf-8"))
        self.assertEqual(len(result), 15)
        self.assertEqual(set(result), set(op.RESULT_ELEMENTS))
        self.assertEqual(result["structural_linkage_status"], "INPUT_LINKED_RELEASE_NOT_ATTEMPTED")
        self.assertEqual(result["release_state"], ["BLOCKED"])
        self.assertEqual(result["execution_authority_reference"], SYN_E)
        self.assertEqual(result["acknowledged_log_record_references"], ["TEST_ONLY_IN"])
        self.assertEqual(result["actor_role_bindings"], [["TEST_ONLY_READER", "EXECUTOR"]])
        self.assertLessEqual(len(w.writes[0][2]), 65536)

    def test_d2_never_attempts_release_even_with_release_objects(self):
        self.o.approval_artifact = {"repository": "x", "path": "y", "commit": "4" * 40, "blob": "5" * 40}
        self.o.release_authorization = api.ActionAuthorization(
            "TEST_ONLY_REL", SYN_E, self.t.approver.actor_id, api.Role.RELEASE_APPROVER,
            api.Action.RELEASE_OUTPUT, api.AuthorizationState.AUTHORIZED)
        self.o.output_record_id = "TEST_ONLY_OUT"
        self.o.accepted_codes = frozenset({op.INPUT_SUCCESS_CODE, op.OUTPUT_SUCCESS_CODE})
        with patch.object(api.A2Harness, "evaluate_output_release",
                          side_effect=AssertionError("release attempted on D2")):
            self.assertEqual(op.finish(api, self.o, MemWriter(), "/srv/a2out", "x.json"), 0)

    def test_structural_linkage_mismatch_stops_without_write(self):
        for mutate in (lambda o: setattr(o, "execution_authority_sha", "4" * 40),
                       lambda o: setattr(o, "binding", replace(o.binding, owner_authority_sha="5" * 40)),
                       lambda o: setattr(o, "accepted_codes", frozenset({"OTHER"}))):
            t, o = synthetic_objects()
            mutate(o)
            w = MemWriter()
            self.assertEqual(op.finish(api, o, w, "/srv/a2out", "x.json"), 30)
            self.assertEqual(w.writes, [])

    def test_out_of_domain_sequence_shapes_stop(self):
        first = op.execute(api, self.o)[1]
        for fake in ((0, first, "INPUT_AND_RELEASE_LINKED"), (0, first, "OTHER"),
                     (10, first, "INPUT_LINKED_RELEASE_NOT_ATTEMPTED"), (0, first + first,
                     "INPUT_LINKED_RELEASE_NOT_ATTEMPTED"), (True, first, "INPUT_LINKED_RELEASE_NOT_ATTEMPTED"),
                     (0, first, None)):
            w = MemWriter()
            with patch.object(op, "execute", lambda api_, o, fake=fake: fake):
                self.assertEqual(op.finish(api, self.o, w, "/srv/a2out", "x.json"), 30, fake[2])
            self.assertEqual(w.writes, [])

    def test_build_result_rejects_14_or_16_elements(self):
        _, ev, link = op.execute(api, self.o)
        for elems in (op.RESULT_ELEMENTS[:-1], op.RESULT_ELEMENTS + ("extra",)):
            with patch.object(op, "RESULT_ELEMENTS", elems):
                with self.assertRaises(op.StopOperation):
                    op.build_result(api, self.o, ev, link)

    def test_build_result_domain_of_linkage_not_self_checked(self):
        # Observation reproduced: build_result alone accepts an out-of-domain linkage string;
        # finish() is the only enforcement point.
        _, ev, _ = op.execute(api, self.o)
        res = op.build_result(api, self.o, ev, "NOT_IN_DOMAIN")
        self.assertEqual(res["structural_linkage_status"], "NOT_IN_DOMAIN")

    def test_output_limit_and_existing_target(self):
        from research.weather_forward.v4.a2_operation.common import bounded_output as bo

        class Big(MemWriter):
            def write_bounded(self, d, n, p):
                raise bo.OutputLimitExceeded()

        class Exists(MemWriter):
            def write_bounded(self, d, n, p):
                raise bo.OutputTargetExists()
        for writer, code in ((Big(), 50), (Exists(), 30)):
            writer.OutputLimitExceeded, writer.OutputTargetExists = bo.OutputLimitExceeded, bo.OutputTargetExists
            writer.InvalidOutputName = bo.InvalidOutputName
            self.assertEqual(op.finish(api, self.o, writer, "/srv/a2out", "x.json"), code)


class G_ContextAndContent(unittest.TestCase):
    def test_fifteen_elements_equal_frozen_manifest_list_in_order(self):
        text = json.loads(frozen_text("output_manifest_d2_v1.json"))["fields"]["exact_metric_or_artifact"]
        prefix = "STRUCTURAL_REPORT_ONLY: "
        self.assertTrue(text.startswith(prefix))
        items = tuple(x.strip() for x in text[len(prefix):].split(";"))
        self.assertEqual(len(items), 15)
        self.assertEqual(len(set(items)), 15)
        self.assertEqual(items, op.RESULT_ELEMENTS)

    def test_context_missing_or_extra_keys_and_d2_release(self):
        base = {"schema": op.CONTEXT_SCHEMA, "branch": "D2", "output_directory": "/srv/a2out",
                "result_file_name": "a2-doc-v1-d2-input-result-001.json",
                "harness_source_blobs": {n: "0" * 40 for n in op.HARNESS_PRODUCTION_FILES},
                "authority_binding": {"owner_authority_sha": "1" * 40, "harness_identity": "TEST_ONLY",
                                      "harness_version_or_commit_identity": "TEST_ONLY",
                                      "manifest_version_identity": "TEST_ONLY"},
                "input_manifest": {"kind": "InputManifest"}, "output_manifest": {"kind": "OutputManifest"},
                "policy": {"kind": "HarnessPolicy"}, "execution_authority_sha": "2" * 40,
                "executor": {"actor_id": "TEST_ONLY_A", "role": "EXECUTOR"},
                "recipient": {"actor_id": "TEST_ONLY_B", "role": "RESEARCH_VIEWER"},
                "approver": {"actor_id": "TEST_ONLY_C", "role": "RELEASE_APPROVER"},
                "read_authorization": {"authorization_id": "TEST_ONLY", "authority_sha": "2" * 40,
                                       "actor_id": "TEST_ONLY_A", "declared_role": "EXECUTOR",
                                       "action": "READ_INPUT", "state": "DENIED"},
                "release": None, "log": {"input_record_id": "TEST_ONLY_IN", "output_record_id": None,
                                         "incident_identifier": None},
                "accepted_detail_codes": [op.INPUT_SUCCESS_CODE]}
        op.validate_context(json.loads(json.dumps(base)))
        bad = []
        c = json.loads(json.dumps(base)); c.pop("log"); bad.append(c)
        c = json.loads(json.dumps(base)); c["extra"] = 1; bad.append(c)
        c = json.loads(json.dumps(base)); c["release"] = {"authorization": None, "approval_artifact": None, "ledger": None}; bad.append(c)
        c = json.loads(json.dumps(base)); c["log"]["output_record_id"] = "TEST_ONLY_OUT"; bad.append(c)
        c = json.loads(json.dumps(base)); c["output_directory"] = "/srv/a2out/"; bad.append(c)
        c = json.loads(json.dumps(base)); c["result_file_name"] = "../x"; bad.append(c)
        c = json.loads(json.dumps(base)); c["branch"] = "D3"; bad.append(c)
        c = json.loads(json.dumps(base)); c["harness_source_blobs"]["extra.py"] = "0" * 40; bad.append(c)
        c = json.loads(json.dumps(base)); c["accepted_detail_codes"] = []; bad.append(c)
        c = json.loads(json.dumps(base)); c["execution_authority_sha"] = E.upper(); bad.append(c)
        for c in bad:
            with self.assertRaises(op.ContextError):
                op.validate_context(c)

    def test_blob_pin_gate(self):
        good = {"__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
                "contract.py": "f6f94a4a472e3f6652a1502f6afb5825721364d0",
                "harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
                "trusted_root.py": CAND_BLOB}
        d = V4 / "a2_harness"
        self.assertEqual(op.verify_harness_blobs(lambda n: (d / n).read_bytes(), good), good)
        for exp in (dict(good, **{"trusted_root.py": H_ROOT_BLOB}),
                    dict(good, **{"contract.py": good["harness.py"], "harness.py": good["contract.py"]}),
                    {k: v for k, v in good.items() if k != "__init__.py"}):
            with self.assertRaises(op.StopOperation):
                op.verify_harness_blobs(lambda n: (d / n).read_bytes(), exp)

    def test_frozen_content_with_missing_or_extra_field_rejected(self):
        for name in ("input_manifest_d2_v1.json", "output_manifest_d2_v1.json", "harness_policy_d2_v1.json"):
            doc = json.loads(frozen_text(name))
            k = next(iter(doc["fields"]))
            missing = json.loads(json.dumps(doc)); missing["fields"].pop(k)
            extra = json.loads(json.dumps(doc)); extra["fields"]["astra_extra"] = "x"
            for d in (missing, extra):
                with self.assertRaises(Exception):
                    via_h.build_object(api, via_h.load_document(json.dumps(d)))


class Z_Counters(unittest.TestCase):
    def test_zz_no_permit_on_real_root(self):
        self.assertEqual(COUNT["real_permits"], 0)
        self.assertEqual(COUNT["authorized_blocked_by_guard"], 0)
        self.assertGreater(COUNT["real_evals"], 30)


if __name__ == "__main__":
    import atexit
    atexit.register(lambda: print("ASTRA_COUNTERS=" + json.dumps(COUNT, sort_keys=True), file=sys.stderr))
    unittest.main(argv=[sys.argv[0], "-v"])
```

## G. Revue du canal D2 et tableau des 15 éléments gardés

### G.1 Route D2 et fermeture de D1

- E (tableau A, B.1, B.3, C) choisit D2 et déclare `D1_ROUTE = CLOSED_IN_CURRENT_STATE` ; aucune autorisation RELEASE_OUTPUT, `release = null`, `output_record_id = null`.
- Le gel output `7651de7e` garde `quarantine_status = BLOCKED_PENDING_OWNER_REVIEW`, `cumulative_disclosure_risk = UNRESOLVED`, `efficacy_leakage_assessment = UNRESOLVED` : les prérequis D1 de L2-D ne sont pas remplis, ce qui est cohérent avec la fermeture de D1.
- Dans le script : `validate_context` refuse toute section `release` ou `output_record_id` sur D2 (rc=30 reproduit) ; `release_prerequisites_present` exige `branch == "D1"` et un output CLEAR. Même avec des objets de release AUTHORIZED injectés, aucun second appel n'a lieu sur D2 (test synthétique). Le code `10` est donc inatteignable sur D2 par construction du script (ST + SY). E B.6 le classe en incident `A2_INC_UNIT_ABNORMAL` s'il apparaissait.
- Barrière de quarantaine : sur la root réelle, `OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE` n'est pas atteignable sans franchir l'autorisation de release (ST, lecture `harness.py`) ; seule sa sémantique synthétique est démontrée.

### G.2 Fail-closed et liaison input/output/policy/root

- **Root ↔ policy** : `_resolve_trusted_root` compare `expected_policy_identity` à `harness_policy_identity(policy)`, puis C, composant, version au binding ; la policy porte les identités input/output ; le harnais vérifie l'input contre la policy. Chaîne reproduite par 3 voies et par les mutations du §F.
- **Root ↔ autorisation ↔ contexte** : l'`authority_sha` de l'autorisation est comparé à `execution_policy_authority_sha` de la root (refus reproduits). Le script compare ensuite l'enregistrement de journal produit au record attendu reconstruit depuis le contexte (`execution_authority_sha`, C, identité, acteur, autorisation, états) ; tout écart → 30 sans écriture (SY).
- **Fail-closed du script** : toute exception → 40 ; tout code hors {0,10,30,40,50} ou non-`int` (y compris `bool`) → 30 ; dépassement → 50 sans résultat final ; cible existante → 30 ; aucune sortie stdout/stderr observée.
- **Limite** : la liaison exacte des **valeurs réelles du contexte** (épingles des 4 fichiers dont `9704a844…`, autorisation `a2-doc-v1-read-input-blue`, `INPUT_LOG_RECORD_ID`, nom de fichier, `accepted_detail_codes`) ne peut pas être revue : le contexte n'existe pas (J-1). `validate_context` ne vérifie que la forme ; l'égalité aux valeurs de E repose sur ce fichier absent et sur une vérification externe B.5(f).

### G.3 Canal de contrôle (codes et mesures)

| Élément du canal | Source | Revue Astra | Statut |
|---|---|---|---|
| `0` fin normale (input valide, pas de release) | Script, E B.6 | Atteint en synthétique ; écrit un fichier unique | SY |
| `10` | Script | Inatteignable sur D2 (ST + SY) ; vaudrait incident | CONFORME |
| `30` STOP | Script | Atteint sur tous les écarts testés, sans écriture | SY + RR (lancements synthétiques) |
| `40` exception | `guarded` | Atteint (y compris `BaseException`) | SY |
| `50` limite | `finish` | Atteint (écrivain simulé) | SY |
| Signaux, timeout, OOM, erreur de lancement, stdout/stderr à null, mesures systemd | Unité `a2_unit_profile.sh` + L2-A | **Non qualifiés** ; dépendent de L2-A | **BLOCKED_MISSING_EVIDENCE** (J-2) |
| Existence/absence de résultat | E C.5 | Le script n'écrit qu'au code 0 (ou 10 sur D1) ; l'existence ne se déduit pas du code seul (E C.5) | ST |

### G.4 Liste canonique des 15 éléments gardés

Source gelée commune : `a2_operation/frozen/output_manifest_d2_v1.json`, blob `7651de7e718a276b596f2256aff0877e771e5d6d`, champ `fields.exact_metric_or_artifact`, identité output `sha256:b8157e4e…990976`, gel `245f193`. Le texte est `STRUCTURAL_REPORT_ONLY: ` suivi de **15** noms distincts séparés par `;`, identiques et dans le même ordre que `RESULT_ELEMENTS` du script (blob `8999ba9d…`). Il y en a 15, ni 14 ni 16 (test Astra G et F.1). `build_result` vérifie l'ensemble exact des clés (14 ou 16 → STOP).

Les valeurs ci-dessous sont **déterminées statiquement** par E et la configuration figée pour un code 0 sur D2. Elles ne sont pas observées sur la configuration réelle (lot 4).

| # | Élément (chemin JSON) | Valeur ou domaine autorisé sur D2 (code 0) | Identité / origine | Preuve L2-I/L2-J | Résultat adversarial Astra |
|---|---|---|---|---|---|
| 1 | `validation_state` | `["VALID"]` | Décision harnais | Prédicat script (L2-B) ; L2-I synthétique | Toute autre valeur → 30 (prédicat) ; SY |
| 2 | `permit_or_deny_state` | `["PERMIT"]` | Décision harnais | idem | DENY → 30 ; 0 PERMIT réel en revue |
| 3 | `quarantine_state` | `["CLEAR"]` — état de la **décision de lecture input**, pas `quarantine_status` de l'output (qui reste `BLOCKED_PENDING_OWNER_REVIEW`) | Décision harnais | idem | Autre → 30 ; voir J-8 (lisibilité) |
| 4 | `release_state` | `["BLOCKED"]` | Décision harnais | idem | `["BLOCKED"]` observé en SY |
| 5 | `completion_state` | `["COMPLETED"]` | Décision harnais | idem | Autre → 30 |
| 6 | `stop_reason` | `[null]` | Décision harnais | idem | Non-null → 30 |
| 7 | `detail_code` | `["INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED"]` ; domaine = `accepted_detail_codes` de E B.4 | E B.4 | L2-B | Code hors scope → 30 sans écriture |
| 8 | `input_manifest_reference` | `sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00` | Blob `f85205f3…`, gel `245f193` | Dossier §2 ; L2-I constantes | 3 voies concordantes ; mutations → DENY |
| 9 | `output_manifest_reference` | `sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976` | Blob `7651de7e…`, gel `245f193` | idem | 3 voies concordantes |
| 10 | `policy_reference` | `sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60` | Blob `6a1fa30f…`, gel `79f6e92` ; = root | idem | Policy altérée → ROOT_MISMATCH |
| 11 | `construction_authority_reference` | `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` (C) | Binding = policy = root | L2-I discordances | Substituts (E, candidat, blobs) → ROOT_MISMATCH |
| 12 | `execution_authority_reference` | `6e0320f15d48a924cef9507af5641e47de9fe938` (E) | Contexte, = root, = autorisation | L2-I constantes | Contexte ≠ root → 30 (SY) ; substituts → DENY (RR) |
| 13 | `actor_role_bindings` | `[["blue.weather-v4.a2.doc-integration.v1","EXECUTOR"]]` (destinataire/approbateur absents sur D2) | E B.3 | L2-B | Paires confondues → DENY ; SY : une seule paire |
| 14 | `acknowledged_log_record_references` | `["a2-doc-v1-d2-log-input-read-001"]` | E B.4 | — | SY : un seul record acquitté |
| 15 | `structural_linkage_status` | `"INPUT_LINKED_RELEASE_NOT_ATTEMPTED"` ; domaine fermé E C.1 (2 valeurs, 1 atteignable sur D2) | E C.1, B.6 | L2-I §6 (observation) | Hors domaine → 30 via `finish` ; `build_result` seul ne contrôle pas (J-7) |

Les éléments 7, 12, 13 et 14 dépendent du **contexte**, qui n'est pas matérialisé. Leurs valeurs sont celles que E fixe. Que le contexte réel les porte exactement reste à prouver (J-1).

## H. Écarts connus

### H.1 Commit d'outillage `1910994` publié par une autre session

- **Octets et provenance.** Auteur et committer `fahimahmedb <fahimbentata@gmail.com>`, 2026-10-07 14:09 +0200, commit **non signé** (`%G? = N`), parent `112933c` (Claude). La session Builder désignée par Owner (`ccd4747`) est `session_016Mii9xHWUhsB3DEuB88zpz` ; les autres commits de la lignée sont signés `Claude <noreply@anthropic.com>`. Le message de commit déclare l'autorité `276fd99`/`ccd4747`. Les 21 fichiers de `1910994` (dont `operation/a2_doc_integration_operation.py`, `common/bounded_output.py`, `identity_*`, `verification/*`) sont inchangés jusqu'à `51f49c8`, `5b381d3` et `5358c7a` (`git diff --stat 1910994 51f49c8` : uniquement des ajouts). Ses tests passent en 3.12.3 et 3.13.16 (§E.3).
- **Indépendance de la présente revue** : non affectée. J'ai revu et testé les octets eux-mêmes.
- **Chaîne de garde** : affectée. L'auteur n'est pas la session Builder désignée, et Git ne peut pas authentifier l'identité de session. Le script d'opération qui serait exécuté au lot 4 provient de ce commit.
- **Validité technique** : établie pour les octets revus, aux blobs du §B.3, dans les limites des catégories ST/SY.
- **Classement : `NON_BLOCKING_JUSTIFIED`** pour la validité technique du lot 3, parce que les octets sont figés, revus et testés indépendamment. **Condition résiduelle** : Owner reconnaît ou rejette explicitement cette provenance au titre de B.5(e) (« origine des autorisations et correspondance de session »). Astra ne peut pas le faire à sa place.

### H.2 Qualification VM L2-A reportée

Aucun constat, transcript ou mutation d'hôte n'existe. Aucune preuve locale de cette revue (hook d'audit, écrivain mémoire, absence de stdout) ne s'y substitue. Le profil d'unité `a2_unit_profile.sh` (`ec58a081…`) n'a pas été exécuté. **Classement : `BLOCKED_MISSING_EVIDENCE`**, élément exigé par L2-J, prérequis du canal de contrôle (G.3) et de B.5(b).

### H.3 Python 3.13 contre 3.12

- Reproduit en 3.13.16 et 3.12.3 : L2-I, outillage (deux snapshots) et suite adversariale Astra donnent des résultats identiques (mêmes tests, mêmes trois écarts aux mêmes lignes, mêmes motifs, 0 PERMIT réel). Différences observées : (a) format des tracebacks (soulignements en 3.13), (b) compteurs d'audit 88/52 contre 89/53, c'est-à-dire un module de bibliothèque standard supplémentaire lu en 3.12 et son cache refusé, sans violation.
- Non reproduit : 3.12.14 (version de la première livraison L2-B), ni la version Python ou l'architecture de la VM, inconnues.
- **Classement : `NON_BLOCKING_JUSTIFIED`** pour l'écart 3.13 ↔ 3.12 du poste Builder, désormais démontré sans effet sur les résultats en 3.12.3. **Borne** : aucune conclusion sur 3.12.14 au-delà de la même ligne mineure, ni sur l'interpréteur de l'hôte, qui reste un point L2-A/B.5(f) (`BLOCKED_MISSING_EVIDENCE` pour l'hôte, inclus dans H.2).

## I. Limite lot 4 et contrôle des conditions d'effet B.5 de E

`REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4`. Cette revue n'a ni exécuté ni simulé une évaluation permissive réelle. Elle n'en conclut pas qu'une telle évaluation réussirait. Le `VALID` de `validate_binding` sur le binding réel (L2-I et Astra) est une propriété statique de liaison, sans autorisation, journal ni PERMIT. **Avis sur la question laissée ouverte par L2-I §7.2** : cet appel ne constitue ni un `evaluate_*` ni un « appel sur le tuple réel complet autorisé » ; il est admissible dans L2-I, mais ne doit jamais être présenté comme un indice de succès du lot 4.

| B.5 | Condition | Autorité propre | Preuve examinée | Statut |
|---|---|---|---|---|
| (a) | PASS Astra lot 3 sur snapshots exacts candidat/outillage/contexte, canal de contrôle et contenu gardé | Astra lot 3 | Présente revue | **NON SATISFAITE** — verdict `BLOCKED_INCOMPLETE_EVIDENCE` (contexte absent, canal partiellement non qualifiable) |
| (b) | Contrôles L2-A réellement qualifiés | Owner (opérateur) + constats | Aucun | **NON SATISFAITE** |
| (c) | Rétention et suppression vérifiées avant garde | Owner | Aucune preuve | **NON SATISFAITE** |
| (d) | Mécanisme d'incident disponible | Owner | Vocabulaire fermé dans E B.4 ; aucune preuve de disponibilité | **NON SATISFAITE** |
| (e) | Origine des autorisations et correspondance de session | Owner | Ratifications consignées par des sessions agents (« délégué ») ; `1910994` hors session désignée | **NON ÉTABLIE** |
| (f) | Code chargé constaté sur l'hôte (4 fichiers harnais dont `9704a844…`, 7 sources d'opération, contexte, profil) | Owner, sur l'hôte | 7 sources = `OPERATION_SOURCE_FILES` (vérifié) ; contexte absent ; aucun constat hôte | **NON SATISFAITE** |
| (g) | Dispositions A1 §5 attestées, sans fixture | Owner | Hors périmètre de cette revue | **NON ÉTABLIE ici** |
| (h) | Canal de diagnostic limité au code accepté | Owner + Astra | Script conforme (ST/SY) ; unité non qualifiée | **PARTIEL** |
| (i) | Décision Owner d'activation nommant commit, blobs, contexte, profil, chemins | Owner lot 4 | Aucune | **NON SATISFAITE** |
| (j) | Plafonds O §8.3 et visibilité | L2-A + Owner | Aucune qualification | **NON SATISFAITE** |
| (k) | Une opération, sans retry | Script + Owner | Script sans boucle de retry (ST) ; exécution future | **NON ÉVALUABLE avant lot 4** |

B.5 n'autorise aucune autre valeur sur les objets examinés : `E_EFFECTIVE = FALSE`.

## J. Constats numérotés, verdict final, conditions résiduelles et prochaine action

| # | Sévérité | Objet exact | Observation | Reproduction | Conséquence | Remède minimal |
|---|---|---|---|---|---|---|
| J-1 | **BLOQUANT (preuve manquante)** | Dossier L2-J `51c6bf2b…` ; outillage `51f49c8` | Aucun fichier de contexte d'opération ni d'épingles finales incluant le blob candidat `9704a844…`. `source_pins.json` (`cbad2196…`) est `L2_B_SYNTHETIC_ONLY` et épingle la root H. | `git ls-tree -r 5358c7a \| grep -i context` → aucun contexte d'opération ; lecture `source_pins.json` | L2-J incomplet ; B.5(a) exige un PASS sur le snapshot du contexte ; éléments 7/12/13/14 et épingles non revus sur l'objet réel | Builder publie le contexte D2 final (valeurs exactes de E B.3/B.4, épingles des 4 fichiers harnais dont `9704a844…`, sans autorisation à l'état AUTHORIZED tant que E est sans effet, si le schéma l'impose : état et règle à expliciter), avec blobs et un test statique d'égalité à E, **sans lancement** ; puis nouvelle revue lot 3 limitée au delta |
| J-2 | **BLOQUANT (preuve manquante)** | L2-A | Constats/transcripts/mutations L2-A absents ; profil d'unité, stdout/stderr null, signaux/OOM/timeout, tmpfs non qualifiés | Dossier §4.1 ; aucun fichier | L2-J incomplet ; canal de contrôle (G.3) partiellement non évaluable ; B.5(b), (j) non satisfaites | Owner exécute L2-A selon `COMMANDS_VM_QUALIFICATION_2026-10-07.md` (`42d953c1…`) et publie les constats expurgés ; revue Astra du delta |
| J-3 | Information | Candidat `73280c3` / `9704a844…` | Conforme à L2-H : un fichier, tuple exact, résolveur, aucune surcharge ; aucune régression hors des 3 écarts prévus | §E.1, §F.1 | Aucun défaut bloquant du candidat | Aucun |
| J-4 | Majeur (limite) | Environnement hôte | Python/architecture de la VM inconnus | — | Compatibilité hôte non démontrée | Inclure version Python et architecture de l'hôte dans les constats L2-A ; rejouer le runner L2-I si la version diffère de 3.12/3.13 |
| J-5 | Majeur (gouvernance, non technique) | `1910994` ; actes `245f193`, `79f6e92`, `6e0320f` | `1910994` publié hors de la session Builder désignée, non signé ; E et les gels consignés par des sessions agents sur la base de messages Owner (E : « Je ratifie le projet e », sans commit cité) | `git cat-file -p 1910994` ; lecture E §Ratification | B.5(e) non établi ; pas d'effet sur la validité technique des octets revus | Owner reconnaît explicitement la provenance de `1910994` et l'attribution des actes, au titre de B.5(e) |
| J-6 | Mineur | L2-I `12432cbc…` §3 et §5 | Anciens runners non relancés ; tests du script d'opération délégués à `test_tooling` (root H) | Comblé par Astra (§E.2, §F.1) | Lacune de preuve, comblée par reproduction indépendante | Aucun pour ce lot ; lors du prochain dossier, consigner les sorties réelles |
| J-7 | Mineur | `a2_doc_integration_operation.py` `8999ba9d…`, `build_result` | Ne contrôle pas lui-même le domaine fermé de `structural_linkage_status` ; `finish` le contrôle avant appel | Test Astra `test_build_result_domain_of_linkage_not_self_checked` + `test_out_of_domain_sequence_shapes_stop` | Pas de fail-open via `finish` ; défense en profondeur absente si `build_result` est réutilisé ailleurs | Optionnel : contrôle de domaine dans `build_result` (changement de blob ⇒ nouvelle revue) |
| J-8 | Mineur (lisibilité) | Élément 3 `quarantine_state` | Vaut `CLEAR` (décision de lecture input) alors que l'output reste `BLOCKED_PENDING_OWNER_REVIEW` | Lecture du script et du harnais | Risque de mauvaise lecture par un futur destinataire | Préciser la sémantique dans la décision lot 4 ; pas de changement de code exigé |
| J-9 | Information | Dossier L2-J | Identité du dossier renvoyée à un commentaire de PR (#22), hors de mon périmètre | Résolu par le commit de la mission | Aucune | Inscrire le commit du dossier dans un objet Git ultérieur |

### Verdict final

**`BLOCKED_INCOMPLETE_EVIDENCE`**. Aucun défaut bloquant n'est trouvé dans le candidat root, dans l'outillage revu ni dans les preuves L2-I reproduites. Le PASS est impossible tant que J-1 (contexte et épingles finales) et J-2 (L2-A) manquent.

```text
VERDICT = BLOCKED_INCOMPLETE_EVIDENCE
CANDIDATE_ROOT_73280c3_TECHNICAL_DEFECT = NONE_FOUND
LEGACY_VERDICT_REPRODUCED = LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED (3.13.16 et 3.12.3)
L2I_RUNNER_REPRODUCED = L2_I_VERIFICATION_PASS (3.13.16 et 3.12.3)
ASTRA_ADVERSARIAL = 27/27 (3.13.16 et 3.12.3) ; REAL_ROOT_EVALUATIONS = 56 ; REAL_ROOT_PERMITS = 0
GUARDED_CONTENT_ELEMENTS = 15 (enumerated) ; CONTEXT_BINDING_OF_ELEMENTS_7_12_13_14 = NOT_REVIEWABLE_CONTEXT_ABSENT
D2_ROUTE = REVIEWED ; D1 = CLOSED ; EXIT_CODE_10_ON_D2 = UNREACHABLE_BY_SCRIPT_CONSTRUCTION
GAP_1910994 = NON_BLOCKING_JUSTIFIED (technique) ; OWNER_B5E_ACKNOWLEDGEMENT_REQUIRED
GAP_L2A_VM = BLOCKED_MISSING_EVIDENCE
GAP_PY313_VS_PY312 = NON_BLOCKING_JUSTIFIED (3.12.3 reproduit) ; HOST_PYTHON = UNKNOWN
VM_QUALIFIED = FALSE_UNLESS_SEPARATELY_PROVEN_BY_OWNER
REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4
E_EFFECTIVE = FALSE
A2_EXECUTION_AUTHORIZED_BY_ASTRA = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED_BY_ASTRA = FALSE
QUARANTINE_LIFTED_BY_ASTRA = FALSE
RELEASE_APPROVAL_BY_ASTRA = NONE
ECONOMIC_AUTHORITY = 0
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```

### Conditions résiduelles

1. J-1 : contexte D2 final et épingles finales publiés, avec leurs blobs, sans lancement.
2. J-2 : constats L2-A d'Owner publiés, expurgés, avec version Python et architecture de l'hôte (J-4).
3. J-5 : reconnaissance Owner de la provenance de `1910994` et de l'attribution des actes (B.5(e)).
4. Toute modification d'un blob listé au §B (candidat, sources d'opération, gels) invalide la partie correspondante de cette revue.

### Prochaine action exacte

```text
NEXT_SAFE_ACTION = FOURNITURE_DES_PREUVES_MANQUANTES :
  (1) Builder désigné : publier le contexte d'opération D2 final + épingles finales (blob candidat 9704a844…), sans lancement ;
  (2) Owner : exécuter et publier L2-A (constats expurgés, Python/architecture hôte) ;
  (3) Owner : statuer sur la provenance de 1910994 (B.5(e)) ;
  puis nouvelle revue Astra lot 3 limitée au delta, sur ces objets exacts.
```

Le commit et le blob de publication de ce rapport sont consignés à l'extérieur du fichier, dans le retour de publication de la session Astra, parce que le fichier ne peut pas contenir son propre hash.
