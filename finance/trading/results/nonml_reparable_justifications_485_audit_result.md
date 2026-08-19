# Audit indépendant — #518, les 11 justifications RÉPARABLE du #485

Route de calcul différente du backtest : parcours **AST** (pas regex
sur le texte source) pour repérer tout appel `.glob(` quel que soit
l'objet visé, et pour compter les segments de texte fixe contenant un
chiffre à l'intérieur des f-strings — sans jamais lire le dictionnaire
`V` de verdicts écrits à la main dans le backtest.

## Présence d'un appel `.glob(` — par script, route AST

| Script | Appels `.glob(...)` trouvés | Segments littéraux chiffrés (f-string) |
|---|---|---|
| `nonml_duplicate_sweep_coverage_audit.py` | `*_pnl.npz`, `nonml_*_backtest.py`, `nonml_*_backtest.py` | 5 |
| `nonml_content_defined_magnitudes_audit.py` | **aucun** | 3 |
| `nonml_content_defined_magnitudes_backtest.py` | **aucun** | 10 |
| `nonml_coverage_wording_fix_audit.py` | **aucun** | 4 |
| `nonml_dsr_corrected_trials_backtest.py` | `nonml_*_pnl.npz` | 11 |
| `nonml_idempotence_famille_capable_backtest.py` | `nonml_*_backtest.py` | 5 |
| `nonml_idempotence_lot2_backtest.py` | `nonml_*_backtest.py` | 7 |
| `nonml_marker_emitter_crossing_backtest.py` | `*.md`, `nonml_*.py` | 3 |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `?`, `?`, `?`, `PREREG_*.md` | 9 |
| `nonml_report_idempotence_backtest.py` | **aucun** | 6 |
| `nonml_reproducibility_campaign_v2_audit.py` | `nonml_*_backtest.py` | 1 |

## Les 3 chutes du backtest sont-elles confirmées par cette route ?

- parmi les scripts dont la **justification publiée** revendique explicitement un `glob` comme preuve (**3** sur 11, extraits du rapport, pas du dictionnaire interne du backtest) : `nonml_coverage_wording_fix_audit.py`, `nonml_report_idempotence_backtest.py`, `nonml_reproducibility_campaign_v2_audit.py`
- ceux d'entre eux **sans aucun** appel `.glob(` détecté par AST : **2**
  - `nonml_coverage_wording_fix_audit.py`
  - `nonml_report_idempotence_backtest.py`

- sous-ensemble testable par ce seul critère (glob revendiqué ET absent) : `nonml_coverage_wording_fix_audit.py`, `nonml_report_idempotence_backtest.py`
- accord exact : **OUI**

> **Accord exact** sur les 2 des 3 chutes testables par la seule présence/absence d'un `.glob(` — `reproducibility_campaign_v2_audit.py` **a** un `.glob(`, mais pour un autre usage, testé séparément ci-dessous plutôt que forcé dans ce même critère.

## Cas particulier vérifié séparément : `reproducibility_campaign_v2_audit.py`

- appels `.glob(` détectés : 'nonml_*_backtest.py'
- l'un d'eux porte-t-il sur un motif `*.npz` : **NON**

> Confirme la nuance du backtest : ce script **a** un `.glob(`, mais il sert à lister les scripts éligibles, pas à compter les `.npz` — le chiffre cité (208) n'est donc dérivé d'aucun des appels présents.

**PASS** — la route AST indépendante confirme, sans lire le dictionnaire de verdicts du backtest, l'ensemble exact des 3 reclassements et la nuance du cas `reproducibility_campaign_v2`.
