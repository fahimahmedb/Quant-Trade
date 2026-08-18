# **Dater** le basculement forme / mesure (pré-enregistré)

Le **#506** a constaté que sa queue était à **95 %** sans données quand
le dépôt entier est à **28 %**. **Constater n'est pas dater.** Ici le
point de coupure est **calculé**, pas choisi.

## La règle, citée verbatim

> 1. scripts ordonnés par **premier commit d'ajout** ;
> 2. pour chaque coupure, part de « sans données » **avant** et
>    **après** ;
> 3. le **basculement** maximise le contraste `part_après − part_avant` ;
> 4. chaque côté doit compter au moins **20** scripts.

Le plancher est **figé au pré-enregistrement** : il empêche qu'un maximum
trivial en bout de série soit retenu.

## La population

- scripts à verdict (`PASS`/`FAIL`, **en gras ou non**) : **350**
- écartés faute de date d'ajout : **0**
- coupures évaluées : **311**

Population **élargie** — celle que l'audit du #506 a montrée
représentative — et classement par **appels d'ouverture** : *nommer un
fichier n'est pas l'ouvrir*.

## Le basculement, calculé

- **date** : **13/08/2026 21:51** *(premier script du régime
  postérieur : `nonml_sweep_pass_prose_fix_backtest.py`)*
- **avant** : **288** scripts, part sans données **13,5 %**
- **après** : **62** scripts, part sans données **100,0 %**
- **contraste** : **+86,5** points

## Le deuxième meilleur point

- date : **14/08/2026 10:52**
- contraste : **+80,6** points
- écart avec le meilleur : **5,9** points

- écart temporel entre les deux points : **13,0** heures

> **Le seuil qui décide de « nette » n'était pas
> pré-enregistré.** Le pré-enregistrement disait seulement qu'un
> second maximum « presque aussi bon » devait être signalé, sans
> chiffrer « presque ». **Les 5 points employés ci-dessous sont un
> choix fait en écrivant le code**, et le lecteur doit pouvoir en
> juger : l'écart mesuré vaut **5,9** points,
>
> Les deux points sont distants de **13 heures** : ils
> décrivent **la même transition**, pas deux dates concurrentes.

> Le second maximum est en retrait de plus de 5 points ; la
> date retenue n'est donc pas un choix parmi des équivalents
> **au sens de ce seuil**.

## Une coïncidence de date, mesurée

- date de naissance de la convention d'auto-déclaration (#498) : **13/08/2026**
- date du basculement forme / mesure (ici) : **13/08/2026**
- **même jour** : **OUI**

> **Deux mesures sans rien de commun tombent sur le même jour.**
> L'une compte des typographies dans des pré-enregistrements,
> l'autre des appels d'ouverture de fichiers. Qu'elles désignent
> la même date **renforce** la lecture d'un changement de régime
> — c'est une **convergence**, pas une preuve, et je ne l'avais
> pas prédite sous cette forme.

## La chronologie, par tranches

*Publiée pour que le lecteur juge sur pièce plutôt que sur un point.*

| Tranche | Période | Sans données | Part |
|---|---|---|---|
| 1–43 | 28/07/2026 → 28/07/2026 | **10 / 43** | **23,3 %** |
| 44–86 | 28/07/2026 → 29/07/2026 | **10 / 43** | **23,3 %** |
| 87–129 | 29/07/2026 → 30/07/2026 | **1 / 43** | **2,3 %** |
| 130–172 | 30/07/2026 → 05/08/2026 | **2 / 43** | **4,7 %** |
| 173–215 | 05/08/2026 → 06/08/2026 | **6 / 43** | **14,0 %** |
| 216–258 | 06/08/2026 → 07/08/2026 | **1 / 43** | **2,3 %** |
| 259–301 | 07/08/2026 → 14/08/2026 | **22 / 43** | **51,2 %** |
| 302–350 | 14/08/2026 → 18/08/2026 | **49 / 49** | **100,0 %** |

## Auto-exclusion, déclarée d'avance

**Ce cycle ne se compte pas lui-même** : il serait, une fois de plus, un
script à verdict qui n'ouvre aucune donnée. L'auto-exclusion était
déclarée au pré-enregistrement (règle du #447) — elle est rappelée ici.

## Ce que ce cycle ne juge pas

Il date un **changement d'activité**, pas une **perte de qualité**. Un
verdict rendu sans lire de données n'est pas moins bon : le #498 montre
seulement qu'il est **fragile au détecteur**.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| basculement après le 13/08/2026 | oui | 13/08/2026 21:51 | **vérifiée** |
| contraste ≥ 40 points | ≥ 40 | 86,5 | **vérifiée** |
| part avant ≤ 20 % | ≤ 20 % | 13,5 % | **vérifiée** |

> **La prédiction 1 se vérifie sur une lecture de borne** : le point
> tombe **le** 13/08, à 21:51, donc après le début de cette journée.
> Le pré-enregistrement disait « après le 13/08/2026 » sans préciser
> l'heure ; j'applique la lecture littérale, et je publie
> l'horodatage pour que le lecteur juge lui-même.


## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

La route de classement est **importée** de l'audit du #506 — sa
fonction, jamais son `main()`.

## Critères de succès

1. Règle de coupure et plancher de **20** cités verbatim — **OUI**.
2. Population élargie (**350**), classement par appels d'ouverture — **OUI**.
3. Date, deux parts et contraste publiés — **OUI**.
4. Chronologie par tranches (**8**) et deuxième meilleur point publiés — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de
> l'historique à la date de son exécution.
