# Audit adversarial — l'incohérence émetteur/rapport (#475)

**Recalcul par une route différente** : `git grep` au lieu de la lecture
du fichier, **AST** au lieu de l'indentation, `git log -S` (pickaxe) au
lieu du dépliage commit par commit.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| lignes d'émission (append/write/print) | **1** | 1 | **concordant** |
| commits où le rapport porte la marque | **1** | 1 | **concordant** |
| rapports déclarés dans `SIX` | **6** | 6 | **concordant** |
| régénérés portant la marque | **4** | 4 | **concordant** |

## Deux grandeurs à ne pas confondre

- occurrences **quelconques** de la marque dans le script (`git grep`) : **2**
- **émissions** au sens du #469 (`append`/`write`/`print`) : **1**

La différence n'est pas une erreur : la ligne surnuméraire est un
`if "…" in av`, c'est-à-dire une **recherche** de la marque, pas une
écriture. **C'est exactement la distinction que le #469 avait dû
introduire**, et un audit qui compterait les occurrences brutes
reproduirait la confusion qu'il a levée.

## La garde conditionnelle, établie par AST

- constantes contenant la marque dans le script : **3**
- **sous au moins une garde** : **3**
  - ligne 228 — boucle (ligne 224) → if (ligne 228)
  - ligne 228 — boucle (ligne 224) → if (ligne 228)
  - ligne 240 — if (ligne 231)

L'AST confirme par une autre voie ce que le backtest a établi en
remontant l'indentation : **l'écriture est conditionnelle**.

## La possession historique, par pickaxe

```
git log --all -S "Rapport dépendant du dépôt" -- finance/trading/results/nonml_six_reports_regeneration_result.md
```

- commits où la chaîne **apparaît ou disparaît** : **2**
  - 1a0c51d #468 : les deux scripts auto-inclusifs sont REPARES et idempotents
  - bbe5165 #450 regeneration des six rapports : PASS — la derive domine, 18 groupes contre 5
- présente **aujourd'hui** : **non**

> **Le pickaxe voit l'ajout *et* le retrait.** La possession puis la
> perte sont confirmées par un mécanisme totalement distinct de celui
> du backtest : **la lecture A tient.**

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- exécution d'un script du dépôt / `checkout` / suppression : **0**

**Aucun effet de bord.**

## Verdict

**CONCORDANT** — **4/4** grandeurs se retrouvent par
une route indépendante.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).