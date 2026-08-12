"""Backtest — Overlay défensif vitesse du taux court DGS3MO
(spécification pré-enregistrée dans PREREG_rate_velocity_regime_overlay.md,
committée avant ce script). Réutilise `load_rate_lag`/fenêtre 63j du
#175 mais avec une construction méthodologiquement distincte (tercile
expanding de la MAGNITUDE, pas le signe brut ; design purement défensif
sans jambe d'amplification) — voir PREREG pour la distinction explicite.
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
N = 63  # meme fenetre que #175, Regle 7
CUT = 0.5
TERCILE_PCT = 100.0 / 3.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def load_rate_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Taux DGS3MO connu a la cloture de la veille (ffill + shift(1)),
    meme convention que #175/#178."""
    raw = pd.read_csv(REPO_ROOT / "data" / "dgs3mo_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")["DGS3MO"].astype(float).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    y = s.reindex(dates, method="ffill")
    return y.shift(1).values


def delta_series(rate_lag: np.ndarray) -> np.ndarray:
    T = len(rate_lag)
    delta = np.full(T, np.nan)
    for t in range(N, T):
        if np.isfinite(rate_lag[t]) and np.isfinite(rate_lag[t - N]):
            delta[t] = rate_lag[t] - rate_lag[t - N]
    return delta


def expanding_tercile_cut_high(delta: np.ndarray) -> np.ndarray:
    """CUT quand delta(t) est dans son tercile expanding le PLUS HAUT
    (resserrement le plus rapide observe jusqu'a present)."""
    T = len(delta)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(delta)))
    for t in range(start, T):
        if not np.isfinite(delta[t]):
            continue
        hist = delta[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = CUT if delta[t] >= thresh else 1.0
    return pos


def main():
    lines = [
        "# Résultat — Overlay défensif vitesse du taux court DGS3MO (pré-enregistré, règle renforcée)",
        "",
        f"`position(t) = {CUT}x` si delta(t-1)=DGS3MO_lag(t-1)-DGS3MO_lag(t-1-{N}) est dans son "
        f"tercile expanding le plus haut (resserrement le plus rapide), `1,0x` sinon. Coûts {COST_BPS:.0f} bps.",
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

        rate_lag = load_rate_lag(dates)
        delta = delta_series(rate_lag)
        pos_full = expanding_tercile_cut_high(delta)

        pos_full = pos_full[:-1]
        bh_full_aligned = bh_full
        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:]
        bh_t = bh_full_aligned[start:]
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
            np.savez(ROOT / "results" / "nonml_rate_velocity_regime_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_rate_velocity_regime_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
