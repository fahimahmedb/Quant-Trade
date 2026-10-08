# Matrice des conditions de prise d'effet d'E (B.5), état au 2026-10-08

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
E = 6e0320f15d48a924cef9507af5641e47de9fe938 (D2, READ_INPUT seul, conditionnelle, sans effet)
E_EFFECTIVE = FALSE
```

Lecture : E §B.5 exige toutes les conditions (a) à (k). Statuts : `ÉQUIPE` = l'équipe peut fermer ; `OWNER-VM` = demande le terminal d'Owner ; `OWNER-ATTEST` = attestation de fait d'Owner (non délégable) ; `ASTRA` = revue indépendante ; `FERMÉ` = preuve suffisante publiée. Aucune condition n'est aujourd'hui `FERMÉ`.

| Cond. | Exigence (E §B.5) | Preuve disponible | Manque | Qui ferme | Statut |
|---|---|---|---|---|---|
| (a) | PASS Astra lot 3 sur les snapshots exacts (candidat, outillage, contexte, canal de contrôle, contenu gardé) | rapport `f236ab2b…` : `BLOCKED_INCOMPLETE_EVIDENCE`, aucun défaut du candidat ; contexte et épingles (Q23, `44bee3b`) | revue limitée au delta après (b) et (e) | ASTRA (Q25) | PARTIEL |
| (b) | contrôles L2-A qualifiés | kit Q15 (`2b3c42fc`), commandes `42d953c1…` | exécution sur la VM, version Python et architecture notées | OWNER-VM (Q24) | OUVERT |
| (c) | rétention et suppression vérifiées avant toute garde | règle de rétention du manifeste de sortie (30 jours) ; tmpfs de 1 MiB | procédure de suppression écrite (Q27, `7ba98795…`, jamais exécutée sur la VM) ; **la rétention de 30 jours n'est pas démontrable sur le tmpfs volatil de `/srv/a2out`** | OWNER-VM exécute `verify_retention_deletion.sh` ; **OWNER décide** : support volatil accepté (écart consigné) ou support persistant (nouvel acte) | OUVERT |
| (d) | mécanisme d'incident disponible | vocabulaire fermé de 7 classes et référence `a2-doc-v1-inc-NNN` attribuée par Owner (E B.4) | attestation qu'Owner attribue les références et reçoit le signal (code de sortie, mesures systemd) | OWNER-ATTEST (Q24) | OUVERT |
| (e) | origine des autorisations et correspondance de session vérifiées | constat Astra J-5 : `1910994`, gels et E enregistrés par des sessions d'agents d'après des messages d'Owner | reconnaissance écrite d'Owner de la provenance et de l'attribution des actes | OWNER-ATTEST (Q24) | OUVERT |
| (f) | code chargé constaté sur l'hôte contre les blobs approuvés (13 objets) | épingles `final_pins_d2_v1.{json,tsv}` ; scripts de déploiement et d'attestation Q22 (`b8725677`), testés sur répertoires temporaires | exécution sur la VM par Owner | OWNER-VM (Q24) | OUVERT |
| (g) | dispositions « A1 §5 » attestées, sans génération de fixture | dossier A1 §5 = matrice de rôles et de capacités (aucun accès efficacité, lecteurs limités aux ensembles des §3 et §4, aucune fixture) | **ambiguïté de renvoi** : « A1 §5 » est lu ici comme cette matrice ; attestation d'Owner qu'aucun accès ou fixture hors matrice n'existe ; lecture à faire confirmer par Astra | OWNER-ATTEST + ASTRA (Q24, Q25) | OUVERT |
| (h) | canal de diagnostic limité au code accepté | script : stdout et stderr non utilisés (SY, Astra §G.3), codes {0,30,40,50} | mesure réelle (stdout et stderr à null sous l'unité) | OWNER-VM (L2-A) | PARTIEL |
| (i) | décision d'activation nommant commit candidat, blobs, contexte, profil, chemins | candidat `73280c3e…`, épingles, contexte pré-effet ; règle : le contexte d'activation ne diffère que par `read_authorization.state` | rédaction et consignation de l'acte (autorité déléguée, élément 6, six conditions) | ÉQUIPE (Codex rédige, Builder contrôle) — après (a) à (h) | BLOQUÉ |
| (j) | plafonds O §8.3 (60 s, 5 s CPU, 128 Mio sans swap, 1 tâche, 1 Mio d'écriture, 64 Kio de résultat) et visibilité | profil `a2_unit_profile.sh` (blob `ec58a081…`) | qualification réelle des limites (L2-A) | OWNER-VM (L2-A) | OUVERT |
| (k) | une seule opération, sans retry | le script refuse une cible existante (code 30) ; aucun retry dans le script | engagement d'exécution unique dans la décision d'activation | ÉQUIPE (dans (i)) | PARTIEL |

**Lecture d'ensemble.** Ce que l'équipe peut encore faire seule : l'acte (i) une fois les autres fermées, et la revue (a) après les preuves d'Owner. Tout le reste demande **une seule session d'Owner** (terminal sur la VM, plus trois attestations : (d), (e), (g)). Aucune condition ne se ferme par présomption.

```text
NEXT_SAFE_ACTION = session Owner unique (Q24) avec le choix de support de (c) ; E reste sans effet
```
