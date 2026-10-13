# Fiche de la session Owner unique (Q24) — tout ce qui reste pour qu'E puisse prendre effet

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
CONTENT = liste et modèles ; AUCUNE attestation ni décision n'est exprimée ici
E_EFFECTIVE = FALSE
```

Rien ci-dessous n'est exécuté par l'équipe. Les modèles de phrases sont à poster **par Owner lui-même** en commentaire de la PR #22 (sans l'en-tête `[A2-TEAM]`), s'il les juge vrais. Matrice de référence : `team/B5_CONDITIONS_MATRIX_2026-10-08.md`.

## Partie 1 — Terminal sur la VM (une seule session)

| Ordre | Quoi | Où trouver | Résultat à noter |
|---|---|---|---|
| 1 | Qualification L2-A (quatre étapes) | `a2_operation/qualification/OWNER_VM_SESSION_KIT_2026-10-08.md` (branche `builder/weather-v4-a2-lot2-vm-kit-2026-10-08`) | code retour `0` de `run_qualification.sh` ; version Python et architecture de la VM |
| 2 | Déploiement des 13 objets approuvés, puis attestation du code chargé (E §5(f)) | `a2_operation/evidence/Q22_HOST_ATTESTATION_2026-10-08.md` (branche `builder/weather-v4-a2-lot2-q22-host-attestation-2026-10-08`) | `LOADED_CODE_MATCHES_APPROVED=13/13`, `UNEXPECTED_FILES=0` |
| 3 | Contrôle de suppression du répertoire de sortie (E §5(c)) | `a2_operation/evidence/Q27_RETENTION_DELETION_2026-10-08.md` (branche `builder/weather-v4-a2-lot2-q27-retention-2026-10-08`) | `DELETION_CAPABILITY=VERIFIED`, type de système de fichiers, `PERSISTENT_ACROSS_REBOOT=NO` attendu pour tmpfs |

Retirer secrets, adresses IP et nom d'hôte avant de publier quoi que ce soit.

## Partie 2 — Quatre phrases d'Owner (modèles, à reformuler ou refuser librement)

1. **Provenance (E §5(e), Astra J-5).** « Je reconnais la provenance du commit 1910994 (publié par une autre session que le Builder désigné), et que les gels, l'autorité E et leurs consignations ont été enregistrés par des sessions d'agents sur la base de mes messages. »
2. **Incident (E §5(d)).** « J'attribuerai les références d'incident a2-doc-v1-inc-NNN, avec une seule classe et sans contenu, et je suis le destinataire du signal (code de sortie, mesures systemd). »
3. **Dispositions A1 §5 (E §5(g)), lecture proposée : matrice de rôles et de capacités.** « J'atteste qu'aucun accès à du contenu porteur d'efficacité ni aucune fixture n'existe ou n'a été générée en dehors de la matrice de rôles du dossier A1 §5. » (Astra doit confirmer que c'est bien ce que vise « A1 §5 ».)
4. **Support de sortie (E §5(c)).** Option 1 : « J'accepte que la sortie D2 reste sur le tmpfs de /srv/a2out, et que sa perte au redémarrage soit un écart consigné à la règle de rétention de 30 jours. » Option 2 : « Je veux un support persistant pour la sortie D2 » (déclenche un nouvel acte et une nouvelle revue).

## Après la session

L'équipe fait alors la revue Astra limitée au delta (Q25), puis rédige et ratifie par délégation l'acte d'activation (E §5(i), élément 6 de l'amendement d'autonomie, six conditions). Aucune action sur la VM n'est faite par l'équipe.
