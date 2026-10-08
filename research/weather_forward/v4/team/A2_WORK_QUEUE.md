# File de travail A2 (mise à jour 2026-10-08)

Statuts : READY, BLOCKED (dépend d'une tâche), OWNER_GATED (décision ou action d'Owner), IN_PROGRESS, DONE.
Niveaux : T = réflexion (Opus), B = construction (Sonnet), M = mécanique (Haiku ou script).

| Id | Tâche | Autorité | Dépend de | Agent | Niv. | Statut |
|---|---|---|---|---|---|---|
| Q1 | Consigner les gels L2-C (input) et L2-D (output D2) sur les blobs `f85205f3` et `7651de7e` | Acte Owner `9d0698b` §5, délégation | rien | builder (Codex n'a pas pu publier) | M | DONE : `245f193` |
| Q2 | L2-E : identités input et output par les deux voies, comparaison | Décision lot 2 `276fd99` | Q1 | builder | B | DONE : identités input `5c55b855…`, output `b8157e4e…`, `1b6416b` |
| Q3 | L2-F : policy D2 (12 champs), gel, identité par les deux voies | idem | Q2 | builder | B | DONE : gel `79f6e92`, identité `2f761da5…`, `51f49c8` |
| Q4 | L2-G : projet de configuration finale et d'autorité d'exécution E | idem, annexe A | Q3 | builder (sous-agent Opus) | T | DONE : `a56467a`, blob `53af1fb3` |
| Q5 | L2-G : ratifier la configuration finale, émettre E (six points à trancher dans le projet `a56467a`) | Owner | Q4 | Owner | - | DONE : E ratifiée, commit `6e0320f` |
| Q6 | L2-H : candidat trusted root (`trusted_root.py` seul) | idem | Q5 | builder | B | DONE : `73280c3`, blob `9704a844` |
| Q7 | L2-I : vérifications du candidat (runner sur les 279 anciens tests : 3 écarts attendus ; nouveaux tests ; refus sur root réelle ; positifs sur objets synthétiques) | idem §4 L2-I | Q6 | builder | B | DONE : rapport sur `builder/weather-v4-a2-lot2-l2i-verification-2026-10-08` @ `5b381d34ccdfc938727ccecaf1d09447dcd29ab5` ; `LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED` (279 : 276 réussis + les 3 écarts prévus), 27 nouveaux tests réussis, aucun PERMIT sur le tuple réel, candidat non modifié, aucun défaut candidat |
| Q8 | L2-J : dossier de preuves | idem | Q7 | builder | B | DONE : branche `builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08`, commit `5358c7ac582b46804be0008cffc78a043751d910`, blob `51c6bf2b3ae324892777439a862e3d0345bcaaf8` ; statut `LOT2_PREPARATION_COMPLETE_WITH_LOCAL_BLOCKERS` (L2-A non faite) |
| Q9 | Lot 3 : revue technique par une Astra neuve (mission écrite, références exactes) | Plan Owner | Q8 | orchestrateur lance | T | IN_PROGRESS : Astra neuve lancée 2026-10-08T00:58Z (session `session_01Et1fGaTRCU1anLuFt32Npd`, Opus, mission `a1879fc` seule) ; contrôle armé 01:24Z |
| Q10 | Fermer le domaine de `structural_linkage_status` et le contenu sous garde (Astra §I.1-2), pour une future route D1 | Owner | rien | orchestrateur prépare, Owner décide | T | OWNER_GATED |
| Q11 | L2-A : qualification de la VM | Décision lot 2 | terminal d'Owner | Owner | - | OWNER_GATED |
| Q12 | Lot 4 : activation et opération | Owner | Q9, Q11 | Owner | - | OWNER_GATED |
| Q13 | Q10 prépare : proposer le domaine fermé de `structural_linkage_status` et le contenu sous garde (projet seul, route D1 future, aucune décision) | classe A | rien | orchestrateur (Codex) | T | DONE : rédigé par Codex, publié par Claude Code, SHA-256 `739e84e7…b670` vérifié, blob `d549cb3829e46a471e6d51a40fdfe3c3a450bf42`, fichier `team/Q13_STRUCTURAL_LINKAGE_DOMAIN_DRAFT_2026-10-08.md` (projet sans effet) |
| Q14 | Grille de triage adverse du rapport Astra lot 3 (à appliquer dès sa publication : constats, remèdes, écarts) | classe A | rien | orchestrateur (Codex) | T | DONE : rédigé par Codex, publié par Claude Code, SHA-256 `9c75ea24…f757` vérifié, blob `8c0b1f54e31dab6c07bee2fa1d246f7b042d0ce9`, fichier `team/Q14_ASTRA_LOT3_TRIAGE_GRID_2026-10-08.md` |
