# Fiche d'exécution Owner — une session de terminal (2026-10-08)

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
A2_COMMIT (remise) = 6539e2e02e95a3e4d3d41d6a497d32e9a3a08775   (branche builder/weather-v4-a2-lot2-owner-package-2026-10-08, ce fichier est dans un commit ultérieur)
NON_EXECUTE_SUR_UNE_VM = TRUE ; ESSAI_A_BLANC_SUR_REPERTOIRES_TEMPORAIRES = FAIT ; E_EFFECTIVE = FALSE
```

La remise contient tout au même endroit : les 11 fichiers de qualification, les 13 fichiers approuvés (dont le `trusted_root.py` candidat, blob `9704a844…`), les trois scripts d'hôte, le contexte D2 et leurs épingles. **Essai à blanc fait côté équipe :** extraction depuis ce commit, puis attestation `LOADED_CODE_MATCHES_APPROVED=13/13`, `UNEXPECTED_FILES=0` ; 19 tests passent ; les épingles de qualification concordent. Rien de tout cela n'a tourné sur la VM.

Valeurs fixes (à copier telles quelles) :

```bash
A2_COMMIT=6539e2e02e95a3e4d3d41d6a497d32e9a3a08775
QUAL_PIN_BLOB=e718b284982a0f8c5c119be6a44cd1b803651f9b
FINAL_PIN_BLOB=ca113021989ca37a31ab4bcd4c7ba72ea9c3859a
```

**Seule valeur à fournir par vous : l'alias SSH habituel de la VM.**

## Partie 1 — Qualification L2-A (commandes déjà publiées)

Suivre `COMMANDS_VM_QUALIFICATION_2026-10-07.md` (blob `42d953c1…`, même dossier) des §1 à §4 en remplaçant seulement `A2_COMMIT` par la valeur ci-dessus et `A2_HOST` par l'alias. Résultat attendu à la fin du §4 : code retour `0`. Noter la version Python et l'architecture de la VM (affichées par `host_facts.sh`).

## Partie 2 — Préparation de l'archive des fichiers approuvés (sur votre poste, dans le checkout Git de Quant-Trade)

```bash
set -euo pipefail
A2_COMMIT=6539e2e02e95a3e4d3d41d6a497d32e9a3a08775
FINAL_PIN_BLOB=ca113021989ca37a31ab4bcd4c7ba72ea9c3859a
A2_HOST='<alias SSH habituel de la VM>'
BASE=research/weather_forward/v4
A2OP=$BASE/a2_operation
git fetch origin builder/weather-v4-a2-lot2-owner-package-2026-10-08
git show "$A2_COMMIT:$A2OP/frozen/final_pins_d2_v1.tsv" > a2-final-pins.tsv
test "$(git hash-object --no-filters a2-final-pins.tsv)" = "$FINAL_PIN_BLOB"
test "$(wc -l < a2-final-pins.tsv)" -eq 13
git archive --format=tar "$A2_COMMIT" $(cut -f2 a2-final-pins.tsv) \
  "$A2OP/frozen/final_pins_d2_v1.tsv" \
  "$A2OP/qualification/deploy_operation_files.sh" \
  "$A2OP/qualification/attest_loaded_code.sh" \
  "$A2OP/qualification/verify_retention_deletion.sh" > a2-operation.tar
scp a2-operation.tar "$A2_HOST:~/a2-operation.tar"
```

Ces commandes ont été jouées à blanc : l'archive fait 27 entrées et son extraction passe l'attestation.

## Partie 3 — Sur la VM, dans le même terminal (après la Partie 1)

```bash
set -euo pipefail
FINAL_PIN_BLOB=ca113021989ca37a31ab4bcd4c7ba72ea9c3859a
BASE=research/weather_forward/v4
STAGE2="$PWD/a2-operation-reception-20261008"
test ! -e "$STAGE2"
mkdir -m 0700 "$STAGE2"
tar -xf a2-operation.tar -C "$STAGE2" --no-same-owner
sudo bash "$STAGE2/$BASE/a2_operation/qualification/deploy_operation_files.sh" "$STAGE2" "$FINAL_PIN_BLOB"
bash "$STAGE2/$BASE/a2_operation/qualification/attest_loaded_code.sh" /opt/a2 "$FINAL_PIN_BLOB"
sudo bash "$STAGE2/$BASE/a2_operation/qualification/verify_retention_deletion.sh" /srv/a2out
```

Résultats attendus, à noter tels quels (en retirant IP, nom d'hôte et secrets) :
- déploiement : `OPERATION_FILES_DEPLOYED_OR_IDENTICAL=13`, `OPERATION_SCRIPT_EXECUTED=0` ;
- attestation : `LOADED_CODE_MATCHES_APPROVED=13/13`, `UNEXPECTED_FILES=0` ;
- suppression : `DELETION_CAPABILITY=VERIFIED`, `OUTPUT_DIR_FSTYPE=tmpfs`, `PERSISTENT_ACROSS_REBOOT=NO`, `RETENTION_30D_DEMONSTRATED=NO`.

**Arrêt en cas d'écart.** Si une commande affiche `STOP:` ou un code autre que `0`, s'arrêter, ne rien réparer, noter le message. Un `UNEXPECTED_FILE=` lors de l'attestation (par exemple un dossier `__pycache__` créé par la qualification) est un constat à rapporter, pas à effacer.

## Partie 4 — À poster en commentaire de la PR #22 (sans l'en-tête `[A2-TEAM]`)

1. Les sorties notées ci-dessus, expurgées, et la version Python et l'architecture de la VM.
2. Les phrases d'attestation que vous jugez vraies (modèles dans `team/OWNER_SESSION_SHEET_Q24_2026-10-08.md`) : provenance de `1910994`, mécanisme d'incident, dispositions A1 §5.
3. Votre choix pour le support de sortie : option 1 (tmpfs volatil accepté, écart consigné) ou option 2 (support persistant, nouvel acte).

Ensuite l'équipe lance la revue Astra limitée à ces écarts, puis rédige l'acte d'activation. Aucune action sur la VM n'est faite par l'équipe.
