# Pré-enregistrement — effet janvier (proxy prix bas), univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Deuxième des 15 PASS exposés au biais du survivant identifiés au #395. Bilan à ce
stade sur cet axe : **7 PASS testés, 4 maintenus, 3 tombés, aucun ne s'améliore.**

## Particularité de ce candidat

Contrairement au cycle précédent (`deep_drawdown_breadth`, dont le P&L était
**indiciel** et qui a survécu), **ce candidat est un portefeuille de titres** :
les poids sont répartis sur le tercile au prix de clôture le plus faible, et le
P&L est `Σ wᵢ·rᵢ`. Le biais du survivant agit donc **directement sur la mesure de
performance**, exactement comme pour `amihud_illiquidity_tilt` (#394), qui est
tombé PASS → FAIL.

**Prédiction non tranchée à l'avance.** Le #396 a suggéré une distinction possible
— les stratégies à P&L indiciel survivraient, celles à P&L de panier tomberaient —
mais elle repose sur 7 observations seulement et n'a **pas** valeur de règle. Je
ne prédis donc rien ici, et je consigne ce point pour ne pas pouvoir rationaliser
le résultat après coup, dans un sens comme dans l'autre.

## Limite héritée, rappelée

Le cycle d'origine utilise le **prix de clôture** comme proxy de taille, faute de
capitalisation boursière disponible. Cette limite est **inchangée** ici : le
portage sur univers point-in-time ne la corrige pas et ne prétend pas la corriger.
Un prix bas n'est pas une petite capitalisation.

## Hypothèse testée

Le verdict PASS de `january_effect_lowprice_overlay` est-il conservé lorsque
l'univers investissable est l'appartenance **réelle à chaque date** au lieu de la
liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `REBAL_EVERY` | 21 |
| `TERCILE` | 1/3 |
| `CAP` | 2,0 (overlay actif en janvier) |
| `COST_BPS` | 5,0 |

**Seul changement :** `PRICES_DIR` (`data/pead/prices/`) devient
`PRICES_PIT_DIR` (`data/pead/prices_pit/`), avec appartenance résolue par
`ndx100_membership.tickers_as_of_date`, comme dans les variantes
`*_pit_universe` déjà committées.

**Agrégation :** rendements **simples** par titre (`P/P.shift(1) - 1`), conforme
à la correction du #378-#380 — le rendement d'un panier pondéré est
`Σ wᵢ·r_simple,ᵢ`. `trading_metrics` reçoit `log1p(pnl)`.

## Univers et période

- **Univers** : titres NDX-100 point-in-time (`data/pead/prices_pit/`).
- **Période** : celle que les données rendent testable, rapportée telle quelle.
  Aucune fenêtre choisie a posteriori.
- **Restriction explicite** : la fenêtre testable démarre là où l'appartenance
  point-in-time est définie. Le masque doit être posé sur le **signal**, pas
  laissé à un `fillna(False)` implicite — piège rencontré et corrigé au #396,
  où la fenêtre démarrait 30 ans trop tôt avec un signal absent.

## Critère de succès — IDENTIQUE à l'original

Critère renforcé : le portefeuille avec overlay janvier doit battre sa référence
**en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes.
- **FAIL** : au moins une jambe manquée.

`n_trials = 1`. Verdict rapporté tel quel, y compris si FAIL.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close, pas réajustée.
3. Audit à recalcul indépendant + vérification anti-lookahead.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
