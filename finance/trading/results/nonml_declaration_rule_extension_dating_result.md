# Rejouer le #483 sous la règle **tolérante** (pré-enregistré)

## Les deux règles, citées verbatim

```python
LITTERALE = "Cycle d[e'’]\\s*\\*\\*([^*]+)\\*\\*"   # celle du #483
TOLERANTE = "\\*\\*Cycle d[e'’]\\s*([^*]+)\\*\\*|Cycle d[e'’]\\s*\\*\\*([^*]+)\\*\\*"   # celle du #492
```

## Le critère du #483, cité mot pour mot — **inchangé**

> **A** si `m_d > m_n` **et** `p ≥ 50 %` ; **B** si `m_d < m_n` **et** `p < 20 %` ; **C** sinon, où `p` est la part des déclarés parmi les **40**
> plus récents.

**Aucun seuil ne bouge.** Seul le détecteur change.

## Une seule population, re-dérivée aujourd'hui

- `PREREG_` datés *(hors celui-ci)* : **473**
- non datables : **0**

> Le garde-fou du pré-enregistrement : sans population commune, un écart
> confondrait **effet de détecteur** et **croissance du dépôt**.

## Les deux mesures, côte à côte

| Règle | Déclarés | Non déclarés | `m_d` | `m_n` | `p` (40 récents) | Verdict |
|---|---|---|---|---|---|---|
| **littérale** | **36** | **437** | 13/08/2026 | 05/08/2026 | **7,5 %** | **C** |
| **tolérante** | **78** | **395** | 14/08/2026 | 04/08/2026 | **92,5 %** | **A** |

- écart de détection : **+42** déclarés, **+85,0** points sur `p`

> Règle **littérale** → **C** — **aucune structure temporelle** — usage irrégulier.
> Règle **tolérante** → **A** — convention **récente et dominante**.

**Le verdict change avec le détecteur**, à critère strictement
identique : **C** en littérale, **A** en tolérante.

> Le #483 n'a pas conclu de travers par erreur de raisonnement : il a
> conclu sur ce que son détecteur lui montrait. **Une typographie a
> tenu lieu de fait**, et son verdict **C** est resté au dossier
> jusqu'ici. *(Aucun nombre de cycles n'est avancé : je ne l'ai pas
> compté.)*

## Le « 380 antérieurs, 0 déclaré » du #483, re-testé

- date du **premier déclaré littéral** : **13/08/2026**
- pré-enregistrements **antérieurs** à cette date : **380**
- parmi eux, **déclarés au sens tolérant** : **0**

> **Le « 380 / 0 » survit.** Même en tolérant la typographie, aucune
> déclaration ne précède cette date : la bascule que le #483
> décrivait est **réelle**, et son détecteur ne l'avait pas inventée.

## La chronologie, sous les deux règles

| Tranche | Période | Littérale | Tolérante |
|---|---|---|---|
| 1–67 | 28/07/2026 → 29/07/2026 | **0 / 67** | **0 / 67** |
| 68–134 | 29/07/2026 → 30/07/2026 | **0 / 67** | **0 / 67** |
| 135–201 | 30/07/2026 → 04/08/2026 | **0 / 67** | **0 / 67** |
| 202–268 | 04/08/2026 → 05/08/2026 | **0 / 67** | **0 / 67** |
| 269–335 | 05/08/2026 → 06/08/2026 | **0 / 67** | **0 / 67** |
| 336–402 | 06/08/2026 → 13/08/2026 | **13 / 67** | **13 / 67** |
| 403–473 | 13/08/2026 → 18/08/2026 | **23 / 71** | **65 / 71** |

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| verdict **A** sous la tolérante | A | A | **vérifiée** |
| le « 380 / 0 » ne survit pas | ≥ 1 | 0 | **réfutée** |
| la littérale reste **C** aujourd'hui | C | C | **vérifiée** |

La prédiction 3 est le **contrôle** de ce cycle : la littérale rendant
le même verdict qu'au #483 sur une population plus grande, l'écart
mesuré vient bien du **détecteur** et non de la croissance du dépôt.

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Les seuls appels externes visent `git log` et `git status`, **en lecture**.

## Critères de succès

1. Les deux règles citées verbatim, critère du #483 mot pour mot — **OUI**.
2. Une seule population (**473**) pour les deux mesures — **OUI**.
3. Les deux verdicts publiés (**C** / **A**) — **OUI**.
4. Le « 380 / 0 » du #483 re-testé et son sort publié — **OUI**.
5. Aucun script du dépôt exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution.
