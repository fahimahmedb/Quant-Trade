# Pré-enregistrement — Structure par terme du VIX (contango/backwardation), overlay défensif

**Committé AVANT tout calcul.** Cycle #340 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le VIX (CBOE, volatilité implicite 30 jours du S&P 500) et le VXV/VIX3M
(CBOE, volatilité implicite 3 mois) forment ensemble une **structure par
terme de la volatilité implicite**. En régime normal, cette structure
est en **contango** (VIX3M > VIX, le marché anticipe un retour à une
volatilité "normale" à moyen terme, prime de terme positive). Lors d'un
choc de stress aigu, elle s'inverse en **backwardation** (VIX > VIX3M,
la peur immédiate domine l'anticipation à moyen terme) — phénomène
documenté (ex. Johnson 2017, "Risk Premia and the VIX Term Structure")
et utilisé comme signal de stress par les praticiens (ex. stratégies
XIV/VXX de suivi de la pente à terme).

**Distinct des deux signaux VIX déjà testés dans ce backlog** :
- #130 (niveau VIX seul comme porte d'un mécanisme hiérarchique
  vol-targeting, FAIL — Sharpe +0,51→+0,50) : ici pas de niveau seul,
  mais un ÉCART entre deux maturités de volatilité IMPLICITE.
- #191 (prime de risque de variance VIX−vol réalisée, FAIL 2/5) : ici
  pas d'écart implicite-vs-réalisé, mais un écart implicite-COURT vs
  implicite-LONG (deux mesures prospectives, pas une prospective et une
  rétrospective) — mécanisme économiquement différent (anticipation de
  persistance du stress, pas magnitude de la surprise réalisée).

Design PUREMENT DÉFENSIF (jamais de levier), cohérent avec les
#175/#178/#186/#187/#191 plutôt qu'avec le mécanisme hiérarchique à deux
sens du #130.

## 2. Données

**Nouvelle donnée à récupérer** : série FRED `VXVCLS` (CBOE S&P 500
3-Month Volatility Index), gratuite, quotidienne depuis le 2007-12-04,
disponibilité déjà vérifiée par fetch de test (HTTP 200, 4872 valeurs
jusqu'au 2026-08-05). Combinée à `data/vixcls_daily.csv` déjà en local
(récupéré au #130, 1990+) — aucun nouveau fetch nécessaire pour le VIX
spot. **Historique effectif limité par VXVCLS (2007-12-04+)** : NDX (40
ans, débute 1985) verra sa fenêtre testée tronquée à partir de fin 2007,
signalé à l'avance comme limite reconnue, pas un bug.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification qu'au #191 (signal de peur global, appliqué au-delà du
seul S&P 500, cohérent avec la pratique établie de ce backlog).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal `ffill+shift(1)` identique aux #130/#191 pour les
  deux séries FRED (Règle 7, aucun nouveau paramètre).
- `Slope(t) = VXV_lag(t) − VIX_lag(t)` (les deux termes déjà décalés
  d'un jour, donc `Slope(t)` est connu à la clôture du jour t-1).
  Positif = contango (normal), négatif = backwardation (stress aigu).
- Seuil : **tercile EXPANDING** de `Slope(t)` (technique établie aux
  #169/#177/#183/#191, `expanding_tercile_cut_low` réutilisée à
  l'identique du #203/#320/#341, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique** des
  #175/#176/#178/#186/#187/#191) si `Slope(t)` est dans son tercile
  expanding le PLUS BAS (backwardation la plus prononcée, stress aigu),
  `1,0x` sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS`
  réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** (ni confirmatoire ni contraire) : le
mécanisme est économiquement distinct des deux tests VIX déjà FAIL,
mais appartient à la même famille de signaux de peur/stress dont
AUCUN n'a encore atteint le seuil renforcé dans ce backlog (VIX niveau
#130 FAIL, VRP #191 FAIL 2/5). Résultat rapporté tel quel, PASS ou
FAIL, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le #191, la backwardation pourrait survenir APRÈS le pic de
   stress (les deux maturités implicites réagissent avec un délai
   similaire à l'événement) plutôt qu'avant, limitant la valeur
   anticipative du signal pour un mécanisme statique sans délai.
2. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme aux #175/#178/#186/#187/#191.
3. Historique VXVCLS plus court (2007+) que VIXCLS (1990+) — la
   troncature réduit l'échantillon effectif sur NDX en particulier,
   limite reconnue à l'avance.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_vix_term_structure_overlay_backtest.py`,
`scripts/nonml_vix_term_structure_overlay_audit.py`,
`results/nonml_vix_term_structure_overlay_{result,audit,anti_cheat}.md`.
