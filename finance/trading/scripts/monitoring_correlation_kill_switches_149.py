"""Monitoring opérationnel pour le déploiement Voie A de #149 (et #134 en
variante) -- PAS un nouveau cycle de backtest, exécution du §3/§4 du
document de déploiement (`results/deploiement_voie_a_risk_management_134_149.md`).

Calcule et rapporte, à partir des données déjà disponibles dans `data/` :
- la corrélation glissante 60 séances entre rendements NDX et rendements du
  proxy obligataire (kill-switch §3.2 -- seuil +0,3 pendant >20 séances) ;
- le niveau de taux DGS10 courant (kill-switch §3.1 -- seuil <=0,5% pendant
  >60 séances) ;
- rappelle explicitement que le kill-switch performance (§3.3) nécessite des
  positions LIVE (shadow-trading), pas encore disponibles -- non calculé ici,
  volontairement, plutôt que simulé avec des données de substitution.

Usage : python3 scripts/monitoring_correlation_kill_switches_149.py
Écrit un rapport horodaté dans results/monitoring/ (committé -- §4 du
document de déploiement : "rapport hebdomadaire committé, pas seulement une
alerte ponctuelle").
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import (  # noqa: E402
    load_dgs10,
    bond_return_proxy,
)

CORR_WINDOW = 60
CORR_THRESHOLD = 0.30
CORR_CONSEC_DAYS = 20
RATE_THRESHOLD_PCT = 0.5
RATE_CONSEC_DAYS = 60

NDX_PATH = FINANCE_ROOT.parent / "data" / "nasdaq100_daily.txt"


def main():
    df = load_ohlc(str(NDX_PATH))
    r_ndx = log_returns_pct(df) / 100.0  # fraction, coherent avec le reste du backlog

    dgs10 = load_dgs10()
    r_bond = bond_return_proxy(dgs10)

    common = r_ndx.index.intersection(r_bond.dropna().index)
    r_ndx_a = r_ndx.reindex(common)
    r_bond_a = r_bond.reindex(common)
    yield_a = dgs10.reindex(common, method="ffill")

    rolling_corr = r_ndx_a.rolling(CORR_WINDOW).corr(r_bond_a)

    # Kill-switch correlation : seuil franchi en continu depuis >20 seances
    above = (rolling_corr > CORR_THRESHOLD).astype(int)
    # longueur de la serie de "above" consecutive se terminant a la derniere observation
    consec_above = 0
    for v in above.values[::-1]:
        if v == 1:
            consec_above += 1
        else:
            break
    corr_kill_triggered = consec_above > CORR_CONSEC_DAYS

    # Kill-switch taux : DGS10 <= 0.5% en continu depuis >60 seances
    below_rate = (yield_a <= RATE_THRESHOLD_PCT).astype(int)
    consec_below_rate = 0
    for v in below_rate.values[::-1]:
        if v == 1:
            consec_below_rate += 1
        else:
            break
    rate_kill_triggered = consec_below_rate > RATE_CONSEC_DAYS

    last_date = common[-1]
    last_corr = float(rolling_corr.iloc[-1]) if pd.notna(rolling_corr.iloc[-1]) else float("nan")
    last_rate = float(yield_a.iloc[-1])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Rapport de monitoring #149/#134 -- {now}",
        "",
        f"Dernière séance couverte : {last_date.date()}.",
        "",
        "## Kill-switch 3.1 -- niveau de taux",
        f"DGS10 courant : {last_rate:.2f}%. Séances consécutives <= {RATE_THRESHOLD_PCT}% : "
        f"{consec_below_rate} (seuil déclenchement : >{RATE_CONSEC_DAYS}).",
        f"**{'DÉCLENCHÉ -- désactiver le switch dynamique' if rate_kill_triggered else 'OK, pas de déclenchement'}**",
        "",
        "## Kill-switch 3.2 -- corrélation actions/obligations",
        f"Corrélation glissante {CORR_WINDOW}j courante : {last_corr:+.3f} (seuil {CORR_THRESHOLD:+.2f}). "
        f"Séances consécutives au-dessus du seuil : {consec_above} (seuil déclenchement : >{CORR_CONSEC_DAYS}).",
        f"**{'DÉCLENCHÉ -- désactiver le switch dynamique' if corr_kill_triggered else 'OK, pas de déclenchement'}**",
        "",
        "## Kill-switch 3.3 -- performance vs comparateur statique",
        "**NON CALCULÉ.** Nécessite des positions LIVE issues du shadow-trading "
        "(§5 du document de déploiement), pas encore démarré -- calculer ce "
        "kill-switch sur des positions backtest reviendrait à évaluer le "
        "mécanisme sur les données mêmes qui l'ont produit, ce que ce "
        "monitoring doit précisément éviter.",
        "",
        f"## Statut global : {'AU MOINS UN KILL-SWITCH DÉCLENCHÉ' if (rate_kill_triggered or corr_kill_triggered) else 'RAS'}",
    ]

    out_dir = ROOT / "results" / "monitoring"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"monitoring_149_{last_date.date()}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
