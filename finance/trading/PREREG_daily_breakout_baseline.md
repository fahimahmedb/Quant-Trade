# Pré-enregistrement — Stratégie A : Daily Breakout (baseline, trades discrets)

**Committé AVANT tout calcul, AVANT le script de backtest.** Stratégie
demandée explicitement par l'utilisateur (specs fournies telles quelles,
hors du backlog non-ML habituel), désignée « Stratégie A — baseline »
dans l'échange. Contrairement à toutes les stratégies du backlog testées
jusqu'ici (overlays à exposition continue 0–2x sur le rendement B&H),
c'est un système de **trades discrets** (entrée/stop/cible/sortie), donc
un moteur de simulation différent, écrit ici pour la première fois.

## Spécification (fixée telle que fournie par l'utilisateur, aucun paramètre
ajusté après avoir vu un résultat)

- **Sens** : long uniquement, une seule position ouverte à la fois
  (trivial ici : un seul instrument).
- **Filtre tendance** : `close(t) > SMA50(t)`.
- **Filtre breakout** : `close(t) > max(high[t-20 .. t-1])` — plus haut
  glissant des 20 séances **précédant** t (fenêtre décalée d'un jour,
  aujourd'hui exclu — lecture littérale de « plus haut des 20 séances
  précédentes »). Basé sur le HIGH (niveau de breakout), comparé au CLOSE
  (confirmation), convention standard.
- **Filtre RSI** : `50 ≤ RSI14(t) ≤ 75` (RSI de Wilder, `prediction.py::_rsi`,
  réutilisé tel quel — même implémentation que partout ailleurs dans le repo).
- **Signal d'entrée jour t** = les 3 filtres réunis, ET aucune position
  ouverte à la clôture de t. Décision prise avec les données disponibles
  jusqu'à la clôture de t inclus (aucune donnée future).
- **Entrée** : à l'ouverture de t+1 (`open(t+1)`).
- **ATR** : ATR14 de Wilder (`prediction.py::_atr`), mesuré à la clôture
  du jour du signal t, **figé à l'entrée** (non recalculé ensuite).
- **Stop** = `entry_price − 1.5 × ATR14(t)`.
- **Take profit** = `entry_price + 3.0 × ATR14(t)` (= 2R, R = 1,5×ATR,
  cohérent avec l'énoncé « TP = 3 ATR = 2R »).
- **Gestion intra-trade** (données quotidiennes OHLC uniquement, aucune
  donnée intrajournalière disponible dans ce repo) : chaque jour à partir
  du jour d'entrée inclus, si `low(t) ≤ stop` ET `high(t) ≥ TP` le **même
  jour** → **stop prioritaire** (règle explicite de l'utilisateur,
  hypothèse conservatrice, l'ordre intrajournalier réel étant inconnu).
  Si seul le stop est touché → sortie au prix du stop. Si seul le TP est
  touché → sortie au prix du TP. Sinon la position continue. Si le stop
  ou le TP peut être touché dès le jour d'entrée (mouvement fort à
  l'ouverture), la même règle s'applique (aucune donnée future utilisée,
  seulement l'OHLC du jour courant).
- **Dimensionnement** : risque = **0,5 % de l'equity courante** (capital
  composé — mark-to-market avant chaque entrée, pas 0,5 % du capital
  initial fixe) par trade. Unités = `(0,5 % × equity_avant_trade) /
  (1,5 × ATR14(t))`. **Hypothèse explicite et assumée** : instrument
  négociable de façon fractionnaire sans contrainte de notionnel/marge
  au-delà du risque (type CFD/future synthétique) — nécessaire car
  l'indice cote ~14 000–16 000 pts, très au-dessus du capital de
  5 000 € ; sans cette hypothèse on ne pourrait quasiment jamais entrer
  en position pleine notionnelle. Ce choix est documenté ici pour éviter
  toute ambiguïté a posteriori.
- **Capital initial** = 5 000 € (suivi d'equity ; conversion 1:1 points
  d'indice → euros, cohérent avec les simulations « 300 € » déjà
  utilisées ailleurs dans le repo).
- **Coûts de transaction** : **ajout méthodologique non présent dans le
  spec utilisateur original**, appliqué pour rester comparable au reste
  du repo — 5 bps du notionnel (unités × prix) à l'entrée, 5 bps du
  notionnel à la sortie (convention identique aux overlays du backlog :
  5 bps par transition). Déclaré ici avant tout calcul.
- **Position finale** : si une position reste ouverte à la fin de
  l'échantillon, elle est marquée au marché (mark-to-market) au dernier
  close disponible pour le calcul des métriques, **sans** coût de sortie
  fictif (le trade n'est pas réellement clos).
- **Sans levier au-delà de ce qui est induit par le sizing au risque**
  (pas de plafond de notionnel imposé, cf. hypothèse ci-dessus).
- **Aucun look-ahead** : tous les indicateurs (SMA50, breakout, RSI14,
  ATR14) n'utilisent que les données jusqu'à la clôture du jour évalué ;
  entrée au jour suivant.

## Univers et période

**Composite pré-enregistré** (`data/nasdaq_composite_daily.txt`, 5 ans,
1251 séances) — choix explicite de l'utilisateur pour ce premier test.
Échantillon testable = à partir de la 56e séance (marge de 5 séances
au-delà de l'amorçage SMA50, cohérent avec les marges de sécurité déjà
utilisées dans le repo pour les lissages EWM/SMA).

## Critère de succès (pré-enregistré, quantifié)

La Stratégie A est un **PASS** si, net de coûts, sur l'échantillon
testable, elle bat Buy & Hold **simultanément** en Sharpe annualisé ET
en rendement total — même critère « renforcé » que les autres
stratégies directionnelles du backlog (ex. `donchian_breakout_overlay`).
Sinon **FAIL**, rapporté honnêtement (le repo a déjà établi à l'Étape B
qu'aucun signal actif testé ne bat Buy & Hold sur le Composite — cette
Stratégie A n'a **aucune garantie** de faire mieux, et le contexte est
transparent : voir `CLAUDE.md`).

`n_trials=1` : tous les paramètres (fenêtres, multiplicateurs ATR,
bande RSI) viennent tels quels du spec utilisateur, fixés a priori,
aucune grille testée avant ce résultat.

## Robustesse (SI PASS uniquement, pas un retuning)

Grille de perturbation sur les paramètres NON centraux au critère lui-même
(le critère est « bat B&H en Sharpe+rendement », pas un seuil sur ces
paramètres) : fenêtre breakout 20j → {16, 24}, bande RSI [50,75] →
[45,80] et [55,70], multiplicateurs ATR (1,5/3,0) → ±20 % (1,2/2,4 et
1,8/3,6). Vérifie un plateau, pas un pic isolé. Rapporté tel quel.

## Anti-cheat

Ce fichier committé seul, avant `nonml_daily_breakout_baseline_backtest.py`.
Vérification via `nonml_anti_cheat_check.py daily_breakout_baseline`.
