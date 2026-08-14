# Pré-enregistrement — les trois écarts silencieux du #444 : mesurer avant de décider

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle de **décision**. Il peut se conclure par *« on ne touche à rien »*, et ce
serait un résultat.

## Ce qui est en cause

Le #444 a classé trois consommateurs de `.npz` en catégorie **C** — ils écartent
le troisième schéma (`pnl_candidate` / `pnl_ref`) **sans le compter ni le
signaler** :

| Script | Ligne qui décide |
|---|---|
| `nonml_empty_pass_requalification_backtest.py` | `if "pos" not in d.files or "r_asset" not in d.files: continue` |
| `nonml_pnl_persistence_lot5_audit.py` | `if "pos" not in p.files: continue` |
| `nonml_npz_report_consistency_backtest.py` | compte ces fichiers, mais sous l'étiquette **fausse** « schéma panier » |

Le #444 était explicite : **ce n'est pas un défaut**, leur résultat reste juste.
C'est une **lacune de couverture** — leur rapport peut laisser croire à un
balayage complet.

## La question n'est donc pas « corriger », mais « est-ce trompeur ? »

Un silence n'induit en erreur que si le rapport **affirme** une couverture que ce
silence contredit. Un rapport qui ne prétend rien sur sa couverture n'a rien à
corriger, et y ajouter un décompte serait du bruit.

**C'est mesurable, et c'est ce que ce cycle mesure.**

## La règle de décision — fixée AVANT toute mesure

Pour chaque script, deux grandeurs :

- **n_skip** — combien de `.npz` il écarte silencieusement ;
- **revendication** — son rapport contient-il une affirmation de couverture
  (« tous les `.npz` », « 100 % », un total présenté comme exhaustif) ?

> **Rendre l'écart visible** si et seulement si `n_skip > 0` **et** le rapport
> **revendique** une couverture que ce silence contredit.
>
> **Ne rien changer** si `n_skip = 0`, ou si le rapport ne revendique rien : le
> silence n'y trompe personne, et l'ajout serait décoratif.

## Une provision déclarée d'avance — la leçon du #449

Un script dont le rapport est le **compte rendu d'un cycle passé** n'est pas
modifié, quelle que soit la mesure : le régénérer ferait re-raconter ce cycle
avec un état du dépôt qu'il n'a pas connu.

`nonml_npz_report_consistency_backtest.py` est dans ce cas — c'est le rapport du
#442. Le #449 avait rencontré ce cas de figure **sans l'avoir prévu** et avait dû
publier une entorse ; ici il est **déclaré avant**.

## Critère de succès — chiffré

1. Les **3** scripts sont mesurés : `n_skip` et revendication, chacun avec la
   **ligne citée** qui la porte (ou son absence constatée).
2. La décision de chacun **suit la règle**, sans appréciation après coup.
3. Toute modification décidée est **confinée** au régime du #449 (zone
   d'imports + lignes de l'occurrence), et publiée en diff.
4. La provision « compte rendu d'un cycle passé » est appliquée telle que
   déclarée, et son application est **dite**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- J'attends **n_skip = 2** pour les deux premiers (les deux fichiers du
  troisième schéma), et que **ni l'un ni l'autre ne revendique** de couverture
  exhaustive : leur rapport parle de candidats, pas de fichiers. La décision
  serait donc **« on ne touche à rien »** — et ce serait la bonne conclusion d'un
  cycle, pas son échec.
- Je **n'exclus pas** l'inverse : le #428 a montré que ces rapports affichent
  volontiers des totaux. Si l'un revendique, la décision bascule.

## Ce que ce cycle ne fait pas

- Il ne **régénère** aucun rapport dont il ne modifie pas le script.
- Il ne **recalcule** aucun verdict.
- Il ne traite **pas** le fond du troisième schéma : le #444 a établi que ces
  trois-là ne le manipulent pas, seulement l'ignorent.

## Engagements

1. La décision suit la règle déclarée, **même si elle est « ne rien faire »**.
2. Chaque mesure publiée avec la ligne qui la porte.
3. Aucun autre script touché.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
