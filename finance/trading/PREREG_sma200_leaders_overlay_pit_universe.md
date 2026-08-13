# Pré-enregistrement — Leaders + overlay SMA200, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Cinquième candidat des PASS encore exposés au biais du survivant (**10**
restants après le #402).

**Vérification préalable effectuée**, règle du #400 : recherche par fichier de
résultat, PREREG, script et historique du backlog. Les seules entrées le
mentionnant sont le #33 (origine), le #253 (décalage causal) et le #318/#383
(batteries Règle 9). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **11 PASS testés, 5 maintenus, 6 tombés.**

## Avertissement déclaré AVANT calcul : ce test peut être un doublon du #401

L'audit du cycle **#41** avait établi que, sur la fenêtre alors testée
(2022-2026), le signal « indice à ≥ 95 % de son plus haut 252 j » est un
**sous-ensemble strict** du signal « indice au-dessus de sa SMA200 » : zéro
séance où le premier est actif sans le second. L'union des deux y était donc
**arithmétiquement identique** à SMA200 seul, et les deux candidats
reproduisaient chiffre pour chiffre les mêmes résultats (+0,84 / +108,0 % pour
la référence, +0,88 / +270,7 % pour l'overlay).

Le portage point-in-time du #401 (`leaders_trend_union_overlay`) porte sur la
fenêtre **2015-2026**, plus longue. Deux cas possibles, tranchés par le calcul
et non par moi :

- **si l'inclusion tient encore sur 2015-2026**, ce cycle reproduira exactement
  le #401 (référence +0,70 / +393,0 %, overlay +0,66 / +1109,9 %, FAIL) et
  n'apportera **aucune observation nouvelle** ;
- **si elle est rompue** (des séances où le 52w-high est actif sans la SMA200),
  les deux candidats divergent et le résultat est une observation propre.

**Règle de comptage fixée d'avance** : le backtest mesure et rapporte le nombre
de séances où les deux signaux diffèrent. **Si ce nombre est nul, ce cycle ne
compte pas comme une nouvelle observation** dans le bilan de l'axe — il ne
serait qu'une identité arithmétique, et l'inscrire au compteur gonflerait
artificiellement le décompte « testés ». Le résultat sera néanmoins committé,
avec ce statut explicite.

Je consigne cet avertissement maintenant pour ne pas pouvoir, après lecture,
présenter un doublon comme une confirmation indépendante.

## Hypothèse testée

Le verdict PASS de `sma200_leaders_overlay` est-il conservé lorsque l'univers
investissable est l'appartenance **réelle à chaque date** au lieu de la liste
NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `LOOKBACK` | 252 |
| `REBAL_EVERY` | 21 |
| `TERCILE` | 1/3 |
| `CAP` | 2,0 |
| `SMA_WINDOW` | 200 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers de sélection des Leaders passe de
`data/pead/prices/` à `data/pead/prices_pit/`, appartenance résolue par
`ndx100_membership.tickers_as_of_date` à chaque date de rebalancement. Le signal
SMA200 porte sur l'**indice** et est donc inchangé.

**Exécution causale** (patch #166/#167, appliqué au #253).
**Agrégation :** rendements simples par titre, `Σ wᵢ·r_simple,ᵢ` (#378-#380),
`trading_metrics` reçoit `log1p(pnl)`.
**Fenêtre testable :** masque explicite sur les dates d'appartenance PIT (#396).

## Critère de succès — IDENTIQUE à l'original

Le portefeuille Leaders + overlay doit battre le portefeuille Leaders 1,0×
**en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes. **FAIL** : au moins une manquée.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune attente formulée. Le décompte actuel de l'axe (5 maintenus sur 11) et la
série des trois candidats Leaders tombés (#163, #401, #402) sont des
observations, pas des prédictions : trois cas ne fondent pas une règle, et j'ai
déjà vu une conjecture de ce type démentie (#396 → #398).

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : recalcul par simulation en nombre de parts, anti-lookahead,
   appartenance à la date de décision, causalité du décalage, **et comparaison
   explicite au P&L du #401** pour établir si les deux candidats coïncident.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
