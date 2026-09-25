# Prompt 1b — Session Blue : revérifier puis adopter la recherche à deux vitesses

> À coller dans une session Claude Code de gouvernance (Blue), à la racine du dépôt Quant.
> Une seule session courte. Un seul commit. Aucun nouveau document.

---

Tu es **Blue**, gouverneur de Quant. Une première vérification a refusé la proposition de recherche à deux vitesses sur deux points. La correction minimale est au commit `ae4f77c` de la branche `claude/new-session-kfwf1b`. Ta tâche est unique : **revérifier et, si tout est bon, adopter**.

## Budget (rempli par le propriétaire avant de coller)

```text
MAX_ITERATIONS      = 10
MAX_DECLARED_TRIALS = 200
MAX_PARALLEL_AGENTS = 5
FAST_RAIL_BRANCH    = fast/rail-01
```

## Lire, et seulement ceci
1. `QUANT_NORTH_STAR.md` et `CLAUDE.md` (section « Integrity invariants »).
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`.
3. `git fetch origin claude/new-session-kfwf1b`, puis, depuis `origin/claude/new-session-kfwf1b` : `governance/TWO_SPEED_RESEARCH_PROPOSAL.md` et `governance/FAST_RAIL_BUILDER_PROMPT.md`.
4. `git show ae4f77c` : le diff de la correction.

## Vérifier (oui ou non, avec une ligne de justification chacune)
1. Aucun fichier existant n'est modifié par rapport à `bd061dc`, en dehors des 3 nouveaux documents de proposition et de `prompts/` : North Star, `REAL_CAPITAL_AUTHORIZED = FALSE`, V4, P0, première verticale, Gate B (`git diff --stat bd061dc origin/claude/new-session-kfwf1b`).
2. Le périmètre du rail sûr (§2 de la proposition et §1 du prompt builder) nomme bien `src/quant/dataplane/sec/`, `deploy/`, `handoff/*.json`, P0, les Gates A, B et C, l'hôte cible, la première verticale et les SHA figés, et le rail rapide les exclut.
3. Les invariants du §3 de la proposition, désormais 10, couvrent chaque invariant d'intégrité de `CLAUDE.md` : la timeline causale unique, le Book idempotent, les manchons par stratégie, l'absence de donnée fabriquée et le risque sur le portefeuille final.
4. Le rail rapide ne peut jamais produire d'autorisation de capital. Il s'arrête à `FORWARD_PASS` avec un dossier de transfert, et c'est le propriétaire qui décide.

## Décider
- **Si tout est oui** :
  - dans `governance/TWO_SPEED_RESEARCH_PROPOSAL.md`, passe le statut de `PROPOSÉE` à `ACCEPTÉE — <date>` et coche les deux premières cases du §9, ainsi que la case du budget ;
  - ajoute à `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` une section `## 9. Rail C — recherche rapide (paper/shadow)` de 15 lignes maximum, qui contient :
    - la branche `FAST_RAIL_BRANCH` et son fichier d'état `FAST_RAIL_STATE.md` ;
    - le budget ci-dessus ;
    - la règle « aucune autorité de capital ; transfert au rail sûr sur `FORWARD_PASS`, décision du propriétaire » ;
    - le périmètre interdit (une ligne, avec un renvoi au §2 de la proposition) ;
    - la règle anti-bureaucratie : un document par décision réelle ; un candidat remplacé par sa version finale part dans `archive/` ;
    - la mention `REAL_CAPITAL_AUTHORIZED = FALSE` (inchangé) ;
  - ajoute à `CLAUDE_CURRENT_MISSION.md` une ligne sous « Current Blue workstreams » qui route vers le rail C : sa branche, `FAST_RAIL_STATE.md` et `governance/FAST_RAIL_BUILDER_PROMPT.md`.
- **Si un point est encore non** : ne corrige rien. Dis au propriétaire, en 5 lignes maximum, quel point échoue et quelle correction exacte est nécessaire, puis arrête-toi. Il n'y a pas de second tour de correction.

Le rangement (`CLEANUP_MANIFEST_PROPOSED.md`) est **hors périmètre** de cette session. Il ne s'exécute pas ici.

## Git
- Pars de `origin/claude/new-session-kfwf1b` sur une branche `blue/two-speed-adoption-<date>` (ou celle que la session impose). Un seul commit, puis un push.
- Ne fusionne pas, ne force-push rien et ne touche à aucune branche `builder/*`, `astra/*` ni à la branche par défaut. Le propriétaire fusionne.

## Rendu
Au plus 10 lignes : la décision, les quatre vérifications et le SHA du commit.
