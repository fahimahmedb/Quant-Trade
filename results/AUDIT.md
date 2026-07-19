# Audit honnête du module « Prédiction politique »

Auto-audit demandé après livraison. Objectif : dire ce qui tient, ce qui ne
tient pas, et ce qui a été corrigé. Écrit sans complaisance.

## Verdict en une phrase

**L'architecture et la plomberie anti-data-snooping sont saines ; les métriques
publiées (« fusion Brier 0.14 / 86 % ») sont TROMPEUSES parce que deux des trois
sources reposent sur des données construites A POSTERIORI, en connaissant le
résultat.** Le seul chiffre défendable est celui des fondamentaux seuls, et il
est faible — comme la théorie le prédit à n≈11.

---

## 1. La faille majeure : contamination par rétrospective (hindsight)

Les instantanés `data/fr_markets_snapshot.json` et `data/fr_nlp_snapshot.csv`
ont été **rédigés en connaissant l'issue des élections** (par les sous-agents et
moi). Exemples :

- Marchés : `p(Macron 2017)=0.87`, `p(Macron 2022)=0.74` — écrits en sachant que
  Macron a gagné deux fois.
- NLP : `ref_trends_share(2012)=0.47` (Sarkozy < Hollande) — écrit en sachant que
  Sarkozy a perdu.

Le backtest à fenêtre expansive (`src/pp_backtest.py`) est **correctement
implémenté** : il n'entraîne jamais sur le futur. Mais **il ne peut pas laver une
donnée qui encode déjà le futur dans sa valeur**. Résultat : le score « OOS » des
marchés (Brier 0.000) et du NLP (0.063) mesure un **ajustement rétrospectif**,
pas une compétence prédictive réelle.

### Preuve par la disponibilité des sources

| Année testée | Fondamentaux (exogène) | Marchés | NLP |
|---|---|---|---|
| 1988 | ✓ | — | — |
| 1995 | ✓ | — | — |
| 2002 | ✓ | — | — |
| 2007 | ✓ | — | ✓ (rétrospectif) |
| 2012 | ✓ | — | ✓ (rétrospectif) |
| 2017 | ✓ | ✓ (rétrospectif) | ✓ (rétrospectif) |
| 2022 | ✓ | ✓ (rétrospectif) | ✓ (rétrospectif) |

Les deux calls spectaculaires de la fusion (2017, 2022, `P(victoire)≈0.98`) sont
**exactement** ceux où les marchés — donnée rétrospective — dominent la
pondération (66 % et 71 %). Le gain de la fusion (Brier 0.37 → 0.14) est donc en
grande partie un **artefact de rétrospective**, pas une vraie découverte.

### Le seul chiffre honnête

Les fondamentaux utilisent des données **exogènes au scrutin** (croissance,
chômage INSEE ; popularité mesurée indépendamment du vote). C'est la seule source
non contaminée — et la plus faible :

| Prédicteur | n plis | Brier | Log-loss | Bonne issue |
|---|---|---|---|---|
| Fondamentaux seuls (HONNÊTE) | 7 | **0.368** | 1.114 | **57 %** |
| Sous-ensemble pré-2007 (fond. seuls, aucune source rétrospective) | 3 | 0.251 | 0.674 | 67 % |
| Fusion toutes sources (CONTAMINÉE) | 7 | 0.139 | 0.409 | 86 % |

Un taux de bonne issue de 57 % sur 7 élections n'est statistiquement **pas
distinguable du hasard**. C'est le résultat réel et attendu : prédire une
présidentielle avec un modèle structurel sur n≈11 est intrinsèquement peu fiable.

### Nuance (pour ne pas sur-corriger)

La littérature (Wolfers & Zitzewitz ; Snowberg & Wolfers) montre que les
**vrais** marchés de prédiction battent souvent les fondamentaux. Donc avec de
**vraies** données de marché horodatées, un gain de fusion serait plausiblement
réel. Le problème n'est pas la thèse — c'est que **CES chiffres-ci ne peuvent pas
la démontrer**, faute de données de provenance propre.

---

## 2. Ce qui est SAIN (vérifié)

- **Discipline OOS** : `run_oos` entraîne sur `ex[:i]` (années strictement
  antérieures, tri par année sans ex-æquo). Aucune fuite de code détectée.
- **Standardisation / résidus fondamentaux** : estimés sur l'entraînement seul.
- **`fit()` no-op des marchés, `scale_` du NLP** : calibrations bornées, sur le
  passé strict — corrects au niveau logique.
- **Aucune requête réseau bloquante** : `_fetch_live` (marchés/NLP) échoue
  proprement et retombe sur snapshot. Reproductible hors-ligne.
- **Fusion** : pondération par précision en logit, avec un plancher
  d'incertitude anti-sur-confiance (corrigé pendant le développement : sans lui,
  `P(victoire)` saturait à 1.000). Mécaniquement correcte.
- **P5 ML** : montre honnêtement le sur-ajustement (GB/XGBoost log-loss > 3 à
  n≈11). Pas de donnée synthétique présentée comme réelle.

## 3. Faiblesses secondaires (documentées, non corrigées)

- **Choix `reference_id = Macron 2017`** : le traiter en « continuité/sortant »
  et lui coller l'impopularité de Hollande (approbation 20) est discutable ; le
  camp sortant réel (PS/Hamon) a été éliminé au 1er tour. Choix documenté, mais
  il pénalise artificiellement le prior fondamental en 2017.
- **Variables macro approximatives** pour les élections anciennes (approbation
  surtout). Ordres de grandeur publics, pas des séries auditées.
- **n = 7 plis OOS** : tout écart de Brier < ~0.1 est du bruit.

## 4. Ce qui a été corrigé suite à l'audit

1. **README « Résultat clé » réécrit** : ne met plus en avant « 0.14 / 86 % »
   comme une compétence ; annonce d'emblée la contamination et le chiffre
   honnête (fondamentaux 0.37 / 57 %).
2. **`results/etape_P4_fusion.md`** : ajout d'une section « Audit de provenance »
   en tête des limites, avec le tableau de disponibilité.
3. **Snapshots** : `_meta`/en-têtes renforcés — mention explicite que les valeurs
   sont RÉTROSPECTIVES et invalident toute interprétation de skill OOS.

## 5. Ce qu'exigerait un vrai correctif (hors périmètre offline)

- Des **prix de marché horodatés** réels (archives Betfair/PredictIt/Polymarket)
  capturés AVANT chaque scrutin — impossible à garantir hors ligne sans risque de
  re-fabriquer du hindsight.
- Des **exports Google Trends / presse** datés d'avant chaque 2nd tour.
- Un jeu **par circonscription** (législatives) pour donner au ML les effectifs
  qui manquent (schéma documenté dans `scripts/run_etape_P5_ml.py`).

Tant que ces données ne sont pas branchées, le module doit être présenté comme
une **démonstration de pipeline**, et la seule métrique de compétence citable
est celle des fondamentaux (faible, honnête).
