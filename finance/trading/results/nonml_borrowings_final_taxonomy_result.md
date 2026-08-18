# Une **taxonomie complète** des emprunts, et la classe qui manquait

L'audit du **#505** a montré que les derniers « introuvables » ne le
sont pas : leur nombre **existe** dans le dépôt, mais **jamais au
voisinage de son sujet**. **Ce statut n'avait pas de classe.**

> Six cycles ont produit six vocabulaires successifs. Celui-ci en fixe
> **un seul**, appliqué à **toute** la population.

## Les quatre classes, citées verbatim

| Classe | Condition |
|---|---|
| **A** | sourcé **au sujet**, dans le cycle cité |
| **B** | sourcé **au sujet**, ailleurs |
| **C** | **orphelin de contexte** — le nombre existe, jamais au sujet |
| **D** | **absent du dépôt** — le nombre n'apparaît nulle part, même nu |

**« Au sujet »** = nombre en gras (ou **nu**, pour les `PREREG_`) avec
**≥ 2** mots-clés dans **±200 caractères**
— règle du #502, **paramètres inchangés** *(quatrième cycle
consécutif)*.

## Le classement

- nombres empruntés : **39**
- sections de registre : **304** ; rapports : **1588** ; pré-enregistrements : **483**

| Classe | Nombre | Part |
|---|---|---|
| **A** | **11** | **28,2 %** |
| **B** | **26** | **66,7 %** |
| **C** | **2** | **5,1 %** |
| **D** | **0** | **0,0 %** |

- **partition** : somme **39** = effectif **39** — **OUI**

## Le contrôle : les 2 résidus du #505

Ils doivent tomber en **C** — sinon la taxonomie **ne recouvre pas le
fait qui l'a motivée**.

| Script | Cite | Nombre | Classe rendue | Où le contexte a été trouvé |
|---|---|---|---|---|
| `nonml_content_defined_magnitudes_audit.py` | `#449` | **2** | **B** | `nonml_content_defined_magnitudes_audit.md` |
| `nonml_report_idempotence_backtest.py` | `#443` | **5,7** | **B** | `nonml_hardcoded_figures_remainder_result.md` |

> **Le contrôle échoue** : les deux cas tombent en **B**, pas en **C**.

**La cause est mesurée, pas invoquée.** La colonne « où » le montre :
le contexte est trouvé dans une source qu'**aucun cycle précédent
n'avait consultée**. Les #501-#503 ont fouillé les **sections** du
registre ; le #504, les **rapports du cycle cité** ; le #505, les
`PREREG_` et les commits. **Personne n'avait cherché au sujet dans
les rapports des *autres* cycles** — ce que la classe **B** fait ici.

> **Ce n'est donc pas la taxonomie qui est mal construite, c'est ma
> prémisse.** J'ai posé comme contrôle que ces deux cas *devaient*
> tomber en **C**, en supposant que **B** ne les trouverait pas. **B**
> est plus large que tout ce que la série avait tenté, et il les
> trouve.
>
> **Le critère pré-enregistré fait néanmoins échouer ce cycle, et je
> l'applique tel quel.** Un contrôle qu'on réinterprète après l'avoir
> vu échouer ne contrôle plus rien — c'est la règle depuis le #480,
> et elle coûte ici un **FAIL** sur un classement que je crois juste.

## Les orphelins de contexte, nommés

- effectif : **2**

| Script | Cite | Nombre | Extrait |
|---|---|---|---|
| `nonml_content_defined_magnitudes_backtest.py` | `#451` | **6** | « | #451 | **6** porteurs | **** à `` |… » |
| `nonml_reproducibility_sample_lot2_audit.py` | `#434` | **8,0** | « | **#434 + #435** | **** | ** %** | **8,0 %** |… » |

> **« Orphelin » ne veut pas dire « faux ».** Il veut dire : *je n'ai
> pas su rattacher ce nombre à un passage qui parle du même sujet*.
> Six cycles ont montré que la distinction est **tout** — et le
> pré-enregistrement interdisait de la durcir après coup.

## La classe B, et son sourçage circulaire

- emprunts en **B** : **26**
- dont le contexte est trouvé dans le **rapport du script lui-même** : **5**
- dont dans une source **tierce** : **21**

> **Le #505 avait établi la règle : trouver un chiffre dans sa propre
> production ne le source pas.** Même auteur, même cycle, même erreur
> possible. Ces **5** classements en **B** sont
> donc **circulaires**, et la classe B les surestime d'autant.

> Je **ne les reclasse pas** : la taxonomie a été figée avant mesure,
> et exclure le rapport du script après coup serait la dérive refusée
> aux #496, #497 et #507. **C'est enregistré comme angle mort.**

## La classe dominante

- classe la plus nombreuse : **B** (**26**)

> **La classe dominante est B, pas A.** La majorité des
> emprunts de ce dépôt **ne se justifient pas par le cycle qu'ils
> citent** — c'est plus grave que tout ce que la série a établi, et
> je l'écris sans l'atténuer.
>
> **Une nuance mesurée, pas une atténuation** : **5** des
> **26** classements en B sont **circulaires** (contexte
> trouvé dans le rapport du script lui-même). Le compte de B qui
> pointent vers une source **tierce** est **21**.

## Ce que cette taxonomie remplace — et ce qu'elle ne remplace pas

Elle **unifie** six vocabulaires ad hoc en un seul, exclusif et
exhaustif. Elle ne **réécrit pas** les rapports des #501-#505 : leurs
classes restent telles qu'elles ont été publiées, avec leurs erreurs et
leurs corrections. **Réécrire l'histoire d'une série pour la rendre
cohérente serait le contraire de ce qu'elle a fait.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| la classe **D** est vide | 0 | 0 | **vérifiée** |
| la classe **C** compte ≥ 2 | ≥ 2 | 2 | **vérifiée** |
| **A** est la plus nombreuse | A | B | **réfutée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population, mots-clés, fenêtres et correspondance cycle → rapport sont
**importés** des backtests des #500 à #504 — leurs fonctions, jamais
leur `main()`.

## Critères de succès

1. Quatre classes citées verbatim, paramètres du #502 inchangés — **OUI**.
2. Les **39** classés, partition vérifiée (**39** = **39**) — **OUI**.
3. Les **2** résidus du #505 classés **C** — **NON**.
4. Membres de **C** nommés individuellement (**2**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**FAIL** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du
> registre et des rapports à la date de son exécution.
