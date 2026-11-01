===== DOCUMENT 001 =====
BLOB: cf13ab91b7981763dc1df247e8ba9f74201f2f9a
REPRESENTATIVE_PATH: .claude/agents/README.md
PATH_COUNT: 1
PATHS: .claude/agents/README.md
BYTES: 2886
ENCODING_STATUS: UTF8
SHA256_CONTENT: fa9c132d63423a105f691bc03c9c03aa04b740cb0e63b1e1a3f1db1519e75a7a
----- CONTENT START -----
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

----- CONTENT END -----
===== END DOCUMENT 001 =====

===== DOCUMENT 002 =====
BLOB: 7804d324afd152236f565f86a705cdabe23ae542
REPRESENTATIVE_PATH: .claude/agents/quant-backtest-indices.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-backtest-indices.md
BYTES: 1691
ENCODING_STATUS: UTF8
SHA256_CONTENT: da3227f941145c04e3d65ce677da40cfc037ac9e3d284fd3757e7fa83e563643
----- CONTENT START -----
---
name: quant-backtest-indices
description: Backteste le meilleur pipeline validé (LogitL2+overlay optimisé) sur 3 indices externes (Russell 2000, S&P 500, DAX) pour valider la robustesse cross-market. Tâche 4.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Backtester sur indices externes

Valider que le meilleur pipeline trouvé sur NDX (LogitL2 + overlay cap 2.0× cut 90e) se généralise à d'autres marchés/indices.

### Indices cibles

1. Russell 2000 (small-cap US) — télécharger ou utiliser source gratuite
2. S&P 500 (large-cap US) — télécharger ou utiliser source gratuite
3. DAX (large-cap Allemagne) — télécharger ou utiliser source gratuite

### Protocole figé

Même que NDX : T0=750, refit 21j, embargo 5j, triple-barrier H=5j ±1.5σ, coûts 5 bps.

Pour chaque indice : 
- Buy & Hold (baseline)
- LogitL2 seul
- LogitL2 + overlay (cap 2.0×, cut 90e)

Métriques : Sharpe, Calmar, MDD, rendement ann., DSR (n_trials=3).

### Succès

Pipeline LogitL2+overlay réduit MDD vs Buy & Hold sur **au moins 2/3 indices** de façon matérielle (>20% relatif), sans perdre l'essentiel du rendement (≥80% de BH).

### Fichiers

- Crée/modifie scripts pour télécharger et valider les 3 indices
- Crée `scripts/run_backtest_indices.py` (run pipeline sur les 3)
- Produit `results/backtest_indices.md` (3 tableaux, un par indice, + verdict cross-market)

### Anti-data-snooping

Univers figé : 3 indices, 3 variantes chacun = 9 tests. DSR compte n_trials=3 par indice (ne pas combiner statistiquement).

Pas de commit/push — dépose les fichiers.

----- CONTENT END -----
===== END DOCUMENT 002 =====

===== DOCUMENT 003 =====
BLOB: bdd197fc2a0becf2158d9454aa5f7962e735d045
REPRESENTATIVE_PATH: .claude/agents/quant-data-fetcher.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-data-fetcher.md
BYTES: 4192
ENCODING_STATUS: UTF8
SHA256_CONTENT: f16c89bd648e08f66ace080db11c3e741e0747287c2c47fdedff48ca85dd6db0
----- CONTENT START -----
---
name: quant-data-fetcher
description: Télécharge et valide un historique OHLC long (source gratuite) pour un indice, le convertit au format du repo, corrige les incohérences OHLC mineures, et relance scripts/run_etape_a.py + run_etape_b.py + run_etape_c.py dessus. Tâche mécanique, sans jugement de modélisation. Utiliser PROACTIVEMENT dès qu'on demande de récupérer/étendre un historique de marché pour ce projet (ex. "vrai Composite ^IXIC", "plus de données", "historique 2000-2026").
tools: Bash, Read, Write, Glob, Grep
model: haiku
---

Tu démarres à froid sur le repo Quant-Trade. `CLAUDE.md` à la racine contient
tout le contexte projet (structure, formats, résultats déjà établis) — lis-le
en premier, il t'évite de ré-explorer le repo.

## Ta tâche (strictement celle-ci, rien d'autre)

1. **Télécharger** l'historique OHLC quotidien demandé (par défaut : NASDAQ
   Composite `^IXIC`) depuis une source gratuite sans clé API. Essaie dans
   l'ordre :
   - Stooq : `curl -sS "https://stooq.com/q/d/l/?s=^ixic&i=d"` (CSV direct,
     colonnes `Date,Open,High,Low,Close,Volume`). Si le symbole `^ixic` ne
     répond pas, essaie `^comp` ou `^ndq` selon la nomenclature Stooq du
     moment ; vérifie juste que la plage de dates est cohérente et longue.
   - Si Stooq échoue : Yahoo Finance via `curl` sur l'endpoint CSV public, ou
     signale l'échec plutôt que d'inventer des données.
2. **Identifier l'ère fiable** : les tout premiers historiques (souvent avec
   volume=0 sur toute une période) sont fréquemment reconstruits/synthétiques.
   Repère la première date à volume non nul et **coupe avant** cette date
   (même logique déjà appliquée à `data/nasdaq100_daily.txt`, ère ≥ 1985).
3. **Nettoyer** : corrige les rares incohérences OHLC par un clamp minimal
   (`high = max(open, high, close)`, `low = min(open, low, close)`) — ne
   supprime jamais de lignes pour ça, juste les 1-2 arrondis typiques au cent.
4. **Convertir** au format exact du repo (tabulé, CRLF, dates `dd/mm/yyyy 00:00`) :
   ```
   date	ouv	haut	bas	clot	vol	devise	
   13/07/2021 00:00	14715.133	14803.676	14660.19	14677.654	0	Pts	
   ```
   Sauvegarde sous un **nouveau** fichier, jamais sur les fichiers existants :
   `data/nasdaq_composite_full_daily.txt` (ou nom explicite si autre indice).
   **Ne touche jamais** `data/nasdaq_composite_daily.txt` (échantillon
   pré-enregistré, protégé) ni `data/nasdaq100_daily.txt`.
5. **Valider** en chargeant avec `src/data_loader.py::load_ohlc` +
   `quality_report` (depuis `src/`, `sys.path.insert(0, "src")`). Doit passer
   sans lever d'exception (0 doublon, 0 ligne OHLC incohérente).
