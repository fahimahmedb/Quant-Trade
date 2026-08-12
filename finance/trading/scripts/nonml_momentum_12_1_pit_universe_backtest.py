"""Backtest — Momentum 12-1 (#73), univers POINT-IN-TIME réel du NDX-100
(spécification pré-enregistrée dans PREREG_momentum_12_1_pit_universe.md,
committée avant ce script). Réutilise STRICTEMENT (Règle 7) la
construction du #73 (LOOKBACK, SKIP, REBAL_EVERY, TERCILE, COST_BPS
inchangés) -- seul le filtre d'univers change, à chaque date de
rebalancement, aux titres RÉELLEMENT membres du NDX-100 ce jour-là
(`ndx100_membership.tickers_as_of_date`, déjà vendorée au #163). Ancrage
2015-01-01 comme au #163/#264. Isole si l'effondrement du #258 sous PIT
(cycle #264) vient du momentum lui-même ou du second tri turnover.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
LOOKBACK = 252
SKIP = 21
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
REBAL_ANCHOR = "2015-01-01"


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Précaution supplémentaire cohérente avec
    la convention actuelle -- #73 lui-même a déjà été vérifié non affecté par
    le bug même barre (SKIP=21j exclut déjà close(t)) le 01/08/2026."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def load_prices():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
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
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

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

    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    membership_log = []
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        elig_all = np.where(np.isfinite(m))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        membership_log.append((P.index[t], len(members), len(eligible)))

        n_top = max(1, int(round(len(eligible) * TERCILE)))
        n_top = min(n_top, len(eligible))
        if n_top > 0:
            top_idx = eligible[np.argsort(-m[eligible])[:n_top]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top
            weights_mom[t:end] = w
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

    weights_mom = lag_one_day(weights_mom)
    weights_bh = lag_one_day(weights_bh)

    start = first_rebal
    pnl_mom = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_mom = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    # P&L BRUT conserve avant deduction des couts + turnover : la batterie
    # Regle 9 (schema portefeuille) doit pouvoir recalculer le P&L a 3x et 5x.
    # Pour un panier le turnover vaut somme(|dw_i|)/2, non derivable d'une
    # exposition scalaire -- il doit donc etre sauvegarde explicitement.
    pnl_gross_ov_, pnl_gross_bh_ = pnl_mom.copy(), pnl_bh.copy()
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)
    np.savez(ROOT / "results" / "nonml_momentum_12_1_pit_universe_pnl.npz",
             pnl_gross_ov=pnl_gross_ov_, pnl_gross_bh=pnl_gross_bh_,
             turn_ov=turn_mom, turn_bh=turn_bh,
             dates=P.index.values[start:], cost_bps=COST_BPS)

    me_mom, me_bh = trading_metrics(np.log1p(pnl_mom)), trading_metrics(np.log1p(pnl_bh))
    ret_mom = np.cumprod(1.0 + pnl_mom)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    sharpe_ok = me_mom["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_mom > ret_bh
    verdict = sharpe_ok and ret_ok

    avg_coverage = np.mean([n_e / max(1, n_m) for _, n_m, n_e in membership_log])

    lines = [
        "# Résultat — Momentum 12-1 (#73), univers POINT-IN-TIME réel (cycle #265)",
        "",
        f"Univers PIT : {n_tickers} tickers avec prix PIT disponibles. Couverture moyenne de "
        f"l'univers investissable (éligibles/membres réels) : {100*avg_coverage:.1f}%. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        "Référence = Buy&Hold équipondéré (univers PIT réel à chaque date). Construction "
        "causale (`lag_one_day`).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT) | {me_bh['sharpe_ann']:+.2f} | "
        f"{100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Momentum 12-1 (univers PIT)** | **{me_mom['sharpe_ann']:+.2f}** | "
        f"**{100*ret_mom:+.1f}%** | {me_mom['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_12_1_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
