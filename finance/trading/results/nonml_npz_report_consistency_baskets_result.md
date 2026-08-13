# Concordance `.npz` / rapport — schémas panier (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## Ce que ce cycle complète

Le #442 a vérifié **165/165** `.npz` à position scalaire, mais en écartait un lot
qu'il a étiqueté « **23 paniers** » faute de formule applicable. Ce sont les
stratégies de **portefeuille**, dont plusieurs portent un **PASS** : si leur
`.npz` ne correspondait pas à la stratégie décrite, le balayage de doublons du
#406 et la requalification du #422 seraient alimentés par des séries fausses.

**Cette étiquette était fausse.** Le balayage nominatif de ce cycle trouve
**21** fichiers au schéma panier, pas 23 : le #442 comptait
dans le même lot **2** fichiers d'un **troisième schéma**, jamais
catalogué (voir plus bas). Le compte du #442 était un *reste* de soustraction, pas
une énumération — le même défaut qu'au #428, où `284 − 208 = 76` soustrayait deux
ensembles non alignés.

Reconstruction par la formule du #419, **avec `log1p`** — les P&L de panier sont
des rendements simples, et l'omettre produirait un Sharpe qui n'est celui de
personne. C'est l'erreur de schéma qui a créé 7 faux discordants au #442.

## Couverture

- `.npz` au schéma **panier** : **21**
- **examinés** (rapport publié disponible) : **21**
- écartés : **0**

## Résultat

Critère **plus exigeant** qu'au #442 : concordant seulement si **les deux
jambes** — candidate et référence — se retrouvent dans le rapport.

| | Nombre |
|---|---|
| **concordants** (deux jambes) | **21** |
| **partiels** (une seule jambe) | **0** |
| **discordants** (aucune) | **0** |

**Taux de concordance complète : 100.0 %** sur 21 examinés.

Dont **6** connus d'avance (essais de faisabilité menés avant le
pré-enregistrement) : comptés mais signalés. Vérifications neuves : **15**.

## Aucun écart

Les deux jambes de chaque panier examiné se retrouvent dans son rapport.
**C'est une absence, pas un exploit** — mais elle porte sur un critère plus
strict que celui du #442, puisqu'elle exige deux valeurs et non une.

## Un troisième schéma, découvert hors périmètre

En vérifiant pourquoi le #442 annonçait 23 paniers et ce cycle en trouve
**21**, **2** fichiers apparaissent qui ne portent
**ni** position scalaire **ni** clés de panier :

| Fichier | Clés |
|---|---|
| `dollar_neutral_composite_pit` | `cost_bps`, `dates`, `pnl_candidate`, `pnl_ref`, `turn_candidate`, `turn_ref` |
| `dollar_neutral_composite_vol_targeted` | `cost_bps`, `dates`, `pnl_candidate`, `pnl_ref` |

Ces fichiers sont **hors du périmètre déclaré** de ce cycle, qui s'est engagé sur
le schéma panier. Ils sont **inscrits à la file, pas couverts** : les compter ici
reviendrait à élargir un critère après avoir vu ce qu'il attrape — exactement ce
que le #437 a refusé de faire.

Un coup de sonde **post-hoc, explicitement hors protocole**, mérite d'être
consigné parce qu'il rejoue le défaut du #442. La reconstruction naïve
(`pnl_candidate − turn_candidate × coût`) donnait une jambe absente du rapport.
Le pré-enregistrement engageait à me méfier **d'abord de ma reconstruction avant
d'accuser un rapport** : lecture du script d'origine, `pnl_candidate` y est
sauvegardé **déjà net** (`pnl_sleeve_net`), `turn_candidate` n'étant stocké que
pour information. Je soustrayais les coûts deux fois. Sans la seconde
soustraction, les deux jambes se retrouvent dans le rapport.

**Deuxième fois sur deux, dans cet axe, que l'écart vient de mon contrôle et non
du dépôt** (#442 : `r_alt` ignoré ; ici : coûts comptés deux fois). Cela n'établit pas que
ces deux fichiers sont concordants — un sondage hors protocole ne vaut pas
vérification —, seulement que le compte mécanique n'aurait pas dû être publié
comme un écart.

## Ce qui reste non couvert

Les `.npz` **sans rapport publié** (20 au #442) relèvent d'une inspection nom par
nom et **ne sont pas traités ici** — ce cycle ne prétend pas les couvrir.

Bilan des deux cycles de concordance :

| Périmètre | Examinés | Concordants |
|---|---|---|
| position scalaire (#442) | 165 | 165 |
| panier (#443) | 21 | 21 |
| **total** | **186** | **186** |
