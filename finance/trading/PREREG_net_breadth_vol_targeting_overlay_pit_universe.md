# Pré-enregistrement — breadth nette hauts-bas, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Septième candidat réellement non vérifié des **7** PASS encore exposés au biais
du survivant.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. La seule entrée le mentionnant
est le **#90** (cycle d'origine, combinant #77 et #89). Aucun portage
point-in-time.

À noter au passage : ce candidat n'a **ni `.npz` sauvegardé ni batterie Règle 9**
— illustration directe de la limite mesurée au #406, où le balayage des doublons
ne voyait que 41 % du backlog.

Bilan de l'axe à ce stade : **13 PASS testés, 7 maintenus, 6 tombés.**

## Ce que ce candidat a de différent des deux précédents

Même architecture générale que les #405 et #407, tous deux maintenus : **le P&L
n'est pas un panier**, les deux jambes sont l'indice NDX-100 ; l'univers de
titres n'alimente que la porte.

Mais la porte a ici une propriété que les deux autres n'avaient pas : **son seuil
est absolu**. Elle s'ouvre quand la breadth nette — (titres à ≥ 95 % de leur plus
haut 252 j, moins titres à ≤ 105 % de leur plus bas) / titres cotés — dépasse
**zéro**, et non une médiane glissante.

C'est une différence de nature vis-à-vis du biais du survivant. Une porte à
médiane glissante est **invariante par translation** du signal : décaler la
breadth d'une constante ne change rien à ses franchissements. Une porte à seuil
absolu ne l'est pas. Or le biais du survivant agit précisément sur le **niveau** :
les sociétés retenues sont celles qui ont survécu jusqu'en 2026, donc plus
souvent proches de leurs plus hauts que de leurs plus bas.

**Ceci est un mécanisme, pas une prédiction de verdict.** Je le sépare d'autant
plus explicitement que le mécanisme que j'avais décrit au #407 a été *contredit*
par la mesure de l'audit. Écrire comment une chose pourrait agir n'est pas
annoncer dans quel sens elle agira.

## Hypothèse testée

Le verdict PASS de `net_breadth_vol_targeting_overlay` est-il conservé lorsque la
breadth nette est calculée sur l'appartenance **réelle à chaque date** au lieu de
la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `INDEX_LOOKBACK` | 252 |
| `INDEX_THRESHOLD_HIGH` | 0,95 |
| `INDEX_THRESHOLD_LOW` | 1,05 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

Le seuil de porte reste **0,0**, en particulier : il serait tentant de le
recalibrer sur le nouveau niveau de breadth, ce serait un retuning et c'est
exclu.

**Seul changement :** l'univers passe de `data/pead/prices/` à
`data/pead/prices_pit/`, et à chaque date seuls les titres membres du NDX-100 à
cette date entrent dans les comptages `n_proche_haut`, `n_proche_bas` et
`n_cotés`.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1`, `trading_metrics` sur la série log.

## Fenêtre testable

Le script d'origine sépare correctement la série **brute** (qui conserve les
`NaN`) de la **porte** (booléenne), et détermine le début de fenêtre par
`~isnan(breadth_brute)`. Ce mécanisme est conservé, et il est ici **suffisant**
puisque la breadth point-in-time est `NaN` avant le 01/01/2015 par construction.

Contrairement au #405, je ne me contente pas de l'affirmer : **le contrôle est
que la fenêtre testable démarre en 2015-2016 et non en 1985**. Si elle démarre
plus tôt, c'est le piège du #396 et le résultat est invalide, à corriger avant
tout commit.

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts.

- **PASS** : les deux jambes atteintes. **FAIL** : au moins une manquée.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning — en particulier, le seuil de porte reste à 0,0 quel que soit
   le niveau de breadth observé sur l'univers réel.
3. Audit : recalcul de la breadth par un chemin de code disjoint, anti-lookahead
   par mutation du futur, contrôle que le filtre d'appartenance change réellement
   le signal, causalité de la porte, **et mesure du décalage de niveau** de la
   breadth entre les deux univers — c'est la quantité que le mécanisme ci-dessus
   met en jeu, elle doit être mesurée et publiée quel que soit son signe.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
