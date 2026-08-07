# Pré-enregistrement — Volatilité implicite du marché pétrolier (indice OVX), overlay défensif

**Committé AVANT tout calcul.** Cycle #359 du backlog non-ML.

## 1. Contexte, hypothèse et distinctions explicites avec les familles déjà closes

**Nouvelle découverte** : l'indice OVX (CBOE Crude Oil ETF Volatility
Index — volatilité implicite des options sur l'ETF pétrolier USO,
équivalent du VIX pour le marché du pétrole brut) est disponible
gratuitement via Yahoo Finance (`^OVX`), **jamais recherché ni mentionné
auparavant dans ce backlog** (vérifié par grep exhaustif — contrairement
à GVZ, VVIX, VXDCLS, explicitement nommés et déclinés à la clôture
formelle de la famille VIX-dérivés au #346).

**Distinction 1 — avec la famille VIX-dérivés equity, close à 0/4**
(niveau #130, VRP #191, structure par terme #340, SKEW #341, clôture
formelle après le #346) : ces 4 constructions mesurent TOUTES la
volatilité implicite d'options sur INDICE ACTIONS (S&P 500). **OVX
mesure la volatilité implicite d'options sur le PÉTROLE BRUT** — classe
d'actif sous-jacente entièrement différente (matière première
énergétique, pas actions), documentée comme baromètre de stress
géopolitique/énergétique (guerre du Golfe 1990, crise financière 2008,
guerre des prix pétroliers 2020, invasion de l'Ukraine 2022) plutôt que
la prime de risque actions.

**Distinction 2 — avec le pétrole déjà testé comme PRIX (#283, FAIL,
famille valeur-refuge/matières premières close à 0/7)** : le #283
testait le MOMENTUM du prix spot du pétrole (tendance directionnelle).
**OVX mesure l'INCERTITUDE implicite dans les options** (volatilité
future anticipée par le marché des dérivés), un mécanisme économique
fondamentalement distinct (jauge de peur/stress vs signal de tendance)
— même distinction déjà validée entre le prix de l'or (#348, momentum,
FAIL 3/5) et une éventuelle volatilité de l'or (jamais testée, GVZ
explicitement décliné au #346 sans hypothèse nouvelle à l'époque).

**Distinction 3 — avec le MOVE obligataire (#357, PASS 4/5, Règle 9 2/5)**
: même TYPE de construction (niveau brut d'un indice de volatilité
implicite, tercile expanding haut = défensif) mais sur une **3e classe
d'actif sous-jacente totalement différente** (matières premières
énergétiques, pas taux). Ce cycle teste si le mécanisme "volatilité
implicite comme jauge de stress" **généralise au-delà des taux** vers
une classe d'actif au comportement structurellement distinct (le
pétrole a des chocs d'offre exogènes — OPEP, géopolitique — sans
équivalent direct sur le marché obligataire).

**Engagement de bornage explicite (Règle anti-snooping)** : ce cycle
ouvre/étend une sous-famille "volatilité implicite inter-classes
d'actifs" (MOVE bonds #357 + OVX pétrole #359 ce cycle). **Cette
sous-famille sera bornée à 3 constructions maximum** — une 3e classe
d'actif (ex. change, `^EVZ`) pourra être testée à un prochain cycle
avec une déclaration de bornage explicite, mais AUCUNE 4e ne sera
testée sans hypothèse économique matériellement nouvelle, conformément
à la discipline déjà appliquée aux autres sous-méthodes (ratio de
force relative, bornée à 2 constructions au #354).

## 2. Données

**Nouvelle donnée** : indice `^OVX` via l'API publique Yahoo Finance
(même mécanisme de fetch que #348/.../#357), gratuit, quotidien depuis
le 10/05/2007, disponibilité déjà vérifiée par fetch de test (HTTP 200,
4841 valeurs jusqu'au 06/08/2026, 100% exploitables sans valeur `null`
détectée sur ce test — contrairement au MOVE, aucun problème de
fraîcheur de données constaté à ce stade, à confirmer au fetch complet).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe (jauge de
stress financier global, appliquée uniformément).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal `ffill+shift(1)` quotidien (Règle 7 standard,
  identique aux #130/#341/#357).
- Seuil : **tercile EXPANDING** de `OVX_lag(t)` sur le NIVEAU BRUT (pas
  de transformation en momentum — **construction réutilisée à
  l'identique du #357 MOVE/#341 SKEW/#291 NFCI**, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `OVX_lag(t)` est dans son tercile expanding le PLUS HAUT (stress
  pétrolier élevé, même direction "niveau élevé = défensif" que
  NFCI/STLFSI4/SKEW/MOVE), `1,0x` sinon. **Jamais de levier**. Coûts
  5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un niveau brut, un critère multi-marché
figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : le précédent MOVE (#357, PASS 4/5) est
encourageant pour la généralisation du mécanisme "volatilité implicite
= jauge de stress", mais le pétrole a une dynamique structurellement
différente (chocs d'offre exogènes, contango/backwardation, moins
directement lié à la politique monétaire qui affecte les indices
actions). Résultat rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le SKEW (#341, pire score de la famille VIX-dérivés), un
   indice de volatilité n'a pas nécessairement de niveau "neutre"
   stable dans le temps — un seuil expanding pourrait mal s'ancrer.
2. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
3. Le lien entre stress du marché pétrolier et stress des indices
   actions n'est pas garanti ni instantané — les chocs pétroliers
   peuvent être idiosyncratiques (choc d'offre géopolitique) sans
   se transmettre aux actions, contrairement au canal taux/actions
   plus direct du MOVE.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_oil_market_volatility_overlay_backtest.py`,
`scripts/nonml_oil_market_volatility_overlay_audit.py`,
`results/nonml_oil_market_volatility_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