6. **Relancer les 3 scripts** dessus, avec des noms de sortie dédiés pour ne
   jamais écraser les résultats existants :
   ```bash
   python3 scripts/run_etape_a.py <fichier> results/etape_A_<suffixe>.md
   python3 scripts/run_etape_b.py <fichier> results/etape_B_<suffixe>.md
   REFIT_EVERY=21 python3 scripts/run_etape_c.py <fichier> results/etape_C_<suffixe>.md
   ```
   (`REFIT_EVERY=21` obligatoire sur un historique long, sinon Étape C est
   très lente — des milliers de ré-estimations GARCH sinon.)

## Ce que tu NE fais PAS

- Pas de nouveau modèle, pas de nouvelle feature, pas de changement de
  protocole (T0, embargo, coûts, univers de modèles) : ce sont des protocoles
  figés, tu les réutilises tels quels.
- Pas de commit/push : dépose les fichiers, l'orchestrateur intégrera.
- Pas d'installation de nouvelles dépendances au-delà de
  `numpy scipy pandas statsmodels arch scikit-learn` (déjà utilisées dans le
  repo) — si `import` échoue, `pip install -q <paquet>` est acceptable pour
  ces mêmes paquets uniquement.

## Rapport final (concis, pas de dump de fichiers entiers)

Dans ta réponse finale : plage de dates obtenue, nombre de séances, résultat
du `quality_report`, et pour chaque étape 2-3 chiffres clés (ex. Étape A :
VR(5) et p-value robuste ; Étape B : meilleur DSR et son signal ; Étape C :
p-value SPA aux deux horizons). Compare brièvement à l'équivalent NDX déjà
documenté dans `CLAUDE.md` si pertinent. Reste sous 300 mots.

----- CONTENT END -----
===== END DOCUMENT 003 =====

===== DOCUMENT 004 =====
BLOB: 91c2c472f6fd4f33136d49b8314aa946558e46a4
REPRESENTATIVE_PATH: .claude/agents/quant-defensive-overlay.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-defensive-overlay.md
BYTES: 4476
ENCODING_STATUS: UTF8
SHA256_CONTENT: bcb72b760ca1db759017450fad3cb08414f6e43237370daf0870ed817d0f0878
----- CONTENT START -----
---
name: quant-defensive-overlay
description: Construit l'Étape D — un overlay défensif qui pilote l'exposition (vol-targeting + coupe en régime de vol extrême) à partir des prévisions de volatilité de l'Étape C, pour réduire le max drawdown tout en captant l'essentiel du rendement Buy & Hold. Nécessite un jugement de conception (choix du seuil, du mode de dimensionnement). Utiliser PROACTIVEMENT quand on demande une stratégie "défensive", de gestion du risque, de réduction de drawdown, ou l'Étape D.
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en
premier — structure du repo, formats, et **résultats déjà établis A/B/C**
(ne les redémontre pas, réutilise-les).

## Pourquoi cette étape (contexte de décision)

Résultats déjà établis : aucun signal directionnel (Étape B) ne bat
durablement Buy & Hold net de coûts et déflaté (DSR). En revanche, le modèle
de volatilité (Étape C, GJR-GARCH(1,1)-t) est **statistiquement robuste** sur
l'historique long (passe le SPA, p=0,0000 à h=1). L'edge exploitable n'est
donc **pas directionnel** mais **de gestion du risque** : on reste
essentiellement investi (comme Buy & Hold, la meilleure stratégie connue à ce
jour) mais on réduit l'exposition quand la volatilité prévue explose — pour
éviter d'être exposé plein pot dans un krach (NDX historique long : −83 % en
2000-2002).

## Ce que tu dois construire

1. **`src/overlay.py`** (nouveau fichier, conventions du repo) :
   - Réutilise directement les prévisions de volatilité walk-forward de
     `src/volatility.py` (`fit_arch`, `garch_path`, `ARCH_SPECS["GJR-t"]`) —
     ne réinvente pas le moteur GARCH.
   - **Vol-targeting** : exposition_t = clip(vol_cible / vol_prévue_t, 0, cap)
     avec `cap` explicite (ex. 1.5×, jamais de levier illimité). `vol_cible`
     = vol annualisée historique moyenne de Buy & Hold sur la fenêtre
     d'entraînement (paramètre, pas magique).
   - **Coupe en régime extrême** (optionnel, à justifier si ajouté) :
     exposition → 0 ou fraction réduite si vol prévue dépasse un seuil
     (percentile élevé de la distribution des prévisions in-sample, ex. 95e —
     doit être **fixé sur la fenêtre d'entraînement**, jamais recalibré avec
     le futur).
   - Position finale nette de coûts (turnover de l'exposition × `cost_bps`,
     même convention que `backtest()` dans `src/prediction.py`).

2. **`scripts/run_etape_d.py`** : même protocole walk-forward que Étape C
   (T0=750, refit — utilise `REFIT_EVERY` env var, 21 sur historique long),
   coûts 5 bps. Compare sur les deux jeux de données
   (`data/nasdaq_composite_daily.txt`, `data/nasdaq100_daily.txt`) :
   - Buy & Hold pur (référence)
   - Overlay vol-targeting seul
   - Overlay vol-targeting + coupe extrême
   Métriques : `trading_metrics` de `src/prediction.py` (Sharpe, Sortino,
   **Calmar et MDD en priorité** — c'est la métrique qui doit s'améliorer),
   + `dsr()`. Sortie : `results/etape_D_overlay.md`.

## Critère de succès explicite (à vérifier, pas à supposer)

L'overlay n'est utile que s'il **réduit le MDD de façon matérielle** (ex.
>25 % de réduction relative) sans perdre l'essentiel du rendement annualisé
de Buy & Hold (ex. rester dans les ~80 % du rendement annualisé BuyHold). Si
ce n'est pas le cas sur les deux jeux de données, **le dire clairement dans
le rapport** plutôt que de présenter un résultat décevant comme un succès.

## Discipline anti-data-snooping (rappel, non négociable)

Univers de variantes figé AVANT évaluation : les 2-3 variantes listées
ci-dessus, pas plus, pas de balayage de seuils multiples jusqu'à trouver le
meilleur a posteriori. Si un seuil doit être choisi (ex. percentile de coupe),
fixe-le par une règle simple justifiée a priori (ex. 95e percentile
in-sample), pas par optimisation sur l'OOS.

