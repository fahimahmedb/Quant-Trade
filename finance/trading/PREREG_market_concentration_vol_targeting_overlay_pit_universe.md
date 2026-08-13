# Pré-enregistrement — concentration du marché (HHI), univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Douzième candidat des PASS exposés au biais du survivant ; il en restera **1**
après celui-ci.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. Les seules entrées le
mentionnant sont le **#102** (cycle d'origine) et les batteries Règle 9
(#318/#383). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **18 PASS testés, 9 maintenus (dont 1 non
informatif), 9 tombés.**

## Architecture — P&L indiciel, porte à médiane glissante

Les deux jambes sont l'indice NDX-100 ; l'univers de titres n'alimente que la
porte. Celle-ci s'ouvre quand la **concentration** — indice de
Herfindahl-Hirschman des parts de contribution positive au rendement cumulé
60 jours — est **sous** sa médiane glissante 252 jours (marché large).

## Un point mécanique à mesurer, pas à supposer

Le HHI dépend du **nombre** de titres retenus : son minimum vaut `1/n`. Le
passage à l'univers point-in-time change ce nombre à chaque date. Le niveau du
signal se déplacera donc mécaniquement, au moins en partie, pour une raison
arithmétique et non économique.

La porte étant à **médiane glissante**, elle est invariante par translation du
signal, ce qui amortit l'effet — mais pas s'il s'agit d'un changement d'échelle
plutôt que d'un décalage. **Je n'en tire aucune prédiction** : l'audit mesurera
le niveau *et* la dispersion du HHI dans les deux univers, et publiera les deux.
C'est une propriété de la formule, pas une hypothèse sur le marché ; la
distinction est faite ici pour qu'on ne la confonde pas avec les mécanismes
économiques que j'ai proposés aux #407 et #408 et qui ont tous deux été
contredits.

## Contrôle d'attribution — pré-enregistré, comme au #412

L'audit recalculera le résultat point-in-time sur la fenêtre du cycle d'origine,
afin de séparer effet d'univers et effet de période. Ce contrôle ne conditionne
aucun verdict.

## Hypothèse testée

Le verdict PASS de `market_concentration_vol_targeting_overlay` est-il conservé
lorsque la concentration est calculée sur l'appartenance **réelle à chaque date**
au lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `CONC_WINDOW` | 60 |
| `MEDIAN_WINDOW` | 252 |
| `MIN_LISTED` | 10 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

La convention du cycle d'origine pour le cas dégénéré — aucune contribution
positive sur la fenêtre → `HHI = 1/n` — est **conservée telle quelle**.

**Seul changement :** l'univers passe de `data/pead/prices/` à
`data/pead/prices_pit/`, avec appartenance résolue à chaque date.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1`, `trading_metrics` sur la série log.

## Fenêtre testable

`concentration ≤ médiane` rend **`False`** et non `NaN` là où le signal est
indéfini. Masque explicite requis dès la première exécution, **doublé d'une garde
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
3. Audit : recalcul du HHI par un chemin de code disjoint, anti-lookahead,
   effet réel du filtre d'appartenance, causalité de la porte, **mesure du niveau
   et de la dispersion** du signal dans les deux univers, et **contrôle
   d'attribution** univers / période.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
