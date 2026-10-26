# L2-J — Dossier de preuves du lot 2 (Q8), 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_EVIDENCE_NOT_AN_OWNER_DECISION
LOT2_STATUS = LOT2_PREPARATION_COMPLETE_WITH_LOCAL_BLOCKERS
LOT2_CANDIDATE_AND_EVIDENCE_READY_FOR_ASTRA_LOT3 = NOT_CLAIMED (L2-A non faite, voir §4)
ASTRA_PASS_WRITTEN_BY_BUILDER = FALSE
```

Chemins relatifs à `research/weather_forward/v4/`. Rôle : Builder, paper/shadow seulement. Aucune décision Owner n'est exprimée ici. Le statut est `WITH_LOCAL_BLOCKERS` parce que L2-J exige les constats de L2-A, qui n'existent pas ; le dossier ne prétend pas l'état « prêt » (décision lot 2, L2-J).

## 1. Branches, commits et blobs

| Objet | Branche | Commit | Blob / note |
|---|---|---|---|
| Décision lot 2 | owner (`276fd99`) | `276fd99` | `d9809d0cca1faa51b713f02e453b7233c7a16811` ; ratification `ccd4747` ; dispositions D2 `9d0698b` |
| Gels input/output | `owner/weather-v4-a2-lot2-freezes-2026-10-08` | `245f193` (gels L2-C/L2-D), `79f6e92…` (policy L2-F), tête `79f6e9290121869cece6d23a259249883b32941a` | input `f85205f3`, output `7651de7e`, policy `6a1fa30f` |
| E (D2, ratifiée, conditionnelle, sans effet) | `owner/weather-v4-a2-execution-authority-e-d2-2026-10-08` | `6e0320f15d48a924cef9507af5641e47de9fe938` | `89890a4f224889bc1cc3606c62ea477bb1e7c6b3` |
| Candidat root | `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08` | `73280c3e9d8604b2f2d8e6d2d174aa940389a760` (parent `276fd99`) | `a2_harness/trusted_root.py` : avant `9d8adeca…` (= H), après `9704a844bae0ef54637c76dded5bb82d9f4c334f` ; un seul fichier modifié |
| Outillage L2-B + transcriptions + identités | `builder/weather-v4-a2-lot2-tooling-2026-10-07` | tête `51f49c81d843e57111135df283b06368cc1546bf` ; `1910994` (L2-B, **publié par une autre session que le Builder désigné**) | `a2_operation/` |
| Vérification L2-I | `builder/weather-v4-a2-lot2-l2i-verification-2026-10-08` | `5b381d34ccdfc938727ccecaf1d09447dcd29ab5` | rapport `12432cbcfea67a01cc334085b30350ba0fef7dcf` ; sortie complète `a6411537fa027a69a7806c82b2c580ded7af141c` ; runner `6dcc9fb2…` ; tests `291f7769…` |
| Présent dossier | `builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08` | voir commentaire de la PR #22 | ce fichier |
| Harnais de référence (H) | — | `78d537de681363ed83a6c7787aba4319f3c73c4d` ; construction C `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` | contract `f6f94a4a`, harness `00ae81d2`, trusted_root `9d8adeca`, `__init__` `bf9a2bdb` |

## 2. Identités et contenus figés (deux méthodes concordantes)

Input `sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00`, output `sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976`, policy `sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60`. Preuves : `a2_operation/evidence/L2_C_L2_D_D2_TRANSCRIPTION_COMPARISON_2026-10-07.md` (blob `72095daa…`), `…L2_E_IDENTITIES_AND_L2_F_POLICY_TRANSCRIPTION_2026-10-08.md` (`7ced3ce2…`), `…L2_F_POLICY_IDENTITY_2026-10-08.md` (`591ea4ce…`). Étalonnage : `identity/calibration_test_only_output_manifest.json`. Les contenus figés sont documentaires, pas des payloads.

## 3. Résultats et couverture

| Élément | Résultat | Source |
|---|---|---|
| Anciens tests (279 = 145 + 134) | 276 réussis, 3 échecs, 0 erreur, 0 skip ; les trois écarts (lignes 198, 179 appelée en 212, 227) concordent avec la décision | L2-I §3 |
| Nouveaux tests (27) | 27 réussis ; 22 évaluations sur la root réelle, 0 PERMIT ; barrière quarantaine : sémantique synthétique seulement, **couverture sur la config réelle NON_DÉMONTRÉE** | L2-I §4 |
| Outillage L2-B (`test_tooling.py`) | 64 tests OK (343 tests synthétiques de L2-B revérifiés en Python 3.13) | L2-I §5, handoff |
| Compteurs d'audit L2-I | réseau 0, sous-processus 0, fichiers interdits 0, lectures permises 88, refus `.pyc` attendus 52 ; hook de processus, pas une isolation | L2-I §3 |
| Environnement | Python 3.13.16, x86_64, Linux 6.18.44 ; la première livraison était en Python 3.12 ; hôte VM inconnu | L2-I §2, §7 |

## 4. Ce qui manque ou reste ouvert (aucun n'est présenté comme fait)

1. **L2-A (qualification de la VM) : NON_FAIT.** Pas de constats, de transcripts ni de mutations d'hôte. Aucune preuve locale ne s'y substitue. Action réservée à Owner (élément 5 de la réserve permanente). Commandes : `qualification/COMMANDS_VM_QUALIFICATION_2026-10-07.md`.
2. Le profil réel d'écriture, d'absence de stdout/stderr et de limites de ressources : relève de L2-A.
3. Le script d'opération n'est pas retesté sur la root réelle (couvert par `test_tooling.py`, objets synthétiques).
4. Mutations de barrières du harnais : NON_FAIT.
5. `build_result` ne valide pas lui-même le domaine fermé de `structural_linkage_status` (observation outillage, non corrigée).
6. `validate_binding` a été appelé sur le tuple réel (retour `VALID`, sans autorisation ni PERMIT) ; à trancher par Astra.
7. Écart de provenance : `1910994` publié par une autre session ; octets vérifiés, à classer par Astra.
8. Visibilité, custody, rétention : aucune donnée réelle ni identité chargée n'a été produite ; la première évaluation permissive sur la config réelle reste au lot 4.

```text
E_EFFECT = NOT_IN_EFFECT
A2_EXECUTION_AUTHORIZED_BY_LOT2 = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
REAL_CONFIGURATION_PERMISSIVE_EVALUATION = NOT_PERFORMED_UNTIL_LOT4
NEXT_SAFE_ACTION = compléter la mission Astra du lot 3 avec ce dossier ; L2-A reste à Owner
```
