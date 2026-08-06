"""Backtest — Overlay défensif "durée du drawdown" (spécification
pré-enregistrée dans PREREG_drawdown_duration_overlay.md, committée
avant ce script). Technique de tercile expanding + CUT=0,5x réutilisée
telle quelle des #169/#177/#183/#191/#192/#193/#195 (Règle 7). n_trials=1,
aucune dépendance ML. Règle de succès renforcée.
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

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def duration_series(close: np.ndarray) -> np.ndarray:
    """duration(t) = nb de seances depuis le dernier plus haut glissant
    causal (running max inclusif). duration(t)=0 si close(t) est un
    nouveau record."""
    n = len(close)
    dur = np.zeros(n, dtype=float)
    running_max = -np.inf
    for t in range(n):
        if close[t] >= running_max:
            dur[t] = 0.0
            running_max = close[t]
        else:
            dur[t] = dur[t - 1] + 1.0 if t > 0 else 1.0
    return dur


def expanding_tercile_cut_high(duration_lag: np.ndarray) -> np.ndarray:
    """CUT quand duration_lag(t) est dans son tercile expanding le PLUS
    HAUT (les phases de repli les plus longues observees jusqu'a present)."""
    T = len(duration_lag)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(duration_lag)))
    for t in range(start, T):
        if not np.isfinite(duration_lag[t]):
            continue
        hist = duration_lag[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = CUT if duration_lag[t] >= thresh else 1.0
    return pos


def main():
    lines = [
        "# Résultat — Overlay défensif durée du drawdown (pré-enregistré, règle renforcée)",
        "",
        f"`position(t) = {CUT}x` si duration(t-1) (séances depuis le dernier plus haut "
        f"glissant) est dans son tercile expanding le plus haut, `1,0x` sinon. Coûts {COST_BPS:.0f} bps.",
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

        dur = duration_series(close)
        dur_lag_full = np.roll(dur, 1)
        dur_lag_full[0] = np.nan
        dur_lag = dur_lag_full[1:]

        pos_full = expanding_tercile_cut_high(dur_lag)
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
            np.savez(ROOT / "results" / "nonml_drawdown_duration_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_drawdown_duration_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
