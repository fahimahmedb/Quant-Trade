# Pré-enregistrement — Anticipation d'inflation à long terme (5 ans dans 5 ans), overlay défensif

**Committé AVANT tout calcul.** Cycle #343 du backlog non-ML.

## 1. Déclaration explicite de la tension avec le canal inflation déjà exploité (Règle 2, transparence, discipline anti-snooping)

Ce cycle traite une idée dont le risque de sur-exploitation d'un canal
déjà productif a été explicitement signalé à l'avance au #342 : le
canal inflation compte déjà 3 constructions (breakeven 10 ans #200
PASS, CPI réalisé #338 PASS, PPI réalisé #339 FAIL) — 2 PASS sur 3, le
meilleur taux de succès de toute la famille macro-externe défensive de
ce backlog. Tester une 4e variante du même canal comporte un risque
réel de recherche non bornée sur un filon déjà productif (contraire à
`PROTOCOLE_ANTI_SNOOPING.md`).

**Décision prise ici, avant tout calcul** : ce cycle teste le
`T5YIFR` (anticipation d'inflation à terme, 5 ans dans 5 ans) car il
mesure un concept économique authentiquement distinct des 3
constructions déjà testées — **l'ANCRAGE des anticipations à LONG
TERME**, une jauge suivie explicitement par la Réserve fédérale
elle-même comme indicateur de sa crédibilité de politique monétaire
(contrairement au breakeven 10 ans #200, qui mélange anticipations
court/moyen terme avec l'inflation immédiate ; contrairement au CPI/PPI
#338/#339, qui mesurent l'inflation RÉALISÉE, pas anticipée).

**Engagement pris à l'avance, quel que soit le résultat** : **ce cycle
CLÔT le canal inflation à 4 constructions, sans extension
supplémentaire sans nouvelle hypothèse économique clairement
distincte** — même discipline de bornage que celle déjà appliquée au
sous-thread combinaison (#332-#335, clôturé après 1 succès). Aucune
5e variante d'inflation ne sera proposée dans les prochains cycles sur
la seule base de ce filon productif.

## 2. Données

**Nouvelle donnée à récupérer** : série FRED `T5YIFR` (5-Year, 5-Year
Forward Inflation Expectation Rate), gratuite, quotidienne depuis le
02/01/2003 (même démarrage que `T10YIE` du #200, aucune troncature
supplémentaire par rapport au signal déjà PASS), disponibilité déjà
vérifiée par fetch de test (HTTP 200, 6156 valeurs jusqu'au
06/08/2026).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le #200 (anticipation d'inflation dérivée du marché
obligataire US, appliquée comme jauge macro globale).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal `ffill+shift(1)` identique au #200 (Règle 7,
  aucun nouveau paramètre).
- Seuil : **tercile EXPANDING** de `T5YIFR_lag(t)` (`expanding_tercile_cut_high`
  **réutilisée à l'identique du #200**, Règle 7 — structure de seuil
  IDENTIQUE, seule la série change).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `T5YIFR_lag(t)` est dans son tercile expanding le PLUS HAUT
  (anticipations d'inflation à long terme les plus désancrées à la
  hausse), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps
  (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une construction strictement identique au
#200 sur une série différente, un critère multi-marché figé, aucun
balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : construction structurellement IDENTIQUE
au #200 (PASS), ce qui pourrait suggérer un PASS probable par pure
similarité mécanique — mais le concept économique est différent
(ancrage long terme vs anticipation court-moyen terme mélangée à
l'inflation immédiate), et le CPI (#338, PASS) suivi du PPI (#339,
FAIL) a déjà montré dans ce backlog qu'une construction identique ne
garantit PAS un résultat identique d'une série d'inflation à l'autre.
Résultat rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le T5YIFR est par construction BEAUCOUP plus stable et moins
   volatil que le T10YIE (il lisse un horizon lointain) — un signal
   trop lisse pourrait manquer les points d'inflexion de marché à
   court terme, contrairement au breakeven 10 ans plus réactif.
2. Comme le PPI (#339) l'a montré, la généralisation d'une
   construction gagnante du canal inflation n'est PAS automatique
   d'une série à l'autre.
3. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_forward_inflation_expectation_overlay_backtest.py`,
`scripts/nonml_forward_inflation_expectation_overlay_audit.py`,
`results/nonml_forward_inflation_expectation_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
