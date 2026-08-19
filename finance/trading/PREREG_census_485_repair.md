# Pré-enregistrement — réparer le dictionnaire `V` du recensement du #485

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de RÉPARATION**, deuxième piste de la file
ouverte au #519 (la première, E1 du fil économique, dépend de
l'arbitrage utilisateur toujours en attente sur le #432 — non tranchée
ici).

## Ce qui est périmé

`nonml_irreparable_figures_census_backtest.py` (le script du #485)
contient un dictionnaire `V` de 17 verdicts RÉPARABLE/IRRÉPARABLE,
**jamais mis à jour** depuis sa rédaction, alors que **4** de ses entrées
ont été contredites par des cycles ultérieurs :

| Script | `V` actuel | Verdict correct | Établi par |
|---|---|---|---|
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | IRRÉPARABLE | **RÉPARABLE** | #493 |
| `nonml_battery_backfill_lot_audit.py` | RÉPARABLE | **IRRÉPARABLE** | #511 |
| `nonml_coverage_wording_fix_audit.py` | RÉPARABLE | **IRRÉPARABLE** | #518 |
| `nonml_report_idempotence_backtest.py` | RÉPARABLE | **IRRÉPARABLE** | #518 |
| `nonml_reproducibility_campaign_v2_audit.py` | RÉPARABLE | **IRRÉPARABLE** | #518 |

Si le script du #485 est relu ou réexécuté aujourd'hui **sans réparation**,
il republie un compte **5 irréparables / 12 réparables** — un chiffre que
les cycles #493, #511, #518 ont chacun démontré **faux**, avec ligne de
code à l'appui. C'est exactement le défaut que le #499 avait nommé :
« la réparation ne change rien, et c'est pourtant elle qui échoue » —
sauf qu'ici, la source **n'a jamais été réparée du tout**.

## Le geste — même forme que le #511, minimal et borné

1. **Modifier les 5 lignes** du dictionnaire `V` pour porter le verdict
   correct, **avec un commentaire citant le cycle qui l'a établi** (pas
   seulement le nouveau mot).
2. **Ne toucher à rien d'autre** : ni la population `DEFAUTS`, ni le
   proxy mécanique, ni la structure du rapport généré.
3. **Réexécuter** le script et publier le nouveau compte
   (**8 irréparables / 9 réparables**, cohérent avec le #518).
4. **Comparer le diff du rapport régénéré** à l'ancien : il doit changer
   **exactement** aux lignes qui dépendent des 5 verdicts corrigés (compte
   total, table des irréparables, table de proxy), **rien ailleurs**.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **5** lignes modifiées dans `V`, chacune avec sa citation de cycle.
2. **0** autre ligne du script modifiée hors ces 5 (diff du `.py` mesuré).
3. Rapport régénéré : compte final **8 irréparables / 9 réparables**,
   cohérent avec le dernier chiffre publié (#518).
4. Le proxy mécanique (déclaré faible d'avance au #485) est **republié
   à jour** avec son taux d'accord recalculé sur la nouvelle partition —
   sans en tirer de conclusion nouvelle sur sa qualité.
5. **Aucun script de marché exécuté** ; le seul effet de bord est la
   régénération du rapport du #485 lui-même.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le diff du `.py` se limite **à 5 lignes de valeurs + leurs
   commentaires** (± quelques lignes de mise en forme).
2. Le nouveau taux d'accord proxy/verdict **change** par rapport aux
   70,6 % du #485 (puisque la partition change).
3. Le rapport régénéré ne modifie **aucune** ligne relative aux 12
   scripts dont le verdict n'a jamais été contesté.

## Ce que ce cycle ne fait pas

- Il ne **rejuge** aucun des 5 verdicts — il **applique** des verdicts
  déjà établis par des cycles antérieurs, chacun avec sa ligne de code.
- Il ne **touche** à aucun autre dictionnaire ou script du dépôt.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432) — le fil économique reste en attente d'arbitrage, inchangé.
- Il n'**exécute** aucun script de marché.

## Simulation 300 € et robustesse

**Sans objet** : cycle de réparation de dépôt, aucune position, aucun
paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le diff déborde de ce qui
   est annoncé (auquel cas le contrôle 2 échoue et c'est publié comme
   tel).
2. Les 5 verdicts corrigés sont ceux, et seulement ceux, listés dans le
   tableau ci-dessus — aucun ajouté après lecture du code.
3. **Chaque changement adossé à la ligne de code et au cycle qui le
   justifie.**
4. **Relecture intégrale du rapport régénéré avant commit** (engagement
   #414).
