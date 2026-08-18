# La convention d'auto-déclaration : **récente ou abandonnée ?** (pré-enregistré)

Le **#483** a constaté que **113** pré-enregistrements sur 126 ne portent
aucune auto-déclaration, et a écrit qu'ils **« ne sont pas fautifs »**
parce que la convention *« date d'un moment du projet, pas de son
origine »*. **Il ne l'a pas vérifié.** C'est une hypothèse commode ; la
voici mise à l'épreuve.

## La population, datée

La commande de datation, pour qu'un lecteur la refasse :

```
git log --diff-filter=A --reverse --format=%ct \
    -- finance/trading/PREREG_<nom>.md   # premier commit d'ajout
```

- `PREREG_` du dépôt *(hors celui-ci)* : **461**
- **datés** : **461** — **non datables** : **0**
- **déclarés** : **33** — **non déclarés** : **428**

## Les deux médianes, côte à côte

*L'engagement 3 l'exige : jamais la seule favorable.*

| Groupe | Effectif | Date médiane d'introduction |
|---|---|---|
| **déclarés** | 33 | **13/08/2026** |
| **non déclarés** | 428 | **04/08/2026** |

- part des déclarés parmi les **40** plus récents : **7,5 %**

## La lecture retenue

Le critère, **fixé avant mesure** :

- **A** si `m_d > m_n` **et** `p ≥ 50 %` ;
- **B** si `m_d < m_n` **et** `p < 20 %` ;
- **C** sinon.

> ### **C** — **Aucune structure temporelle** — usage irrégulier

Le critère n'a **pas** été atteint : la part des déclarés parmi les
**40** plus récents est de **7,5 %**, très
au-dessous du seuil de 50 % qu'exigeait la lecture A.

**Mais la chronologie ci-dessous dit autre chose que mes deux
médianes**, et je dois le publier contre mon propre critère :

- **premier `PREREG_` déclaré** : 13/08/2026 ;
- pré-enregistrements introduits **avant** cette date : **380**, dont **déclarés : 0**.

> **La bascule existe, et elle est nette.** Aucun des **380** pré-enregistrements antérieurs au 13/08/2026 ne
> porte d'auto-déclaration ; **tous les déclarés lui sont
> postérieurs**. La phrase du #483 — « la convention date d'un
> moment du projet » — est **corroborée**, pas infirmée.

**Ce qui échoue, c'est mon critère, pas son hypothèse.** J'avais
exigé que la convention **domine** les 40 plus récents (≥ 50 %)
pour la dire « récente ». Elle est récente **et minoritaire même
dans sa propre période** — un cas que mes trois lectures ne
prévoyaient pas.

> **Le seuil était arbitraire et préalable ; il reste appliqué tel
> quel.** Le verdict **C** tient, et je publie à côté le fait qui
> aurait donné **A** avec un seuil plus bas. Choisir ce seuil
> maintenant serait exactement le retuning que ces cycles
> refusent depuis le #480.

## La chronologie, par tranches

*Publiée pour que le lecteur juge la lecture sur pièce plutôt que sur
deux médianes.*

| Tranche (par ordre d'introduction) | Période | Déclarés | Part |
|---|---|---|---|
| 1–76 | 28/07/2026 → 29/07/2026 | **0 / 76** | 0,0 % |
| 77–152 | 29/07/2026 → 30/07/2026 | **0 / 76** | 0,0 % |
| 153–228 | 30/07/2026 → 05/08/2026 | **0 / 76** | 0,0 % |
| 229–304 | 05/08/2026 → 06/08/2026 | **0 / 76** | 0,0 % |
| 305–380 | 06/08/2026 → 13/08/2026 | **0 / 76** | 0,0 % |
| 381–456 | 13/08/2026 → 18/08/2026 | **33 / 76** | 43,4 % |
| 457–461 | 18/08/2026 → 18/08/2026 | **0 / 5** | 0,0 % |

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| lecture A retenue | A | C | **réfutée** |
| part des déclarés récents ≥ 50 % | ≥ 50 % | 7,5 % | **réfutée** |
| aucun `PREREG_` ne résiste à la datation | 0 | 0 | **vérifiée** |

## Critères de succès

1. **461/461** datés, échecs publiés et comptés (**0**) — **OUI**.
2. Deux médianes et part `p` publiées, avec la commande — **OUI**.
3. Une lecture nommée par le critère chiffré — **OUI**.
4. Phrase du #483 rétractée si lecture B — **sans objet**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).