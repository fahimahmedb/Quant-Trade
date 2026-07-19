# Étape P4 — Fusion bayésienne multi-source (présidentielle FR, deux tours)

## 1. Principe

On prédit un résultat électoral **sans sondage déclaratif**, en fusionnant trois familles de sources hétérogènes :

- **Fondamentaux** (P1) : régression structurelle économie-politique (croissance, chômage, approbation, ancienneté) — le *prior*.
- **Marchés de prédiction** (P2) : prix implicites dé-biaisés (favori-outsider).
- **NLP / sentiment** (P3) : proxy comportemental (notoriété, tonalité).

La fusion combine leurs estimations gaussiennes de la part 2nd tour par **pondération de précision en espace logit** (1/σ²), avec un prior diffus et un plancher d'incertitude anti-sur-confiance (on ne peut être plus certain que sa meilleure source unique). Voir `src/pp_fusion.py`.

## 2. Comparaison OOS — sources seules vs fusion

*Fenêtre expansive, entraînement sur le passé strict. Marchés (2017/2022) et NLP (2007+) ne sont scorés que là où ils existent ; la fusion, elle, exploite ce qui est disponible à chaque date.*

| Prédicteur | n | Brier | Log-loss | MAE part | Bonne issue |
|---|---|---|---|---|---|
| Fondamentaux | 7 | 0.368 | 1.114 | 0.130 | 57% |
| Marchés | 2 | 0.000 | 0.005 | 0.015 | 100% |
| NLP | 4 | 0.063 | 0.257 | 0.067 | 100% |
| Fusion | 7 | 0.139 | 0.409 | 0.071 | 86% |

*Brier : 0 = parfait, 0.25 = pile ou face. Comparer à effectif égal : la fusion et les fondamentaux couvrent les 7 plis ; marchés/NLP moins.*

## 3. Détail de la fusion, élection par élection

| Année | Référence | Part prévue | P(victoire) | Part réelle | Issue | Poids dominant |
|---|---|---|---|---|---|---|
| 1988 | mitterrand_1988 | 0.576 | 0.94 | 0.540 | ✓ gagne ✓ | fundamentals 99% |
| 1995 | jospin_1995 | 0.490 | 0.42 | 0.474 | ✗ perd ✓ | fundamentals 99% |
| 2002 | chirac_2002 | 0.466 | 0.25 | 0.822 | ✓ gagne ✗ | fundamentals 99% |
| 2007 | sarkozy_2007 | 0.537 | 0.69 | 0.531 | ✓ gagne ✓ | nlp 63% |
| 2012 | sarkozy_2012 | 0.473 | 0.36 | 0.484 | ✗ perd ✓ | nlp 60% |
| 2017 | macron_2017 | 0.593 | 0.99 | 0.661 | ✓ gagne ✓ | markets 66% |
| 2022 | macron_2022 | 0.583 | 0.98 | 0.586 | ✓ gagne ✓ | markets 71% |

## 4. Lecture des contributions

- **1988** : fundamentals 99%, prior 1%
- **1995** : fundamentals 99%, prior 1%
- **2002** : fundamentals 99%, prior 1%
- **2007** : nlp 63%, fundamentals 36%, prior 1%
- **2012** : nlp 60%, fundamentals 38%, prior 2%
- **2017** : markets 66%, nlp 22%, fundamentals 12%, prior 0%
- **2022** : markets 71%, nlp 21%, fundamentals 8%, prior 0%

## 5. Audit de provenance des données (lecture critique OBLIGATOIRE)

⚠️ **Les scores de cette page surestiment la compétence prédictive réelle.** Les instantanés marchés (`fr_markets_snapshot.json`) et NLP (`fr_nlp_snapshot.csv`) ont été rédigés en CONNAISSANT l'issue des élections (hindsight). Le backtest expansif n'entraîne jamais sur le futur, mais il ne peut pas laver une donnée qui encode déjà le résultat dans sa valeur.

- Marchés (Brier 0.000) et NLP (0.063) mesurent un **ajustement rétrospectif**, pas une prévision. Les deux calls confiants (2017/2022) sont exactement ceux où les marchés — donnée rétrospective — dominent la pondération.
- La **seule source exogène** (macro/popularité indépendantes du scrutin) est les **fondamentaux** : Brier **0.368**, bonne issue **57 %** — non distinguable du hasard à n=7. C'est le seul chiffre de compétence défendable.
- La thèse (fusion multi-source > source seule) reste plausible avec de VRAIES données de marché ; ces métriques-ci ne la démontrent simplement pas. Voir `results/AUDIT.md`.

## 6. Limites (honnêteté méthodologique)

- **Échantillon minuscule** : 11 présidentielles, 7 plis OOS. Aucun chiffre n'est significatif au sens statistique ; ce sont des ordres de grandeur.
- **Données approximatives** : macro agrégées, prix de marché et features NLP illustratifs (2017/2022 pour les marchés, 2007+ pour le NLP). À remplacer par des séries primaires sourcées avant tout usage réel.
- **2017 = réalignement** : les fondamentaux ratent Macron ; seule la disponibilité d'autres sources (le cas échéant) corrige le prior.
- **Indépendance supposée** : la fusion suppose des sources non corrélées ; le plancher d'incertitude en tient compte grossièrement, pas exactement.
- **Anti-snooping** : univers de prédicteurs et calibrations figés AVANT lecture des scores ; fiabilités a priori égales, non ajustées sur le test.
