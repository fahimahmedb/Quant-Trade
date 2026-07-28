"""Backtest — Effet jour-de-semaine / Skip-Monday (spécification
pré-enregistrée dans PREREG_day_of_week.md, committée avant ce script).
n_trials=1, aucune dépendance ML.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = [
        "# Résultat — Effet jour-de-semaine / Skip-Monday (pré-enregistré, exécuté une fois)",
        "",
        "| Marché | BH Sharpe | Skip-Monday Sharpe | Skip-Monday bat BH ? |",
        "|---|---|---|---|",
    ]
    n_markets = 0
    n_success = 0
    details = []

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.to_datetime(df["date"])
        bh_full = np.log(close[1:] / close[:-1])
        # jour de semaine du jour t (jour d'ARRIVEE du rendement, pas de depart)
        dow = dates.dt.dayofweek.values[1:]  # 0=lundi
        is_monday = (dow == 0)

        pos = (~is_monday).astype(float)
        turn = np.abs(np.diff(pos, prepend=1.0))  # position de depart = investi (BH par defaut avant t=0)
        pnl_skip = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_skip = trading_metrics(pnl_skip)
        beats = me_skip["sharpe_ann"] > me_bh["sharpe_ann"]
        n_markets += 1
        n_success += int(beats)

        lines.append(f"| {name} | {me_bh['sharpe_ann']:+.2f} | {me_skip['sharpe_ann']:+.2f} | "
                     f"{'OUI' if beats else 'non'} |")
        mon_mean = bh_full[is_monday].mean()
        other_mean = bh_full[~is_monday].mean()
        details.append({"market": name, "mon_mean": mon_mean, "other_mean": other_mean})

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où Skip-Monday bat Buy&Hold net de coûts "
                 f"(critère pré-enregistré : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    lines.append("")
    lines.append("## Décomposition brute (rendement moyen quotidien, avant coûts)")
    lines.append("")
    lines.append("| Marché | Rendement moy. LUNDI (brut) | Rendement moy. AUTRES JOURS (brut) |")
    lines.append("|---|---|---|")
    for d in details:
        lines.append(f"| {d['market']} | {100*d['mon_mean']:+.4f}% | {100*d['other_mean']:+.4f}% |")

    lines.append("")
    lines.append(
        "**Lecture honnête** : cette anomalie est parmi les plus anciennes et les plus "
        "arbitrées de la littérature (French 1980, ~45 ans de publication) — si elle "
        "échoue, c'est cohérent avec la décennie de décroissance documentée des "
        "anomalies de calendrier une fois largement connues."
    )

    out = ROOT / "results" / "nonml_day_of_week_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
