# Pré-enregistrement — réécrire la ligne « Couverture 100 % » du balayage de doublons

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**outillage documentaire**, et le premier à **modifier** une ligne déjà
publiée. Aucune stratégie évaluée, aucun verdict recalculé, aucun seuil touché.

## La limite que le #428 a laissée ouverte, et pourquoi il l'a laissée

Le #428 a ajouté au rapport du balayage la section qui dit ce que son « 100 % »
recouvre. Mais la ligne elle-même est restée :

> `**Couverture 100 %** — critère 1 du pré-enregistrement atteint.`

La corriger aurait **modifié** une ligne existante, ce que le contrôle du #428
(« insertions seulement ») interdisait. Le compromis a été signalé plutôt que
dissimulé, et la réécriture inscrite en tête de file. C'est ce cycle.

## Régime déclaré : ce cycle MODIFIE une ligne publiée

Les cinq lots de persistance (#416 → #427) tenaient « 0 différence octet à
octet ». Le #428 en est sorti pour n'ajouter que des insertions. **Celui-ci va
plus loin : il remplace du texte publié.** Je le déclare avant de commencer,
comme les deux régimes précédents.

Le garde-fou n'est donc plus « ne rien changer » mais « ne changer **que** ce qui
est annoncé ici, mot pour mot ».

## Le texte, fixé avant tout calcul

**Avant** (ligne unique, dans le rapport du balayage de doublons) :

```
**Couverture 100 %** — critère 1 du pré-enregistrement atteint.
```

**Après** — rédaction arrêtée maintenant, non ajustable après lecture du résultat :

```
**100 % des fichiers trouvés ont été relus** — critère 1 du pré-enregistrement
atteint. Ce taux ne mesure pas la couverture du dépôt : voir juste en dessous.
```

Le mot « Couverture » disparaît de cette ligne parce que c'est lui qui induit en
erreur : il suggère une part du dépôt, alors que le dénominateur est l'ensemble
des fichiers déjà présents.

## Le cas jumeau — vérifié, et laissé intact

Deux rapports portent la même formule. Vérification faite **avant** d'écrire ce
pré-enregistrement :

| Rapport | Ce que « 100 % » y mesure | Verdict |
|---|---|---|
| `nonml_pnl_duplicate_sweep_result.md` | les **fichiers `.npz` trouvés** ont pu être relus ; le dénominateur dépend de ce qui existe | **ambigu → corrigé** |
| `nonml_capitulation_gate_floor_sweep_result.md` | les **284 scripts `nonml_*_backtest.py` du dépôt** ont été examinés, 0 illisible | **exact → laissé tel quel** |

Le second dit vrai : son volet A examine réellement la totalité des scripts, et
son volet B publie sa propre couverture séparément (62/62 depuis le #427).
**Je ne le touche pas.** Corriger une formulation exacte au motif qu'elle
ressemble à une formulation fautive serait du zèle, pas de la rigueur.

## Contrôles — fixés avant calcul

1. **Une seule ligne remplacée** dans le rapport du balayage. Le `diff` doit
   montrer **exactement 1 suppression**, et le texte inséré doit être celui
   ci-dessus, au caractère près.
2. **Tout le reste identique octet à octet** — décomptes, paires, section ajoutée
   au #428, répartition par schéma.
3. **Décomptes de doublons inchangés** : 218 séries, 3 groupes exacts,
   1 quasi-doublon.
4. **Le rapport du balayage de capitulation reste identique octet à octet** —
   contrôle explicite que le zèle n'a pas débordé.

## Critère de succès — chiffré

1. `diff` du rapport de doublons : **1 suppression, ≥ 1 insertion**, et rien
   d'autre modifié.
2. Texte inséré **identique** à celui pré-enregistré ci-dessus.
3. Décomptes **218 / 3 / 1** inchangés.
4. Rapport de capitulation : **0 différence**.

## Prédiction — déductive

Remplacer une chaîne de caractères dans la construction du rapport ne touche
aucun calcul ni aucun seuil.

> **Attente : 1 suppression, décomptes inchangés, 0 différence sur le jumeau.**

## Engagements

1. Résultat rapporté tel quel, y compris si le `diff` déborde de la ligne prévue.
2. **Le texte de remplacement n'est pas modifié après avoir vu le rendu.** S'il
   se révèle imparfait, je le publie tel qu'annoncé et note le défaut.
3. Aucun seuil de détection touché, aucun verdict modifié.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
