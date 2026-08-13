# Pré-enregistrement — position moyenne dans le range annuel, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Huitième candidat des PASS exposés au biais du survivant ; il en reste **6** après
celui-ci.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. Les seules entrées le
mentionnant sont le **#103** (cycle d'origine) et le **#318/#383** (batteries
Règle 9). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **14 PASS testés, 8 maintenus, 6 tombés.**

## Ce que ce candidat combine

Même architecture que les #405, #407 et #408, tous maintenus : **le P&L n'est pas
un panier**, les deux jambes sont l'indice NDX-100 ; l'univers de titres
n'alimente que la porte.

La porte : moyenne transversale de la **position dans le range annuel**
`(close − plus-bas 252 j) / (plus-haut 252 j − plus-bas 252 j)`, comparée à sa
**médiane glissante 252 j**. Seuil relatif, donc invariant par translation du
signal — comme aux #405 et #407, contrairement au seuil absolu du #408.

## Sur les mécanismes : abstention motivée

Aux #407 et #408 j'ai écrit avant calcul un mécanisme expliquant comment le biais
du survivant devait agir. **Les deux ont été contredits par la mesure** — 0 sur 2.

Je n'en formule pas un troisième. Ce n'est pas pour éviter d'être démenti : les
deux précédents étaient écrits pour l'être, et c'est ce qui a permis de constater
mon taux d'erreur. C'est parce qu'un troisième mécanisme n'aurait aucune base
meilleure que les deux premiers — ce serait de l'intuition présentée comme du
raisonnement. L'abstention et sa raison sont consignées ici plutôt que passées
sous silence.

En revanche, l'audit **mesurera** l'effet du changement d'univers sur le niveau et
la dispersion du signal, comme au #408, et publiera le résultat sans hypothèse
préalable à confirmer ou infirmer.

## Hypothèse testée

Le verdict PASS de `range_position_vol_targeting_overlay` est-il conservé lorsque
la position moyenne dans le range est calculée sur l'appartenance **réelle à
chaque date** au lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `RANGE_LOOKBACK` | 252 |
| `MEDIAN_WINDOW` | 252 |
| `MIN_LISTED` | 10 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers passe de `data/pead/prices/` à
`data/pead/prices_pit/`, et à chaque date seuls les titres membres du NDX-100 à
cette date entrent dans la moyenne transversale.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1`, `trading_metrics` sur la série log.

## Fenêtre testable — masque explicite ET garde exécutable

`position ≥ médiane` rend **`False`** et non `NaN` là où le signal est indéfini.
Le masque explicite est donc requis dès la première exécution :

```python
signal_defined = avg_position.notna() & median_position.notna()
gate_series = (avg_position >= median_position).where(signal_defined)
```

Et, comme au #408, le script **lève une exception** si la fenêtre testable démarre
avant le 01/01/2015. Une affirmation dans un pré-enregistrement ne vaut rien tant
qu'elle n'est pas un test qui casse — leçon du #405, où j'avais affirmé le piège
évité alors qu'il ne l'était pas.

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts.

- **PASS** : les deux jambes atteintes. **FAIL** : au moins une manquée.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune, pour la raison exposée plus haut.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : recalcul du signal par un chemin de code disjoint, anti-lookahead par
   mutation du futur, contrôle que le filtre d'appartenance change réellement le
   signal, causalité de la porte, et **mesure du décalage de niveau** entre les
   deux univers sur les mêmes dates.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
