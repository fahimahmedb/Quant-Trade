# Audit adversarial — spread décile de momentum, univers point-in-time

## 1. Recalcul du spread par un chemin de code disjoint

Le backtest décale les prix par tranches NumPy puis trie la colonne entière ;
l'audit passe par `pandas.shift` et `nlargest`/`nsmallest`. Les deux chemins ne
partagent aucune ligne.

| Date | Spread backtest | Spread audit | Écart |
|---|---|---|---|
| 2015-01-02 | 0.951190 | 0.951190 | 2.22e-16 |
| 2017-04-25 | 1.291907 | 1.291907 | 0.00e+00 |
| 2019-08-15 | 0.908621 | 0.908621 | 0.00e+00 |
| 2021-12-03 | 1.066736 | 1.066736 | 2.22e-16 |
| 2024-03-28 | 1.448531 | 1.448531 | 0.00e+00 |
| 2026-07-27 | 11.021290 | 11.021290 | 3.55e-15 |

- écart maximal : **3.55e-15**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Les prix postérieurs à l'indice 12808 (2020-10-09) sont multipliés
par 7. Le spread calculé **à** cette date doit être strictement inchangé.

- spread avant mutation : **2.914767**
- spread après mutation : **2.914767**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

Un filtre sans effet rendrait le « maintenu » vide de sens. Le spread est
recalculé en forçant l'univers à **tous** les tickers disponibles ; il doit
différer de la version point-in-time.

- dates comparées : **6**
- dates où le spread diffère : **6**
- écart moyen (univers élargi − point-in-time) : **-0.3370**
- couverture moyenne rapportée par le backtest : **87.8%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

Le pré-enregistrement décrivait un mécanisme possible : retirer
rétroactivement les sociétés sorties de l'indice amputerait surtout le décile
**faible**, donc l'univers élargi devrait produire un spread **plus large**.

L'écart mesuré est **négatif** : l'univers élargi produit un spread plus
**étroit**, soit l'inverse de ce que le mécanisme proposé prédisait. Le
mécanisme écrit au pré-enregistrement est donc **contredit** par cette
mesure — c'est consigné plutôt que passé sous silence.

Dans les deux cas, six dates ne constituent pas une mesure mais une
indication : ce contrôle sert à établir que le filtre agit, pas à quantifier
son sens.

## 4. Causalité de la porte

`combined_position` consomme `gate_aligned[:-1]` : la porte appliquée au
rendement du jour t est celle observée en t−1. Vérifié sur une porte synthétique
n'ayant qu'un seul jour actif (indice 20).

- indices de position modifiée : **[np.int64(20)]**

**CONFORME — décalage d un jour, aucune décision prise sur le rendement du jour même.**

## Verdict de l'audit

**CONFORME — les quatre contrôles passent.**