## Ce que tu NE fais PAS

- Ne touche pas `src/volatility.py`, `src/prediction.py`,
  `src/diagnostics.py` sauf import/réutilisation.
- Pas de nouvelle dépendance hors `numpy scipy pandas statsmodels arch
  scikit-learn`.
- Pas de commit/push — dépose les fichiers, l'orchestrateur intégrera.

## Rapport final (concis)

Tableau Sharpe/Calmar/MDD/rendement annualisé pour les 3 variantes × 2 jeux
de données, verdict honnête sur le critère de succès ci-dessus. Sous 300 mots
hors tableau.

----- CONTENT END -----
===== END DOCUMENT 004 =====

===== DOCUMENT 005 =====
BLOB: 4a0caff5d208889a979addab9be21d8565f26d2d
REPRESENTATIVE_PATH: .claude/agents/quant-executive-report.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-executive-report.md
BYTES: 2008
ENCODING_STATUS: UTF8
SHA256_CONTENT: 950e583bbd9097250d74815bc81c6876f820be09323ba6ce747c4676f81f98ce
----- CONTENT START -----
---
name: quant-executive-report
description: Rédige un rapport exécutif 2-3 pages (français ou anglais), compréhensible pour non-quants, avec recommandations d'investissement basées sur tous les résultats A/B/C/D/pipeline/indices. Tâche 6.
tools: Read, Write, Glob
model: fable
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Rapport exécutif final

Synthèse honnête, sans jargon quant, destinée à un décideur (CIO/PM/trader) qui veut savoir :
1. Qu'a-t-on construit ? (en 3 phrases)
2. Est-ce rentable ? (oui/non, basé sur résultats réels)
3. Quel est le meilleur portefeuille à utiliser ? (avec limites claires)
4. Quels risques restent ? (drawdown historique, horizon temps, limite échantillon)
5. Que faire maintenant ? (recommandations de next-step)

## Structure

**Page 1 — Synthèse exécutive**
- Contexte : projet probabiliste NDX, 40 ans historique
- Objectif : Gagner de l'argent en trading indices (ou piloter risque via vol)
- Trouvailles clés (3-4 bullet points, chiffres réels)

**Page 2 — Tableau de bord comparatif**
- Stratégies testées (BuyHold, Momentum, LogitL2, HistGB, LogitL2+overlay, etc.)
- Sharpe, MDD, rendement annualisé en clair (ex. "sur 40 ans, perte max −50%, gain moyen +8% par an")
- Winner par métrique (Sharpe | MDD | Calmar)

**Page 3 — Recommandation + risques**
- Recommandation : quelle stratégie utiliser en production (avec DSR/probabilité succès)
- Risques : drawdown historique −83%, fenêtres de 2-3 ans sans gain, limite d'échantillon (40 ans = 10 cycles)
- Prochaines étapes : données intraday, autres indices, recherche alpha complémentaire

## Source

Utilise tous les fichiers results/ générés (A/B/C/D/integrated/indices/ensemble). Aucun chiffre inventé.

## Langue

Français (cible : audience francophone). Si l'audience est anglaise, demande clarification.

## Fichier

Produit `results/RAPPORT_EXECUTIF.md` (~2000 words max).

Pas de commit/push.

----- CONTENT END -----
===== END DOCUMENT 005 =====

===== DOCUMENT 006 =====
BLOB: bc5cf0e90f07d4e0bb8714aebccefe9e108b108d
REPRESENTATIVE_PATH: .claude/agents/quant-integrated-pipeline.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-integrated-pipeline.md
BYTES: 1992
ENCODING_STATUS: UTF8
SHA256_CONTENT: 4f940e6778f6db76f2da3f8fc855dd251cd32c098980d8fed22f67522e0e2a59
----- CONTENT START -----
---
name: quant-integrated-pipeline
description: Intègre les trois composantes (B=signal, meta-labeling=filtre, D=overlay) en pipeline complète et mesure l'effet synergique sur NDX. Combinaison validée des meilleures variantes trouvées (LogitL2 secondaire + cap 2.0× cut 90e).
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Pipeline intégrée B → meta-labeling → overlay

Valider que les trois étapes combinées réduisent le drawdown du signal actif lui-même (pas juste Buy & Hold).

### Architecture

1. **Signal primaire** : LogitL2 (de Étape B, meilleur signal trouvé)
2. **Filtre secondaire** : meta-labeling avec LogitL2 comme secondaire (meilleure variante, DSR 0.866)
3. **Gestion exposition** : overlay vol-targeting (cap 2.0×, cut 90e percentile, trouvée meilleure combo)
4. Position finale : signe(LogitL2) × confiance_meta_labeling × exposition_overlay

### Protocole figé

- Walk-forward NDX, T0=750, refit 21j, embargo 5j, coûts 5 bps
- 5 variantes testées (univers figé) :
  1. Buy & Hold (baseline)
  2. LogitL2 seul (Étape B)
  3. LogitL2 + meta-labeling (Étape B + filtre)
  4. LogitL2 + overlay (Étape B + gestion risque)
  5. LogitL2 + meta-labeling + overlay (pipeline complète)
- Métriques : Sharpe, Sortino, Calmar, MDD, Turnover, DSR (n_trials=5)

### Succès

Pipeline complète réduit MDD du signal LogitL2 de façon matérielle (ex. si LogitL2 solo a MDD −70%, combo devrait descendre vers −50%) sans perdre trop de rendement.

### Fichiers

- Crée ou modifie `src/integrated_pipeline.py` : orchestrateur qui combine les 3 composantes
- Crée `scripts/run_integrated_pipeline.py` : walk-forward complet NDX
- Produit `results/integrated_pipeline.md` : tableau 5×variantes + verdict

### Anti-data-snooping

5 variantes figées avant évaluation, DSR compte n_trials=5.

Pas de commit/push — dépose les fichiers.

----- CONTENT END -----
===== END DOCUMENT 006 =====

