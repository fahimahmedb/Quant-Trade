"""Backtest — Momentum 12-1 + filtre Low-Volatility, double tri
(spécification pré-enregistrée dans PREREG_momentum_lowvol_doublesort.md,
committée avant ce script). Combine #73 (momentum) et #15 (filtre vol,
VOL_WINDOW=60). n_trials=1, aucune dépendance ML. Règle de succès
renforcée -- référence = momentum 12-1 seul (#73), pas Buy&Hold.
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
LOOKBACK = 252
SKIP = 21
VOL_WINDOW = 60
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0


def load_all_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > LOOKBACK + REBAL_EVERY:
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
    T, n_tickers = P.shape
    close = P.values
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    # signal momentum 12-1 (identique au #73)
    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    # vol realisee 60j (identique au #15 : ecart-type des rendements simples, causal)
    vol60 = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values

    weights_double = np.zeros((T, n_tickers))
    weights_momentum_only = np.zeros((T, n_tickers))
    n_top_mom_full = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        m = momentum[t]
        v = vol60[t]
        eligible = np.where(np.isfinite(m) & np.isfinite(v))[0]

        # reference : momentum 12-1 seul (#73), sur le meme univers eligible
        n_top_mom = min(n_top_mom_full, len(eligible))
        if n_top_mom > 0:
            top_mom_idx = eligible[np.argsort(-m[eligible])[:n_top_mom]]
            w = np.zeros(n_tickers)
            w[top_mom_idx] = 1.0 / n_top_mom
            weights_momentum_only[t:end] = w

        # double tri : etape 1, exclure le tercile le plus volatil parmi eligible
        n_keep = len(eligible) - max(1, int(round(len(eligible) * TERCILE)))
        if n_keep > 0 and len(eligible) > 0:
            survivors = eligible[np.argsort(v[eligible])[:n_keep]]  # les moins volatils gardes
            # etape 2 : parmi les survivants, tercile momentum le plus eleve (des survivants)
            n_top_double = max(1, int(round(len(survivors) * TERCILE)))
            n_top_double = min(n_top_double, len(survivors))
            if n_top_double > 0:
                top_double_idx = survivors[np.argsort(-m[survivors])[:n_top_double]]
                w2 = np.zeros(n_tickers)
                w2[top_double_idx] = 1.0 / n_top_double
                weights_double[t:end] = w2

    start = LOOKBACK
    pnl_double = (weights_double[start:] * R_safe[start:]).sum(axis=1)
    pnl_mom = (weights_momentum_only[start:] * R_safe[start:]).sum(axis=1)

    turn_double = np.abs(np.diff(weights_double[start:], axis=0, prepend=weights_double[start:start+1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_momentum_only[start:], axis=0, prepend=weights_momentum_only[start:start+1])).sum(axis=1) / 2.0
    pnl_double = pnl_double - turn_double * (COST_BPS / 1e4)
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)

    me_double = trading_metrics(np.log1p(pnl_double))
    me_mom = trading_metrics(np.log1p(pnl_mom))

    equity_double = np.cumprod(1.0 + pnl_double)
    equity_mom = np.cumprod(1.0 + pnl_mom)
    ret_double_total = equity_double[-1] - 1.0
    ret_mom_total = equity_mom[-1] - 1.0

    sharpe_ok = me_double["sharpe_ann"] > me_mom["sharpe_ann"]
    ret_ok = ret_double_total > ret_mom_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum 12-1 + filtre Low-Volatility, double tri (pré-enregistré, combinaison #73+#15)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les {REBAL_EVERY}j. "
        f"Référence = momentum 12-1 seul (cycle #73), PAS Buy&Hold. "
        f"Double tri : exclusion du tercile le plus volatil (vol {VOL_WINDOW}j), puis tercile momentum "
        "le plus élevé parmi les survivants.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Momentum 12-1 seul (référence, cycle #73, univers restreint) | {me_mom['sharpe_ann']:+.2f} | "
        f"{100*ret_mom_total:+.1f}% | {me_mom['max_drawdown_pct']:.1f}% |",
        f"| **Momentum 12-1 + filtre Low-Vol (double tri)** | **{me_double['sharpe_ann']:+.2f}** | "
        f"**{100*ret_double_total:+.1f}%** | {me_double['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe double tri > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement double tri > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_lowvol_doublesort_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
