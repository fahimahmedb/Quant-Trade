# Réparer le **seul candidat actionnable** (pré-enregistré)

Après le #507, `nonml_battery_backfill_lot_audit.py` est le **seul** des
13 « réparables » qui soit candidat committable **et** sans dépendance à
`sys.argv`. Si le geste borné n'aboutit pas ici, le mot « actionnable »
ne veut rien dire.

## Les quatre causes de non-committabilité, mesurées

| Cause | Occurrences |
|---|---|
| exécution d'un tiers | **0** |
| balayage de `scripts/` ou `results/` | **0** |
| appel `git` | **0** |
| dépendance à `sys.argv` | **0** |

- classe candidate confirmée : **OUI**

## Le « 0,00 % » — la justification du #485 confrontée au code

Le #485 rangeait ce chiffre parmi les réparables au motif que l'audit
« lit les `.npz` d'activation ». **Le code dit autre chose.**

- occurrences de `np.load(` ou `.npz` dans la cible : **0**
- le littéral `0,00 %` est bien présent : **1**

Sa seule source de données est `read_battery()`, qui relit des rapports
`.md`. **Aucune donnée d'activation n'est ouverte.**

> **La justification du #485 est fausse sur ce chiffre.** Il n'est pas
> réparable par interpolation : le produire exigerait d'ouvrir une
> source que le script n'ouvre pas — un cycle distinct, pas « une
> interpolation ». **C'est la deuxième justification du #485 que la
> lecture du code contredit**, après celle que le #493 avait retirée.
>
> **Ce constat a été fait avant d'écrire le pré-enregistrement et y est
> déclaré : il n'est pas compté comme une prédiction.**

## Le diff du `.py`

- lignes changées : **3**

```
    L.append("reste **1** candidat hors de portée de l'outil (schéma panier), listé et non")
    _hors = sum(1 for _r in SET_ASIDE.values() if "panier" in _r)
    L.append(f"reste **{_hors}** candidat hors de portée de l'outil (schéma panier), listé et non")
```

## Le diff du rapport

- lignes changées : **0**

## La valeur calculée face au littéral

| | Valeur |
|---|---|
| littéral d'origine | **1** |
| valeur calculée | **1** |

> Le littéral était **exact**. Le défaut n'était pas une erreur de
> calcul mais une **duplication de source** — et il est levé : le
> nombre est désormais dérivé de `SET_ASIDE`.

## Le geste est-il resté borné ?

- autres fichiers de l'arbre touchés : **0**
- échec : **aucun**

> **Le geste a tenu.** La réparation est **committée** — c'est la
> différence avec le #499, et la seule preuve que le mot
> « actionnable » du #507 recouvrait quelque chose.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| diff du rapport limité au site réparé | oui | oui | **vérifiée** |
| la valeur calculée vaut le littéral | 1 | 1 | **vérifiée** |
| les quatre causes valent 0 | 0 | 0 | **vérifiée** |


## Critères de succès

1. Les quatre causes mesurées et publiées (**0**) — **OUI**.
2. Diff du `.py` limité au site réparé (**3** lignes) — **OUI**.
3. Diff du rapport réduit au site réparé (**0** lignes) — **OUI**.
4. Valeur calculée publiée face au littéral — **OUI**.
5. Justification du #485 sur le « 0,00 % » confrontée et tranchée — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de réparation,
aucune position, aucun paramètre numérique de stratégie.

> **Ce script-ci exécute et modifie un tiers** : il est lui-même non
> committable au sens du #507, et le dire vaut mieux que feindre
> l'inertie.
