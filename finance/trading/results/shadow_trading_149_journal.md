# Journal officiel de shadow-trading — #149 (NDX vol-targeting + diversification obligataire)

Ouvert le 31/07/2026, suite à la décision Voie A de démarrer le
shadow-trading (`results/deploiement_voie_a_risk_management_134_149.md`,
§5). Paramètres **figés à partir d'ici, aucune modification en cours de
route** (Règle 8) :

- Mécanisme : `finance/trading/scripts/nonml_cash_rate_correction_defensive_vol_targeting_44_backtest.py`
  (vol-targeting 20j, cible 20% annualisé, cap 1,0×, diversification vers
  proxy obligataire DGS10 au lieu de cash sur la fraction dé-risquée).
- Coût pris en compte : 5 bps aller-retour.
- Durée minimale avant réévaluation capital réel : **6 mois calendaires**
  (fin de fenêtre : 31/01/2027).
- Kill-switches actifs : §3.1 (taux), §3.2 (vigilance, pas arrêt dur depuis
  le 31/07/2026), §3.3 (non calculable tant que ce journal n'a pas au moins
  quelques points de données live).

## Limite opérationnelle connue au démarrage

Les données sous-jacentes de ce repo sont des fichiers statiques
rafraîchis périodiquement, pas un flux live : au 31/07/2026, `data/
nasdaq100_daily.txt` s'arrête au **13/07/2026** (18 jours de retard),
`data/dgs10_daily.csv` va jusqu'au **28/07/2026**. Le shadow-trading ne
peut être mis à jour qu'au rythme de rafraîchissement de ces fichiers, pas
quotidiennement au sens strict — chaque entrée ci-dessous précise la date
réelle des données utilisées, pas seulement la date d'écriture.

## État au démarrage (calculé sur les dernières données disponibles, 13/07/2026)

| Date | Position #149 (fraction NDX) | Corrélation 60j | DGS10 | Kill-switch taux | Kill-switch corrélation (vigilance) |
|---|---|---|---|---|---|
| 2026-07-13 | voir `results/monitoring/monitoring_149_2026-07-13.md` | +0,495 | 4,62% | OK | actif (vigilance, ne bloque pas) |

*(à compléter à chaque rafraîchissement des données sous-jacentes —
utiliser `scripts/monitoring_correlation_kill_switches_149.py` pour
générer chaque nouvelle ligne)*