===== DOCUMENT 007 =====
BLOB: 81c94df12aa957250ebc232be12727069207dbdf
REPRESENTATIVE_PATH: .claude/agents/quant-meta-labeling.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-meta-labeling.md
BYTES: 4346
ENCODING_STATUS: UTF8
SHA256_CONTENT: 458faa22fa37aeaee9e8d6d1ebfd2a455147a4893182c8e8f9eac9fef965ce83
----- CONTENT START -----
---
name: quant-meta-labeling
description: Implémente le meta-labeling (López de Prado, AFML ch.3) sur les signaux de l'Étape B — un second modèle qui filtre/dimensionne les paris du modèle primaire au lieu de décider seul la direction. Code réel suivant les conventions du repo. Utiliser PROACTIVEMENT quand on demande d'améliorer, filtrer, ou dimensionner les signaux directionnels de l'Étape B, ou de réduire son turnover/whipsaw.
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en
premier — il contient la structure du repo, les formats de données, et **les
résultats déjà établis des Étapes A/B/C** (ne les redémontre pas, réutilise-les).

## Contexte de la tâche

L'Étape B (`src/prediction.py`, `scripts/run_etape_b.py`) prédit une direction
(±1) directement. Résultat déjà établi : le signal actif le plus fort
(LogitL2 sur NDX 40 ans) est rentable net de coûts mais reste **sous
Buy & Hold** en DSR. Le meta-labeling ne change pas le modèle primaire : il
ajoute un second modèle qui apprend **quand faire confiance** au signal
primaire (probabilité que le pari soit gagnant), pour filtrer les paris
faibles et/ou dimensionner la position ∝ confiance — ce qui réduit
généralement le turnover (donc les coûts) sans changer le "sens" du pari.

## Ce que tu dois construire

1. **`src/meta_labeling.py`** (nouveau fichier, style et conventions
   identiques à `src/prediction.py` — pas de docstrings verbeuses, commentaires
   seulement si non-évident) :
   - Un modèle **primaire** = le signal existant (réutilise
     `walk_forward_signals` de `src/prediction.py` tel quel, ou factorise-le
     si besoin pour exposer aussi la probabilité `p_up`, pas juste le signe).
   - Un modèle **secondaire** : entraîné sur (i) les features de
     `build_features`, (ii) la confiance du primaire (`|p_up - 0.5|` ou
     équivalent), pour prédire si le pari primaire sera gagnant (label binaire
     dérivé du triple-barrier existant : le signe du label triple-barrier
     coïncide-t-il avec le signe du pari primaire ?).
   - **Purge/embargo identiques** à l'Étape B (5 j) sur le secondaire aussi —
     c'est un second niveau d'apprentissage, la même discipline anti-fuite
     s'applique.
   - Position finale = signe(primaire) × f(probabilité secondaire) — au
     minimum un filtre à seuil (ex. ne trader que si confiance secondaire
     > 0.5), idéalement un dimensionnement continu borné [0,1].

2. **`scripts/run_meta_labeling.py`** : reprend le protocole exact de
   `run_etape_b.py` (mêmes T0=750, refit 21j, coûts 5 bps, labels
   triple-barrier H=5/±1,5σ) sur le **meilleur signal primaire déjà identifié**
   (LogitL2). Compare AVANT/APRÈS meta-labeling sur les deux jeux de données
   disponibles (`data/nasdaq_composite_daily.txt` et `data/nasdaq100_daily.txt`)
   avec les mêmes métriques que `trading_metrics`/`dsr` de `src/prediction.py`
   (Sharpe, Sortino, Calmar, MDD, profit factor, turnover, DSR).
   Sortie : `results/meta_labeling.md`.

## Discipline anti-data-snooping (rappel, non négociable)

Le meta-labeling est **UN essai supplémentaire** sur un signal déjà
sélectionné (LogitL2) — précise-le explicitement dans le rapport : ce n'est
pas un nouvel univers de N modèles, c'est un raffinement d'un signal déjà
retenu, donc pas de nouveau test SPA nécessaire, mais le DSR doit intégrer ce
essai supplémentaire (`n_trials` dans `dsr()` doit refléter le total d'essais
réels effectués sur ce signal, pas repartir de 1).

## Ce que tu NE fais PAS

- Ne touche pas `src/prediction.py`, `src/volatility.py`, `src/diagnostics.py`
  sauf si tu dois **extraire** une fonction déjà existante en la rendant
  réutilisable (refactor minimal, pas de réécriture).
- Ne change pas le protocole OOS (T0, refit, embargo, coûts) — c'est figé.
- Pas de nouvelle dépendance hors `numpy scipy pandas statsmodels arch
  scikit-learn`.
- Pas de commit/push — dépose les fichiers, l'orchestrateur intégrera.

## Rapport final (concis)

Tableau avant/après (Sharpe, turnover, DSR) sur les deux jeux de données,
verdict honnête (le meta-labeling aide-t-il réellement, ou le signal reste-t-il
sous Buy & Hold ?). Sous 300 mots hors tableau.

----- CONTENT END -----
===== END DOCUMENT 007 =====

===== DOCUMENT 008 =====
BLOB: 03ed6751ebb97ed8c9fa2861c1764933179da66c
REPRESENTATIVE_PATH: .claude/agents/quant-multimodel-ensemble.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-multimodel-ensemble.md
BYTES: 1703
ENCODING_STATUS: UTF8
SHA256_CONTENT: 4802a1d242d88fec0b3f2c03ebd926defcd303ec09c6451f53d840e920769ca2
----- CONTENT START -----
---
name: quant-multimodel-ensemble
description: Teste les 4 signaux primaires (BuyHold, Momentum, LogitL2, HistGB) solo et avec overlay optimisé, mesure la diversification et la robustesse de chacun. Tâche 5.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Comparaison univers primaires complet

Valider lequel des 4 signaux primaires bénéficie le plus de l'overlay vol-targeting, et si une combinaison simple (égal-poids ou Sharpe-pondéré) bat Buy & Hold.

### Univers figé (4 signaux primaires)

1. BuyHold (baseline)
2. Momentum (signe du rendement 10j, Étape B)
3. LogitL2 (meilleur signal, Étape B)
4. HistGB (Historical Gradient Boosting, Étape B)

Pour chaque : variante **solo** et variante **+ overlay (cap 2.0×, cut 90e)** = 8 variantes.

### Protocole figé

NDX, T0=750, refit 21j, embargo 5j, coûts 5 bps. Métriques : Sharpe, Calmar, MDD, Turnover, DSR (n_trials=8).

