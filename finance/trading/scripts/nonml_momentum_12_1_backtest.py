"""Backtest — Momentum "12-1 mois" (Jegadeesh & Titman 1993, spécification
pré-enregistrée dans PREREG_momentum_12_1.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée (Sharpe ET
rendement absolu). Structure reprise du #4 (momentum_52w_high).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
LOOKBACK = 252
SKIP = 21
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

    # meme correction de bug que le #4 : calendrier de reference = UNION
    # des dates (pas intersection stricte, qui s'effondrerait a la date
    # de la plus recente introduction en bourse parmi les tickers)
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
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.

    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)

    # signal momentum 12-1 : close(t-SKIP)/close(t-LOOKBACK) - 1
    # (exclut explicitement le rendement du dernier mois du signal)
    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    weights_mom = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    n_top = max(1, int(round(n_tickers * TERCILE)))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        m = momentum[t]
        valid = np.isfinite(m)
        eligible_idx = np.where(valid)[0]
        n_top_t = min(n_top, len(eligible_idx))
        if n_top_t > 0:
            top_idx = eligible_idx[np.argsort(-m[eligible_idx])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_mom[t:end] = w

        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    start = LOOKBACK
    R_safe = np.nan_to_num(R, nan=0.0)
    pnl_mom = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)

    turn_mom = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    # Sauvegarde INCONDITIONNELLE du P&L (cycle #427, lot 5) : ce candidat porte
    # un PASS et restait invisible au balayage de doublons. Schema PANIER du #419
    # (le turnover d'un panier n'est pas derivable d'une exposition scalaire).
    # Les P&L stockes sont BRUTS. Aucune ligne de calcul n'est modifiee.
    np.savez(ROOT / "results" / "nonml_momentum_12_1_pnl.npz",
             pnl_gross_ov=pnl_mom + turn_mom * (COST_BPS / 1e4),
             pnl_gross_bh=pnl_bh + turn_bh * (COST_BPS / 1e4),
             turn_ov=turn_mom, turn_bh=turn_bh,
             dates=np.asarray(P.index)[start:], cost_bps=COST_BPS)

    me_mom = trading_metrics(np.log1p(pnl_mom))
    me_bh = trading_metrics(np.log1p(pnl_bh))

    equity_mom = np.cumprod(1.0 + pnl_mom)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_mom_total = equity_mom[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_mom["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_mom_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum 12-1 mois (Jegadeesh & Titman, pré-enregistré, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les "
        f"{REBAL_EVERY}j, tercile supérieur ({n_top} titres) par momentum(t)="
        f"close(t-{SKIP})/close(t-{LOOKBACK})-1.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Momentum 12-1 (tercile sup.)** | **{me_mom['sharpe_ann']:+.2f}** | "
        f"**{100*ret_mom_total:+.1f}%** | {me_mom['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe momentum > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total momentum > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_12_1_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
