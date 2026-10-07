# File de travail A2 (mise à jour 2026-10-08)

Statuts : READY, BLOCKED (dépend d'une tâche), OWNER_GATED (décision ou action d'Owner), IN_PROGRESS, DONE.
Niveaux : T = réflexion (Opus), B = construction (Sonnet), M = mécanique (Haiku ou script).

| Id | Tâche | Autorité | Dépend de | Agent | Niv. | Statut |
|---|---|---|---|---|---|---|
| Q1 | Consigner les gels L2-C (input) et L2-D (output D2) sur les blobs `f85205f3` et `7651de7e` | Acte Owner `9d0698b` §5, délégation | rien | builder (Codex n'a pas pu publier) | M | DONE : `245f193` |
| Q2 | L2-E : identités input et output par les deux voies, comparaison | Décision lot 2 `276fd99` | Q1 | builder | B | DONE : identités input `5c55b855…`, output `b8157e4e…`, `1b6416b` |
| Q3 | L2-F : policy D2 (12 champs), gel, identité par les deux voies | idem | Q2 | builder | B | DONE : gel `79f6e92`, identité `2f761da5…`, `51f49c8` |
| Q4 | L2-G : projet de configuration finale et d'autorité d'exécution E | idem, annexe A | Q3 | builder (sous-agent Opus) | T | DONE : `a56467a`, blob `53af1fb3` |
| Q5 | L2-G : ratifier la configuration finale, émettre E (six points à trancher dans le projet `a56467a`) | Owner | Q4 | Owner | - | OWNER_GATED : alerte envoyée |
| Q6 | L2-H : candidat trusted root (`trusted_root.py` seul) | idem | Q5 | builder | B | BLOCKED |
| Q7 | L2-I : vérifications du candidat | idem | Q6 | builder | B | BLOCKED |
| Q8 | L2-J : dossier de preuves | idem | Q7 | builder | B | BLOCKED |
| Q9 | Lot 3 : revue technique par une Astra neuve (mission écrite, références exactes) | Plan Owner | Q8 | orchestrateur lance | T | BLOCKED |
| Q10 | Fermer le domaine de `structural_linkage_status` et le contenu sous garde (Astra §I.1-2), pour une future route D1 | Owner | rien | orchestrateur prépare, Owner décide | T | OWNER_GATED |
| Q11 | L2-A : qualification de la VM | Décision lot 2 | terminal d'Owner | Owner | - | OWNER_GATED |
| Q12 | Lot 4 : activation et opération | Owner | Q9, Q11 | Owner | - | OWNER_GATED |
