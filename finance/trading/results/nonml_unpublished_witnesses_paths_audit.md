# Audit adversarial — les témoins non publiés (#494)

Le cycle classe deux scripts **« sans danger »** et déclare **faux** un
motif du #487. **C'est une accusation**, et elle doit être vérifiée par
une route propre.

## 1. `nonml_sweep_pass_prose_fix_backtest.py` écrit-il vraiment **un seul** fichier ?

Route : **résoudre** chaque `X.write_text(...)` vers le chemin littéral
affecté à `X` au niveau module — et non compter les appels.

| Ligne | Objet | Chemin résolu |
|---|---|---|
| 250 | `OUT` | `RESULTS / 'nonml_sweep_pass_prose_fix_result.md'` |
| 316 | `OUT` | `RESULTS / 'nonml_sweep_pass_prose_fix_result.md'` |

- appels à `write_text` : **2**
- **chemins distincts** : **1**

> **L'accusation est fondée.** Deux appels, **un seul chemin** — son
> propre rapport. Le #487 avait bien **compté des appels, pas des
> cibles**, et a refusé d'exécuter un script sans danger.

## 2. Les deux **classe C** exécutent-ils vraiment un script tiers ?

| Script | Lignes de `run([sys.executable…])` |
|---|---|
| `nonml_battery_coverage_backtest.py` | **[110]** |
| `nonml_six_reports_regeneration_backtest.py` | **[75]** |

> **Confirmé.** Les deux lancent bien un interpréteur sur un autre
> script. **Le classement C n'est pas une précaution excessive.**

## 3. La population de **4** est-elle exacte ?

Route : `git grep` sur les préfixes, au lieu d'une lecture fichier par
fichier.

- scripts portant un préfixe *(git grep)* : **4**
  - `nonml_battery_coverage_backtest.py`
  - `nonml_net_pnl_correction_backtest.py`
  - `nonml_six_reports_regeneration_backtest.py`
  - `nonml_sweep_pass_prose_fix_backtest.py`

> **Quatre, confirmé par une route indépendante.** La file du #493
> annonçait **3** — la dette était plus large que quatre entrées
> successives ne le disaient.

## 4. Le cycle a-t-il vraiment rien exécuté ?

- fichiers modifiés hors ceux du cycle : **0**

> **Aucun.** L'annonce est vérifiée par ses conséquences.

## 5. Le cycle publie-t-il ce qui l'affaiblit ?

| Contrôle | Résultat |
|---|---|
| il reconnaît qu'une de ses prédictions n'était pas réfutable | **OUI** |
| il déclare l'idempotence hors de portée | **OUI** |
| il exclut d'éditer un rapport à la main | **OUI** |
| il compte 3 motifs faux dans la série | **OUI** |
| il dit que le blocage de la classe A est de méthode, pas technique | **OUI** |

> **Le cycle signale lui-même qu'une de ses prédictions était
> infalsifiable**, et refuse la voie détournée qui aurait clos la
> dette.

## Verdict

**CONCORDANT** — l'accusation contre le #487
est **fondée par résolution des chemins**, le classement C est
**confirmé**, la population de 4 l'est par `git grep`, rien n'a été
exécuté, et **5/5**
contrôles de transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).