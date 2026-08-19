# Audit indépendant — #522, écran de staleness sur 4 dictionnaires V

Route distincte du backtest : extraction des clés par regex sur
texte brut (pas AST), découpage du backlog par bornes de ligne
issues de `grep -n` (pas un scan regex unique en mémoire).

## Effectifs par dictionnaire, recomptés

| Script | Effectif (regex) | Effectif (backtest, AST) | Accord |
|---|---|---|---|
| `nonml_hardcoded_figures_remainder_backtest.py` | 32 | 32 | **OUI** |
| `nonml_guards_witness_remainder_backtest.py` | 10 | 10 | **OUI** |
| `nonml_guards_without_witness_backtest.py` | 5 | 5 | **OUI** |
| `nonml_orphan_audits_declared_reading_backtest.py` | 4 | 4 | **OUI** |

- total recompté : **51**
- total publié par le backtest : **51**
- accord : **OUI**

## Candidats, recomptés

- candidats trouvés par cette route : **32**
- candidats publiés par le backtest : **32**
- accord : **OUI**

**PASS** — la route indépendante (regex + grep -n) reproduit les effectifs et le compte de candidats publiés par le backtest.
