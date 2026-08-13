# Requalification des PASS obtenus par inactivité (pré-enregistré)

Requalification **documentaire** : aucun verdict n'est recalculé ni annulé.
Le critère est l'**identité du P&L** avec Buy & Hold, pas un seuil
d'activation — distinction établie au #416.

## Couverture

- fichiers `nonml_*_pnl.npz` trouvés : **173**
- exploitables (schéma `pos` / `r_asset`) : **158**
- inexploitables (autre schéma) : **15**

Les schémas « panier » et « deux jambes » n'entrent pas dans ce balayage : leur
jambe de référence n'est pas Buy & Hold mais un portefeuille, et le critère
d'identité ne s'y transpose pas tel quel. C'est une limite de portée, pas un
oubli — elle est chiffrée ci-dessus.

## Résultat

- candidats **requalifiés** par ce cycle : **0**
- déjà étiquetés avant ce cycle : **2**
- PASS dont l'overlay **agit** (non requalifiables) : **72**

**Aucun candidat requalifié par ce cycle.**

Déjà étiquetés : `weakness_breadth_vol_targeting_overlay_pit_universe`, `weakness_breadth_vol_targeting_overlay`.

## Ce que le balayage établit

Sur **158** candidats mesurables, **72** portent un
PASS dont l'overlay agit réellement. Le cas de l'inactivité totale est donc
**isolé**, et non un travers répandu du backlog.

Le balayage a porté sur l'ensemble des `.npz` et non sur le seul cas connu du
#416 — restreindre la recherche à ce qui est déjà su est ce qui avait fait
manquer un foyer au #390, un portage au #395 et un doublon au #406.

> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).
