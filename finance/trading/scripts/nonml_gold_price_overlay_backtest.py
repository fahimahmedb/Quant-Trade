"""Backtest — Momentum de l'or (ETF GLD via Yahoo Finance, log-return
21j), overlay défensif (spécification pré-enregistrée dans
PREREG_gold_price_overlay.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, RET_WINDOW=21 et TERCILE_PCT du #198 (force du
dollar, Règle 7). Direction du gate : tercile le PLUS HAUT (hausse de
l'or = flight-to-quality = défensif), OPPOSÉE à la direction des 3
commodités déjà testées (#283/#284/#326, tercile le plus bas), Règle 2
déclarée au PREREG.
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

TERCILE_PCT = 100.0 / 3.0


def load_gold_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "gold_gld_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["GLD"] = pd.to_numeric(raw["GLD"], errors="coerce")
    s = raw.dropna(subset=["GLD"]).set_index("observation_date")["GLD"]
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_gold_mom_lag(dates: pd.DatetimeIndex, gold_series: pd.Series) -> np.ndarray:
    gold_aligned = gold_series.reindex(dates, method="ffill")
    gold_vals = gold_aligned.values
    mom = np.full(len(gold_vals), np.nan)
    mom[RET_WINDOW:] = np.log(gold_vals[RET_WINDOW:] / gold_vals[:-RET_WINDOW])
    mom_series = pd.Series(mom, index=dates)
    return mom_series.shift(1).values


def expanding_tercile_cut_high(mom: np.ndarray) -> np.ndarray:
    """CUT quand mom(t) est dans son tercile expanding le PLUS HAUT
    (hausse marquee de l'or sur 21j = flight-to-quality = defavorable
    pour les actions, direction opposee aux commodites industrielles
    deja testees, declaree au PREREG)."""
    T = len(mom)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(mom)))
    for t in range(start, T):
        if not np.isfinite(mom[t]):
            continue
        hist = mom[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = CUT if mom[t] >= thresh else 1.0
    return pos


def main():
    gold_series = load_gold_series()

    lines = [
        "# Résultat — Momentum de l'or (GLD, log-return 21j), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si GoldMom_lag(t)=log(GLD(t-1)/GLD(t-1-{RET_WINDOW})) est dans son tercile "
        f"expanding le plus HAUT (hausse marquée de l'or, flight-to-quality), `1.0x` sinon. "
        f"Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        gold_mom_lag_full = load_gold_mom_lag(dates, gold_series)
        gold_mom_lag = gold_mom_lag_full[1:]
        pos_full = expanding_tercile_cut_high(gold_mom_lag)

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
            np.savez(ROOT / "results" / "nonml_gold_price_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_gold_price_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
