# Prompt 3 — Session ménage : archiver les documents remplacés

> À coller dans une session Claude Code, à la racine du dépôt Quant.
> **Autorisation du propriétaire incluse dans ce prompt** : déplacer, sans jamais supprimer, les documents listés comme SUPERSEDED ou HISTORICAL par le manifeste.

---

Tu fais le ménage documentaire de Quant. Tu ne changes **aucun** code, **aucune** donnée et **aucun** contenu de décision : tu déplaces des fichiers et tu répares les liens.

## Source de vérité
`governance/CLEANUP_MANIFEST_PROPOSED.md`, sur la branche `origin/claude/two-speed-cleanup-6vr22g`. Seules les lignes des sections **SUPERSEDED** et **HISTORICAL** sont concernées. Les autres fichiers ne bougent pas.

## Étapes
1. Crée une branche `chore/archive-superseded-docs-<date>` (ou celle que la session impose) depuis la branche par défaut `blue/master-v2-2026-09-20`. Récupère le manifeste depuis la branche ci-dessus.
2. **Garde-fou avant déplacement.** Pour chaque fichier listé, vérifie que son nom n'est cité par aucun fichier non markdown :
   ```bash
   git grep -l -F "<nom>" -- ':!*.md'
   ```
   S'il est cité par du code, un test, la CI, un script ou un JSON, **ne le déplace pas** et note-le dans le rapport.
3. Déplace chaque fichier retenu avec `git mv <chemin> archive/<chemin>`, sous le même nom et la même arborescence.
4. **Répare les liens.** Dans tous les fichiers restants, remplace les références de chemin `governance/<nom>` ou `handoff/<nom>` d'un fichier déplacé par `archive/governance/<nom>` ou `archive/handoff/<nom>`. Ne touche pas aux mentions du nom seul, qui restent trouvables par recherche.
5. Écris `archive/INDEX.md` : un tableau `fichier | classe | remplacé par | raison`, repris du manifeste. Transforme ensuite le manifeste en « EXÉCUTÉ », avec la date et le SHA.
6. **Incohérences du manifeste.** Corrige seulement celle-ci : unifier l'ordre de lecture de `README.md`, `AGENTS.md`, `CLAUDE.md` et `CLAUDE_CURRENT_MISSION.md` sur un seul point de reprise, le plus récent qui existe encore hors archive. Pour les autres (CODEX.md, RUNTIME*), ajoute une ligne « à décider » dans le rapport, sans agir.
7. **Vérification complète** (tout doit être vert) :
   ```bash
   PYTHONPATH=src python3 -m unittest discover -s tests -q
   python3 scripts/demo_quant_system.py
   python3 scripts/generate_schemas.py --check
   PYTHONPATH=src python3 scripts/status_artifacts.py --check
   ```
   Puis cherche les liens cassés : pour chaque chemin `governance/...` ou `handoff/...` cité dans un `.md`, le fichier doit exister.
8. Un commit, `chore(docs): archive N superseded governance/handoff docs`. Push, puis ouvre une PR vers la branche par défaut **seulement** si le propriétaire l'a demandé.

## Interdits
- Supprimer un fichier, modifier le contenu d'une décision, toucher `src/`, `tests/`, `deploy/`, `schemas/`, `data/`, `.github/`, `handoff/*.json` ou les SHA et digests figés.
- Supprimer des branches. Le propriétaire le fait lui-même depuis `governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`.

## Rendu
Au plus 10 lignes :
- le nombre de fichiers déplacés et de fichiers retenus par le garde-fou ;
- le nombre de liens réparés ;
- les tests ;
- le SHA ;
- les points « à décider ».
