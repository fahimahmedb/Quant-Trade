# Étape P4 — Fusion bayésienne multi-source (présidentielle FR, deux tours)

## 1. Principe

On prédit un résultat électoral **sans sondage déclaratif**, en fusionnant trois familles de sources hétérogènes :

- **Fondamentaux** (P1) : régression structurelle économie-politique (croissance, chômage, approbation, ancienneté) — le *prior*.
- **Marchés de prédiction** (P2) : prix implicites dé-biaisés (favori-outsider).
- **NLP / sentiment** (P3) : proxy comportemental (notoriété, tonalité).

La fusion combine leurs estimations gaussiennes de la part 2nd tour par **pondération de précision en espace logit** (1/σ²), avec un prior diffus et un plancher d'incertitude anti-sur-confiance (on ne peut être plus certain que sa meilleure source unique). Voir `src/pp_fusion.py`.

## 2. Comparaison OOS — sources seules vs fusion

*Fenêtre expansive, entraînement sur le passé strict. **Correction d'audit** : les snapshots marchés/NLP rétrospectifs ont été SUPPRIMÉS (ils encodaient l'issue connue — cf. `results/AUDIT.md`). Ces deux sources sont désormais **réservées à la prévision live** (élections à venir) : sur tout l'historique 1965-2022 elles se déclarent indisponibles (n=0), ce qui est le comportement honnête attendu. La fusion historique se réduit donc au **prior fondamental**.*

| Prédicteur | n plis | Brier | Log-loss | Bonne issue |
|---|---|---|---|---|
| Fondamentaux | 7 | 0.295 | 0.909 | 57% |
| Marchés | 0 | indisponible (forward-only) | — | — |
| NLP | 0 | indisponible (forward-only) | — | — |
| Fusion | 7 | 0.294 | 0.892 | 57% |

*Brier : 0 = parfait, 0.25 = pile ou face. Marchés/NLP n'ayant plus de donnée historique honnête, leur valeur ne pourra être mesurée que sur des scrutins **futurs** (2027), où aucun hindsight n'est possible par construction.*

## 3. Détail de la fusion, élection par élection

| Année | Référence | Part prévue | P(victoire) | Part réelle | Issue | Poids dominant |
|---|---|---|---|---|---|---|
| 1988 | mitterrand_1988 | 0.576 | 0.94 | 0.540 | ✓ gagne ✓ | fundamentals 99% |
| 1995 | jospin_1995 | 0.490 | 0.42 | 0.474 | ✗ perd ✓ | fundamentals 99% |
| 2002 | chirac_2002 | 0.466 | 0.25 | 0.822 | ✓ gagne ✗ | fundamentals 99% |
| 2007 | sarkozy_2007 | 0.564 | 0.74 | 0.531 | ✓ gagne ✓ | fundamentals 96% |
| 2012 | sarkozy_2012 | 0.649 | 0.95 | 0.484 | ✗ perd ✗ | fundamentals 96% |
| 2017 | hamon_2017 | 0.392 | 0.14 | — (éliminé T1) | ✗ perd ✓ | fundamentals 96% |
| 2022 | macron_2022 | 0.483 | 0.43 | 0.586 | ✓ gagne ✗ | fundamentals 96% |

## 4. Lecture des contributions

- **1988** : fundamentals 99%, prior 1%
- **1995** : fundamentals 99%, prior 1%
- **2002** : fundamentals 99%, prior 1%
- **2007** : fundamentals 96%, prior 4%
- **2012** : fundamentals 96%, prior 4%
- **2017** : fundamentals 96%, prior 4%
- **2022** : fundamentals 96%, prior 4%

## 5. Provenance des données — correction d'audit appliquée

✅ **Correction effectuée** (cf. `results/AUDIT.md`). Un premier jet avait backtesté marchés et NLP sur des snapshots **rédigés en connaissant l'issue** (hindsight), gonflant artificiellement la fusion (Brier apparent 0.14). Ces données rétrospectives ont été **supprimées** :

- Marchés/NLP ne portent plus AUCUNE donnée historique → indisponibles sur les 7 plis (forward-only). La fusion historique = prior fondamental, dont le score honnête est **Brier ≈ 0.30, bonne issue ≈ 57 %** — et qui, à n=7, ne bat même pas nettement une heuristique « avantage sortant » (cf. Étape P1).
- La thèse « fusion multi-source > source seule » (littérature : marchés de prédiction souvent > fondamentaux) reste **plausible mais NON démontrée ici** ; elle ne pourra l'être que sur des scrutins futurs avec de vraies données horodatées (prévision 2027).

## 6. Limites (honnêteté méthodologique)

- **Échantillon minuscule** : 11 présidentielles, 7 plis OOS. Aucun chiffre n'est significatif au sens statistique ; ce sont des ordres de grandeur.
- **Données approximatives** : macro agrégées, prix de marché et features NLP illustratifs (2017/2022 pour les marchés, 2007+ pour le NLP). À remplacer par des séries primaires sourcées avant tout usage réel.
- **2017 = réalignement** : les fondamentaux ratent Macron ; seule la disponibilité d'autres sources (le cas échéant) corrige le prior.
- **Indépendance supposée** : la fusion suppose des sources non corrélées ; le plancher d'incertitude en tient compte grossièrement, pas exactement.
- **Anti-snooping** : univers de prédicteurs et calibrations figés AVANT lecture des scores ; fiabilités a priori égales, non ajustées sur le test.