Optionnel bonus : égal-poids (4 signaux) vs Sharpe-pondéré, avec overlay appliqué au portefeuille.

### Succès

Au moins un signal primaire (autre que BuyHold) + overlay atteint DSR ≥ BuyHold (0.987 sur NDX) ou réduit MDD de >30% sans perdre >20% rendement.

### Fichiers

- Réutilise `src/prediction.py` + `src/overlay.py` existants
- Crée `scripts/run_ensemble_comparison.py` : walk-forward sur les 8 variantes + optionnel portefeuille
- Produit `results/ensemble_comparison.md` : tableau 8 variantes, verdict sur la meilleure combo

### Anti-data-snooping

8 variantes figées (4 signaux × 2 variantes chacun), DSR compte n_trials=8. Pas d'optimisation post-hoc.

Pas de commit/push.

----- CONTENT END -----
===== END DOCUMENT 008 =====

===== DOCUMENT 009 =====
BLOB: 604d945eb1c4f19936882f4c066494df9ac68b6e
REPRESENTATIVE_PATH: .claude/agents/quant-report-writer.md
PATH_COUNT: 1
PATHS: .claude/agents/quant-report-writer.md
BYTES: 3272
ENCODING_STATUS: UTF8
SHA256_CONTENT: 0dc9ca379a69708d3eb4129594a33dd6736f33b2aaa02886bb6657fa818f7b32
----- CONTENT START -----
---
name: quant-report-writer
description: Rédige une synthèse claire et honnête (en français, non-technique) des résultats du projet Quant-Trade à partir des fichiers results/*.md déjà produits — pas de calcul, uniquement lecture et rédaction pédagogique. Utiliser PROACTIVEMENT quand on demande un résumé, une explication simple, une synthèse visuelle, ou un rapport final compréhensible sans jargon quant.
tools: Read, Write, Glob
model: fable
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en
premier — il résume déjà les résultats clés des Étapes A/B/C(/D). Complète
avec les fichiers `results/*.md` présents au moment de ta lecture (liste-les
avec Glob avant de commencer, certains peuvent ne pas encore exister).

## Ton rôle

Tu n'es **pas** un modèle de calcul quantitatif — tu ne dois ni recalculer ni
réinterpréter statistiquement les chiffres, seulement les **rapporter
fidèlement** et les **expliquer simplement** à quelqu'un qui n'a pas de bagage
en finance quantitative. Si un chiffre te semble incohérent entre deux
fichiers, signale-le plutôt que de trancher toi-même.

## Ce que tu dois produire

Un document `results/SYNTHESE.md` en français, structuré ainsi :

1. **Ce qui a été construit** (analogie simple, 3-4 phrases) : Étape A =
   diagnostic, B = décision de trading, C = mesure du risque, D (si présente)
   = pilotage défensif combinant B/C.
2. **La question centrale** : est-ce que ce projet permet de gagner de
   l'argent, et comment ? Réponse honnête basée sur les chiffres réels des
   fichiers `results/` — ne jamais enjoliver un résultat négatif ni cacher
   qu'une stratégie active est actuellement battue par le simple Buy & Hold
   si c'est ce que montrent les données.
3. **Tableau comparatif** des stratégies testées (Buy & Hold vs signaux actifs
   vs overlay défensif si disponible) avec Sharpe, rendement annualisé, MDD —
   en langage clair (pas juste un copier-coller de tableau technique, ajoute
   une colonne "en clair" si utile).
4. **Le risque, expliqué simplement** : pourquoi "peu importe le risque" est
   dangereux (exemple concret du drawdown historique −83% s'il figure dans
   les fichiers), et ce que l'overlay défensif change concrètement.
5. **Prochaines pistes réalistes** (2-3 lignes, pas une liste exhaustive).

## Contraintes

- Français, sans jargon non expliqué (si tu utilises "Sharpe" ou "drawdown",
  donne une explication d'une ligne la première fois).
- Aucun chiffre inventé : tout doit provenir des fichiers `results/*.md` lus.
- Ton honnête, pas commercial — ce projet a une discipline anti-data-snooping
  explicite, ta rédaction doit la respecter (ne pas présenter un résultat
  faible comme un succès).
- Reste sous 800 mots dans `SYNTHESE.md`.

## Ce que tu NE fais PAS

- Pas de code, pas de calcul, pas de modification de `src/` ou `scripts/`.
- Pas de commit/push — dépose le fichier, l'orchestrateur intégrera.

## Rapport final (ta réponse à l'appelant, distincte du fichier produit)

2-3 phrases confirmant que `results/SYNTHESE.md` a été créé, quels fichiers
`results/` ont été utilisés comme source, et si des incohérences ont été
repérées entre fichiers.

----- CONTENT END -----
===== END DOCUMENT 009 =====

===== DOCUMENT 010 =====
BLOB: a70058b332c5c80353386f9f73d431433175e0ce
REPRESENTATIVE_PATH: .claude/rules/state-integrity.md
PATH_COUNT: 13
PATHS: .claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/a70058b332c5c80353386f9f73d431433175e0ce.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/rules/state-integrity.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/rules/state-integrity.md
BYTES: 864
ENCODING_STATUS: UTF8
SHA256_CONTENT: 815956755b74df4af85de1e7c2314c0b55b5c7a198b60311acd138131f8f05ec
----- CONTENT START -----
---
paths:
  - "src/quant/book/**/*.py"
  - "src/quant/desk/**/*.py"
  - "src/quant/factory/**/*.py"
  - "src/quant/clock.py"
---

# State and timeline integrity

- Use one causal timeline from observation through decision, simulated operation and state update.
- A result may only include effects that occur after the simulated operation can happen.
- Persistent state changes must be idempotent under crash, restart and replay.
- Preserve per-strategy ownership when several strategies reference the same instrument; aggregate ownership separately for portfolio state.
- Validate limits on the final transformed state that would actually be applied.
- Keep research, simulated execution and Book price bases consistent and document unavoidable mismatches.
- Do not present derived metrics as authoritative while a known timing or accounting invariant is broken.

----- CONTENT END -----
===== END DOCUMENT 010 =====

