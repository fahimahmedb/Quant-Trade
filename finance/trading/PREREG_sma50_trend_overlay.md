# Pré-enregistrement — Overlay levé filtre de tendance SMA50 (moyen terme)

**Committé AVANT tout calcul.** Cycle #60 du backlog non-ML. Teste un
signal de tendance à horizon INTERMÉDIAIRE entre les signaux courts qui
ont échoué (MACD #36, Donchian-20 #40, ~12-26j) et les signaux longs qui
ont réussi (SMA200 #29, 52w-high #37, ~200-252j) : SMA50 seul (≈10
semaines), sans la comparaison SMA50>SMA200 déjà testée au golden cross
(#34, qui combine deux moyennes).

## Hypothèse

Le backlog a établi un schéma clair : les signaux de tendance COURTS
(MACD, Donchian-20) échouent comme déclencheurs de levier, tandis que
les signaux LONGS (SMA200, 52w-high) réussissent systématiquement. La
SMA50 seule (comparaison prix/moyenne, pas moyenne/moyenne comme le
golden cross) permet de tester où se situe le seuil de robustesse sur
cet axe horizon court→long, avec un signal structurellement identique au
#29 (SMA200) mais deux fois et demie plus réactif.

## Définition (fixée ici, avant tout résultat)

- Filtre de tendance = clôture > moyenne mobile simple des 50 dernières
  clôtures (`SMA_WINDOW=50`), identique à la construction du #29 (SMA200)
  mais avec une fenêtre plus courte.
- Position = **1,0x** en permanence, **CAP = 2,0x** les jours où la
  clôture est au-dessus de sa SMA50, **1,0x** sinon.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2,0x et fenêtre 50j fixés a priori par
analogie directe avec le #29, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_sma50_trend_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py sma50_trend_overlay`.
