"""Backtest — Overlay levé "turn-of-quarter" (spécification
pré-enregistrée dans PREREG_turn_of_quarter_overlay.md, committée avant
ce script). Variante trimestrielle du #8 (ToM mensuel), restreinte aux 4
changements de trimestre/an au lieu des 12 changements de mois.
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
LAST_N_DAYS = 4
FIRST_N_DAYS = 3
CAP = 2.0
QUARTER_END_MONTHS = {3, 6, 9, 12}
QUARTER_START_MONTHS = {4, 7, 10, 1}  # mois suivant un mois de fin de trimestre

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def turn_of_quarter_mask(dates: pd.Series) -> np.ndarray:
    """Meme construction que tom_mask (#8) mais restreinte aux fenetres
    dont le mois de fin appartient a QUARTER_END_MONTHS (dernieres
    LAST_N_DAYS seances) ou dont le mois de debut appartient a
    QUARTER_START_MONTHS (premieres FIRST_N_DAYS seances)."""
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["month"] = df["date"].dt.month
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    is_qend_month = df["month"].isin(QUARTER_END_MONTHS)
    is_qstart_month = df["month"].isin(QUARTER_START_MONTHS)
    mask = ((df["rank_desc"] <= LAST_N_DAYS) & is_qend_month) | \
           ((df["rank_asc"] <= FIRST_N_DAYS) & is_qstart_month)
    return mask.values


def main():
    lines = [
        "# Résultat — Overlay levé turn-of-quarter (pré-enregistré, règle renforcée)",
        "",
        f"Position 1.0x en permanence, CAP={CAP}x pendant la fenêtre turn-of-quarter "
        f"({LAST_N_DAYS}j fin mars/juin/sept/déc + {FIRST_N_DAYS}j début avr/juil/oct/jan), "
        "1.0x sinon (y compris les 8 autres changements de mois ordinaires).",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
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

        mask_full = turn_of_quarter_mask(df["date"])
        # meme convention que #8/#17/#21/#54/#56/#64 : calendrier connu a
        # l'avance, alignement [1:] (jour de cloture du rendement)
        pos = np.where(mask_full[1:], CAP, 1.0)

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*(pos > 1.0).mean():.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_turn_of_quarter_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
