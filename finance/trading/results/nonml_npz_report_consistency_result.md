# Concordance entre le P&L sauvegardé et les chiffres publiés (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## La question posée, et pourquoi elle est neuve

La campagne #434-#441 comparait le **rapport à son code** : ré-exécuté, le script
reproduit-il son rapport ? Oui, borne 4,2 % sur 69 tirages.

**Ce cycle pose une question différente** : le `.npz` sauvegardé produit-il les
chiffres que le rapport annonce ? Un script peut se reproduire parfaitement et
sauvegarder une série qui ne correspond pas à la stratégie décrite. Les balayages
qui consomment ces `.npz` (doublons #406, activation #415, batterie Règle 9)
seraient alors alimentés par des séries fausses **sans qu'aucun ne s'en aperçoive**.

## Couverture

- `.npz` trouvés : **208**
- **examinés** (position scalaire + rapport publié) : **165**
- écartés : **43**

| Raison d'écartement | Nombre |
|---|---|
| schéma panier (pas de position scalaire) | **23** |
| aucun rapport publié | **20** |

## Résultat

| | Nombre |
|---|---|
| **concordants** (Sharpe du `.npz` publié au rapport) | **165** |
| **discordants** | **0** |

**Taux de concordance : 100.0 %** sur 165 examinés.

Dont **5** dont la concordance était **connue d'avance** (essais de
faisabilité menés avant le pré-enregistrement) : ils restent comptés, mais ne
constituent pas une vérification neuve. Vérifications neuves : **160**.

## Aucun discordant

Tous les `.npz` examinés produisent un Sharpe qui figure dans leur rapport.
**C'est une absence, pas un exploit** : elle signifie que les séries
consommées par les balayages correspondent bien aux stratégies décrites, sur
le périmètre examiné.

## Portée

Le contrôle porte sur **165** `.npz` à position scalaire, dont
**158** au schéma indiciel et **7**
au schéma « deux jambes », chacun reconstruit avec **sa** formule.

**Défaut attrapé par l'inspection des discordants** : le premier passage
appliquait la formule indicielle à tous les fichiers portant `pos` et `r_asset`,
y compris ceux qui portent en plus `r_alt`. Il produisait **7 discordants**, tous
de ce type, tous redevenus concordants avec la formule du #406. Le
pré-enregistrement annonçait des faux positifs — il en attendait d'un rapport
multi-marchés, ils sont venus d'ailleurs.

Les schémas **panier** n'ont pas de position scalaire et restent **écartés, pas
ignorés** : leur nombre figure au tableau de couverture.
