# Q27 — Vérification de la suppression et de la persistance du répertoire de sortie (E B.5(c)), 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
EXECUTED_ON_VM = NO ; TESTED_ON = SYNTHETIC_TEMP_DIRECTORIES_ONLY
E_EFFECTIVE = FALSE
```

**Constat qui change la suite.** La règle de rétention du manifeste de sortie gelé (`7651de7e…`) dit : 30 jours calendaires après la clôture, gardien PROJECT_OWNER, « retention and deletion capabilities verified before custody ». Or le répertoire de résultat `/srv/a2out` est un **tmpfs de 1 MiB non inscrit dans `/etc/fstab`** (`setup_host.sh`) : il est **perdu au redémarrage**. Une rétention de 30 jours n'y est donc **pas garantie** et ne peut pas être démontrée par une vérification. La suppression, elle, est vérifiable.

| Fichier (`a2_operation/`) | Rôle |
|---|---|
| `qualification/verify_retention_deletion.sh` | root ou propriétaire du dossier ; refuse un répertoire non vide (aucun fichier existant n'est lu, listé ni touché) ; crée une sonde synthétique, la supprime, vérifie l'absence ; imprime `DELETION_CAPABILITY=VERIFIED`, le type de système de fichiers, `PERSISTENT_ACROSS_REBOOT=NO` pour tmpfs/ramfs (sinon `UNVERIFIED`), `RETENTION_30D_DEMONSTRATED=NO` toujours |
| `verification/test_retention_script.py` | 4 tests synthétiques ; contrôle négatif : la suppression de la garde « non vide » fait échouer le test correspondant |

**Usage (Owner, après le déploiement Q22, avec `/srv/a2out` vide) :** `sudo bash <verified-script> /srv/a2out`. Attendu : `DELETION_CAPABILITY=VERIFIED`, `OUTPUT_DIR_FSTYPE=tmpfs`, `PERSISTENT_ACROSS_REBOOT=NO`, `RETENTION_30D_DEMONSTRATED=NO`. Le script n'a jamais tourné sur une VM.

**Décision d'Owner nécessaire, non prise ici (condition E B.5(c))** — une des deux options, nommée explicitement :
1. **Accepter le support volatil** : la sortie D2 est une preuve structurelle sans valeur d'efficacité ; sa perte au redémarrage est consignée comme écart à la règle de rétention de 30 jours (le manifeste gelé ne change pas) ;
2. **Changer de support** (dossier persistant en `0700`) : cela modifie la configuration de l'unité et du manifeste de la sortie (périmètre « écriture bornée sous `/srv/a2out` »), donc un nouvel acte et une nouvelle revue d'Astra.

Tant qu'aucune option n'est choisie, (c) reste `OUVERT`.

```text
NEXT_SAFE_ACTION = Owner choisit l'option 1 ou 2 (B.5(c)) pendant la session Q24 ; contre-lecture de Codex du script (Q16 étendue)
```
