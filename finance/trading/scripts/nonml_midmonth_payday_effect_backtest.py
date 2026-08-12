"""Backtest — Effet mi-mois / jour de paie (spécification pré-enregistrée
dans PREREG_midmonth_payday_effect.md, committée avant ce script). Fenêtre
data-driven basée sur le RANG de séance dans le mois (comme le ToM #2),
centrée sur le milieu du mois plutôt que sa frontière. n_trials=1, aucune
dépendance ML. Règle de succès renforcée.
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
HALF_WIDTH = 2  # fenêtre = 2*HALF_WIDTH+1 = 5 séances centrées sur le milieu du mois

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def midmonth_mask(dates: pd.Series) -> np.ndarray:
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["n_in_month"] = df.groupby("ym")["date"].transform("size")
    df["mid"] = ((df["n_in_month"] + 1) / 2).round()
    mask = (df["rank_asc"] - df["mid"]).abs() <= HALF_WIDTH
    return mask.values


def main():
    lines = [
        "# Résultat — Effet mi-mois / jour de paie (pré-enregistré, règle renforcée)",
        "",
        f"Fenêtre = {2*HALF_WIDTH+1} séances centrées sur le rang médian de séance du mois "
        "(milieu du mois en jours de bourse, data-driven). Position longue uniquement "
        "pendant la fenêtre, flat le reste du mois.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | Midmonth Sharpe | Midmonth Rdt total | % jours investis | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])

        mask = midmonth_mask(df["date"])[1:]

        pos = mask.astype(float)
        turn = np.abs(np.diff(pos, prepend=0.0))
        pnl_mm = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_mm = trading_metrics(pnl_mm)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_mm = np.exp(pnl_mm.sum()) - 1.0

        sharpe_ok = me_mm["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_mm > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_mm['sharpe_ann']:+.2f} | {100*ret_mm:+.1f}% | {100*mask.mean():.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où Midmonth-only bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_midmonth_payday_effect_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
