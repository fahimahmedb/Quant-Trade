"""Backtest — Effet janvier stock-level (Keim 1983, spécification
pré-enregistrée dans PREREG_january_effect_stocklevel.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée (Sharpe ET rendement absolu).
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
COST_BPS = 5.0
DECILE = 0.10


def load_all_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > 60:
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
    print(f"Univers exploitable : {n_tickers} tickers, {T} séances "
          f"({P.index[0].date()} → {P.index[-1].date()})")

    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    dates = P.index
    years = dates.year.values
    months = dates.month.values

    # dernier indice de chaque (annee, mois) et premier indice
    last_idx_of_month, first_idx_of_month = {}, {}
    for i in range(T):
        key = (years[i], months[i])
        last_idx_of_month[key] = i
        if key not in first_idx_of_month:
            first_idx_of_month[key] = i

    n_top = max(1, int(round(n_tickers * DECILE)))
    weights_strategy = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    # portefeuille par defaut = univers complet equipondere (identique a BH)
    for i in range(T):
        listed = exists[i]
        n_listed = listed.sum()
        if n_listed > 0:
            w = listed.astype(float) / n_listed
            weights_bh[i] = w
            weights_strategy[i] = w

    all_years = sorted(set(years))
    n_january_windows = 0
    for y in all_years:
        i_nov_first = first_idx_of_month.get((y, 11))
        i_dec_last = last_idx_of_month.get((y, 12))
        i_jan_first = first_idx_of_month.get((y + 1, 1))
        i_jan_last = last_idx_of_month.get((y + 1, 1))
        if None in (i_nov_first, i_dec_last, i_jan_first, i_jan_last):
            continue

        c_nov = close[i_nov_first]
        c_dec = close[i_dec_last]
        with np.errstate(all="ignore"):
            nov_dec_ret = c_dec / c_nov - 1.0
        valid = np.isfinite(c_nov) & np.isfinite(c_dec)
        eligible_idx = np.where(valid)[0]
        if len(eligible_idx) == 0:
            continue

        n_top_t = min(n_top, len(eligible_idx))
        losers_idx = eligible_idx[np.argsort(nov_dec_ret[eligible_idx])[:n_top_t]]

        # applique le portefeuille perdants pendant janvier(Y+1), uniquement
        # sur les titres encore cotes ce jour-la (reponderation implicite,
        # coherent avec la convention exists du reste du backlog)
        for i in range(i_jan_first, i_jan_last + 1):
            listed_losers = losers_idx[exists[i, losers_idx]]
            if len(listed_losers) > 0:
                w = np.zeros(n_tickers)
                w[listed_losers] = 1.0 / len(listed_losers)
                weights_strategy[i] = w
        n_january_windows += 1

    pnl_strategy = (weights_strategy * R).sum(axis=1)
    pnl_bh = (weights_bh * R).sum(axis=1)

    turn_strategy = np.abs(np.diff(weights_strategy, axis=0, prepend=weights_strategy[:1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_strategy = pnl_strategy - turn_strategy * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_strategy = trading_metrics(pnl_strategy)
    me_bh = trading_metrics(pnl_bh)

    equity_strategy = np.cumprod(1.0 + pnl_strategy)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_strategy_total = equity_strategy[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_strategy["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_strategy_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Effet janvier stock-level, tax-loss selling (Keim 1983, pré-enregistré, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T} séances ({P.index[0].date()} → "
        f"{P.index[-1].date()}), {n_january_windows} fenêtres de janvier testables. "
        f"Décile ({n_top} titres) des plus perdants nov-déc, détenu pendant janvier suivant, "
        "équipondéré univers complet le reste de l'année.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Décile perdants nov-déc en janvier** | **{me_strategy['sharpe_ann']:+.2f}** | "
        f"**{100*ret_strategy_total:+.1f}%** | {me_strategy['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        "**Prudence méthodologique** : seulement "
        f"{n_january_windows} fenêtres de janvier testables sur cet échantillon (2021-2026) — "
        "échantillon limité, comparable à la prudence déjà déclarée au January Barometer (#59).",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_january_effect_stocklevel_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
