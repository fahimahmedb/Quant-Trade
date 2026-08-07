# Pré-enregistrement — Volatilité implicite du marché obligataire (indice MOVE), overlay défensif

**Committé AVANT tout calcul.** Cycle #357 du backlog non-ML.

## 1. Contexte, hypothèse et distinction avec la famille VIX-dérivés déjà close

**Nouvelle découverte** : l'indice MOVE (ICE BofA Merrill Lynch
Option Volatility Estimate — mesure de la volatilité implicite des
options sur bons du Trésor US, l'équivalent du VIX pour le marché
obligataire) est disponible gratuitement via Yahoo Finance (`^MOVE`),
**jamais recherché ni mentionné auparavant dans ce backlog** (vérifié
par grep exhaustif).

**Distinction explicite avec la famille VIX-dérivés close à 0/4**
(niveau #130, VRP #191, structure par terme #340, SKEW #341, famille
formellement déclarée close après le #346) : ces 4 constructions
mesurent TOUTES la volatilité implicite d'options sur INDICE ACTIONS
(S&P 500). **MOVE mesure la volatilité implicite d'options sur BONS DU
TRÉSOR** — une classe d'actifs sous-jacente entièrement différente
(taux d'intérêt, pas actions), reflétant l'incertitude de politique
monétaire/trajectoire des taux plutôt que la prime de risque actions.
Documenté comme précurseur de stress financier plus large à plusieurs
reprises (pic en 2008, mars 2020, mars 2023 lors de la crise
bancaire régionale US) — **jamais testé dans ce backlog sous quelque
forme que ce soit**, ce n'est donc pas une réouverture de la famille
close mais une catégorie authentiquement nouvelle (volatilité du
marché des TAUX, pas des ACTIONS).

## 2. Données

**Nouvelle donnée** : indice `^MOVE` via l'API publique Yahoo Finance
(même mécanisme de fetch que #348/.../#356), gratuit, quotidien depuis
le 11/08/2011, disponibilité déjà vérifiée par fetch de test (HTTP
200, 3767 valeurs exploitables jusqu'au 05/08/2026 — la dernière
observation du jour courant est parfois `null`/manquante en fin de
journée avant clôture officielle, traitée comme NaN standard, aucun
biais).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe (jauge de
stress financier global, appliquée uniformément).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal `ffill+shift(1)` quotidien (Règle 7 standard,
  identique aux #130/#341, aucun décalage de publication
  supplémentaire — indice calculé et publié en continu).
- Seuil : **tercile EXPANDING** de `MOVE_lag(t)` sur le NIVEAU BRUT
  (pas de transformation en momentum — **construction réutilisée à
  l'identique du #341 SKEW/#291 NFCI**, Règle 7, un indice de
  volatilité/stress n'a pas de "croissance" économiquement
  significative, seul le niveau compte).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `MOVE_lag(t)` est dans son tercile expanding le PLUS HAUT (stress
  obligataire élevé, même direction "niveau élevé = défensif" que
  NFCI/STLFSI4/SKEW), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps
  (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un niveau brut, un critère multi-marché
figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : mécanisme économiquement distinct et
documenté (précurseur de stress financier via le canal des taux), mais
appartient à la même famille large "indice de volatilité implicite
comme jauge de stress" dont AUCUNE variante (côté actions) n'a encore
atteint le seuil renforcé dans ce backlog. Résultat rapporté tel quel,
sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le SKEW (#341, pire score de la famille VIX-dérivés), un
   indice de volatilité n'a pas nécessairement de niveau "neutre"
   stable dans le temps — un seuil expanding pourrait mal s'ancrer,
   même risque déjà documenté.
2. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
3. La transmission d'un choc de volatilité obligataire vers les
   actions n'est pas instantanée ni garantie — risque de décalage
   temporel similaire à celui documenté pour l'inversion de courbe des
   taux (#187).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_bond_market_volatility_overlay_backtest.py`,
`scripts/nonml_bond_market_volatility_overlay_audit.py`,
`results/nonml_bond_market_volatility_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
