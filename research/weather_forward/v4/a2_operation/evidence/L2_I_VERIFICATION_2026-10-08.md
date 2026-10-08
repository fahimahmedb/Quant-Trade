# L2-I — Vérification du candidat root (Q7), 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_EVIDENCE_NOT_AN_OWNER_DECISION
VERDICT_RUNNER = L2_I_VERIFICATION_PASS (code de retour 0 = critère composé, pas « 279 tests verts »)
LEGACY_VERDICT = LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED
CANDIDATE_MODIFIED = NO
ACTIVATION = NO ; VM = NON_ACCEDEE ; REAL_TUPLE_PERMIT = 0
```

Chemins relatifs à `research/weather_forward/v4/`. Rôle : Builder, paper/shadow seulement. Aucune décision Owner n'est exprimée ici.

## 1. Références exactes

| Objet | Référence |
|---|---|
| Décision lot 2 (L2-I, annexe A) | `276fd99` ; fichier `owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md`, blob `d9809d0cca1faa51b713f02e453b7233c7a16811` |
| E (D2, ratifiée, conditionnelle) | commit `6e0320f15d48a924cef9507af5641e47de9fe938` ; fichier `owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_D2_2026-10-08.md`, blob `89890a4f224889bc1cc3606c62ea477bb1e7c6b3` |
| Candidat root | branche `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08` @ `73280c3e9d8604b2f2d8e6d2d174aa940389a760`, parent `276fd995fe494e1734bba13827e6103864ce68da` ; un seul fichier modifié (`git diff --stat 276fd99 73280c3` : 1 fichier, +24 −8) ; `a2_harness/trusted_root.py` avant `9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94` (= H), après `9704a844bae0ef54637c76dded5bb82d9f4c334f` |
| Outillage | `builder/weather-v4-a2-lot2-tooling-2026-10-07` @ `51f49c81d843e57111135df283b06368cc1546bf` |
| Sources du harnais (H) | `78d537de681363ed83a6c7787aba4319f3c73c4d` |
| File d'équipe lue | `team/weather-v4-a2-coordination-2026-10-08` @ `c6d4230a9210e0c483912405de4ccd6518822e30` |
| Cette branche | `builder/weather-v4-a2-lot2-l2i-verification-2026-10-08`, créée depuis `51f49c81` (nouveaux fichiers seulement) |

Blobs vérifiés par le runner avant tout import (tous concordants, `PINS_MISMATCH=[]`) : `__init__.py` `bf9a2bdb…`, `contract.py` `f6f94a4a…`, `harness.py` `00ae81d2…`, `trusted_root.py` `9704a844…` (candidat) ; anciens `test_bounded_runtime.py` `aa0159c2…`, `test_d5_public_state_types.py` `52bb94ed…`, `run_bounded_runtime_tests.py` `25b7d3bd…`, `run_d5_type_regression_tests.py` `f660a24d…` ; gels `input_manifest_d2_v1.json` `f85205f3…`, `output_manifest_d2_v1.json` `7651de7e…`, `harness_policy_d2_v1.json` `6a1fa30f…` (identités E tableau A recalculées : input `sha256:5c55b855…bbd00`, output `sha256:b8157e4e…90976`, policy `sha256:2f761da5…3de60`, toutes égales à E et au tuple de la root).

Le candidat n'a pas été modifié. Aucun défaut du candidat n'a été trouvé (section 6).

## 2. Environnement et commandes

Python 3.13.16 (CPython), x86_64, `Linux-6.18.44-fc-v80-x86_64-with-glibc2.39`. **Écart non testé : l'hôte VM n'a pas été accédé ; sa version Python et son architecture sont inconnues (limite pour le lot 3, non acceptée implicitement).**

Répertoire de travail isolé hors dépôt (dossier de scratchpad de session), assemblé sans merge ni activation :

1. `git archive 51f49c81… research/weather_forward/v4/a2_harness research/weather_forward/v4/a2_operation | tar x` (outillage + H).
2. `git show 73280c3e…:research/weather_forward/v4/a2_harness/trusted_root.py > …/a2_harness/trusted_root.py` ; `git hash-object` = `9704a844…` (code retour 0).
3. Copie de `a2_operation/verification/run_l2i_candidate_verification.py` et `test_l2i_candidate.py` (cette branche).
4. `timeout 600 python3 -I -S -B a2_operation/verification/run_l2i_candidate_verification.py` → **code retour 0**, durée 0,29 s (limite externe 600 s).

Blobs des nouveaux fichiers (état final exécuté) : runner `6dcc9fb2304588a1d3fac35e5ee217d1a88ccfa9`, tests `291f7769f68ae5a817f521a5813e931d8bcf4a22`. Sortie complète : `a2_operation/evidence/L2_I_RUN_OUTPUT_2026-10-08.txt` (383 lignes, SHA-256 `660e61225aa1f18c6c0f82928db98a3614dcac708cedb1a7cddb891a278c8f97`).

Historique de réparation des nouveaux fichiers (permis par L2-I) : 1re exécution, 1 échec sur 27 nouveaux tests (`test_no_setter_override_or_environment_path_in_source`, blob de test alors `5a571f33…`) causé par mon test (la sous-chaîne `environ` matchait « environment » du docstring), pas par le candidat ; test réparé (analyse AST du code hors docstring, motifs à frontières de mot) ; le runner a ensuite reçu un seul changement (le champ `real_configuration_evaluated_permissively` est dérivé du compteur au lieu d'être codé en dur) ; l'exécution finale ci-dessus est postérieure aux deux changements.

## 3. Anciennes suites (279 = 145 + 134)

Anciens fichiers de test et runners non modifiés (blobs H ci-dessus). Les anciens runners ne sont pas lancés (ils s'arrêtent sur `PRODUCTION_TRUSTED_ROOT_MODIFIED` / `AUDITED_SOURCE_BYTES_MISMATCH`, refus attendus ; **NON_FAIT : non relancés ici, car l'outillage L2-B les couvre et la décision demande seulement de consigner ces refus attendus**).

Résultat : collectés 279, exécutés 279, réussis 276, échecs 3, erreurs 0, skips 0, expectedFailures 0, unexpectedSuccesses 0.

| Test (préfixe `…test_bounded_runtime.TrustedRootTests.`) | Observé | Prévu par la décision |
|---|---|---|
| `test_production_root_absent_denies_all_authority_bearing_paths` | `AssertionError` ligne **198** `assertIsNone(production_root.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)` : la root est présente | ligne 198, absence de la constante : concordant |
| `test_coordinated_caller_substitution_cannot_create_production_root` | `AssertionError` assertion ligne **179** appelée ligne **212** : `EXECUTION_POLICY_ROOT_MISMATCH is not MISSING_EXECUTION_POLICY_ROOT` ; refus DENY/BLOCKED/non-VALID toujours obtenu, seul le motif change | ligne 179 appelée ligne 212, motif ROOT_MISMATCH au lieu de MISSING : concordant |
| `test_test_only_root_exercises_positive_paths_and_is_restored` | `AssertionError` ligne **227** `assertIsNone(h.get_trusted_execution_policy_root())` après restauration ; les trois chemins positifs sous root patchée ont réussi avant l'assertion | ligne 227 : concordant |

Le runner compare ensemble d'identifiants, type d'exception, numéros de ligne et motifs (pas seulement les trois identifiants). Tout autre écart, erreur, skip ou changement de collecte aurait donné un échec (aucun). Verdict : `LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED`. Les tracebacks complets sont dans la sortie.

Audit (hook d'audit de processus, non une isolation système) : réseau 0, sous-processus 0, fichiers interdits 0 ; lectures permises 88 ; refus attendus de caches `.pyc` 52 (non nuls attendus, ce ne sont pas des violations).

## 4. Nouveaux tests (27, tous réussis ; 0 échec, 0 erreur, 0 skip)

Fichier `a2_operation/verification/test_l2i_candidate.py`. Réparties : constantes de root (5), discordances de binding (4), refus d'action sur root réelle (8), synthétique seul (7), blob/commit (3).

**Root réelle — constantes (L2-I.1).** Tuple exact `(6e0320f1… , 37e3b25f… , research/weather_forward/v4/a2_harness , weather-v4-a2-doc-integration-v1 , sha256:2f761da5…3de60)` ; résolveur renvoie la constante ; `harness.get_trusted_execution_policy_root` est la fonction de `trusted_root` (pas de shadow) ; identités réelles recalculées = E ; analyse AST : une seule fonction, imports limités, aucun `environ/getenv/setattr/global/open/exec/eval/importlib`, SHA E présent 3 fois, aucun SHA de commit candidat dans le code ; root immuable.

**Root réelle — discordances (L2-I.1).** Baseline : `validate_binding` du binding réel contre la root réelle est `VALID` (`AUTHORITY_AND_TRUSTED_ROOT_VALID`) ; ce n'est ni un `evaluate_*`, ni un PERMIT, ni un journal, ni une autorisation (voir limite 7.2). Écart unique, chacun refusé à sa barrière : construction → `TRUSTED_ROOT_CONSTRUCTION_AUTHORITY_MISMATCH` ; composant → `TRUSTED_ROOT_HARNESS_IDENTITY_MISMATCH` ; version → `TRUSTED_ROOT_HARNESS_VERSION_MISMATCH` ; policy altérée → `TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH` (tous `EXECUTION_POLICY_ROOT_MISMATCH`) ; version de manifest → `AUTHORITY_MISMATCH / MANIFEST_VERSION_IDENTITY_MISMATCH` (passe la root, échoue après). Substitution coordonnée binding+policy → `ROOT_MISMATCH / POLICY_IDENTITY_MISMATCH`.

**Root réelle — actions (L2-I.2).** 22 appels `evaluate_input_read` sur root + manifests + policy réels, **tous avec une autorisation jamais AUTHORIZED** (garde `real_eval` qui lève une exception sinon, vérifiée : 1 tentative AUTHORIZED refusée par la garde, 0 évaluation créée), tous DENY/BLOCKED/non-VALID : état DENIED ou UNRESOLVED citant E → `UNAUTHORIZED_READER / ACTION_AUTHORIZATION_NOT_AUTHORIZED` ; SHA E erroné (zéros, commit candidat `73280c3e…` pris pour E, majuscules, dernier caractère modifié) → `AUTHORITY_MISMATCH / …EXECUTION_POLICY_AUTHORITY_MISMATCH` ; acteur/rôle/action discordants → `…ACTOR_MISMATCH / ROLE_MISMATCH / ACTION_MISMATCH` (avant l'autorité) ; statut hors domaine (`"APPROVED"`, `None`, `1`) → refus ou exception, jamais PERMIT, et `AuthorizationState("APPROVED")` lève `ValueError` ; substitution de manifest et de policy ; root patchée avec SHA E différent → `AUTHORITY_MISMATCH` ; fail-closed : root `None`, champs vides, SHA court, identité de policy invalide, objet non-root, getter qui lève → refus ou exception, jamais PERMIT. Compteurs finaux : `real_tuple_evaluations = 22`, `real_tuple_permits = 0`.

**Synthétique seul (L2-I.3, I.4).** Objets `TestContext` (`TEST_ONLY_*`), root patchée à autorité `"2"*40` (≠ E, vérifié), identifiants synthétiques : séquence positive read PERMIT/release BLOCKED + release AUTHORIZED synthétique, root réelle rétablie ensuite ; substitution refusée ; statuts hors domaine (y compris la chaîne `"AUTHORIZED"` non-enum) refusés ; **barrière quarantaine** (`QUARANTINED`, `BLOCKED_PENDING_OWNER_REVIEW`) → `OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE` ; ledger vide ou BLOCKED refusé ; ID de journal dupliqué non acquitté ; fuite `UNRESOLVED` refusée. Constat statique I.4 : la root réelle ne peut atteindre `OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE` sans franchir l'autorisation de release ; le lot 2 ne la franchit pas. **Couverture de la quarantaine sur la config réelle : NON_DÉMONTRÉE ; seule la sémantique synthétique l'est.**

**Blob/commit (adversarial).** `verify_harness_blobs` accepte les quatre blobs réels ; refuse `trusted_root.py` avec SHA E remplacé, un octet ajouté, un caractère modifié ; refuse le blob H deny-all pris pour candidat.

## 5. Script d'opération (L2-I.5) et suite L2-B

**NON_FAIT dans les nouveaux tests** : la logique du script d'opération (succès input avec release BLOCKED, absence de preuve de release, codes inattendus, limites de sortie) n'est pas retestée ici ; elle est couverte par `test_tooling.py` (L2-B, objets synthétiques). Vérification informative sur le candidat (hors verdict) : `PYTHONPATH=. python3 -S -B -m unittest …verification.test_tooling` → 64 tests, OK. Le profil réel d'écriture et d'absence de stdout/stderr relève de L2-A (non faite).

## 6. Défauts et observations

- **Défaut candidat : aucun** (diff d'un seul fichier conforme à L2-H ; tuple conforme à E).
- Défaut de mon nouveau test, réparé (section 2).
- Observation outillage (non-candidat) : `build_result(..., linkage)` du script d'opération ne valide pas lui-même le domaine fermé de `structural_linkage_status` (E §C.1) ; seules les deux valeurs produites par `execute()` sont atteignables. Non corrigé (hors périmètre, outillage L2-B) ; à relever par le lot 3.
- Porte d'épingles : une copie de `trusted_root.py` dont l'identité de policy diffère d'un caractère fait sortir le runner avec le code 2 (`PINS_MISMATCH`) avant tout import (essai de mutation sur copie jetable ; aucun test de mutation des barrières du harnais n'a été fait : NON_FAIT).

## 7. Limites pour le lot 3

1. Python 3.13.16 / x86_64 Builder ; hôte VM non comparé.
2. `validate_binding` a été appelé sur le tuple réel (retour `VALID`, sans autorisation ni PERMIT). Je l'ai jugé hors de l'interdiction « évaluation permissive » ; Astra ou Owner peuvent trancher autrement.
3. Sémantique du hook d'audit : contrôle de processus, pas une isolation.
4. Les commits de l'outillage `1910994` (autre session) restent à signaler au lot 3 (fiche de reprise).
5. Aucun artefact d'approbation de release n'existe ; RELEASE_OUTPUT n'a pas été exercée sur le tuple réel.

```text
A2_EXECUTION_AUTHORIZED_BY_LOT2 = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
E_EFFECT = NOT_IN_EFFECT
NEXT_SAFE_ACTION = Q8_L2_J_EVIDENCE_DOSSIER (Builder), puis lot 3 (Astra neuve)
```
