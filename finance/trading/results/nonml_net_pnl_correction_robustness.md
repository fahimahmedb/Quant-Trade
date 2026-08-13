# Robustesse — la conclusion du #445 tient-elle hors du seuil du balayage ?

**Étape 7a. Ce n'est pas un retuning.** Le seuil du balayage reste **0,9999**,
inchangé par ce rapport. On vérifie seulement que la conclusion « la correction
ne déplace aucun appariement » n'est pas un artefact de ce seuil précis.

La grille a été fixée **avant exécution**. Une perturbation de ±20 % n'a pas de
sens sur une corrélation (0,9999 × 1,2 > 1) : la perturbation pertinente est de
**desserrer** le seuil par ordres de grandeur, ce qui augmente le nombre
d'appariements et rend donc la conclusion **plus difficile** à tenir.

| Seuil | Groupes avant | Groupes après | Groupes identiques | Paires exactes id. | Paires quasi id. | quasi (av./ap.) |
|---|---|---|---|---|---|---|
| **0.9999** *(seuil du balayage)* | 3 | 3 | oui | oui | oui | 1 / 1 |
| **0.999** | 3 | 3 | oui | oui | oui | 8 / 8 |
| **0.99** | 3 | 3 | oui | oui | oui | 144 / 144 |
| **0.95** | 3 | 3 | oui | oui | oui | 412 / 412 |
| **0.9** | 3 | 3 | oui | oui | oui | 781 / 781 |

## Plateau, pas pic

Sur **toute** la grille, la correction laisse les appariements inchangés —
y compris aux seuils desserrés, où le balayage apparie beaucoup plus de
paires et où un déplacement aurait donc été plus probable.

La conclusion du #445 ne dépend pas du seuil : elle tient parce que la série
corrigée n'a **qu'une seule** série de même longueur dans tout le dépôt, avec
une corrélation de **+0,017** — très loin de n'importe quel seuil plausible.

## Ce que ce rapport ne montre pas

Il perturbe **un** paramètre — le seuil de corrélation. La conclusion dépend
aussi du filtre de **longueur égale** (deux séries de tailles différentes ne
sont jamais comparées), qui n'est pas un seuil réglable mais une règle du
balayage. C'est elle, plus que le seuil, qui isole la série corrigée.
