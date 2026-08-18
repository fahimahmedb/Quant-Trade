# Les **gardes sans témoin inconditionnel** (pré-enregistré)

Le **#478** avait établi la bonne question sans pouvoir la mesurer :

> **La ligne de partage n'est pas « section conditionnelle ou non »,
> mais « la garde a-t-elle un témoin inconditionnel ».**

Une section gardée dont l'effectif est publié **sans garde** ne disparaît
pas silencieusement. Une section **sans** ce témoin s'efface sans trace —
la forme qui a coûté **trois cycles** (#469, #472, #475).

## Le classement

- titres de section conditionnels : **58** *(#478 en comptait 58, écart **+0**)*
- **AVEC TÉMOIN** — la disparition est signalée : **36**
- **SANS TÉMOIN** — la section s'efface silencieusement : **14**
- **GARDE NON NOMMÉE** — hors de portée de ma règle : **8**

> **Les gardes non nommées ne sont dans aucun total de dette.** Ma règle
> ne sait traiter que la forme `if <var>:` ; une condition composée ou un
> test de valeur lui échappe, et **l'ignorance n'est pas une charge**.

> **Et « sans témoin » n'est pas une faute.** Une section peut
> légitimement n'exister que dans un cas particulier. Le défaut du #475
> est plus étroit : la section portait **l'unique mention de son sujet**.
> **Ma règle ne distingue pas les deux** — d'où l'examen ci-dessous.

## Les **14** sans témoin, nommés

| Script | Ligne | Garde | Titre |
|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | 159 | `if indet:` | ### Une limite de la règle unifiée, découverte ici |
| `nonml_citer_451_resolution_backtest.py` | 187 | `if meme:` | ### Un fait qui départage partiellement |
| `nonml_marker_emitter_crossing_backtest.py` | 175 | `if douteux:` | ### L'examen, mené — et il retire le seul citeur |
| `nonml_net_pnl_correction_backtest.py` | 279 | `if incoh:` | ### Une incohérence exposée par le rafraîchissement |
| `nonml_net_pnl_correction_robustness.py` | 76 | `if tous:` | ## Plateau, pas pic |
| `nonml_net_pnl_correction_robustness.py` | 86 | `if tous:` | ## La conclusion ne tient pas partout |
| `nonml_prereg_convention_coverage_backtest.py` | 174 | `if aucun_fichier:` | ### Les seuls cas sans aucun fichier |
| `nonml_prereg_convention_coverage_backtest.py` | 182 | `if autre_nom:` | ### Ceux dont le rapport existe autrement *(extrait  |
| `nonml_self_inclusion_detector_backtest.py` | 106 | `if rates:` | ### Pourquoi il l'a manqué — diagnostic, sans touche |
| `nonml_silent_skip_decision_backtest.py` | 119 | `if not a_modifier:` | ### **Décision : on ne touche à rien.** |
| `nonml_six_reports_regeneration_backtest.py` | 232 | `if perdus:` | ## Un effet de bord découvert — les marqueurs du #43 |
| `nonml_sweep_pass_prose_fix_backtest.py` | 134 | `if strategies:` | ## Le résultat qui prime sur la correction de prose |
| `nonml_verdict_detector_complete_robustness.py` | 124 | `if plateau:` | ### La question qu'il faut poser franchement |
| `nonml_verdict_detector_fix_backtest.py` | 248 | `if idem:` | ### Ce n'est pas un défaut de la correction — c'est  |

> **Contrôle positif.** `six_reports_regeneration` / `if perdus:` — **le
> cas exact du #475** — est bien classé *sans témoin* par la règle. Une
> règle qui l'aurait manqué serait à jeter.

## L'examen à la main — 5 cas, **déclarés avant mesure**

Le **#480** avait classé mécaniquement, découvert après coup que sa règle
avait mal lu, et **dû refuser le reclassement** faute d'examen déclaré.
**La leçon est appliquée ici** : le pré-enregistrement fixait l'ordre
(alphabétique du script, puis ligne croissante) et le verdict binaire.

### `nonml_battery_coverage_backtest.py` l.159 — **MASQUANT**

Garde : `if indet:` — section : *### Une limite de la règle unifiée, découverte ici*

La section est **l'unique mention** de la limite découverte : la règle de verdict du #448 ne couvre pas les rapports de batterie. La variable `indet` n'apparaît **nulle part** hors de la garde. Si elle valait 0, la découverte — *« personne ne l'avait remarqué, ni le #448, ni le #449, ni le #454 »* — s'effacerait **sans laisser un mot**. C'est la forme du #475.

### `nonml_citer_451_resolution_backtest.py` l.187 — **ANODIN**

Garde : `if meme:` — section : *### Un fait qui départage partiellement*

La section ajoute un **argument** (« le désaccord est stable, pas accidentel ») à une conclusion déjà exposée sans garde au-dessus. Son absence retirerait un renfort de raisonnement, **pas un fait**.

### `nonml_marker_emitter_crossing_backtest.py` l.175 — **ANODIN**

Garde : `if douteux:` — section : *### L'examen, mené — et il retire le seul citeur*

La section porte l'examen qui retire le seul citeur. Mais le rapport publie **sans garde** son tableau de comptes — « candidats citeurs : 1 », « citeurs établis : 0 ». Un lecteur voyant 1 candidat et 0 établi **sait qu'un examen a eu lieu** ; si la section manquait, les deux nombres seraient égaux et il n'y aurait rien à expliquer.

### `nonml_net_pnl_correction_backtest.py` l.279 — **MASQUANT**

Garde : `if incoh:` — section : *### Une incohérence exposée par le rafraîchissement*

La variable `incoh` n'apparaît **que** sous sa garde. La section est la **seule** trace d'une incohérence trouvée en passant — « le compte est calculé, la prose est figée ». Si le dépôt cessait de la produire, la découverte disparaîtrait **sans qu'aucun compte ne le signale**.

### `nonml_net_pnl_correction_robustness.py` l.76 — **ANODIN**

Garde : `if tous:` — section : *## Plateau, pas pic*

**C'est une branche de `if/else`.** Les deux issues écrivent une section — « Plateau, pas pic » ou « La conclusion ne tient pas partout ». **Une section paraît toujours** ; seul son contenu change. **Ma règle ne reconnaît pas l'exhaustivité d'un `if/else`** et compte les deux branches comme sans témoin. **C'est un défaut de ma règle, trouvé par l'examen que le pré-enregistrement avait déclaré** — et c'est précisément à cela qu'il servait.

- **MASQUANTS** : **2 / 5**

## Ce que l'examen a révélé sur ma propre règle

Le cinquième cas est une **branche de `if/else`** : les deux issues
écrivent une section, donc **une section paraît toujours**. **Ma règle ne
reconnaît pas l'exhaustivité d'un `if/else`** et compte les deux branches
comme sans témoin.

- gardes apparaissant **deux fois ou plus** dans la liste des sans
  témoin *(indice d'un `if/else`)* : **1**
  - `nonml_net_pnl_correction_robustness.py` — `if tous:` aux lignes 76, 86

> **Le total de 14 est donc un majorant.** Il est publié tel quel, avec
> sa cause : corriger la règle après mesure serait un retuning, et le
> pré-enregistrement l'interdit.

**C'est exactement ce à quoi servait l'examen déclaré d'avance** : il a
trouvé un défaut de ma règle **sans que j'aie à changer la règle**, parce
qu'il faisait partie du protocole au lieu d'y être ajouté.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 30 avec témoin | ≥ 30 | 36 | **vérifiée** |
| ≤ 15 sans témoin | ≤ 15 | 14 | **vérifiée** |
| ≥ 1 masquant parmi les examinés | ≥ 1 | 2 | **vérifiée** |

**Le cas du #475 n'est pas isolé** : **2** sections
masquantes trouvées **sur 5 lues**, dans des scripts sans rapport entre
eux. Chacune porte l'unique mention d'une découverte faite *en passant*
— exactement le motif qui avait envoyé trois cycles chercher un encart
qui n'avait jamais été écrit.

**Les 9 autres sans témoin ne sont pas jugés.**
Cinq ont été lus parce que cinq avaient été déclarés ; le taux de 2/5
**ne s'extrapole pas** aux autres.

## Critères de succès

1. Tous classés (**58**), écart au #478 signalé (**+0**) — **OUI**.
2. Chaque « sans témoin » nommé avec script, ligne et garde — **OUI**.
3. Gardes non nommées (**8**) comptées à part et exclues de tout
   total de dette — **OUI**.
4. **5** examinés à la main avec verdict — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).