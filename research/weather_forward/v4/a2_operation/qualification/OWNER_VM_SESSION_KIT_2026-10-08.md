# Kit de session de terminal Owner — qualification L2-A (Q15), 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
ACTION_ON_VM_BY_TEAM = NONE ; aucune commande ci-dessous n'a été exécutée par Builder
NEW_COMMANDS_INVENTED = NONE (toutes renvoient à COMMANDS_VM_QUALIFICATION_2026-10-07.md)
```

Résumé d'une page des commandes **déjà publiées** : `a2_operation/qualification/COMMANDS_VM_QUALIFICATION_2026-10-07.md`, blob `42d953c19cb09dc3390b19f44f69adda0c2139ef` (branche `builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08` @ `5358c7ac582b46804be0008cffc78a043751d910`). Ce kit n'ajoute aucune commande et ne remplace pas ce fichier : en cas d'écart, ce fichier fait foi.

## 0. Avant de commencer

- Un terminal sur la VM, avec l'accès SSH et sudo déjà existants (aucune nouvelle clé, infrastructure ou compte).
- Un poste avec un checkout Git de Quant-Trade, pour préparer l'archive (§1 des commandes). Dire comment obtenir ce terminal (poste local, console du fournisseur) est une décision d'accès d'Owner ; ce kit n'en choisit aucune.
- Valeurs à fournir : le commit complet de la remise (`<A2_COMMIT>`, commit qui contient ces fichiers : à désigner explicitement par Owner ou par le commentaire de remise sur la PR #22) et l'alias SSH.

## 1. Quatre étapes, dans l'ordre (arrêt immédiat à la première commande qui échoue)

| # | Où | Contenu | Résultat attendu | Si autre chose |
|---|---|---|---|---|
| 1 | poste Owner | commandes §1 : fetch du commit, extraction de `file_pins.tsv`, contrôle du blob `e718b284982a0f8c5c119be6a44cd1b803651f9b`, archive de 11 fichiers, envoi par `scp` | `test` silencieux ; archive envoyée | **Stop** ; ne pas « réparer » |
| 2 | terminal VM | commandes §2 : répertoire de réception neuf, contrôle des 11 blobs un à un, puis `host_facts.sh` | constat local lu par Owner (Ubuntu, cgroup v2, Python ≥ 3.10, systemd, sudo) | répertoire déjà présent, blob différent ou version inattendue : **stop** et noter ; pas d'installation ni de mise à niveau |
| 3 | terminal VM | commandes §3 : `setup_host.sh` puis `deploy_files.sh` | compte et tmpfs de 1 MiB créés ; copie vérifiée avant la première écriture | compte, groupe ou chemin déjà présent, `/opt/a2` non vide : **stop** |
| 4 | terminal VM | commande §4 : `run_qualification.sh e718b284982a0f8c5c119be6a44cd1b803651f9b` | code retour `0` (critère composé) | code `2` : noter `NOT_VERIFIED` ou `DETECTED_AFTER_BREACH` par limite ; ne pas modifier le profil ni relancer pour obtenir un succès |

## 2. À rapporter ensuite (§5 des commandes)

Les transcripts de qualification et le constat local, après retrait de secrets, adresses IP, nom d'hôte public et autres identifiants d'hôte. Aucun payload, aucune preuve d'opération A2. Indiquer aussi : version Python et architecture observées sur la VM (aujourd'hui **NON_OBSERVÉES** ; Builder a 3.12.14 puis 3.13.16 en x86_64), et chaque mutation réellement faite.

## 3. Ce que ce kit ne couvre pas

- **Condition E §5(f)** (code chargé constaté sur l'hôte contre les blobs approuvés : 4 fichiers du harnais dont le `trusted_root.py` candidat, 7 sources d'opération, contexte, profil d'unité) : **aucune commande n'existe aujourd'hui**. Le paquet de qualification ne déploie pas H. Les écrire est un nouveau travail Builder, à faire après un PASS d'Astra au lot 3 et à faire revoir ; le marquer comme tel.
- Conditions E §5 (c) (rétention et suppression vérifiées avant toute garde) : non couvertes par ces sondes telles que décrites (« la perte du tmpfs au redémarrage ne démontre pas une purge contrôlée »).
- Aucune activation, aucune évaluation permissive, aucune exécution de `a2_doc_integration_operation.py`.

```text
Q11_O_REQUIRES_OWNER_TERMINAL = TRUE
E_EFFECTIVE = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
```
