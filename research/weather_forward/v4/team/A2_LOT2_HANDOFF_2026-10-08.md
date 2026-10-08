# Fiche de reprise — Weather V4 A2, lot 2 (2026-10-08)

> **Directive permanente d'Owner :** Claude Code et Codex gèrent le projet **à parts égales (50/50)** ; Claude Code n'a aucun rang sur Codex, il propose et Codex peut refuser. Voir l'en-tête de `A2_WORK_QUEUE.md` (commentaire `6055519521`). Cette ligne est la plus oubliée : la relire à chaque reprise.

Lire cette fiche, puis seulement les passages cités. Chemins relatifs à `research/weather_forward/v4/`.

## État

| Élément | Statut | Référence |
|---|---|---|
| Constat Astra lot 1 | Input `CLEAR_SUPPORTED` ; output et cumul `UNRESOLVED` ; quarantaine maintenue ; ledger `NONE` | `audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_2026-10-07.md` @ `52e5ff2` |
| Décision lot 2 | Ratifiée ; route D2 choisie, D1 fermée | `owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md` @ `276fd99` ; ratification @ `ccd4747` ; dispositions D2 @ `9d0698b` |
| Outillage L2-B | Livré ; 343 tests synthétiques verts (revérifiés en Python 3.13) | `builder/weather-v4-a2-lot2-tooling-2026-10-07` @ `1910994` |
| Transcriptions L2-C / L2-D | Publiées et vérifiées ; **gels Owner non consignés** | même branche @ `492bd05` ; input blob `f85205f3`, output blob `7651de7e` ; preuve `a2_operation/evidence/L2_C_L2_D_D2_TRANSCRIPTION_COMPARISON_2026-10-07.md` |
| Qualification VM (L2-A) | Reportée, non faite | commandes : `a2_operation/qualification/COMMANDS_VM_QUALIFICATION_2026-10-07.md` @ `1910994` |
| Charte d'équipe | Projet, à ratifier | `team/A2_TEAM_CHARTER_DRAFT_2026-10-08.md`, PR #22 |

## Mise à jour 2026-10-08 (charte ratifiée, `ca65c1b`)

Q1 à Q3 terminées. Gels input/output/policy consignés (`245f193`, `79f6e92`) ; identités par deux voies concordantes : input `sha256:5c55b855…bbd00`, output `sha256:b8157e4e…90976`, policy `sha256:2f761da5…3de60` (preuves `a2_operation/evidence/` @ `51f49c8`). Q4 (projet E) en cours. **Limite connue : une tâche Codex ne publie rien sur GitHub sans « Create PR » ; ne pas lui confier d'écriture de fichiers.**

## Prochaines actions (état antérieur)

1. **Owner (ou son délégué)** : consigner les gels L2-C et L2-D sur les blobs `f85205f3` et `7651de7e`.
2. **Builder, après les gels** : L2-E, identités input et output par les deux voies (`a2_operation/identity/`), puis L2-F : policy D2 avec les 10 valeurs non dérivées de D §14.2C (dossier `blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md` @ `49d3d00`).
3. **Owner** : L2-G, configuration finale et autorité d'exécution E. Puis Builder : L2-H (root candidate, `a2_harness/trusted_root.py` seul), L2-I (vérifications).

## Décisions Owner en attente

- Domaine fermé de `structural_linkage_status` et contenu exact conservé sous garde (Astra §I, points 1 et 2) : condition pour une future route D1.
- Format des identifiants d'enregistrement et d'incident, vocabulaire d'incident (Astra §I, point 7) : avant toute exécution.
- Qualification VM : quand Owner a un terminal.

## Règles à retenir

- Sources du harnais = H `78d537de` ; construction C `37e3b25f`.
- Aucun digest réel avant gel ratifié ; aucun SHA inventé ; un agent n'écrit que sur ses branches.
- Le commit `1910994` vient d'une autre session que le Builder désigné ; vérifié, mais à signaler au lot 3.

## Coût

Session Builder précédente (`session_016Mii9xHWUhsB3DEuB88zpz`) : environ 37 $. Session Astra lot 1 : environ 21 $. Budget recommandé par lot : 15 $.

## Quotas (mise à jour 2026-10-08)

| Agent | Statut | Remise à zéro | Modèle | Coût du lot |
|---|---|---|---|---|
| Claude Code (cette session) | `allowed`, contexte 64 % | 2026-10-08T04:40Z (fenêtre de 5 h) | Sonnet, sous-agents Haiku/Opus | environ 57 $ au total |
| Codex | `NON_VISIBLE` (réponse de Codex sur la PR #22 : il ne voit pas son quota, ses autres modèles ni comment en choisir un) ; à lire par Owner dans la page d'usage de Codex | inconnue | GPT-5.6 Sol (déclaré par Codex) | inconnu |

## Mise à jour (E ratifiée, candidat construit)

- Owner a ratifié la configuration finale et E (D2) : fichier `owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_D2_2026-10-08.md`, branche `owner/weather-v4-a2-execution-authority-e-d2-2026-10-08`, **commit E = `6e0320f15d48a924cef9507af5641e47de9fe938`**. E est conditionnelle et sans effet.
- Q6 faite : candidat root `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08` @ `73280c3e9d8604b2f2d8e6d2d174aa940389a760` (un seul fichier, `trusted_root.py`, blob `9704a844…`), base `276fd99`. Non chargé, non vérifié.
- **Prochaine action : Q7 (L2-I)**, à confier à une session Sonnet neuve. Le chargement du candidat n'est autorisé que par L2-I.
- **Amendement délégation et co-gérance en vigueur :** Owner l'a ratifié au commit `b38e94e93d7e520281eb7914f3671dd8bcdadac0` par son propre commentaire sur la PR #22 (id `6049291116`, sans l'en-tête `[A2-TEAM] DE:`, forme prévue au §7 de la charte). Aucun fichier de consignation Owner séparé n'existe ; ce commentaire fait foi. Les actes de classe C restent réservés à Owner.
- Le commit `1910994` de l'outillage vient d'une autre session que le Builder désigné : à signaler à Astra au lot 3.
