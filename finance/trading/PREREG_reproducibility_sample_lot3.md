# Pré-enregistrement — reproductibilité, lot 3 (borne visée ~4,9 %) et représentativité en âge

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## La décision, prise sur le tableau chiffré du #435

Le #435 a publié le rendement décroissant pour que le choix d'un lot 3 ne se
prenne pas « à l'impression » :

| Total sans divergence | Borne | Divergents encore possibles (sur 285) |
|---|---|---|
| 36 (actuel) | 8,0 % | ~22 |
| **60 (après ce lot)** | **4,9 %** | **~13** |
| 150 | 2,0 % | ~5 |

Le gain visé est donc de **~22 → ~13** rapports divergents encore possibles. Il
est réel mais **modeste**, et je l'écris ainsi plutôt que de le vendre : c'est le
dernier lot dont le gain reste franc. Au-delà, chaque lot de 24 rapportera de
moins en moins.

## Le lot — taille et graine fixées maintenant

> **24** scripts tirés avec la graine **20260815**, parmi les éligibles
> **privés des 36 déjà testés** aux #434 et #435.

Délai maximal **300 s** par script, repris tel quel. Au-delà : **« non
concluant »**, ni réussite ni échec.

**Régime identique et non assoupli** : chaque rapport est sauvegardé, comparé,
puis **restauré à l'identique**. En fin de cycle, `git status` doit être vide de
toute modification de `results/*_result.md`.

## Une faiblesse de la borne que les deux premiers lots n'ont pas examinée

La borne suppose que les scripts testés sont **représentatifs** du dépôt. Or
l'hypothèse de risque la plus naturelle est que les rapports **anciens** divergent
davantage : le code partagé a évolué, et les corrections #375-#404 ont touché des
fonctions communes **après** la publication de beaucoup de rapports.

Si les 60 scripts tirés se trouvaient concentrés sur les rapports **récents**, la
borne serait rassurante à tort.

> **Mesure ajoutée, sans ré-exécution** : comparer la distribution des **dates de
> publication** (commit d'ajout) des scripts testés à celle du vivier entier.

C'est un contrôle de **métadonnées** — il ne coûte aucun calcul et ne peut pas
échouer « faute de temps ». Critère fixé avant mesure :

> Médiane d'âge des testés et du vivier, et proportion de testés parmi le
> **tiers le plus ancien** du vivier. Si cette proportion s'écarte de plus de
> **10 points** de la proportion attendue (part des testés dans le vivier), le
> tirage est déclaré **non représentatif en âge**, et la borne est publiée avec
> cette réserve.

Je fixe le seuil avant de regarder. Un tirage aléatoire uniforme *devrait* être
représentatif — ce contrôle vérifie que c'est bien le cas plutôt que de le
supposer.

## Critère de succès — chiffré

1. **24** scripts tirés avec la graine annoncée, liste publiée **avant** les
   résultats individuels.
2. Chacun classé : **identique**, **divergent** (avec son `diff`), ou **non
   concluant**.
3. `git status` **vide** de toute modification de `results/*_result.md`.
4. Borne cumulée sur **60** recalculée et publiée, avec sa version prudente.
5. Contrôle de représentativité en âge exécuté et publié, **quel que soit** son
   verdict.

## Prédiction

**Aucune prédiction chiffrée** sur les 24 tirages : 36 scripts sans divergence ne
disent rien de 24 autres.

Sur la représentativité, la prédiction est **déductive et faible** : un tirage
aléatoire uniforme sans remise devrait donner une proportion d'anciens proche de
l'attendu. Si l'écart dépassait 10 points, ce serait le signe d'un défaut dans ma
procédure de tirage plutôt qu'une propriété du dépôt — et ce serait alors le
résultat principal du cycle.

## Engagements

1. Résultat rapporté tel quel, y compris **24/24 identiques**.
2. Aucun script exclu du tirage après l'avoir vu.
3. Aucun rapport publié modifié ni committé.
4. Le seuil de 10 points n'est **pas** ajusté après avoir vu l'écart.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
