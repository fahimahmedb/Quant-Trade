# Audit global A → Z du module « Prédiction politique »

Audit complet demandé pour repartir sur de bonnes bases : état réel, écarts au
plan, erreurs à corriger, et bilan gagné/perdu. Écrit sans complaisance.
(Complète `results/AUDIT.md`, centré sur la contamination hindsight.)

## 1. Inventaire (état réel)

9 modules `src/pp_*.py` (~1600 lignes), 8 scripts `P1..P8`, 8 rapports, 7 jeux de
données. **Les 8 scripts s'exécutent à neuf sans erreur et sont reproductibles**
(random_state figés, md5 stables). Données réelles committées : présidentielle
2017/2022 1er tour + 2022 2nd tour par circonscription (validées à ≤0.25 pt
contre l'officiel).

## 2. Plan initial vs réalisé

| Prévu au plan | Réalisé | Écart |
|---|---|---|
| P1 Fondamentaux (Haiku) | ✅ fait, Haiku | conforme |
| P2 Marchés (Sonnet) | ⚠️ fait puis vidé (forward-only) | dévié (hindsight retiré) |
| P3 NLP (Sonnet) | ⚠️ fait puis vidé (forward-only) | dévié (hindsight retiré) |
| P4 Fusion (Opus) | ✅ codée, mais **dormante** (96 % fondamentaux) | inerte en pratique |
| P5 ML **par circonscription** | ❌ ML fait sur le **national** (11 obs) | **non réalisé** |
| Éco. de tokens (sous-agents+tiering) | ✅ Vague 1 seulement | abandonné ensuite |
| (non prévu) Audit hindsight | ➕ ajouté | gain |
| (non prévu) P6 prévision 2027 | ➕ ajouté | gain |
| (non prévu) P7/P8 circonscription réelle | ➕ ajouté | gain majeur |

**Constat de fond** : le centre de gravité du projet a **basculé**. Le plan visait
un modèle NATIONAL par fusion multi-source ; en pratique cette fusion est vide de
substance (marchés/NLP sans données honnêtes), et **toute la valeur empirique
réelle est venue du travail par circonscription (P7/P8) sur données réelles** —
qui n'était pas au plan.

## 3. Erreurs / dettes à corriger (par sévérité)

### 🔴 E1 — P5 est incohérent avec le reste du dépôt (à corriger)
`scripts/run_etape_P5_ml.py` §4 dit que la maille circonscription est un « schéma
de données cible (à collecter, **NON fourni ici**) » — **or ces données existent
maintenant** (`data/fr_pres2022_circo.csv`, 577 circos). Le texte est périmé, et
surtout **le ML par circonscription — l'objectif réel du plan pour P5 — n'a
jamais été construit**. Le « P5 » actuel n'est qu'un ML sur 11 élections
nationales (utile pour montrer le sur-ajustement, mais pas ce qui était visé).

### 🟠 E2 — La fusion/marchés/NLP ne « paient » pas (dette de conception)
Sur tout l'historique, la fusion = 96 % fondamentaux (marchés/NLP forward-only,
0 donnée). Trois modules (`pp_fusion`, `pp_markets`, `pp_nlp`) + P2/P3/P4 sont
donc de la **machinerie en attente de données live** qui n'existent pas encore
(2027 sans marché liquide). Ce n'est pas faux, mais c'est ~40 % du code qui ne
produit aujourd'hui aucun résultat vérifiable.

### 🟠 E3 — La seule donnée encore approximative alimente le seul modèle « actif »
`data/fr_fundamentals.csv` (croissance, chômage, **approbation**) est
« approximatif, à dire d'expert », non sourcé ligne à ligne. Or c'est la SEULE
entrée du seul prédicteur national qui tourne (fondamentaux). Toute la prévision
2027 (P6) en dépend. À remplacer par des séries INSEE/baromètres datées — d'autant
qu'on sait désormais récupérer du réel sur data.gouv.

### 🟡 E4 — Deux univers déconnectés
Le modèle national (P1–P6, niveau camp/2 tours) et le réel par circonscription
(P7/P8, niveau parti) **ne communiquent pas** : la carte réelle 2022 n'alimente
ni la fusion, ni la prévision 2027. Le projet est de facto **deux demi-projets**.

### 🟡 E5 — Objectif « économie de tokens » abandonné après la Vague 1
Le méta-objectif du plan (sous-agents + tiering Haiku/Sonnet/Opus) n'a servi que
P1–P3. Tout le reste (audit, corrections, P6–P8) a tourné sur Opus seul.
Défendable (ce travail exigeait de la rigueur, et les sous-agents avaient
justement introduit le hindsight), mais c'est un écart assumé au plan.

