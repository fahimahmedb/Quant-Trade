"""Backtest — "January effect" (proxy prix bas) en overlay
(spécification pré-enregistrée dans
PREREG_january_effect_lowprice_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée -- référence
= portefeuille tercile "prix bas" 1.0x en permanence.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0


def load_all_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > REBAL_EVERY:
            series[path.stem] = close
    return series


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()

    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T = len(P)
    tickers = list(P.columns)
    n_tickers = len(tickers)
    print(f"Univers exploitable : {n_tickers} tickers, {T} séances (calendrier UNION) "
          f"({P.index[0].date()} → {P.index[-1].date()})")

    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)

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
            # tercile au prix de cloture LE PLUS FAIBLE (proxy taille)
            low_idx = elig[np.argsort(c[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowprice[t:end] = w

    is_january = np.array([d.month == 1 for d in P.index])
    exposure = np.where(is_january, CAP, 1.0)

    weights_base = weights_lowprice
    weights_lev = weights_lowprice * exposure[:, None]

    R_safe = np.nan_to_num(R.values, nan=0.0)
    pnl_base = (weights_base[start:] * R_safe[start:]).sum(axis=1)
    pnl_lev = (weights_lev[start:] * R_safe[start:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start:], axis=0, prepend=weights_base[start:start+1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(pnl_base)
    me_lev = trading_metrics(pnl_lev)
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    n_jan_days = int(is_january[start:].sum())
    n_total_days = T - start

    lines = [
        "# Résultat — \"January effect\" (proxy prix bas) en overlay (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {n_total_days} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les "
        f"{REBAL_EVERY}j, tercile au PRIX DE CLÔTURE le plus faible (proxy taille — "
        f"vraie capitalisation boursière non disponible, voir limite dans PREREG). "
        f"Overlay actif {100*n_jan_days/n_total_days:.1f}% du temps (mois de janvier).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Tercile prix bas 1.0x (référence) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **+ overlay janvier x{CAP}** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_january_effect_lowprice_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
