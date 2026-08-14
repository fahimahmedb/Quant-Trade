# Audit — persistance du P&L, lot 4 : les 2 derniers candidats du #415 (pré-enregistré)

Cycle d'**infrastructure**. Aucune stratégie évaluée, aucun verdict recalculé.
Cet audit ne rejoue pas les backtests : il relit les `.npz` produits et les
confronte aux rapports publiés par les candidats eux-mêmes.

## Le motif inscrit à la file était faux

La file du #425 conditionnait ce cycle au retour de « sources externes ».
Vérification par lecture du code, faite **avant** le pré-enregistrement :
les deux candidats ne lisent que des fichiers **locaux et présents**. Leur
`.npz` manquait parce que la sauvegarde était placée sous `if verdict:` et
que les deux portent un **FAIL** — le cas banal des #416, #423 et #424.

Quatrième récidive du défaut de chiffre recopié sans re-vérification
(#417, #420, #425, celui-ci), et la phrase fautive a été écrite au #425,
dans le cycle même où j'énonçais la règle l'interdisant.

## Contrôle de non-régression — 2/2 identiques octet à octet

Vérifié par comparaison binaire des `results/nonml_<nom>_result.md` avant et
après ré-exécution. Prédiction déductive du pré-enregistrement **confirmée**,
comme aux #416 (10/10), #423 (4/4) et #424 (12/12).

**Vingt-huit résultats publiés** ont désormais été testés contre leur propre
code par ces quatre lots.

## Mesure — activation des 2 candidats, et discrimination du #416

| Candidat | Séances | Exposition > 1,0× | Inactif (< 2 %) | Séances P&L ≠ B&H | Verdict |
|---|---|---|---|---|---|
| `rebound_speed_breadth_vol_targeting_overlay` | 1385 | 23.90 % | non | 378 / 1384 | FAIL |
| `vix_regime_vol_targeting_overlay` | 9197 | 16.88 % | non | 1855 / 9196 | FAIL |

- nouveaux candidats **structurellement inactifs** : **0**
- dont P&L **strictement identique** à Buy & Hold (overlay neutralisé) : **0**
- nouveaux **PASS vides** : **0** (les 2 portent un FAIL, aucun ne pouvait l'être)

### Contrôle de cohérence — le `.npz` contre le rapport du candidat

Le `.npz` doit reproduire un chiffre que le rapport publiait déjà, calculé
indépendamment par le script du candidat. Contrôle ajouté à cet audit parce
qu'un `.npz` produit sans être confronté à rien ne prouve rien.

| Candidat | Séances au rapport | Séances au `.npz` | Accord |
|---|---|---|---|
| `rebound_speed_breadth_vol_targeting_overlay` | 1385 | 1385 | ✔ |
| `vix_regime_vol_targeting_overlay` | 9197 | 9197 | ✔ |

**2/2 en accord.**
Le nombre de séances stocké coïncide avec celui que le rapport annonçait :
le `.npz` porte bien la série du candidat, pas une fenêtre décalée.

## Mesure — couverture du volet B du balayage #415

| | Avant | Après |
|---|---|---|
| candidats structurés (volet A) | 62 | 62 |
| **mesurés** (volet B) | 60 | **62** |
| non mesurés | 2 | **0** |

**Couverture complète : 62/62.** Le diagnostic du
#415 ne repose plus sur aucun candidat manquant. La dette ouverte au #406,
chiffrée puis réduite aux #416, #423, #424 et #425, est **soldée**.

### Effet sur le verdict du balayage

- candidats structurellement **inactifs** : **3**
- dont **PASS vides** : **3**

- `santa_vol_targeting_overlay` — activation 1.70 %, rapport : PASS
- `weakness_breadth_vol_targeting_overlay` — activation 0.00 %, rapport : PASS
- `weakness_breadth_vol_targeting_overlay_pit_universe` — activation 0.00 %, rapport : PASS

## Mesure — balayage de doublons rejoué sans modification

| | #424 | #426 |
|---|---|---|
| séries de P&L reconstruites | 200 | **218** |
| groupes de doublons exacts | 3 | **3** |
| quasi-doublons | 1 | **1** |

Les deux séries ajoutées n'introduisent **aucun doublon** : le décompte
d'hypothèses indépendantes est inchangé. Aucune prédiction n'avait été faite
sur ce point — je n'avais pas de base pour l'anticiper, et je le note comme
mesure, pas comme confirmation.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| scripts modifiés et `.npz` produit | 2/2 | 2/2 | ✔ |
| différences de résultat | 0 | 0 | ✔ |
| couverture du volet B | publiée | 62/62 | ✔ |
| cohérence `.npz` / rapport | — | 2/2 | ✔ |

La prédiction déductive « 0 différence, couverture 60 → 62/62 » est **vérifiée**,
chiffre de départ compris — il avait été re-mesuré au moment d'écrire le
pré-enregistrement, précisément parce que ce cycle documente le défaut inverse.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun. Les 2
candidats portent un FAIL avant comme après.
