# Pré-enregistrement — reproductibilité, lot 2 (resserrer la borne du #434)

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## Ce que le #434 a laissé ouvert, chiffré

Le #434 a tiré **12** scripts et les a trouvés **12/12 identiques** octet à
octet. Mais son audit a publié la limite de ce résultat :

> **p ≤ 22,1 %** à 95 % de confiance — **p ≤ 23,8 %** en ne comptant que les
> **11** vérifications réellement neuves.

Autrement dit : un problème **massif** est écarté, un problème **fréquent** ne
l'est pas. La dette a été *mesurée*, pas soldée, et le seul moyen de resserrer la
borne est d'**échantillonner davantage**.

## Ce lot — taille et graine fixées maintenant

> **24** scripts tirés avec la graine **20260814**, parmi les éligibles
> **privés des 12 déjà testés au #434**.

L'exclusion est essentielle : retirer les mêmes scripts n'apporterait aucune
information neuve. Le vivier exclut aussi les artefacts des cycles
`reproducibility_sample*` eux-mêmes — leçon du #434, où le cycle s'était ajouté
à son propre vivier et avait décalé le tirage.

Délai maximal **300 s** par script, repris tel quel du #434. Au-delà :
**« non concluant »**, ni réussite ni échec.

## La borne visée — annoncée avant de mesurer

Si les 24 se reproduisent, le total **sans divergence** passe à **36** scripts
distincts (12 + 24), et la borne devient :

| Total sans divergence | Borne à 95 % |
|---|---|
| 12 (#434) | 22,1 % |
| **36 (après ce lot)** | **8,0 %** |

En ne comptant que les vérifications réellement neuves (**11** au #434 + 24 =
**35**), la borne prudente serait **8,2 %**.

Je publie ces valeurs **avant** de mesurer pour ne pas pouvoir présenter après
coup n'importe quel chiffre comme « une nette amélioration ».

**Si une divergence apparaît**, la borne ne s'applique plus : le résultat
principal du cycle devient la divergence elle-même, et je publierai le `diff`.

## Régime — identique au #434, et non assoupli

> Chaque rapport est **sauvegardé**, comparé, puis **restauré à l'identique**.
> En fin de cycle, `git status` doit être **vide** de toute modification de
> `results/*_result.md`.

Une divergence serait **publiée et analysée, jamais committée** : corriger un
résultat publié demanderait son propre pré-enregistrement et son propre régime
déclaré, comme aux #428, #429 et #430.

## Une réserve sur la borne, dite d'avance

La formule `p ≤ 1 − 0,05^(1/N)` suppose des tirages **indépendants**. Ici
l'échantillonnage est **sans remise** dans un vivier fini (~285), et les deux
lots sont disjoints par construction. Dans ce cadre la borne binomiale est
**conservatrice** — elle surestime légèrement `p`. Je la garde telle quelle
plutôt que de la raffiner : une borne prudente qui se trompe du côté sévère est
préférable à une borne optimisée après coup.

## Critère de succès — chiffré

1. **24** scripts tirés avec la graine annoncée, la liste publiée **avant** les
   résultats individuels.
2. Chacun classé : **identique**, **divergent** (avec son `diff`), ou **non
   concluant** (délai / erreur, avec le message).
3. `git status` **vide** de toute modification de `results/*_result.md`.
4. Borne recalculée et publiée sur le **cumul des deux lots**, avec sa version
   prudente.

## Prédiction

**Aucune prédiction chiffrée.** Le #434 n'a rien trouvé sur 12 tirages ; cela ne
dit rien de 24 autres, tirés dans le même vivier mais disjoints. Prédire sans
base m'a déjà trompé deux fois (#407, #408).

## Engagements

1. Résultat rapporté tel quel, y compris **24/24 identiques** — auquel cas
   j'écrirai la borne obtenue sans la présenter comme une preuve.
2. Aucun script exclu du tirage après l'avoir vu.
3. Aucun rapport publié modifié ni committé par ce cycle.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
