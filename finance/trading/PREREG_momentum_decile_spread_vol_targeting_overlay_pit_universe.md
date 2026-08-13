# Pré-enregistrement — spread décile de momentum, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Sixième candidat réellement non vérifié des **8** PASS encore exposés au biais du
survivant.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. La seule entrée le mentionnant
est le **#100** (cycle d'origine). Aucun portage point-in-time.

Bilan de l'axe à ce stade : **12 PASS testés, 6 maintenus, 6 tombés.**

## Ce que ce candidat combine

Même architecture que le #405 (`smallcap_proxy_outperformance_breadth_overlay`,
maintenu) : **le P&L n'est pas un panier de titres**. Les deux jambes sont
l'indice NDX-100 lui-même, en Buy & Hold pur ou avec exposition modulée par un
vol-targeting. L'univers de titres n'intervient **que dans la porte** — ici le
spread décile de momentum 12-1 (moyenne du décile le plus fort moins moyenne du
décile le plus faible), comparé à sa médiane glissante 252 j.

Le biais du survivant ne peut donc agir que par ce canal. Il est cependant
**plausible qu'il y agisse plus fortement qu'au #405** : un spread de queues de
distribution est, par construction, sensible à la composition de l'univers, et
retirer rétroactivement les sociétés sorties de l'indice ampute surtout le décile
**faible**. Ce raisonnement est écrit ici comme mécanisme possible, **pas comme
prédiction de verdict** — je n'annonce pas de résultat.

## Hypothèse testée

Le verdict PASS (niveau 1) de `momentum_decile_spread_vol_targeting_overlay`
est-il conservé lorsque le spread décile est calculé sur l'appartenance **réelle
à chaque date** au lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `LOOKBACK` | 252 |
| `SKIP` | 21 |
| `MEDIAN_WINDOW` | 252 |
| `MIN_LISTED` | 10 |
| `DECILE_FRACTION` | 0,10 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers servant à calculer le spread passe de
`data/pead/prices/` à `data/pead/prices_pit/`, et à chaque date seuls les titres
membres du NDX-100 à cette date (`ndx100_membership.tickers_as_of_date`) entrent
dans le classement de momentum.

Le P&L reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1` pour le rendement total, `trading_metrics`
directement sur la série log (conventions rétablies au #404).

## Fenêtre testable — masque explicite, exigé d'emblée

`spread >= médiane` rend **`False`** et non `NaN` là où le spread est indéfini.
Le script d'origine s'en sortait par accident, son univers `prices/` démarrant
tard ; `prices_pit/` remonte à 1985.

**Au #405 j'ai écrit que le mécanisme d'origine suffisait. C'était faux** : la
première exécution partait de 1985 avec la porte fermée par défaut pendant trente
ans. Le masque explicite

```python
signal_defined = spread.notna() & median_spread.notna()
gate_series = (spread >= median_spread).where(signal_defined)
```

est donc **exigé dès la première exécution** de ce cycle, et non ajouté après
constat. C'est la troisième rencontre du piège du #396 ; il est ici traité comme
une contrainte du protocole, pas comme un incident.

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts.

- **PASS niveau 1** : les deux jambes atteintes. **FAIL** : au moins une manquée.

Un PASS de niveau 1 **n'est pas un verdict final** (Règle 9).

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune. Le mécanisme décrit plus haut explique *comment* le biais pourrait agir,
il ne dit pas dans quel sens le verdict basculera — et la seule conjecture que
j'aie formulée sur cet axe (#396) a été démentie (#398).

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : recalcul du spread par un chemin de code disjoint, anti-lookahead par
   mutation du futur, contrôle que le filtre d'appartenance **change réellement**
   le signal, causalité de la porte.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
