# Fiche de reprise — Weather V4 A2, lot 2 (2026-10-08)

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

## Prochaines actions

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
