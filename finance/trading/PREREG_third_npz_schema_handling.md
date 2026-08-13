# Pré-enregistrement — le troisième schéma `.npz` et son traitement par les balayages

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## Ce que le #443 a laissé ouvert

Le #443 a découvert **2** fichiers portant un schéma jamais catalogué :

| Fichier | Clés |
|---|---|
| `dollar_neutral_composite_pit` | `cost_bps`, `dates`, `pnl_candidate`, `pnl_ref`, `turn_candidate`, `turn_ref` |
| `dollar_neutral_composite_vol_targeted` | `cost_bps`, `dates`, `pnl_candidate`, `pnl_ref` |

Ils étaient hors de son périmètre déclaré et sont restés **en file, non couverts**.

## La question qui compte n'est pas la concordance

Un sondage post-hoc du #443 a déjà montré que les deux jambes de
`dollar_neutral_composite_pit` se retrouvent dans son rapport, une fois comprise
la convention : **`pnl_candidate` est sauvegardé déjà net** (`pnl_sleeve_net`),
`turn_candidate` n'étant stocké que pour information.

> **Cette concordance est donc CONNUE D'AVANCE.** La vérifier proprement ne
> produit **aucune vérification neuve**. Elle sera refaite et publiée pour que le
> résultat soit reproductible et pré-enregistré, mais comptée **zéro**.

La question **non mesurée** est ailleurs :

> Les balayages qui **consomment** les `.npz` traitent-ils ces 2 fichiers
> correctement, les écartent-ils explicitement, ou les manipulent-ils
> **silencieusement avec une formule fausse** ?

Le troisième cas est le seul qui importe : un consommateur qui applique la
formule indicielle ou panier à un P&L **déjà net** publierait un chiffre faux
sans que rien ne le signale. C'est exactement l'erreur que j'ai commise moi-même
au #443, et qu'aucun compte mécanique n'a détectée.

## Périmètre — énuméré avant mesure

Consommateurs = scripts de `scripts/` qui **balayent** l'ensemble des `.npz`
(motif `glob(...*_pnl.npz)`), par opposition aux producteurs qui écrivent le
leur. Comptés avant d'écrire ces lignes : **12**.

**Je n'ai regardé comment aucun d'eux traite ce schéma.** Le compte de 12 est un
périmètre, pas un résultat.

Parmi eux, **2 sont connus d'avance** — les miens :
- `nonml_npz_report_consistency_backtest.py` (#442) : les écarte, mais sous
  l'étiquette **fausse** « schéma panier » ;
- `nonml_npz_report_consistency_baskets_backtest.py` (#443) : les isole
  correctement dans une catégorie à part.

Ces deux-là sont classés mais **ne comptent pas** comme vérification neuve.
**10 consommateurs restent inconnus.**

## Le contrôle — classification par lecture, chacun justifié par une ligne citée

Chaque consommateur est classé dans **une** catégorie :

| Code | Traitement | Gravité |
|---|---|---|
| **A** | traité correctement (convention « déjà net » respectée) | aucune |
| **B** | écarté **explicitement**, avec raison publiée ou comptée | aucune |
| **C** | écarté **silencieusement** (ni compté ni signalé) | lacune de couverture |
| **D** | **consommé avec une formule fausse** | **défaut : chiffre publié faux** |

La classification se fait par **lecture du code**, chaque classement accompagné
de la **ligne du script qui le décide**, citée dans le rapport — pas par un
compte mécanique. Justification : dans ce projet, **aucun** défaut réel n'a été
trouvé par la mesure elle-même — tous par relecture (#428, #436, #442, #443). Un
balayage automatique de garde-fous produirait ici le même faux confort.

Douze scripts sont lisibles individuellement : la lecture est faisable, donc elle
est due.

## Critère de succès — chiffré, et il peut échouer

1. **12/12** consommateurs classés A, B, C ou D, chacun avec sa ligne citée.
2. **FAIL si au moins un consommateur est en catégorie D** — un chiffre publié
   serait alors construit sur une formule fausse, et le cycle devrait dire
   lesquels.
3. **PASS** si tous sont en A, B ou C, les C étant **listés nommément** comme
   lacune de couverture restante — une lacune n'est pas un défaut, mais elle se
   publie.
4. La concordance des 2 fichiers est republiée, **explicitement comptée zéro
   vérification neuve**.
5. **Aucun rapport ni `.npz` modifié.**

## Prédiction

**Falsifiable, et je peux me tromper :**

- j'attends **au moins un C** — plusieurs balayages sont antérieurs à l'existence
  de ce schéma et n'ont aucune raison de le mentionner ;
- je **n'ai aucune idée** s'il existe un D. C'est précisément pourquoi le cycle
  vaut d'être fait. Si D = 0, ce sera une absence, pas un exploit.

Contre-prédiction utile : si je trouve **12 A**, je devrai me méfier — un dépôt
qui gère parfaitement un schéma que personne n'avait catalogué serait surprenant,
et j'irais d'abord vérifier ma lecture.

## Engagements

1. Résultat rapporté tel quel, **y compris un D** — surtout un D, qui
   invaliderait des chiffres que j'ai moi-même publiés.
2. Aucun consommateur classé sans **ligne citée** ; aucun classement « par
   défaut » faute d'avoir lu.
3. Aucun élargissement du périmètre après avoir vu ce qu'il attrape (refus #437).
4. Aucun rapport publié modifié ni committé ; ce cycle ne fait que **lire**.
5. **Relecture intégrale du rapport produit avant commit** (engagement #414).
