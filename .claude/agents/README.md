# Quant-Trade Sub-Agents — Architecture de réutilisabilité

## Principes d'optimisation

Chaque agent `.md` dans ce répertoire suit une structure figée pour maximiser la réutilisabilité et minimiser les tokens/latence :

### Frontmatter (YAML)
```yaml
---
name: quant-XXXX
description: Une ligne claire du rôle (UTILISER PROACTIVEMENT quand...)
tools: [liste minimale réelle]
model: [fable|haiku|sonnet|opus] 
---
```

**Modèle par rôle** :
- **fable** : Prose, synthèse, aucun code → Rapide, peu coûteux
- **haiku** : Tâches mécaniques/téléchargement → Rapide
- **sonnet** : Implémentation code, design décisionnel → Standard production

### Instructions (corps)

1. **Première ligne** : toujours `Tu démarres à froid sur le repo Quant-Trade. Lis CLAUDE.md à la racine.`
   - Évite la re-exploration du repo
   - Centralise le contexte figé (A/B/C/D, protocoles, résultats)

2. **Univers figé déclaré explicitement** avant tout travail
   - Exemple : "5 variantes testées (univers figé) :" + liste
   - DSR doit compter n_trials = taille univers exact

3. **Pas de commit/push** — standard pour tous
   - L'orchestrateur intègre et pousse une fois

4. **Sections optionnelles** (adapter au rôle) :
   - Tâche / Fichiers / Protocole figé / Critère succès / Anti-data-snooping
   - Concis : max 200-300 lignes d'instructions

### Bénéfices

| Aspect | Gain |
|--------|------|
| Token efficiency | CLAUDE.md partagé ≫ instructions répétées |
| Context reuse | Chaque agent relance auto avec contexte figé |
| Model dispatch | Frontmatter model = pas de débat interface |
| Reusability | Agents découvrables, invocables par nom si intégré au runtime |
| Honest results | Anti-data-snooping déclaré a priori dans chaque agent |

## Agents actuels

- **quant-data-fetcher.md** (haiku) — Télécharger historiques
- **quant-meta-labeling.md** (sonnet) — Meta-labeling, benchmark vs BH
- **quant-defensive-overlay.md** (sonnet) — Étape D vol-targeting
- **quant-report-writer.md** (fable) — Synthèse French honnête
- **quant-integrated-pipeline.md** (sonnet) — Pipeline B+meta+overlay

## Prochains agents candidats

- **quant-overlay-optimize.md** → renommer existing run_etape_d_optimize
- **quant-meta-labeling-variants.md** → renommer existing run_meta_labeling_multi
- **quant-backtest-indices.md** (sonnet) — Tester sur Russell/S&P 500/DAX
- **quant-executive-summary.md** (fable) — Rapport C-suite commercial

## Usage au-delà de "Démarre tout"

Pour les utilisateurs : invoquer via `Agent(subagent_type="quant-XXXX")` le découvre automatiquement.
Pour intégration avancée : charger `.claude/agents/*.md`, parser frontmatter, dispatcher au runtime.

---

**Philosophie** : Un agent = une mission bien définie, contexte figé partagé, modèle juste-dimensionné, anti-snooping déclaré d'avance.
