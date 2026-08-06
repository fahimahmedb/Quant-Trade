"""Backtest — Indice des conditions financières NFCI, overlay défensif
(spécification pré-enregistrée dans
PREREG_financial_conditions_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5
marchés (≥4/5).

Réutilise CUT=0,5, le NIVEAU brut (comme BAA10Y #199, DRCCLACBS #286)
et la technique de tercile expanding déjà établies, et le décalage de
publication de 7 jours pour série hebdomadaire déjà validé à l'ICSA
(#204), Règle 7.
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
PUBLICATION_LAG_DAYS = 7

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def build_nfci_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "nfci_weekly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["NFCI"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["NFCI"].astype(float).values
    obs_dates = raw["observation_date"].values

    # Publication ~7 jours apres la fin de la semaine (meme convention
    # que l'ICSA #204).
    available_dates = pd.DatetimeIndex(obs_dates) + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    s = pd.Series(vals, index=available_dates)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_nfci_lag(dates: pd.DatetimeIndex, nfci_series: pd.Series) -> np.ndarray:
    y = nfci_series.reindex(dates, method="ffill")
    return y.shift(1).values


def expanding_tercile_cut_high(level: np.ndarray) -> np.ndarray:
    """CUT quand level(t) est dans son tercile expanding le PLUS HAUT
    (conditions financieres les plus tendues observees jusqu'a present)."""
    T = len(level)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(level)))
    for t in range(start, T):
        if not np.isfinite(level[t]):
            continue
        hist = level[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = CUT if level[t] >= thresh else 1.0
    return pos


def main():
    nfci_series = build_nfci_series()

    lines = [
        "# Résultat — Indice des conditions financières NFCI, overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si NFCI_lag(t-1) est dans son tercile expanding le plus HAUT, "
        f"`1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        nfci_lag_full = load_nfci_lag(dates, nfci_series)
        nfci_lag = nfci_lag_full[1:]
        pos_full = expanding_tercile_cut_high(nfci_lag)

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
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

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
            np.savez(ROOT / "results" / "nonml_financial_conditions_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_financial_conditions_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
