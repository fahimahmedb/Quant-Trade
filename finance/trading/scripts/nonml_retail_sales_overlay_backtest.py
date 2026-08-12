"""Backtest — Ventes au détail US (RSXFS, glissement annuel), overlay
défensif (spécification pré-enregistrée dans
PREREG_retail_sales_overlay.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, la technique de tercile expanding, le glissement
annuel 12 mois et le décalage de publication d'un mois déjà établis au
#195/#203/#283/#284 (Règle 7). Dernière construction du canal
"activité économique réelle" testée dans ce backlog.
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
CUT = 0.5
TERCILE_PCT = 100.0 / 3.0
YOY_MONTHS = 12
PUBLICATION_LAG_MONTHS = 1

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def build_retail_growth_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "retail_sales_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["RSXFS"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["RSXFS"].astype(float).values
    obs_dates = raw["observation_date"].values

    growth = np.full(len(vals), np.nan)
    growth[YOY_MONTHS:] = np.log(vals[YOY_MONTHS:] / vals[:-YOY_MONTHS])

    # Publication ~2-3 semaines apres la fin du mois : decalage d'un
    # mois calendaire avant ffill (meme convention que #195/#203/#283).
    available_dates = pd.DatetimeIndex(obs_dates) + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    s = pd.Series(growth, index=available_dates).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_retail_growth_lag(dates: pd.DatetimeIndex, retail_series: pd.Series) -> np.ndarray:
    y = retail_series.reindex(dates, method="ffill")
    return y.shift(1).values


def expanding_tercile_cut_low(growth: np.ndarray) -> np.ndarray:
    """CUT quand growth(t) est dans son tercile expanding le PLUS BAS
    (consommation la plus faible = faiblesse economique = defavorable)."""
    T = len(growth)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(growth)))
    for t in range(start, T):
        if not np.isfinite(growth[t]):
            continue
        hist = growth[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, TERCILE_PCT)
        pos[t] = CUT if growth[t] <= thresh else 1.0
    return pos


def main():
    retail_series = build_retail_growth_series()

    lines = [
        "# Résultat — Ventes au détail US (RSXFS, glissement annuel), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si RetailGrowth(t)=log(RSXFS(t)/RSXFS(t-12)) est dans son tercile "
        f"expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
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
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        retail_lag_full = load_retail_growth_lag(dates, retail_series)
        retail_lag = retail_lag_full[1:]
        pos_full = expanding_tercile_cut_low(retail_lag)

        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:]
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)
        assert np.isfinite(pos).all()

        frac_cut = float((pos == CUT).mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(bh_t)} | {100*frac_cut:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_retail_sales_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_retail_sales_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
