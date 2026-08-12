"""Backtest — Momentum 52-semaines / proximité du plus haut annuel
(spécification pré-enregistrée dans PREREG_momentum_52w_high.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Soumis à la règle de
succès renforcée (Sharpe ET rendement absolu).

CORRECTION 01/08/2026 -- fuite d'exécution « même barre » (voir
`results/nonml_same_bar_execution_audit.md`) : les poids décidés sur la
clôture du jour t (signal close(t)/max252(t), qui inclut le rendement du
jour t) étaient appliqués au rendement DU JOUR t lui-même. `main` décale
désormais les poids d'un jour par défaut (`causal=True` : décider à la
clôture de t-1, détenir pendant t). `causal=False` reproduit exactement le
comportement fautif d'origine.
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

    # Calendrier de reference = UNION des dates (pas intersection stricte) : une
    # intersection stricte s'effondre a la date de la plus RECENTE introduction en
    # bourse parmi les 99 tickers (ex. CoreWeave, IPO 2025-03-28), tronquant
    # artificiellement ~4 ans d'historique a 80 jours -- bug trouve et corrige ici,
    # AVANT tout commit de resultat. Chaque titre est traite comme absent (NaN, exclu
    # du classement ce jour-la) avant sa date d'introduction, pas comme manquant.
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

    # Rendements SIMPLES par titre. Le rendement d'un panier pondere est
    # somme(w_i * r_simple_i) ; une moyenne ponderee de rendements LOG n'est le
    # rendement log de rien (l'agregation entre titres n'est pas additive en log).
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    # .copy() : sous pandas >= 3 (copy-on-write) `.values` peut etre en lecture seule.
    R = (P / P.shift(1) - 1.0).values.copy()  # rendement quotidien [T, n], NaN si absent
    R[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)  # ticker cote ce jour-la

    # plus haut glissant 252j -- nanmax, NaN tant que le titre n'a pas 252j d'historique
    rolling_max = np.full((T, n_tickers), np.nan)
    has_full_window = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full_window[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full_window, close / rolling_max, np.nan)

    weights_leaders = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    n_top = max(1, int(round(n_tickers * TERCILE)))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        r = ratio[t]
        valid = np.isfinite(r)
        eligible_idx = np.where(valid)[0]
        n_top_t = min(n_top, len(eligible_idx))
        if n_top_t > 0:
            top_idx = eligible_idx[np.argsort(-r[eligible_idx])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w

        listed = exists[t]  # univers "buy&hold" = tous les titres cotes ce jour-la (equipondere)
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    if causal:
        weights_leaders = lag_one_day(weights_leaders)
        weights_bh = lag_one_day(weights_bh)

    start = LOOKBACK
    R_safe = np.nan_to_num(R, nan=0.0)  # position=0 sur un titre absent -> contribution nulle, coherent
    pnl_leaders = (weights_leaders[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)

    turn_leaders = np.abs(np.diff(weights_leaders[start:], axis=0, prepend=weights_leaders[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_leaders = pnl_leaders - turn_leaders * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    # pnl_* sont desormais des rendements SIMPLES de portefeuille. trading_metrics
    # attend une serie LOG (eq = cumsum, MDD converti par exp) : on convertit.
    assert (pnl_leaders > -1.0).all() and (pnl_bh > -1.0).all(), \
        "rendement simple <= -100% : log1p non defini"
    me_leaders = trading_metrics(np.log1p(pnl_leaders))
    me_bh = trading_metrics(np.log1p(pnl_bh))

    equity_leaders = np.cumprod(1.0 + pnl_leaders)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_leaders_total = equity_leaders[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_leaders["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_leaders_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum 52-semaines (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les "
        f"{REBAL_EVERY}j, tercile supérieur ({n_top} titres) par ratio prix/plus-haut-52sem.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Leaders 52w-high (tercile sup.)** | **{me_leaders['sharpe_ann']:+.2f}** | "
        f"**{100*ret_leaders_total:+.1f}%** | {me_leaders['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe leaders > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total leaders > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_52w_high_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
