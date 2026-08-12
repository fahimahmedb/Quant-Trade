"""Backtest — Régime de NIVEAU du taux LONG DGS10, overlay coupé/levé
(spécification pré-enregistrée dans
PREREG_long_rate_level_regime_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5 marchés
(≥4/5).

Même structure exacte que le #175 (`nonml_rate_level_regime_overlay_backtest.py`,
DGS3MO), Règle 7 — seule la série de taux change (DGS10 au lieu de DGS3MO).
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
N = 63  # ~1 trimestre, meme fenetre que le #175
CUT = 0.5
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def load_rate_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Taux DGS10 connu a la cloture de la veille (ffill + shift(1)),
    meme convention que le #175 (DGS3MO)."""
    raw = pd.read_csv(REPO_ROOT / "data" / "dgs10_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")["DGS10"].astype(float).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    y = s.reindex(dates, method="ffill")
    y_lag = y.shift(1)
    return y_lag.values


def regime_position(rate_lag: np.ndarray) -> np.ndarray:
    T = len(rate_lag)
    pos = np.full(T, np.nan)
    for t in range(N, T):
        if not (np.isfinite(rate_lag[t]) and np.isfinite(rate_lag[t - N])):
            continue
        delta = rate_lag[t] - rate_lag[t - N]
        if delta > 0:
            pos[t] = CUT
        elif delta < 0:
            pos[t] = CAP
        else:
            pos[t] = 1.0
    return pos


def main():
    lines = [
        "# Résultat — Régime de niveau du taux LONG DGS10 (pré-enregistré, complète le #175)",
        "",
        f"`position(t) = {CUT}x` si taux(t-1) > taux(t-1-{N}) (hausse), "
        f"`{CAP}x` si baisse, `1.0x` si égal. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps régime hausse | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
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

        rate_lag = load_rate_lag(dates)
        pos_full = regime_position(rate_lag)

        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:-1] if start < len(pos_full) - 1 else np.array([])
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)
        assert np.isfinite(pos).all()

        frac_hausse = float((pos == CUT).mean())

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
            f"| {name} | {len(bh_t)} | {100*frac_hausse:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_long_rate_level_regime_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
