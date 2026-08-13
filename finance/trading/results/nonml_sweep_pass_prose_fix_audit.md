# Audit indépendant — la phrase calculée du balayage (#446)

**Critère 2** : chaque nom publié est vérifié **indépendamment**. Cet audit
ne lit ni le balayage ni le script de cycle — il repart du dépôt, refait le
raisonnement, puis compare.

Un nom publié doit satisfaire **les trois** conditions :
(a) script de backtest non-ML du dépôt ; (b) aucun `.npz` à son nom ;
(c) rapport portant un PASS.

## Vérification nom par nom

| Nom publié | (a) script | (b) sans `.npz` | (c) PASS | Verdict |
|---|---|---|---|---|
| `capitulation_gate_floor_sweep` | ✔ | ✔ | ✔ | **vérifié** |
| `npz_report_consistency_baskets` | ✔ | ✔ | ✔ | **vérifié** |
| `protocol_inventory` | ✔ | ✔ | ✔ | **vérifié** |
| `sweep_pass_prose_fix` | ✔ | ✔ | ✔ | **vérifié** |
| `tom_decomposition_overlay` | ✔ | ✔ | ✔ | **vérifié** |

## L'ensemble est-il complet et sans excédent ?

- attendus par la reconstruction indépendante : **5**
- publiés par le rapport : **5**
- **manquants** (attendus, non publiés) : **0**
- **en trop** (publiés, non attendus) : **0**

Les deux ensembles **coïncident exactement**. Le contrôle porte sur
l'ensemble, pas seulement sur le compte : un même effectif avec des noms
différents aurait échoué ici.

## Verdict de l'audit

**CONFORME** — chaque nom publié satisfait
les trois conditions, et l'ensemble publié coïncide avec l'ensemble reconstruit
indépendamment.

### Ce que cet audit ne prouve pas

Il vérifie que la phrase **dit vrai**, pas que la situation soit saine. Un des
noms vérifiés — `tom_decomposition_overlay` — est une **stratégie PASS sans**
**`.npz`**, donc hors de portée du balayage de doublons. La phrase le nomme
désormais correctement ; le problème qu'elle nomme reste entier.