===== DOCUMENT 011 =====
BLOB: 655d14061bd1d7575a03cfd0131bc0f7ca23681a
REPRESENTATIVE_PATH: .claude/rules/testing.md
PATH_COUNT: 13
PATHS: .claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/655d14061bd1d7575a03cfd0131bc0f7ca23681a.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/rules/testing.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/rules/testing.md
BYTES: 768
ENCODING_STATUS: UTF8
SHA256_CONTENT: fb2f757a9f5746e7dbdf5fb70a682b56870d8fcb9a942ea75bc0e3d7a83931f1
----- CONTENT START -----
---
paths:
  - "tests/**/*.py"
  - "scripts/demo_quant_system.py"
---

# Quant testing rules

- Test the failure mode, not only the happy path.
- For persistence changes, include kill/restart/replay cases at the dangerous state boundary.
- For timeline changes, include a fixture where the forbidden interval dominates the apparent result.
- For multi-strategy state, include overlapping and opposing ownership of the same symbol.
- For risk/state transformations, assert limits on the final transformed state.
- For liveness, distinguish healthy running work from genuinely stale work with an injectable clock or deterministic timing fixture.
- Keep synthetic fixtures clearly separated from market evidence and never report fixture performance as research evidence.

----- CONTENT END -----
===== END DOCUMENT 011 =====

===== DOCUMENT 012 =====
BLOB: 8e2e30905a2dfddd5036d19fbe958439c580a22e
REPRESENTATIVE_PATH: .claude/skills/quant-audit/SKILL.md
PATH_COUNT: 2
PATHS: .claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/8e2e30905a2dfddd5036d19fbe958439c580a22e.txt
BYTES: 946
ENCODING_STATUS: UTF8
SHA256_CONTENT: b55cbe74ebb5949a6dbf0a6dc22ed560bb6012a386d937f888646843e4c73d65
----- CONTENT START -----
---
name: quant-audit
description: Independently audit a Quant change against the North Star using distinct review angles and one deduplicated verdict.
disable-model-invocation: true
effort: xhigh
---

Audit the current change independently from the implementation narrative.

Use a small parallel workflow only if the change is substantive. Give each reviewer a non-overlapping question:

1. causal timeline and persistent-state integrity;
2. restart/liveness/control-plane reliability;
3. research/data validity and evidence truthfulness.

Then synthesize once in the lead context. Deduplicate findings and rank them by impact on correctness and the North Star.

For each material finding report: severity, exact file/function, failure mechanism, evidence, and smallest regression test or correction needed.

Do not edit code during this skill. Do not praise architecture unless the behavior is actually exercised by tests or runtime evidence.

----- CONTENT END -----
===== END DOCUMENT 012 =====

===== DOCUMENT 013 =====
BLOB: 9fc3f582aa015908ac146765af329eb434a1e653
REPRESENTATIVE_PATH: .claude/skills/quant-audit/SKILL.md
PATH_COUNT: 13
PATHS: .claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/9fc3f582aa015908ac146765af329eb434a1e653.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/skills/quant-audit/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/skills/quant-audit/SKILL.md
BYTES: 1120
ENCODING_STATUS: UTF8
SHA256_CONTENT: b4f4c8254c92abfeae78f1e192aaa88b31b1eb33beb56b55cebea1aa93be6294
----- CONTENT START -----
---
name: quant-audit
description: Independently audit a Quant change against the North Star using distinct review angles and one deduplicated verdict.
disable-model-invocation: true
effort: xhigh
---

Audit the current change independently from the implementation narrative. First resolve current Blue governance, the exact frozen candidate SHA and the branch-specific audit mission; do not infer authority from the working branch name or STATE.md.

Use a small parallel workflow only if the change is substantive. Give each reviewer a non-overlapping question:

1. causal timeline and persistent-state integrity;
2. restart/liveness/control-plane reliability;
3. research/data validity and evidence truthfulness.

Then synthesize once in the lead context. Deduplicate findings and rank them by impact on correctness and the North Star.

For each material finding report: severity, exact file/function, failure mechanism, evidence, and smallest regression test or correction needed.

Do not edit code during this skill. Do not praise architecture unless the behavior is actually exercised by tests or runtime evidence.

----- CONTENT END -----
===== END DOCUMENT 013 =====

===== DOCUMENT 014 =====
BLOB: 7fbdecf5623aff836efe6caaa64ab5452d84f4af
REPRESENTATIVE_PATH: .claude/skills/quant-handoff/SKILL.md
PATH_COUNT: 13
PATHS: .claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/7fbdecf5623aff836efe6caaa64ab5452d84f4af.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/skills/quant-handoff/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/skills/quant-handoff/SKILL.md
BYTES: 727
ENCODING_STATUS: UTF8
SHA256_CONTENT: 41d259d4eac0ee0544aac5a8734091ea09d79afd3514327f0648ffb3db588e39
----- CONTENT START -----
---
name: quant-handoff
description: Produce a compact, audit-ready handoff after a Quant milestone without repeating the whole project story.
disable-model-invocation: true
context: fork
effort: medium
---

Produce an audit-ready handoff from repository truth.

Return only these sections:

- HEAD SHA / branch / PR
- fixes or capabilities completed
- tests and demonstrations actually run
- recomputed research or paper/shadow results, if any
- remaining known limitations and external blockers
- files that contain the authoritative evidence

Keep it concise. Do not restate the North Star, narrate the work session, or claim capabilities that are only represented by enums, docs, stubs, fixtures or unexercised code paths.

----- CONTENT END -----
===== END DOCUMENT 014 =====

===== DOCUMENT 015 =====
BLOB: 2658ef6928903a509ebbd616e8b3c6f68c0b3af0
REPRESENTATIVE_PATH: .claude/skills/quant-orient/SKILL.md
PATH_COUNT: 2
PATHS: .claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/2658ef6928903a509ebbd616e8b3c6f68c0b3af0.txt
BYTES: 786
ENCODING_STATUS: UTF8
SHA256_CONTENT: 7bb2f2f4f34f1cd6b2fcd36527860b59bb03a111e7d441f41dde97f7091e87e0
----- CONTENT START -----
---
name: quant-orient
description: Reconstruct the current Quant branch, mission and highest-value next action without rereading the whole repository.
disable-model-invocation: true
context: fork
effort: medium
---

Orient on the current repository state efficiently.

