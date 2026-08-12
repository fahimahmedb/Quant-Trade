"""Backtest — Force relative marchés émergents vs développés (EEM/SPY,
log-return 21j du ratio), overlay défensif (spécification
pré-enregistrée dans PREREG_em_dm_relative_strength_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, RET_WINDOW=21 et TERCILE_PCT du #198 (force du
dollar, Règle 7). Direction du gate : tercile le PLUS BAS
(sous-performance des émergents = risk-off = défensif), construction
de ratio identique au #353 (rotation sectorielle) mais direction
inversée (déclarée au PREREG par cohérence économique).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_dollar_strength_overlay_backtest import COST_BPS, CUT, MARKETS, RET_WINDOW  # noqa: E402
from nonml_bitcoin_momentum_overlay_backtest import expanding_tercile_cut_low  # noqa: E402


def load_ratio_series() -> pd.Series:
    eem = pd.read_csv(REPO_ROOT / "data" / "eem_etf_daily.csv")
    spy = pd.read_csv(REPO_ROOT / "data" / "spy_etf_daily.csv")
    eem["observation_date"] = pd.to_datetime(eem["observation_date"])
    spy["observation_date"] = pd.to_datetime(spy["observation_date"])
    eem["EEM"] = pd.to_numeric(eem["EEM"], errors="coerce")
    spy["SPY"] = pd.to_numeric(spy["SPY"], errors="coerce")
    s_eem = eem.dropna(subset=["EEM"]).set_index("observation_date")["EEM"]
    s_spy = spy.dropna(subset=["SPY"]).set_index("observation_date")["SPY"]
    s_eem = s_eem[~s_eem.index.duplicated(keep="first")].sort_index()
    s_spy = s_spy[~s_spy.index.duplicated(keep="first")].sort_index()
    common = s_eem.index.intersection(s_spy.index)
    ratio = (s_eem.reindex(common) / s_spy.reindex(common)).dropna()
    return ratio


def load_ratio_mom_lag(dates: pd.DatetimeIndex, ratio_series: pd.Series) -> np.ndarray:
    ratio_aligned = ratio_series.reindex(dates, method="ffill")
    ratio_vals = ratio_aligned.values
    mom = np.full(len(ratio_vals), np.nan)
    mom[RET_WINDOW:] = np.log(ratio_vals[RET_WINDOW:] / ratio_vals[:-RET_WINDOW])
    mom_series = pd.Series(mom, index=dates)
    return mom_series.shift(1).values


def main():
    ratio_series = load_ratio_series()

    lines = [
        "# Résultat — Force relative marchés émergents vs développés (EEM/SPY, log-return 21j), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si RatioMom_lag(t)=log(Ratio(t-1)/Ratio(t-1-{RET_WINDOW})) avec "
        "Ratio=EEM/SPY est dans son tercile expanding le plus BAS (sous-performance marquée des "
        f"émergents), `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        ratio_mom_lag_full = load_ratio_mom_lag(dates, ratio_series)
        ratio_mom_lag = ratio_mom_lag_full[1:]
        pos_full = expanding_tercile_cut_low(ratio_mom_lag)

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
            np.savez(ROOT / "results" / "nonml_em_dm_relative_strength_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_em_dm_relative_strength_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
