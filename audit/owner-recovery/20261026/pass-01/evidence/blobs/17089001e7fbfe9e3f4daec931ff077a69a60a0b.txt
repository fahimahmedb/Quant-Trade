# Prompt 1 — Session Blue : adopter la recherche à deux vitesses

> À coller dans une session Claude Code de gouvernance (Blue), à la racine du dépôt Quant.
> Durée visée : une seule session courte. Ne produit **qu'un seul** document.

---

Tu es **Blue**, gouverneur de Quant. Ta tâche est unique et bornée : **statuer sur la proposition de recherche à deux vitesses** et, si elle est acceptée, l'inscrire dans l'autorité courante. Pas de nouvelle chaîne de documents : pas de prestage, de réception, de candidat ni de revue de revue.

## Lire, et seulement ceci
1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. Depuis la branche `origin/claude/two-speed-cleanup-6vr22g` : `governance/TWO_SPEED_RESEARCH_PROPOSAL.md`, `governance/FAST_RAIL_BUILDER_PROMPT.md` et `governance/CLEANUP_MANIFEST_PROPOSED.md`.

## Vérifier (réponse oui ou non, avec une ligne de justification chacune)
- La proposition ne change ni la North Star, ni `REAL_CAPITAL_AUTHORIZED = FALSE`, ni aucun artefact figé : V4, P0, première verticale, Gate B.
- Le périmètre du rail rapide exclut bien tout le rail sûr : `src/quant/dataplane/sec/`, `deploy/`, `handoff/*.json`, P0, Gate A/B/C, hôte cible, première verticale.
- Les 8 invariants du §3 couvrent les invariants d'intégrité de `CLAUDE.md` : timeline causale unique, Book idempotent, manchons par stratégie, aucune donnée fabriquée, risque sur le portefeuille final.
- Le rail rapide ne peut jamais produire d'autorisation de capital. Il ne produit qu'un dossier de transfert vers le rail sûr.

## Décider
- **Si tout est oui** : ajoute à `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` une section courte (15 lignes maximum) `Rail C — recherche rapide (paper/shadow)`. Elle doit contenir :
  - la branche du rail rapide et son fichier d'état (`FAST_RAIL_STATE.md`) ;
  - le budget fixé par le propriétaire ;
  - la règle « aucune autorité de capital ; transfert au rail sûr sur `FORWARD_PASS` » ;
  - la règle anti-bureaucratie : un document par décision réelle ; un candidat remplacé par sa version finale part dans `archive/`.

  Ajoute aussi une ligne à `CLAUDE_CURRENT_MISSION.md` qui route vers le rail C.
- **Si un point est non** : écris la correction minimale directement dans la proposition, sur sa branche, et arrête-toi.

## Git
- Travaille sur une branche `blue/two-speed-adoption-<date>` (ou celle que la session impose), un seul commit.
- Ne fusionne pas et ne force-push rien. Le propriétaire fusionne.

## Rendu
Au plus 10 lignes : la décision, les vérifications et le SHA du commit.
