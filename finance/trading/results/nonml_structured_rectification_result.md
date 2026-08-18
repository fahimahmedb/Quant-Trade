# Un détecteur de rectification qui **survive au témoin négatif**

Le **#512** comptait un marqueur dans **±200 caractères** d'une
référence. Son témoin neutre a fait **mieux** — **89,3 %** contre
**59,4 %** — donc **le détecteur mesurait la densité du texte**, pas la
rectification. Ici, l'appariement exige une **même unité syntaxique**.

## Les deux règles structurelles, citées verbatim

> - **S1 — titre de section** : une ligne `##`/`###` contenant **à la
>   fois** une référence `#NNN` (`NNN < MMM`) et un marqueur ;
> - **S2 — assertion en gras** : un span `**…**` contenant **à la fois**
>   la référence et un marqueur, sur une même ligne.

**Marqueurs — identiques au #512, sans un mot de plus ni de moins** :

```
réfut   rétract   corrig   invalid   fauss   faux   erron   sur-affirm   surestim   sur-estim   dissou   tombe
```

**Témoin neutre — repris verbatim de l'audit du #512** :

```
cycle   rapport   mesure   script   publie   critère   verdict   audit   population   chiffre   règle   dépôt
```

## Les quatre taux

- sections de backlog : **309**

| Détecteur | Liste | Cycles rectifiés | Taux |
|---|---|---|---|
| **S1** | réel | **12** | **3,9 %** |
| **S1** | témoin | **51** | **16,5 %** |
| **S2** | réel | **14** | **4,5 %** |
| **S2** | témoin | **41** | **13,3 %** |

## Les deux écarts, et le verdict au seuil de **20 points**

| Détecteur | Écart réel − témoin | Verdict |
|---|---|---|
| **S1** | **-12,6** points | **ne passe pas** |
| **S2** | **-8,7** points | **ne passe pas** |

> Le seuil de **20 points** a été fixé **au pré-enregistrement**, avant
> toute mesure. **Le témoin négatif est ici un critère, pas un audit** —
> c'est la leçon du #512 institutionnalisée.

## Aucun détecteur ne passe

**Les deux prédictions sont réfutées.** Deux familles de méthodes —
**lexicale** (#512) et **structurelle** (ici) — échouent au même
test.

> **Le registre ne permet pas de mesurer son propre taux de
> rectification par appariement automatique.** C'est un résultat, pas
> un échec de cycle : la question du #509 est **close faute d'outil**,
> et non laissée ouverte par négligence.

### Pourquoi le témoin gagne — mesuré, pas invoqué

| Unité | Total | Portant une référence | dont marqueur | dont mot neutre |
|---|---|---|---|---|
| titres (`##`/`###`) | **1097** | **369** | **41** | **136** |
| spans `**…**` | **7679** | **646** | **80** | **102** |

> Parmi les unités qui **citent** un cycle, un **mot neutre** est
> présent bien plus souvent qu'un marqueur : `cycle`, `rapport`,
> `audit` appartiennent au vocabulaire ordinaire de toute phrase qui
> parle d'un cycle. **Le témoin ne gagne pas par hasard : il gagne
> parce que ces mots sont le tissu même du registre.**

**Une référence n'est pas une accusation**, et aucun appariement de
forme — voisinage ou unité syntaxique — ne sait faire la différence.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| **S1** bat son témoin de ≥ 20 pts | ≥ 20 | -12,6 | **réfutée** |
| **S2** bat son témoin de ≥ 20 pts | ≥ 20 | -8,7 | **réfutée** |
| taux du meilleur < 59,4 % | < 59,4 % | 4,5 % | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Marqueurs, liste neutre et découpage du registre sont **importés** des
#501, #512 et de son audit — leurs constantes, jamais leur `main()`.

## Critères de succès

1. Deux règles, marqueurs et liste neutre cités verbatim — **OUI**.
2. Les **quatre** taux publiés — **OUI**.
3. Les deux écarts publiés et tranchés au seuil de **20** points — **OUI**.
4. Tendance nommée si un détecteur passe, question déclarée ouverte sinon — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**, et **la valeur de
la mesure est elle-même publiée** : c'est la correction que le #512
appelait.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état du registre à la
> date de son exécution.
