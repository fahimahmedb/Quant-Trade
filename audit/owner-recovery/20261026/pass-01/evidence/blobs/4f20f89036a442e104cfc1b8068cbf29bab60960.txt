# Q22 — Déploiement et attestation du code chargé (E B.5(f)), 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
EXECUTED_ON_VM = NO ; EXECUTED_ON_REAL_FILES = NO ; TESTED_ON = SYNTHETIC_TEMP_DIRECTORIES_ONLY
E_EFFECTIVE = FALSE ; NEW_COMMANDS_FOR_OWNER = YES (non encore relues par Codex, jamais lancées sur une VM)
```

Comble le manque relevé au kit Q15 : E §5(f) (« code chargé constaté sur l'hôte contre les blobs approuvés ») n'avait aucune commande. Les 13 objets approuvés sont ceux de `a2_operation/frozen/final_pins_d2_v1.json` (même contenu, format TSV pour l'hôte : `final_pins_d2_v1.tsv`).

| Fichier (`a2_operation/`) | Rôle |
|---|---|
| `qualification/deploy_operation_files.sh` | root ; vérifie les 13 sources en réception contre les épingles, refuse tout remplacement d'un fichier différent, installe en 0444 `root:root`, n'exécute rien |
| `qualification/attest_loaded_code.sh` | lecture seule ; compare les 13 fichiers déployés aux blobs approuvés, refuse tout lien symbolique et tout fichier `.py/.sh/.pth/.so/.pyc/.json` non épinglé dans `a2_harness` et `a2_operation` (le dossier `qualification/` est ignoré) ; n'importe et n'exécute rien |
| `verification/test_host_scripts.py` | 6 tests synthétiques (déploiement, idempotence, source altérée ou en lien, chemin hors périmètre, cible différente, attestation altérée/absente/en trop) |

Contrôle négatif : le test échoue (1 échec) quand le contrôle de blob de l'attestation est désactivé, puis repasse après restauration. Les 9 tests de l'égalité à E passent toujours.

**Enchaînement pour Owner (après L2-A, avec le même terminal), à relire avant usage — modèle : `COMMANDS_VM_QUALIFICATION_2026-10-07.md` §1 à §3.** Le blob des épingles `$A2_PINS_BLOB` est celui de `frozen/final_pins_d2_v1.tsv` au commit de la remise, donné extérieurement.
1. Poste Owner : `git show "$A2_COMMIT:$BASE/a2_operation/frozen/final_pins_d2_v1.tsv" > pins.tsv`, contrôle `git hash-object --no-filters pins.tsv` = `$A2_PINS_BLOB`, puis `git archive --format=tar "$A2_COMMIT" $(cut -f2 pins.tsv) $BASE/a2_operation/frozen/final_pins_d2_v1.tsv $BASE/a2_operation/qualification/deploy_operation_files.sh $BASE/a2_operation/qualification/attest_loaded_code.sh > a2-operation.tar` ; `scp` vers la VM.
2. VM : réception dans un répertoire neuf (comme §2 des commandes), puis `sudo bash <reception>/$BASE/a2_operation/qualification/deploy_operation_files.sh <reception> $A2_PINS_BLOB`, puis `bash <reception>/$BASE/a2_operation/qualification/attest_loaded_code.sh /opt/a2 $A2_PINS_BLOB` : attendu `LOADED_CODE_MATCHES_APPROVED=13/13`, `UNEXPECTED_FILES=0`.
3. Rapporter la sortie (expurgée) ; aucune exécution du script d'opération.

**Limites** : les scripts n'ont pas tourné sur la VM (tmpfs, propriétaire `root`, `git` de l'hôte non observés) ; l'attestation vérifie les octets déployés, pas les modules déjà importés en mémoire ; le candidat `trusted_root.py` déployé doit aussi être le blob `9704a844…` du commit candidat (épinglé dans le TSV) ; les conditions E §5 (c) rétention/suppression et (b) L2-A restent séparées.

```text
NEXT_SAFE_ACTION = contre-lecture Codex de ces scripts (Q22) ; usage seulement après L2-A et après la revue Astra limitée au delta (Q25)
```
