"""Backtest — Rallye de fin d'année / Santa Claus Rally (spécification
pré-enregistrée dans PREREG_santa_claus_rally.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
LAST_N_DEC = 5
FIRST_N_JAN = 2

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def santa_mask(dates: pd.Series) -> np.ndarray:
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    is_dec_tail = (df["date"].dt.month == 12) & (df["rank_desc"] <= LAST_N_DEC)
    is_jan_head = (df["date"].dt.month == 1) & (df["rank_asc"] <= FIRST_N_JAN)
    # bug trouve et corrige par l'audit (nonml_santa_claus_rally_audit.py) : sans cette
    # ligne, le tout premier janvier de l'echantillon est marque comme fenetre Santa
    # meme si le decembre precedent n'existe pas dans les donnees (ex. S&P 500, debute
    # 1970-01-02) -- fragment orphelin sans jambe decembre correspondante, exclu ici.
    years_with_dec = set(df.loc[df["date"].dt.month == 12, "date"].dt.year)
    has_preceding_dec = df["date"].dt.year.sub(1).isin(years_with_dec)
    is_jan_head = is_jan_head & has_preceding_dec
    return (is_dec_tail | is_jan_head).values


def main():
    lines = [
        "# Résultat — Rallye de fin d'année / Santa Claus Rally (pré-enregistré, règle renforcée)",
        "",
        f"Fenêtre = {LAST_N_DEC} derniers j. de déc. + {FIRST_N_JAN} premiers j. de janv.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | Santa Sharpe | Santa Rdt total | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|",
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

        mask = santa_mask(df["date"])
        mask_r = mask[1:]
        pos = mask_r.astype(float)
        turn = np.abs(np.diff(pos, prepend=0.0))
        pnl_santa = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_santa = trading_metrics(pnl_santa)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_santa = np.cumprod(1.0 + pnl_santa)[-1] - 1.0

        sharpe_ok = me_santa["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_santa > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_santa['sharpe_ann']:+.2f} | {100*ret_santa:+.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où Santa-only bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_santa_claus_rally_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