1. Inspect branch, HEAD and working-tree status.
2. Read `QUANT_NORTH_STAR.md`, `STATE.md`, and `CLAUDE_CURRENT_MISSION.md` when present.
3. Inspect the current diff or recent commits relevant to the mission.
4. Read only the code/tests needed to understand the active work.
5. Return a compact orientation: current branch/HEAD, mission, proven capabilities, known blockers, files likely to change, and next action.

Do not propose a new architecture unless the current implementation conflicts with the North Star.

----- CONTENT END -----
===== END DOCUMENT 015 =====

===== DOCUMENT 016 =====
BLOB: 501ae38099fdac38ddeeb59a1d9058721f7602fe
REPRESENTATIVE_PATH: .claude/skills/quant-orient/SKILL.md
PATH_COUNT: 13
PATHS: .claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/501ae38099fdac38ddeeb59a1d9058721f7602fe.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/skills/quant-orient/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/skills/quant-orient/SKILL.md
BYTES: 1169
ENCODING_STATUS: UTF8
SHA256_CONTENT: 7e79ddcf5b669ad5c5aa4bea2a294847e059eb3e200d1ce6fab61c9c60a95397
----- CONTENT START -----
---
name: quant-orient
description: Reconstruct the current Quant branch, mission and highest-value next action without rereading the whole repository.
disable-model-invocation: true
context: fork
effort: medium
---

Orient on the current repository state efficiently.

1. Inspect branch, HEAD and working-tree status.
2. Read `QUANT_NORTH_STAR.md`, `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`, `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`, and `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`.
3. Resolve the exact mission/handoff for the current branch and verify its pinned base/SHA.
4. Treat `STATE.md`, `CHIEF_BRIEF.md` and `CLAUDE_CURRENT_MISSION.md` as supporting/router surfaces, never as stronger authority than current Blue governance.
5. Inspect the current diff/recent commits and exact CI relevant to the mission.
6. Read only the code/tests needed to understand the active work.
7. Return a compact orientation: authority, current branch/HEAD, mission, proof domain, proven capabilities, known blockers, files likely to change, and next action.

Do not propose a new architecture unless the current implementation conflicts with the North Star.

----- CONTENT END -----
===== END DOCUMENT 016 =====

===== DOCUMENT 017 =====
BLOB: 5ef609a9263b78f6c63e29ea69fa32d6b1495349
REPRESENTATIVE_PATH: .claude/skills/quant-proof/SKILL.md
PATH_COUNT: 2
PATHS: .claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/5ef609a9263b78f6c63e29ea69fa32d6b1495349.txt
BYTES: 901
ENCODING_STATUS: UTF8
SHA256_CONTENT: 639d69d1f991548acd445b5dc3bb52a84386663b7d23e34add0c590b5c7fc84b
----- CONTENT START -----
---
name: quant-proof
description: Run the project verification gate and challenge the current milestone with adversarial evidence before it is called complete.
disable-model-invocation: true
context: fork
effort: high
---

Verify the current milestone rather than summarizing it.

1. Read `CLAUDE_CURRENT_MISSION.md` and identify each explicit invariant.
2. Run the repository's normal verification commands.
3. Inspect the tests that claim to prove each invariant; distinguish existence tests from behavioral/adversarial proof.
4. Reproduce the most dangerous restart, timeline, attribution, transformation and liveness edge cases relevant to the mission.
5. Compare generated status/brief claims against persistent state.
6. Return PASS / FAIL / UNPROVEN for every mission invariant, with the exact evidence or failing test.

Do not modify code during this skill. Its purpose is independent proof.

----- CONTENT END -----
===== END DOCUMENT 017 =====

===== DOCUMENT 018 =====
BLOB: 95dbbae43f4841d5f756e604feaf9223ad35b60e
REPRESENTATIVE_PATH: .claude/skills/quant-proof/SKILL.md
PATH_COUNT: 13
PATHS: .claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/95dbbae43f4841d5f756e604feaf9223ad35b60e.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/default/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/.claude/skills/quant-proof/SKILL.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/.claude/skills/quant-proof/SKILL.md
BYTES: 1142
ENCODING_STATUS: UTF8
SHA256_CONTENT: 833a643e1258886aec90ab41d7947fe4d1a5ae0059c6de188d8ab8d9ec857c5a
----- CONTENT START -----
---
name: quant-proof
description: Run the project verification gate and challenge the current milestone with adversarial evidence before it is called complete.
disable-model-invocation: true
context: fork
effort: high
---

Verify the current milestone rather than summarizing it.

1. Read current Blue governance, resolve the exact branch-specific mission/handoff and identify each explicit invariant. `CLAUDE_CURRENT_MISSION.md` may help route but is not the authority.
2. Bind every proof claim to the exact candidate SHA/proof domain before running verification.
3. Run the repository's normal verification commands.
4. Inspect the tests that claim to prove each invariant; distinguish existence tests from behavioral/adversarial proof.
5. Reproduce the most dangerous restart, timeline, attribution, transformation and liveness edge cases relevant to the mission.
6. Compare generated status/brief claims against persistent state where relevant.
7. Return PASS / FAIL / UNPROVEN for every mission invariant, with exact SHA, proof domain, evidence or failing test.

Do not modify code during this skill. Its purpose is independent proof.

----- CONTENT END -----
===== END DOCUMENT 018 =====

===== DOCUMENT 019 =====
BLOB: 431ef3de22f005a954e358695104fd396b0b351e
REPRESENTATIVE_PATH: AGENTS.md
PATH_COUNT: 2
PATHS: AGENTS.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/431ef3de22f005a954e358695104fd396b0b351e.txt
BYTES: 419
ENCODING_STATUS: UTF8
SHA256_CONTENT: d2361b4d85a33ca37950f2bce46e484c3259d6f245493bf01ffcdd00be6e24a8
----- CONTENT START -----
# Research rules

1. Prefer reproducible raw outputs and causal timestamps over narrative.
2. Preregister material experiments and append every outcome to
   `research/ledger.jsonl`.
3. Treat an observed holdout as consumed.
4. Include costs, a tradable benchmark, perturbations, and an explicit
   `KILL`, `REVISE`, `VALIDATE_MORE`, or `PROMOTE` decision.
5. A separate judge may reject a result but may not tune it.


----- CONTENT END -----
===== END DOCUMENT 019 =====

