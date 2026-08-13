# Pré-enregistrement — breadth de faiblesse, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Neuvième candidat des PASS exposés au biais du survivant ; il en restera **4**
après celui-ci.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. La seule entrée le mentionnant
est le **#89** (cycle d'origine). Aucun portage point-in-time. Ce candidat n'a
**ni `.npz` ni batterie Règle 9** — même lacune qu'au #408.

Bilan de l'axe à ce stade : **15 PASS testés, 8 maintenus, 7 tombés.**

## Le PASS d'origine est déjà déclaré NON INFORMATIF

Point décisif, et il ne vient pas de moi : le rapport du cycle d'origine porte
lui-même un avertissement. La porte s'ouvre quand la breadth de faiblesse —
fraction des titres à ≤ 105 % de leur plus bas 252 j — dépasse **50 %**. Sur
l'échantillon d'origine (1385 séances, majoritairement haussières) ce seuil n'est
atteint que **5 jours, soit 0,36 %** du temps. L'overlay ne s'active donc
essentiellement jamais, le résultat est quasi identique à Buy & Hold, et le
« PASS » formel (+0,68 → +0,68 en Sharpe, +132,4 % → +132,5 % en rendement)
**ne démontre aucun edge**.

Porter un tel candidat sur univers point-in-time ne peut donner qu'une de deux
choses :

1. **la porte reste inactive** — le verdict formel se reproduit à l'identique et
   reste tout aussi vide ;
2. **la fenêtre plus longue (2015-2026, qui contient 2015-2016, 2018 et 2020)
   active la porte** — et alors seulement le test devient informatif.

## Critère d'informativité — FIXÉ AVANT CALCUL

Pour ne pas décider après coup si un résultat « compte », je fixe ici la règle :

> Le verdict est déclaré **informatif** si la porte brute (breadth ≥ seuil, avant
> tout effet du vol-targeting) est active sur **au moins 2 %** des séances
> testables. En deçà, il est déclaré **NON INFORMATIF**, quel que soit son sens.

2 % ≈ une séance par trimestre en moyenne. C'est une **convention de lisibilité,
pas un seuil statistique** — je l'écris pour qu'on ne me voie pas choisir la
limite après avoir vu le chiffre, pas pour lui donner une autorité qu'elle n'a
pas.

Cette étiquette **ne modifie pas** le verdict PASS/FAIL, qui reste celui du
critère d'origine. Elle dit seulement si ce verdict apprend quelque chose.

## Hypothèse testée

Le verdict PASS de `weakness_breadth_vol_targeting_overlay` est-il conservé
lorsque la breadth de faiblesse est calculée sur l'appartenance **réelle à chaque
date** — et ce verdict est-il informatif ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié**, seuil de porte compris :

| Paramètre | Valeur |
|---|---|
| `INDEX_LOOKBACK` | 252 |
| `INDEX_THRESHOLD_LOW` | 1,05 |
| `BREADTH_THRESHOLD` | 0,50 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

Le seuil de 50 % est celui repris du #77 par symétrie. **Le baisser pour rendre
la porte active serait un retuning**, et c'est exclu — même si c'est précisément
ce qui rendrait le cycle intéressant. C'est la tentation à nommer ici plutôt qu'à
subir plus tard.

**Seul changement :** l'univers passe de `data/pead/prices/` à
`data/pead/prices_pit/`, avec appartenance résolue à chaque date.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1`, `trading_metrics` sur la série log.

## Fenêtre testable

Le script d'origine sépare correctement la série brute (qui conserve les `NaN`)
de la porte, et détermine le début de fenêtre par `~isnan(breadth_brute)`. Ce
mécanisme est conservé, **et doublé d'une garde exécutable** : le script lève une
exception si la fenêtre démarre avant le 01/01/2015 (leçon du #405, appliquée
depuis le #408).

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts. **PASS** si les deux ; **FAIL** sinon.

`n_trials = 1`. Verdict rapporté tel quel, avec son étiquette d'informativité.

## Prédiction — non tranchée

Aucune, conformément à l'abstention motivée du #409 (deux mécanismes proposés,
deux contredits).

## Engagements

1. Résultat rapporté **tel quel**, avec l'étiquette informatif / non informatif
   déterminée par la règle ci-dessus et non après coup.
2. Aucun retuning, en particulier pas d'abaissement du seuil de 50 %.
3. Audit : recalcul du signal par un chemin de code disjoint, anti-lookahead,
   effet réel du filtre d'appartenance, causalité de la porte, et **comptage
   explicite des activations** dans les deux univers.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
