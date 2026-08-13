# Pré-enregistrement — Leaders + overlay vol-targeting 20 %, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Quatrième candidat réellement non vérifié des **11** PASS encore exposés au biais
du survivant (liste corrigée au #400, décomptée au #401).

**Vérification préalable effectuée**, conformément à la règle inscrite au #400 :
recherche d'un portage existant par fichier de résultat, PREREG, script **et
historique du backlog**. Les seules entrées mentionnant ce candidat sont le #48
(cycle d'origine), le #253 (correction du décalage causal) et le #318 (batterie
Règle 9). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **10 PASS testés, 5 maintenus, 5 tombés.**

## Ce que ce candidat combine

`leaders_vol_targeting_20_overlay` (#48) superpose deux briques :

1. un **portefeuille Leaders** (tercile le plus proche de son plus haut
   52-semaines) — c'est ici que joue le biais du survivant ;
2. un **overlay de vol-targeting continu** : exposition = 20 % / volatilité
   réalisée du portefeuille sur 20 jours, plafonnée à 2,0×.

Différence importante avec le #401 (`leaders_trend_union_overlay`, tombé) : là,
le signal d'exposition venait de l'**indice** et était donc insensible au
changement d'univers. Ici l'exposition est pilotée par la volatilité **du
portefeuille Leaders lui-même** — elle change donc mécaniquement avec l'univers.
Ce n'est **pas** un changement de paramètre mais une conséquence directe et
inévitable du changement d'univers ; je le consigne pour qu'on ne le confonde
pas avec une modification de protocole.

## Hypothèse testée

Le verdict PASS de `leaders_vol_targeting_20_overlay` est-il conservé lorsque
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
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers de sélection des Leaders passe de
`data/pead/prices/` (liste NDX-100 de 2026 appliquée rétroactivement) à
`data/pead/prices_pit/`, avec appartenance résolue par
`ndx100_membership.tickers_as_of_date` à chaque date de rebalancement.

**Exécution causale** (patch #166/#167, appliqué à ce candidat au #253) :
les poids décidés à la clôture de t−1 sont ceux détenus pendant la séance t.

**Agrégation :** rendements **simples** par titre, `Σ wᵢ·r_simple,ᵢ`, conforme à
la correction #378-#380. `trading_metrics` reçoit `log1p(pnl)`.

**Fenêtre testable :** masque explicite sur les dates où l'appartenance
point-in-time est définie — piège rencontré et corrigé au #396.

## Critère de succès — IDENTIQUE à l'original

Critère renforcé : le portefeuille Leaders + overlay doit battre le portefeuille
Leaders 1,0× **en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes.
- **FAIL** : au moins une jambe manquée.

`n_trials = 1`. Verdict rapporté tel quel, y compris si FAIL.

## Prédiction — non tranchée

Je ne formule aucune attente. La conjecture émise au #396 a été démentie au
#398 ; celle qu'on tirerait du décompte actuel (5 sur 10) le serait sur dix
observations. Je consigne cette abstention pour ne pas pouvoir rationaliser le
résultat après coup.

**Élément de contexte, à ne pas confondre avec une prédiction** : ce candidat
n'obtient que **1/5** à la batterie Règle 9 (#318) sur l'univers d'origine —
c'est déjà l'un des PASS les plus fragiles du backlog. Cela ne détermine rien
quant au présent test, qui porte sur le seul critère de niveau 1.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close, pas réajustée.
3. Audit à recalcul indépendant (simulation en nombre de parts) +
   vérification anti-lookahead + contrôle d'appartenance à la date de décision +
   contrôle de causalité de l'exposition (la volatilité utilisée en t doit être
   celle connue en t−1).
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