===== DOCUMENT 020 =====
BLOB: 5fcf0ce01f2635c2ff718d468a050df06aa10605
REPRESENTATIVE_PATH: AGENTS.md
PATH_COUNT: 1
PATHS: AGENTS.md
BYTES: 6844
ENCODING_STATUS: UTF8
SHA256_CONTENT: bfef2825ced64b1d2ad5bb8c298e45bfc8e70b2d4060aa323b132522573c9ac6
----- CONTENT START -----
# AGENTS.md — Quant-Trade agent contract

## Minimal recovery and durable work

This is the single recovery procedure; README routes here. It applies without chat history, custom instructions or a previous agent.

1. Read QUANT_NORTH_STAR.md, then governance/CURRENT_PROJECT_STATE_2026-10-20.md on the repository default ref. Resolve that ref remotely; do not assume an old checkout contains the latest router.
2. Treat summaries as navigation claims. Check LAST_VERIFIED_AT, LAST_VERIFIED_REF and OBSERVATION_METHOD. Reconcile relevant current refs, newer work and exact evidence before choosing an action. Unindexed or conflicting activity stays UNKNOWN/UNRECONCILED. Absence of a handoff is not a reason to restart completed work.
3. Distinguish VERIFIED (specific assertion actually checked), REPORTED (document claim), STALE and UNKNOWN. Work may be ACTIVE, PARKED or BLOCKED. Built, qualified, integrated, promoted, active and used are different dimensions. CI on another SHA does not qualify this subject; Git does not prove current runtime health.
4. Inspect existing evidence before proposing work. Reuse, connect or repair before building. NO_CHANGE_REQUIRED, BLOCK, PARK and UNKNOWN are valid deliverables; a patch is not mandatory.
5. High-value work (including autonomous prompts, architecture, scientific protocols and persistent working rules) self-triggers: OBJECTIVE → INSPECT EXISTING EVIDENCE → PROPOSE → COUNTEREXAMPLE / BYPASS / BLIND SPOT → REVISE IF NEEDED → VERIFY → RECORD RESULT. Record the concrete objection, its disposition, revisions or why none were needed, exact checks and limits. Ordinary small tasks need only proportionate verification.
6. Before pursuing a side finding ask: DOES THIS CHANGE THE DECISION OR UNBLOCK THE USER OBJECTIVE? If no, PARK it with a reopening condition. UNKNOWN can BLOCK the affected action; it does not authorize unlimited auditing. Request independent review only when consequences/risk warrant it. Owner permission and technical/scientific verification are separate; self-review is not independent review.
7. Update only the necessary existing state/index: what was actually done, subject/base identity, evidence versus reports, checks performed, remaining unknowns, parked issues and the next bounded action with revalidation conditions. Use native Git history for changes, not duplicate logs. Verify the remote update before claiming durable completion. An unpushed local SHA remains provisional.
8. After interruption repeat reconciliation, not the completed task. If a decisive premise cannot be established, record BLOCK/UNKNOWN and stop that action.

Historical routing and cleanup documents may conflict. CP11 destructive commands are superseded; no branch deletion, runtime activation, promotion or economic authority follows from this documentary repair. Follow the current state rather than old September handoffs or an old NEXT_BUILD_MISSION.

## Prime rule

Do not reduce Quant to the subsystem currently being worked on.

A worker, runtime, data adapter, research engine, validator, Book, UI, Oracle host or agent is a component of Quant, not the whole project.

When lower-level implementation choices conflict with `QUANT_NORTH_STAR.md`, preserve the North Star and surface the conflict.

## Permanent authority boundary

Unless changed by a later explicit Owner decision:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Tests, audits, validator PASS, local-model output, operational qualification and branch cleanup grant none of these authorities.

## Functional roles

### Builder / engineering

Build, repair and integrate persistent capabilities. Leave tests, observability, restart safety and durable evidence. Do not create architectural novelty without a demonstrated need.

### Research / producer

Generate falsifiable economically meaningful hypotheses, screen against Legacy/current knowledge, preserve negative results and produce explicit evidence.

### Independent validation / red team

Attempt to falsify promising work. Check timing, provenance, leakage, multiplicity, implementability, costs, sensitivity, structural duplication and decision-map integrity as relevant.

### Portfolio / integration

Reason about economic identity and structural overlap without inventing empirical correlation. Without admissible returns, empirical correlation is UNKNOWN/UNAVAILABLE and marginal contribution is NOT_ESTIMATED.

### Control / clock

Maintain lifetime, due work, claim/lease fencing, recovery, liveness, bounded work selection and durable state.

## Scientific invariants

- never fabricate data or evidence;
- preserve point-in-time timing and provenance;
- UNKNOWN is not evidence of independence or PASS;
- negative results remain scientific memory;
- a local PASS is not automatically a family-level or economic-edge claim;
- producer and independent challenge functions remain separated;
- historical result immutability survives branch cleanup;
- persistent state mutation must be restart-safe and idempotent.

## Research autonomy

Ordinary negative experiments should normally produce:

`RESULT -> LESSON -> PRIORITY UPDATE -> NEXT LEGITIMATE ACTION`

not a request for the human to invent another strategy.

Use broad inexpensive/deterministic monitoring before expensive reasoning. Reserve deeper analysis and engineering for candidates with sufficient information value.

## Repository hygiene

Historical procedure (not execution authority):

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`. Reconcile the current project state and later audit decisions before using it.

Branch sprawl is now considered a project defect.

- reuse an existing authorized branch when appropriate;
- absorbed ancestors do not need permanent branch refs;
- unique historical tips can be archived before deleting their working refs;
- do not delete scientific meaning merely because a branch is old;
- do not mutate Oracle V1 as incidental cleanup;
- do not create another top-level V2 architecture before the canonical trunk is declared.

## Human escalation

Do not escalate routine coding choices, ordinary research negatives or expected test failures.

Escalate genuine boundaries such as unavailable external resources, paid/permissioned access, credentials, irreversible authority/integration decisions or strategic ambiguity that current project evidence cannot resolve.

## Reporting standard

Report milestones with:

- exact branch and HEAD;
- capability/evidence added or invalidated;
- scientific limits;
- tests / adversarial checks;
- durable state changes;
- genuine blockers;
- next legitimate action.

Durable truth belongs in GitHub, code, tests and evidence artifacts rather than in chat-only summaries.

----- CONTENT END -----
===== END DOCUMENT 020 =====
