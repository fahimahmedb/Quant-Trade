# Audit — réécriture de la ligne « Couverture 100 % » (pré-enregistré)

Cycle d'**outillage documentaire**, et le **premier à modifier une ligne déjà
publiée**. Aucune stratégie évaluée, aucun verdict recalculé, aucun seuil touché.

Les cinq lots de persistance (#416 → #427) tenaient « 0 différence octet à
octet » ; le #428 en est sorti pour n'ajouter que des insertions ; celui-ci
remplace du texte. Chaque régime a été déclaré avant d'être appliqué, et le
garde-fou est ici « ne changer **que** ce qui est annoncé, mot pour mot ».

## Contrôles 1 et 2 — une seule ligne remplacée, par le texte annoncé

- lignes **supprimées** : **1**
- lignes **insérées** : **2**

| Contrôle | Attendu | Obtenu | |
|---|---|---|---|
| suppressions | 1, exactement la ligne annoncée | 1 | ✔ |
| texte inséré | identique au pré-enregistrement | conforme | ✔ |

Ligne supprimée :

```
**Couverture 100 %** — critère 1 du pré-enregistrement atteint.
```

Lignes insérées :

```
**100 % des fichiers trouvés ont été relus** — critère 1 du pré-enregistrement
atteint. Ce taux ne mesure pas la couverture du dépôt : voir juste en dessous.
```

**Contrôles passés.** Le `diff` se limite à la ligne annoncée, et le texte
de remplacement est celui fixé avant tout calcul — il n'a pas été retouché
après avoir vu le rendu, ce que l'engagement 2 interdisait.

## Contrôle 3 — décomptes de doublons inchangés

| | #428 | #429 | |
|---|---|---|---|
| séries de P&L reconstruites | 218 | **218** | ✔ |
| groupes de doublons exacts | 3 | **3** | ✔ |
| quasi-doublons | 1 | **1** | ✔ |

**Aucun décompte n'a bougé.**

## Contrôle 4 — le rapport jumeau est resté intact

Deux rapports portaient la même formule. Le second dit **vrai** : son volet A
examine réellement les **284** scripts `nonml_*_backtest.py` du dépôt, 0 illisible,
et son volet B publie sa propre couverture séparément (62/62 depuis le #427).

Corriger une formulation exacte parce qu'elle **ressemble** à une formulation
fautive serait du zèle, pas de la rigueur. Ce contrôle vérifie que je m'en suis
abstenu.

- `nonml_capitulation_gate_floor_sweep_result.md` : **identique octet à octet** ✔

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| suppressions dans le rapport | 1 | 1 | ✔ |
| texte inséré | celui du pré-enregistrement | conforme | ✔ |
| décomptes | 218 / 3 / 1 | 218 / 3 / 1 | ✔ |
| rapport jumeau | 0 différence | 0 | ✔ |

**Prédiction déductive vérifiée.** La limite que le #428 avait signalée est
fermée : la ligne ne promet plus une couverture du dépôt qu'elle ne mesure
pas, et la section ajoutée au #428 la complète juste en dessous.

Trois régimes de modification auront donc été déclarés puis tenus : **0
différence** (#416 → #427), **insertions seulement** (#428), **remplacement
d'une ligne annoncée** (#429). Aucun n'a été élargi en cours de route.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
