"""Backtest — Momentum de constance (spécification pré-enregistrée dans
PREREG_momentum_consistency.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée (Sharpe ET rendement
absolu).

CORRECTION 01/08/2026 -- fuite d'exécution « même barre » (voir
`results/nonml_same_bar_execution_audit.md`) : `consistency_at` calcule la
fraction de blocs positifs sur les BLOCK_LEN séances précédant ET
INCLUANT le jour t (`end_idx = t`), donc le premier bloc contient le
rendement du jour t lui-même ; les poids qui en découlaient étaient
appliqués au rendement `R[t]` déjà réalisé. `main` décale désormais les
poids finaux d'un jour par défaut (`causal=True`). `causal=False`
reproduit le comportement fautif d'origine.
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
BLOCK_LEN = 21
N_BLOCKS = 12
LOOKBACK = BLOCK_LEN * N_BLOCKS  # = 252
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


def consistency_at(close: np.ndarray, t: int) -> np.ndarray:
    """Renvoie, pour chaque titre, la fraction des N_BLOCKS blocs de
    BLOCK_LEN seances precedant (et incluant) le jour t avec un rendement
    de bloc positif. NaN si le titre n'a pas les LOOKBACK jours requis
    (donnee manquante dans un des blocs)."""
    n_tickers = close.shape[1]
    block_positive_count = np.zeros(n_tickers)
    block_valid_count = np.zeros(n_tickers)
    for b in range(N_BLOCKS):
        end_idx = t - b * BLOCK_LEN
        start_idx = end_idx - BLOCK_LEN
        c_end = close[end_idx]
        c_start = close[start_idx]
        valid = np.isfinite(c_end) & np.isfinite(c_start)
        block_valid_count += valid
        with np.errstate(all="ignore"):
            block_ret = np.where(valid, c_end / c_start - 1.0, np.nan)
        block_positive_count += np.where(valid & (block_ret > 0), 1.0, 0.0)

    full_history = block_valid_count == N_BLOCKS
    consistency = np.where(full_history, block_positive_count / N_BLOCKS, np.nan)
    return consistency


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Correction de la fuite « même barre »
    documentée dans `results/nonml_same_bar_execution_audit.md`."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main(causal=True):
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
    print(f"Univers exploitable : {n_tickers} tickers, {T} séances (calendrier UNION, "
          f"chaque titre pondéré seulement depuis sa 1ère cotation) "
          f"({P.index[0].date()} → {P.index[-1].date()})")

    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)

    weights_consistency = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    n_top = max(1, int(round(n_tickers * TERCILE)))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        cons = consistency_at(close, t)
        valid = np.isfinite(cons)
        eligible_idx = np.where(valid)[0]
        n_top_t = min(n_top, len(eligible_idx))
        if n_top_t > 0:
            top_idx = eligible_idx[np.argsort(-cons[eligible_idx])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_consistency[t:end] = w

        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    if causal:
        weights_consistency = lag_one_day(weights_consistency)
        weights_bh = lag_one_day(weights_bh)

    start = LOOKBACK
    R_safe = np.nan_to_num(R, nan=0.0)
    pnl_cons = (weights_consistency[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)

    turn_cons = np.abs(np.diff(weights_consistency[start:], axis=0, prepend=weights_consistency[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_cons = pnl_cons - turn_cons * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_cons = trading_metrics(pnl_cons)
    me_bh = trading_metrics(pnl_bh)

    equity_cons = np.cumprod(1.0 + pnl_cons)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_cons_total = equity_cons[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_cons["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_cons_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum de constance (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les "
        f"{REBAL_EVERY}j, tercile supérieur par fraction de {N_BLOCKS} blocs de {BLOCK_LEN}j positifs.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Momentum de constance (tercile sup.)** | **{me_cons['sharpe_ann']:+.2f}** | "
        f"**{100*ret_cons_total:+.1f}%** | {me_cons['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
