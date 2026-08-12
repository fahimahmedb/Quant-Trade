"""Backtest — Low-Volatility Tilt (spécification pré-enregistrée dans
PREREG_low_vol_tilt.md, committée avant ce script). n_trials=1, aucune
dépendance ML. Réutilise la construction d'univers dynamique des cycles
#4/#5/#14.

CORRECTION 01/08/2026 -- fuite d'exécution « même barre » (voir
`results/nonml_same_bar_execution_audit.md`) : `vol.rolling(60).std()`
inclut par défaut pandas le rendement du jour t dans sa fenêtre, et les
poids qui en découlaient étaient appliqués au rendement `R[t]` déjà
réalisé. `main` décale désormais les poids d'un jour par défaut
(`causal=True`). `causal=False` reproduit le comportement fautif
d'origine. Ce cycle était déjà un FAIL avant correction (le verdict
n'était donc pas menacé par un excès de confiance) ; il est ré-exécuté
ici par souci d'exhaustivité, dans la même famille que #39.
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
VOL_WINDOW = 60
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > VOL_WINDOW + REBAL_EVERY:
            series[path.stem] = close
    return series


def build_universe():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    return P


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Correction de la fuite « même barre »
    documentée dans `results/nonml_same_bar_execution_audit.md`."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main(causal=True):
    P = build_universe()
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    # vol realisee roulante 60j par titre (pandas, gere nativement les NaN en debut de serie)
    vol = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values  # simple-return std, causal

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowvol = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    start = VOL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        v = vol[t]
        elig = np.where(np.isfinite(v) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(v[elig])[:n_low_t]]  # les PLUS FAIBLES vol
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowvol[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    if causal:
        weights_lowvol = lag_one_day(weights_lowvol)
        weights_bh = lag_one_day(weights_bh)

    pnl_lv = (weights_lowvol[start:] * R_safe[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_lv = np.abs(np.diff(weights_lowvol[start:], axis=0, prepend=weights_lowvol[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_lv = pnl_lv - turn_lv * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_lv, me_b = trading_metrics(np.log1p(pnl_lv)), trading_metrics(np.log1p(pnl_b))
    equity_lv = np.cumprod(1.0 + pnl_lv)
    equity_b = np.cumprod(1.0 + pnl_b)
    ret_lv, ret_b = equity_lv[-1] - 1.0, equity_b[-1] - 1.0

    sharpe_ok = me_lv["sharpe_ann"] > me_b["sharpe_ann"]
    ret_ok = ret_lv > ret_b
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Low-Volatility Tilt (pré-enregistré, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), vol réalisée {VOL_WINDOW}j, "
        f"rebalancement {REBAL_EVERY}j, tercile INFÉRIEUR de vol ({n_low} titres).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_b['sharpe_ann']:+.2f} | {100*ret_b:+.1f}% | "
        f"{me_b['max_drawdown_pct']:.1f}% |",
        f"| **Low-Vol (tercile inf.)** | **{me_lv['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lv:+.1f}%** | {me_lv['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe low-vol > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total low-vol > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_low_vol_tilt_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
