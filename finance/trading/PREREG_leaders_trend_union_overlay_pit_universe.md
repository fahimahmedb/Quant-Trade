# Pré-enregistrement — Leaders + overlay union de tendance, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Troisième candidat réellement non vérifié des **12** PASS exposés au biais du
survivant (liste corrigée au #400 — l'audit du #395 en annonçait 15, dont 3
avaient déjà été portés).

**Vérification préalable effectuée**, conformément à la règle inscrite au #400 :
recherche d'un portage existant par fichier de résultat, PREREG et script.
Aucun. Ce candidat n'a jamais été testé sur univers point-in-time.

Bilan de l'axe à ce stade : **9 PASS testés, 5 maintenus, 4 tombés.**

## Ce que ce candidat combine

`leaders_trend_union_overlay` (#41) superpose deux briques :

1. un **portefeuille Leaders** (tercile le plus proche de son plus haut
   52-semaines, titre par titre) — c'est ici que joue le biais du survivant ;
2. un **overlay d'exposition** piloté par un signal de tendance sur l'INDICE
   (union SMA200 ∪ 52w-high), non concerné par le biais.

La référence est le **portefeuille Leaders 1,0×**, pas Buy & Hold — convention du
PREREG d'origine, conservée.

**Le biais agit donc sur les deux jambes à la fois** (candidat et référence sont
tous deux des paniers Leaders), ce qui le distingue du #394 (`amihud`, tombé) où
la référence était l'univers équipondéré complet.

**Prédiction non tranchée à l'avance.** J'ai déjà formulé au #396 une conjecture
(« P&L indiciel survit, panier tombe ») que le #398 a démentie. Je ne formule
donc aucune attente ici, et je le consigne pour ne pas pouvoir rationaliser le
résultat après coup.

## Hypothèse testée

Le verdict PASS de `leaders_trend_union_overlay` est-il conservé lorsque
l'univers investissable est l'appartenance **réelle à chaque date** au lieu de la
liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `LOOKBACK` | 252 |
| `REBAL_EVERY` | 21 |
| `TERCILE` | 1/3 |
| `CAP` | 2,0 |
| `SMA_WINDOW` | 200 |
| `INDEX_LOOKBACK` | 252 |
| `INDEX_THRESHOLD` | 0,95 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers de sélection des Leaders passe de
`data/pead/prices/` à `data/pead/prices_pit/`, avec appartenance résolue par
`ndx100_membership.tickers_as_of_date` à chaque date de rebalancement. Le signal
de tendance sur l'indice est **inchangé** (il ne dépend pas de l'univers titres).

**Agrégation :** rendements **simples** par titre, `Σ wᵢ·r_simple,ᵢ`, conforme à
la correction #378-#380. `trading_metrics` reçoit `log1p(pnl)`.

**Fenêtre testable :** masque explicite sur les dates où l'appartenance
point-in-time est définie — piège rencontré et corrigé au #396, où un
`fillna(False)` implicite faisait démarrer la fenêtre 30 ans trop tôt.

## Critère de succès — IDENTIQUE à l'original

Critère renforcé : le portefeuille Leaders + overlay doit battre le portefeuille
Leaders 1,0× **en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes.
- **FAIL** : au moins une jambe manquée.

`n_trials = 1`. Verdict rapporté tel quel, y compris si FAIL.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close, pas réajustée.
3. Audit à recalcul indépendant (simulation en nombre de parts) +
   vérification anti-lookahead + contrôle d'appartenance à la date de décision.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