### 🟡 E6 — « Hybride live » à moitié réel
Le fetch marchés interroge vraiment Polymarket (bien), mais renvoie toujours None
(pas de marché mappé) ; le fetch Trends (NLP) reste un stub non câblé. L'« hybride
live » n'est donc réel qu'à moitié.

### 🟢 Points sains vérifiés
Discipline OOS (train sur passé strict) ; `sd` fondamentaux honnêtement calibré
(×1.5 + plancher 0.05) ; `pp_ml` correct (features fondamentales, cas mono-classe
géré) ; parsing des données réelles validé au centième ; aucun chiffre périmé
(« 0.368 », « 0.14/86 % ») ne subsiste hors contexte de correction ; non-
identifiabilité des reports correctement refusée (P8).

## 4. Bilan : gagné / perdu

**Gagné (au-delà du plan)** :
- Une **discipline d'honnêteté** (audit hindsight) qui a évité de publier des
  chiffres faux (« fusion 0.14/86 % »).
- Des **données réelles** (2017/2022 T1, 2022 T2 par circo, niveau parti, **LFI
  explicite**), validées.
- Un **résultat de skill réel** : la régression de circonscription bat le swing
  uniforme 2017→2022 (MAE 1.19 vs 1.78).
- Une **leçon méthodo solide** : sophisme écologique (reports non identifiables).
- Une **prévision 2027** honnête (≈ 50/50, incapacité assumée à nommer le vainqueur).

**Perdu / non réalisé** :
- Le **ML par circonscription** (l'ambition réelle de P5) — jamais construit,
  alors que les données existent désormais.
- La **fusion multi-source vivante** — inerte faute de données non-hindsight.
- L'**intégration national ↔ circonscription** — les deux moitiés ne se parlent pas.
- L'**économie de tokens** — objectif transverse abandonné en cours de route.
- Le **NLP** — jamais validé sur quoi que ce soit (0 donnée honnête).

## 5. Recommandation pour repartir sur de bonnes bases

Ordre de correction proposé (du plus rentable au moins) :
1. **E1** : réécrire P5 pour brancher le ML sur les **vraies circonscriptions**
   (2017→2022, features par circo) — l'ambition initiale, désormais faisable, et
   c'est là qu'est le signal (P7 l'a montré : erreur divisée par ~2).
2. **E4** : connecter les deux univers — la carte réelle par circo devient le
   substrat de désagrégation d'une prévision nationale (P6/P4) → projection sièges.
3. **E3** : remplacer `fr_fundamentals.csv` par des séries sourcées et datées.
4. **E2/E6** : assumer marchés/NLP comme *purement 2027-live* (les sortir des
   étapes historiques), ou les câbler pour de vrai quand une donnée existe.
5. **E5** : décider explicitement si on ré-active le tiering de modèles pour la
   suite (les tâches mécaniques restantes — loaders, parsing — s'y prêtent).

---

## 6. Résolution appliquée (itération suivante)

Tous les incidents traités en une passe (itération + un sous-agent Sonnet en
parallèle pour E2/E6). Nouveau plan = **retour à l'ambition du plan (ML par
circonscription) là où la significativité est atteignable**.

| Incident | Statut | Ce qui a été fait |
|---|---|---|
| 🔴 E1 | **résolu** | `src/pp_circo_ml.py` + `run_etape_P9` : GB par circo, CV 5-fold, **bat le swing uniforme, p ≈ 0 sur 5094 préd., significatif pour les 9 partis** (MAE 1.78→0.56). Le ML par circonscription du plan existe enfin, sur données réelles, **statistiquement significatif**. |
| 🟠 E2/E6 | **résolu** | marchés/NLP reformulés en « échafaudage 2027-live, 0 skill démontrée » ; distinction honnête fetch Polymarket réel (mais None) vs stub Trends non câblé. |
| 🟠 E3 | **atténué** | en-tête `fr_fundamentals.csv` : sourçage par colonne (growth/chômage réels, approval reconstruite) ; assumé comme TODO faible-ROI, le national étant désormais secondaire. |
| 🟡 E4 | **amorcé** | `project_national_to_circos` : désagrégation national→circos (projection de sièges) ; national et local connectés. |
| 🟡 E5 | **adressé** | tiering ré-activé : sous-agent Sonnet pour E2/E6 pendant qu'Opus construit E1/E4. |

**Bascule statistique** : le projet a désormais **une brique significative** (P9,
n=5094, p≈0), là où le national restera à jamais non-significatif (n=11). Le
centre de gravité assumé est la **circonscription sur données réelles**.

**Reste ouvert (prochaine itération)** : covariables socio-éco INSEE par circo →
régression de Dirichlet compositionnelle ; plusieurs transitions (ajouter 2012)
pour passer du *downscaling* à une vraie prévision inter-scrutins.
