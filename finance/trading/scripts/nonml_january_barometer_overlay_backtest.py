"""Backtest — Overlay levé "January Barometer" (spécification
pré-enregistrée dans PREREG_january_barometer_overlay.md, committée
avant ce script). Décision annuelle (pas récurrente intra-mois comme les
overlays calendaires précédents). n_trials=1, aucune dépendance ML.
Règle de succès renforcée.
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
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def position_for(df) -> np.ndarray:
    """Renvoie la position pour chaque rendement r=log(close[1:]/close[:-1])
    (longueur T-1) : CAP de fev a dec de l'annee Y si le rendement de
    janvier(Y) (dec(Y-1) -> jan(Y)) est positif, 1.0 sinon (et 1.0
    toujours en janvier et pour la premiere annee civile, faute de
    decembre precedent disponible)."""
    dates = pd.to_datetime(df["date"])
    close = df["close"].values
    years = dates.dt.year.values
    months = dates.dt.month.values
    T = len(close)

    # dernier indice de chaque (annee, mois)
    last_idx_of_month = {}
    for i in range(T):
        last_idx_of_month[(years[i], months[i])] = i

    all_years = sorted(set(years))
    jan_return_positive = {}
    for y in all_years:
        dec_prev_idx = last_idx_of_month.get((y - 1, 12))
        jan_idx = last_idx_of_month.get((y, 1))
        if dec_prev_idx is None or jan_idx is None:
            continue
        jan_ret = close[jan_idx] / close[dec_prev_idx] - 1.0
        jan_return_positive[y] = jan_ret > 0

    pos_full = np.ones(T)
    for i in range(T):
        y = years[i]
        if months[i] == 1:
            continue  # janvier toujours 1.0x
        if jan_return_positive.get(y, False):
            pos_full[i] = CAP

    return pos_full[1:]  # aligne sur r=log(close[1:]/close[:-1])


def main():
    lines = [
        "# Résultat — Overlay levé January Barometer (pré-enregistré, règle renforcée)",
        "",
        f"Position = CAP={CAP}x de février à décembre de l'année Y si le rendement de janvier(Y) "
        "(déc(Y-1)→jan(Y)) est positif, 1.0x sinon (et toujours 1.0x en janvier). Décision annuelle.",
        "",
        "| Marché | Nb années testables | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
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

        pos = position_for(df)
        n_years = len(set(pd.to_datetime(df["date"]).dt.year.values)) - 1

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
            f"| {name} | {n_years} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*(pos > 1.0).mean():.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append("**Prudence méthodologique** : le Composite (5 ans, ~4 observations annuelles) et "
                 "les marchés à historique court fournissent un nombre d'observations de janvier "
                 "bien plus faible que NDX (40 ans, ~40 observations) — le résultat NDX est le "
                 "plus informatif des cinq, les autres marchés doivent être lus avec prudence.")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_january_barometer_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
