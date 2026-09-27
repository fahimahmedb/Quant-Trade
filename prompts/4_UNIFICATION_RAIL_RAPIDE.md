# Unifier le rail rapide : deux sessions builder tournent en parallèle

Il y a deux builders du rail rapide :

| Session | Branche | Adoption Blue `bd19712` | Avancement |
|---|---|---|---|
| `session_01EJxGhb8q1qefVeK3XpAbMF` | `claude/new-session-0ydmkg` | **absente** : lancé depuis la proposition non corrigée | 16 essais consommés ; H-003, H-004 et H-005 en REJECT ; H-001 débloqué ; H-002 en cours |
| `session_017q7DK3yJNfnEEcGADxBjDj` | `claude/new-session-3ujgeu` | présente | 6 essais consommés ; H-006 en REJECT ; H-002 et H-004 en WIP |

Décision : **garder `0ydmkg`**, qui est le plus avancé, lui faire intégrer l'adoption et le registre de l'autre, puis **arrêter `3ujgeu`**.
Ordre : coller d'abord le prompt A dans `3ujgeu` et attendre son SHA final. Coller ensuite le prompt B dans `0ydmkg`.

---

## Prompt A — à coller dans la session `claude/new-session-3ujgeu` (arrêt)

```text
STOP_OWNER. Un autre builder (claude/new-session-0ydmkg) devient le seul rail rapide et reprend ton registre. Arrête-toi proprement :
1. N'exécute plus aucun essai et ne déclare plus rien.
2. Sauvegarde tout le travail en cours : commit + push sur ta branche et sur tes branches -wip-* (patch compris).
3. Écris en tête de FAST_RAIL_STATE.md : « ARRÊTÉ (STOP_OWNER) — unifié dans claude/new-session-0ydmkg ». Pour chaque hypothèse, indique le nombre exact d'essais consommés et la branche/le fichier qui contient son travail.
4. Supprime la routine « Fast rail hourly resume » (watchdog horaire).
5. Commit, push, puis réponds en une ligne : SHA final, essais consommés, branches WIP.
```

---

## Prompt B — à coller dans la session `claude/new-session-0ydmkg` (reprise unifiée)

```text
REPRISE — unification du rail rapide. Tu deviens le SEUL builder du rail rapide. Un second builder a tourné en parallèle sur claude/new-session-3ujgeu ; il est arrêté (STOP_OWNER). Ta branche n'a pas l'adoption Blue. Corrige ces deux points, puis reprends l'itération là où tu en étais.

0. Checkpoint d'abord : bash scripts/fast_rail_checkpoint.sh (ne perds pas le travail H-002 en cours).

1. Adoption Blue (proposition corrigée + prompt corrigé) :
   git fetch origin claude/new-session-kfwf1b claude/new-session-3ujgeu 'refs/heads/claude/new-session-3ujgeu-wip-*:refs/remotes/origin/claude/new-session-3ujgeu-wip-*'
   git merge --no-edit origin/claude/new-session-kfwf1b
   git merge-base --is-ancestor bd19712 HEAD || arrêt
   En cas de conflit sur governance/*.md ou prompts/*.md, garde la version de kfwf1b ; pour le reste, garde la tienne.
   Relis seulement le §2 (périmètre : Gate C incluse) et le §3 (désormais 10 invariants) de governance/TWO_SPEED_RESEARCH_PROPOSAL.md. Vérifie que tes lanes respectent les invariants 9 (manchons par stratégie) et 10 (RISK sur le portefeuille final réellement simulé). Tout écart est un constat HIGH à corriger dans cette itération.

2. Import du registre de 3ujgeu (git show origin/claude/new-session-3ujgeu:research/fast_rail/registry.jsonl), dans sa version FINALE après l'arrêt. Ton registre reste append-only : ne réécris aucune ligne existante. Pour chaque entrée de l'autre registre, ajoute un événement "imported" portant source_branch, source_id et le "at" d'origine :
   - même hypothèse que l'une des tiennes → pas de nouvel id : note sur ton id, et ajout de SES essais consommés à ton compte ;
   - hypothèse distincte → nouvel id (à partir de H-007), déclaration et verdict repris tels quels.
   Correspondances déjà relevées (à confirmer sur la version finale) :
   - 3ujgeu H-001 (Pinnacle vs PM/Kalshi) = ton H-001 : note seulement ;
   - 3ujgeu H-002 (funding HL vs dYdX avec hystérésis, 6 déclarés) = ton H-002. Si l'autre a consommé des essais (voir sa branche -wip-h002), ils s'ajoutent aux tiens sur ce jeu de données, et ton seuil required_t les inclut AVANT ton run ;
   - 3ujgeu H-004 (Kalshi météo, P&L maker au règlement, 2 déclarés) : expression distincte de ton H-004, sur le même jeu de données → nouvel id. Ses essais comptent dans le budget Kalshi météo ;
   - 3ujgeu H-006 (fade des listings HL, 6 essais, REJECT : t 1,82 < 2,64) = même mécanisme que ton H-005 → verdict importé. Le budget du jeu de données HL listings passe à 12 essais. Recalcule required_t avec 12 et note-le ; les deux verdicts restent REJECT.
   Mets à jour prior_trials dans lanes.py pour chaque jeu de données touché. N'exécute aucun essai importé sans le re-déclarer avec le seuil combiné.

3. Réécris FAST_RAIL_STATE.md :
   - branche unique ;
   - budget = essais consommés des DEUX builders / 200 ;
   - une ligne « unifié avec 3ujgeu le <date>, adoption bd19712 intégrée » ;
   - constats HIGH éventuels issus de l'étape 1.
   Ne crée aucun autre fichier de gouvernance.

4. Un commit : « fast-rail: unify with 3ujgeu registry + Blue adoption bd19712 », puis push. Lance la vérification complète (unittest, demo, generate_schemas --check). Ensuite, reprends l'itération en cours selon ton état (H-002, puis H-006 foot, puis collecteur H-001), dans les règles du prompt corrigé (au plus 2 agents par vague).

Réponse au propriétaire : 3 lignes (SHA, essais totaux, HIGH ouverts).
```
