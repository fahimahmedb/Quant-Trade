# Pré-enregistrement — Momentum de l'Ethereum, overlay défensif

**Committé AVANT tout calcul.** Cycle #346 du backlog non-ML.

## 1. Déclaration explicite de la tension avec la classe d'actif crypto (Règle 2, transparence, discipline anti-snooping)

Le Bitcoin (#344) a produit un PASS NET 5/5 — le meilleur profil brut
de session avec le CPI (#338). L'univers des crypto-actifs candidats
est potentiellement immense (des milliers de "coins") : tester
systématiquement chaque nouvelle crypto-monnaie disponible librement
constituerait une recherche combinatoire non bornée, contraire à
`PROTOCOLE_ANTI_SNOOPING.md` — le risque a été explicitement signalé
au #345.

**Décision et engagement pris ici, avant tout calcul** : ce cycle
teste l'Ethereum (2e crypto-actif par capitalisation, mécanisme
économique DISTINCT du Bitcoin — plateforme de contrats intelligents/
finance décentralisée, pas seulement une "réserve de valeur" comme le
Bitcoin est généralement présenté) car (a) il s'agit d'un actif
majeur, pas un choix arbitraire dans la longue traîne des milliers de
coins, et (b) le mécanisme économique diffère suffisamment pour
constituer un test distinct plutôt qu'une simple redite. **Quel que
soit le résultat, ce cycle CLÔT la classe d'actif crypto à 2
constructions (Bitcoin #344, Ethereum #346) — aucune 3e crypto-monnaie
ne sera testée sans nouvelle hypothèse économique clairement
distincte** (même discipline de bornage que celle déjà appliquée à la
sous-famille corrélation cross-marché après le #196 et au canal
inflation après le #343).

## 2. Données

**Nouvelle donnée à récupérer** : série FRED `CBETHUSD` (Coinbase
Ethereum, prix de clôture quotidien en USD), gratuite, depuis le
18/05/2016, disponibilité déjà vérifiée par fetch de test (HTTP 200,
3732 valeurs jusqu'au 05/08/2026). **Historique encore plus court que
le Bitcoin** (~10 ans utilisables contre ~11 ans pour BTC), limite
reconnue à l'avance.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le #344.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier — STRICTEMENT IDENTIQUE au #344)

Construction IDENTIQUE au #344 (Règle 7), seule la série change :

- `ETH_mom(t) = log(ETH(t)/ETH(t-21))` (**RET_WINDOW=21 réutilisé à
  l'identique** des #198/#283/#284/#326/#344), ETH aligné sur le
  calendrier de chaque marché actions par `ffill`.
- Alignement causal `shift(1)` supplémentaire (Règle 7 standard).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `ETH_mom_lag(t)` est dans son tercile expanding le PLUS BAS (repli
  marqué de l'Ethereum, même direction que le #344), `1,0x` sinon.
  **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une construction strictement identique au
#344 sur une série différente, un critère multi-marché figé, aucun
balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : construction IDENTIQUE au #344 (PASS),
ce qui pourrait suggérer un PASS probable — mais comme le T5YIFR
(#343, FAIL malgré une construction identique au #200 PASS) et le PPI
(#339, FAIL malgré une construction identique au CPI #338 PASS)
l'ont déjà montré à deux reprises dans ce backlog, une construction
identique NE GARANTIT PAS un résultat identique d'un actif à l'autre
au sein d'une même classe. Résultat rapporté tel quel, sans retuning
après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Historique encore plus court que le Bitcoin — puissance
   statistique réduite plus sévèrement.
2. Ethereum est historiquement PLUS volatil et plus corrélé aux
   cycles spéculatifs "altcoins" que le Bitcoin (qui bénéficie d'un
   statut de "valeur refuge crypto" relatif) — le signal pourrait être
   plus bruyant.
3. Comme démontré 2 fois dans ce backlog (PPI/T5YIFR), une
   construction identique ne généralise pas automatiquement entre
   deux séries proches économiquement.
4. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_ethereum_momentum_overlay_backtest.py`,
`scripts/nonml_ethereum_momentum_overlay_audit.py`,
`results/nonml_ethereum_momentum_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
