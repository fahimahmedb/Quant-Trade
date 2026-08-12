"""Simulation — 300 EUR, "January effect" (proxy prix bas) en overlay,
~3 derniers mois. Spécification pré-enregistrée (CAP=2.0x), aucun
paramètre retouché après les résultats précédents.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_january_effect_lowprice_overlay_backtest import (  # noqa: E402
    load_all_prices, REBAL_EVERY, TERCILE, COST_BPS, CAP,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowprice = np.zeros((T, n_tickers))
    start = REBAL_EVERY
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        c = close[t]
        elig = np.where(np.isfinite(c) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(c[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowprice[t:end] = w

    is_january = np.array([d.month == 1 for d in P.index])
    exposure = np.where(is_january, CAP, 1.0)
    weights_lev = weights_lowprice * exposure[:, None]

    pnl_base_full = (weights_lowprice * R).sum(axis=1)
    turn_base = np.abs(np.diff(weights_lowprice, axis=0, prepend=weights_lowprice[:1])).sum(axis=1) / 2.0
    pnl_base_full = pnl_base_full - turn_base * (COST_BPS / 1e4)

    pnl_lev_full = (weights_lev * R).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev, axis=0, prepend=weights_lev[:1])).sum(axis=1) / 2.0
    pnl_lev_full = pnl_lev_full - turn_lev * (COST_BPS / 1e4)

    pnl_base = pnl_base_full[-WINDOW_DAYS:]
    pnl_lev = pnl_lev_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]
    n_jan_in_window = int(is_january[-WINDOW_DAYS:].sum())

    equity_base = CAPITAL0 * np.cumprod(1.0 + pnl_base)
    equity_lev = CAPITAL0 * np.cumprod(1.0 + pnl_lev)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_base, me_lev = trading_metrics(np.log1p(pnl_base)), trading_metrics(np.log1p(pnl_lev))

    lines = [
        "# Simulation — 300 EUR, \"January effect\" (proxy prix bas) en overlay (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_base)} séances). "
        "Référence = tercile prix bas 1.0x (pas Buy&Hold classique).",
        "",
    ]
    if n_jan_in_window == 0:
        lines.append(
            "**Attention — fenêtre non informative** : les ~3 derniers mois disponibles "
            f"({dates[0].date()} → {dates[-1].date()}) ne contiennent AUCUN jour de janvier. "
            "L'overlay est donc rigoureusement IDENTIQUE à la référence 1.0x sur cette fenêtre "
            "précise (0 jour de levier) — signalé honnêtement plutôt que de présenter un "
            "résultat trompeur. Le verdict statistique réel reste celui du backtest complet "
            "(2021-2026, PASS, voir robustesse plateau 4/4)."
        )
        lines.append("")
    lines.extend([
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Tercile prix bas 1.0x (référence) | {equity_base[-1]:.2f} EUR | "
        f"{100*(equity_base[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_base):.1f}% | {me_base['sharpe_ann']:+.2f} |",
        f"| **+ overlay janvier x{CAP}** | **{equity_lev[-1]:.2f} EUR** | "
        f"**{100*(equity_lev[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_lev):.1f}% | {me_lev['sharpe_ann']:+.2f} |",
        "",
        f"Jours de janvier dans cette fenêtre : {n_jan_in_window}/{len(pnl_base)}.",
    ])

    out = ROOT / "results" / "nonml_january_effect_lowprice_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
