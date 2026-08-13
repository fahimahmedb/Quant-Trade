# Pré-enregistrement — dispersion du momentum, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte — dernier des 20

**Vingtième et dernier** candidat de la liste des PASS exposés au biais du
survivant. Après ce cycle, l'axe ouvert au #393 est entièrement couvert.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. Les seules entrées le
mentionnant sont le **#100** (cycle d'origine) et les batteries Règle 9
(#318/#383). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **19 PASS testés, 10 maintenus (dont 1 non
informatif), 9 tombés.**

## Architecture

P&L indiciel, porte à médiane glissante. La porte s'ouvre quand la **dispersion
transversale** — écart-type (ddof=1) des scores de momentum 12-1 mois sur les
titres éligibles — est **au-dessus** de sa médiane glissante 252 jours.

## Proximité avec le #407, à mesurer et non à supposer

Le #407 (`momentum_decile_spread`, maintenu) est construit sur la **même matrice
de momentum 12-1**, agrégée autrement : écart entre déciles extrêmes plutôt
qu'écart-type global. Le rapport d'origine du #100 souligne d'ailleurs cette
distinction.

Deux mesures de dispersion sur la même matrice peuvent produire des portes très
proches. Le #403 a montré qu'un tel voisinage pouvait aller jusqu'à l'identité
arithmétique, et le #406 que le décompte d'essais du backlog en dépend.

**Le `.npz` de ce cycle sera donc sauvegardé** (comme celui du #407), afin que le
balayage de doublons du #406 puisse comparer les deux séries. Je ne préjuge pas
du résultat : deux agrégats différents de la même matrice **peuvent** coïncider
comme ils peuvent diverger. L'audit mesurera en outre la corrélation des deux
portes, et publiera le chiffre quel qu'il soit.

## Hypothèse testée

Le verdict PASS de `momentum_dispersion_vol_targeting_overlay` est-il conservé
lorsque la dispersion est calculée sur l'appartenance **réelle à chaque date** au
lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `LOOKBACK` | 252 |
| `SKIP` | 21 |
| `MEDIAN_WINDOW` | 252 |
| `MIN_LISTED` | 10 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers passe de `data/pead/prices/` à
`data/pead/prices_pit/`, avec appartenance résolue à chaque date.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1`, `trading_metrics` sur la série log.

## Fenêtre testable

`dispersion ≥ médiane` rend `False` et non `NaN` là où le signal est indéfini.
Masque explicite requis dès la première exécution, **doublé d'une garde
exécutable** : le script lève une exception si la fenêtre démarre avant le
01/01/2015.

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts. **PASS** si les deux ; **FAIL** sinon.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune, abstention motivée maintenue depuis le #409.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : recalcul de la dispersion par un chemin de code disjoint,
   anti-lookahead, effet réel du filtre d'appartenance, causalité de la porte,
   **contrôle d'attribution** univers / période, et **corrélation de la porte
   avec celle du #407**.
4. **Relecture intégrale de chaque rapport produit avant commit** — trois
   incidents de dérivation consécutifs (#412, #413 ×2) ont publié des valeurs
   héritées d'un autre candidat ; tous détectés par cette relecture, qui devient
   ici un engagement explicite plutôt qu'une habitude.
5. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
