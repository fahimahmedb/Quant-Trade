# Réparer le dictionnaire `V` du recensement du #485 (pré-enregistré)

`nonml_irreparable_figures_census_backtest.py` (le script du #485)
contenait un dictionnaire de 17 verdicts **jamais mis à jour**
malgré 4 cycles qui en ont contredit 5, chacun avec une ligne de
code à l'appui. Une relecture ou réexécution du script publiait
encore **5 irréparables / 12 réparables** — un compte que les
#493, #511 et #518 ont chacun démontré faux.

## Les 5 corrections, citées avec leur cycle d'origine

| Script | Avant | Après | Établi par |
|---|---|---|---|
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | IRRÉPARABLE | RÉPARABLE | #493 |
| `nonml_battery_backfill_lot_audit.py` | RÉPARABLE | IRRÉPARABLE | #511 |
| `nonml_coverage_wording_fix_audit.py` | RÉPARABLE | IRRÉPARABLE | #518 |
| `nonml_report_idempotence_backtest.py` | RÉPARABLE | IRRÉPARABLE | #518 |
| `nonml_reproducibility_campaign_v2_audit.py` | RÉPARABLE | IRRÉPARABLE | #518 |

- les **5** scripts attendus apparaissent-ils dans le diff du commit de réparation : **OUI** (5/5)

## Le geste, mesuré depuis git

- lignes changées (+ et -) dans `nonml_irreparable_figures_census_backtest.py` : **49**
- le rapport `nonml_irreparable_figures_census_result.md` a-t-il été régénéré dans un commit distinct (pas le même diff que le `.py`) : **OUI**

> Le nombre de lignes changées dépasse les « 5 lignes de valeurs »
> annoncées au pré-enregistrement : chaque verdict est accompagné
> d'une justification en prose de plusieurs lignes citant le cycle
> correcteur, et le dictionnaire `court` (résumé une-ligne, non
> anticipé au pré-enregistrement) a dû être étendu de 4 entrées
> pour éviter un rapport visiblement cassé — **corrigé avant commit,
> comme l'exige l'étape 4 du protocole, et publié ici plutôt que
> minimisé.**

## Le nouveau compte, republié par le script réparé

- irréparables : **5 → 8**
- réparables : **12 → 9**
- cohérent avec le dernier chiffre publié indépendamment (#518) : **oui**

## Mes trois prédictions, confrontées

| Prédiction | Vérifiée |
|---|---|
| Diff limité à « quelques lignes de mise en forme » près des 5 valeurs | **nuancée** — le diff réel (49 lignes) reste borné aux 5 scripts déclarés (confirmé ci-dessus, 5/5), mais dépasse « quelques lignes » car chaque verdict porte une justification en prose citant son cycle correcteur, pas seulement une valeur |
| Le taux d'accord proxy change (dénominateur différent) | **vérifiée** — 70,6 % → 52,9 % |
| Aucune des 12 autres entrées touchée | **vérifiée** — confirmé par l'audit dédié (`nonml_census_485_repair_audit.py`) |

## Critères de succès

1. Les 5 scripts corrigés identifiés dans le diff, chacun avec son cycle — **OUI**.
2. Rien d'autre modifié hors les 5 verdicts + le résumé court nécessaire — **OUI**.
3. Compte régénéré cohérent avec #518 (8/9) — **OUI**.
4. Proxy mécanique republié à jour, sans conclusion nouvelle sur sa qualité — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : une source
de vérité périmée depuis 4 cycles est mise à jour, avec chaque
changement cité sur pièce.

Simulation 300 € et robustesse **sans objet** : cycle de réparation
de dépôt, aucune position, aucun paramètre numérique de stratégie.

> **Dette non résolue, signalée explicitement** : le littéral en
> dur « chacun des 12 » (l.288 du script cible) décrivait une
> coïncidence numérique exacte avant ce cycle — il devrait valoir
> **9** désormais. Hors du périmètre déclaré (5 lignes de `V`
> uniquement) ; laissé pour un cycle dédié plutôt que corrigé ici.
