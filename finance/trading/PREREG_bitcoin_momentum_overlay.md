# Pré-enregistrement — Momentum du Bitcoin comme jauge de sentiment de risque, overlay défensif

**Committé AVANT tout calcul.** Cycle #344 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le Bitcoin (première crypto-monnaie par capitalisation) s'est
progressivement établi depuis 2020 comme un actif "risk-on" à bêta
élevé, dont les mouvements de prix sont documentés comme fortement
corrélés au sentiment de risque global des marchés actions, en
particulier les valeurs technologiques (ex. Baur & Dimpfl 2021, "The
volatility of Bitcoin and its role as a medium of exchange and a
store of value"). Une chute abrupte du prix du Bitcoin (momentum
négatif) est documentée comme un signal précoce de désendettement
("de-risking") généralisé sur les actifs spéculatifs, souvent
antérieur ou concomitant à un repli plus large des indices actions
(ex. mai 2021, novembre 2021-2022 pré-krach tech).

**Distinct de la sous-famille corrélation cross-marché DÉJÀ FERMÉE
dans ce backlog** (#90 intra-titre FAIL de justesse, #193 NDX-DAX PASS
niveau 1/FAIL Règle 9, #196 NDX-Russell FAIL — clôture EXPLICITEMENT
déclarée au PREREG du #196, "pas le début d'une recherche systématique
sur toutes les paires possibles"). **Ce cycle NE ROUVRE PAS cette
sous-famille** : il ne s'agit pas d'une corrélation glissante entre
deux séries de rendements, mais d'un signal de NIVEAU/MOMENTUM sur le
prix d'un actif tiers observable directement — même famille
méthodologique que la force du dollar (#198), le pétrole (#283), le
cuivre (#284) ou le gaz naturel (#326), qui utilisent tous un
`log(prix(t)/prix(t-21))` comme signal, jamais une corrélation.

**Première utilisation d'une CLASSE D'ACTIF entièrement nouvelle dans
ce backlog** (crypto-actif), distincte de toutes les catégories
déjà testées (macro FRED, options sur indice, matières premières
traditionnelles, taux, crédit).

## 2. Données

**Nouvelle donnée à récupérer** : série FRED `CBBTCUSD` (Coinbase
Bitcoin, prix de clôture quotidien en USD), gratuite, depuis le
01/12/2014, disponibilité déjà vérifiée par fetch de test (HTTP 200,
4266 valeurs jusqu'au 05/08/2026). **Limite reconnue à l'avance** :
35 valeurs manquantes et 3 écarts >3 jours calendaires détectés dans
la série brute (le Bitcoin trade en continu 24/7, ces trous sont donc
probablement des lacunes de collecte de la source, pas des jours de
marché fermé) — traités par ffill comme toutes les autres séries
externes de ce backlog (Règle 7), pas un bug.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe : jauge de
sentiment de risque globale, appliquée uniformément.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `BTC_mom(t) = log(BTC(t)/BTC(t-21))` (**RET_WINDOW=21 réutilisé à
  l'identique** des #198/#283/#284/#326, Règle 7). BTC aligné sur le
  calendrier de chaque marché actions par `ffill` (BTC trade tous les
  jours calendaires, les indices actions non).
- Alignement causal `shift(1)` supplémentaire (Règle 7 standard).
- Seuil : **tercile EXPANDING** de `BTC_mom_lag(t)`.
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `BTC_mom_lag(t)` est dans son tercile expanding le PLUS BAS
  (Bitcoin en repli marqué sur 21 jours, proxy de désendettement
  spéculatif généralisé), `1,0x` sinon. **Jamais de levier**. Coûts
  5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, un critère
multi-marché figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : le mécanisme économique est documenté
et plausible, mais l'historique disponible (2014+, réellement
utilisable ~2015+) est le PLUS COURT de toute construction testée dans
ce backlog après troncature — troncature sévère attendue sur
NDX/Russell 2000/S&P 500 (historiques longs), limite reconnue à
l'avance et non un signe de biais. Résultat rapporté tel quel, sans
retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. **Historique le plus court du backlog** (~11 ans utilisables) —
   puissance statistique réduite, risque de sur-influence d'un petit
   nombre d'épisodes (2018, 2022) sur le tercile expanding.
2. Le régime de corrélation BTC-actions tech n'est PAS stable dans le
   temps (quasi nulle avant 2020, montée nette 2020-2022, plus
   ambiguë ensuite) — un signal supposé stable sur toute la fenêtre
   pourrait être structurellement non stationnaire, limite reconnue à
   l'avance (distincte du risque de bug).
3. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
4. Les 35 valeurs manquantes/écarts de la série brute pourraient
   introduire un bruit de ffill localisé, sans configurer une fuite
   (vérifié à l'audit).
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_bitcoin_momentum_overlay_backtest.py`,
`scripts/nonml_bitcoin_momentum_overlay_audit.py`,
`results/nonml_bitcoin_momentum_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
