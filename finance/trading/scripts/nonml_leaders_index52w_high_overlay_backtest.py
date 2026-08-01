"""Backtest — Leaders 52-semaines + overlay levé proximité plus haut
52-semaines indice (spécification pré-enregistrée dans
PREREG_leaders_index52w_high_overlay.md, committée avant ce script).
Combine les cycles #4 et #37. n_trials=1, aucune dépendance ML. Règle de
succès renforcée -- référence = leaders 1.0x (cycle #4), pas Buy&Hold.

CORRECTION 01/08/2026 -- fuite d'exécution « même barre » (voir
`results/nonml_same_bar_execution_audit.md`) : les poids décidés sur la
clôture du jour t étaient appliqués au rendement DU JOUR t, alors que
R[t] = log(close[t]/close[t-1]) est antérieur à la décision. `build_weights`
décale désormais les poids d'un jour par défaut (`causal=True` : décider à la
clôture de t-1, détenir pendant t). `causal=False` reproduit exactement le
comportement fautif d'origine, uniquement pour l'audit qui le chiffre.
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

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
LOOKBACK = 252
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95


def load_prices(prices_dir=None, panel_start=None):
    """`panel_start` (cycle #163) : tronque le panneau de prix à cette date.
    Purement calculatoire (borne le coût du calcul sur un univers de 214
    titres) -- aucune quantité évaluée après `panel_start + 252 séances`
    n'en dépend. `None` par défaut = comportement d'origine inchangé."""
    series = {}
    for path in sorted((prices_dir or PRICES_DIR).glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if panel_start is not None:
            close = close[close.index >= pd.Timestamp(panel_start)]
        if len(close) > LOOKBACK + REBAL_EVERY:
            series[path.stem] = close
    return series


def index_trend_series() -> pd.Series:
    """Signal de tendance calcule sur l'indice NDX-100 lui-meme (proximite
    du plus haut 252j), aligne ensuite (ffill causal) sur le calendrier du
    portefeuille."""
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(near_high, index=dates)


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Correction de la fuite « même barre »
    documentée dans `results/nonml_same_bar_execution_audit.md`."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def build_weights(prices_dir=None, panel_start=None, membership_fn=None,
                  rebal_anchor=None, membership_log=None, causal=True):
    """Reconstruit exactement les poids Leaders et Leaders+overlay (T x
    n_tickers), les rendements bruts par titre R, les dates alignées et
    l'indice `start` (fin du lookback). Extraction non-comportementale de
    l'ancien corps de `main()` -- réutilisée par
    `nonml_leaders_index52w_high_overlay_pass_validation_battery.py`
    (cycle #161) pour éviter toute réimplémentation divergente (Règle 7).
    `prices_dir` optionnel (cycle #162, historique étendu) : n'affecte
    aucun calcul, seulement la source des prix.

    Cycle #163 (univers point-in-time, pré-enregistré dans
    PREREG_leaders_index52w_high_overlay_pit_universe.md) :
    - `membership_fn(timestamp) -> set[str]` restreint, à CHAQUE date de
      rebalancement, les titres éligibles à ceux réellement membres de
      l'indice ce jour-là. C'est le SEUL changement de logique du cycle,
      déclaré comme tel dans le PREREG.
    - `rebal_anchor` : première séance ≥ cette date sert d'ancrage à la
      grille de rebalancement (première date couverte par la composition).
    - `membership_log` : liste optionnelle remplie, à chaque rebalancement,
      de (date, n_membres_réels, n_investissables) -- sert à quantifier le
      biais résiduel, n'intervient dans aucun calcul.

    Tous ces arguments valent `None` par défaut : le comportement d'origine
    (#38/#161/#162) est alors strictement inchangé."""
    series = load_prices(prices_dir, panel_start)
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full, close / rolling_max, np.nan)

    weights_leaders = np.zeros((T, n_tickers))
    first_rebal = LOOKBACK
    if rebal_anchor is not None:
        first_rebal = max(LOOKBACK,
                          int(P.index.searchsorted(pd.Timestamp(rebal_anchor))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        if membership_fn is not None:
            members = membership_fn(P.index[t])
            elig = np.array([j for j in elig if tickers[j] in members], dtype=int)
            if membership_log is not None:
                membership_log.append((P.index[t], len(members), len(elig)))
        # TERCILE s'applique au nombre de titres RÉELLEMENT dans l'univers à
        # cette date (identique au comportement d'origine quand
        # membership_fn is None : elig vaut alors tout le panneau éligible).
        n_ref = n_tickers if membership_fn is None else len(elig)
        n_top = max(1, int(round(n_ref * TERCILE)))
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)
    exposure = np.where(trend_aligned, CAP, 1.0)

    weights_base = weights_leaders
    weights_lev = weights_leaders * exposure[:, None]
    if causal:
        # Correction 01/08/2026 : décider à la clôture de t-1, détenir pendant
        # t. Décaler le PRODUIT corrige simultanément la sélection titre et la
        # bascule de l'overlay, qui souffraient tous deux de la même fuite.
        weights_base = lag_one_day(weights_base)
        weights_lev = lag_one_day(weights_lev)
        trend_aligned = np.concatenate(([False], trend_aligned[:-1]))
    return P.index, weights_base, weights_lev, R, trend_aligned


def main():
    dates_full, weights_base, weights_lev, R, trend_aligned = build_weights()
    T = R.shape[0]
    start = LOOKBACK
    pnl_base = (weights_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)

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

    lines = [
        "# Résultat — Leaders 52-semaines + overlay levé proximité plus haut 52-semaines indice (pré-enregistré, combinaison #4+#37)",
        "",
        f"Référence = portefeuille leaders 1.0x (cycle #4), PAS Buy&Hold. "
        f"{T - start} séances testables ({dates_full[start].date()} → {dates_full[-1].date()}). "
        f"Overlay actif {100*trend_aligned[start:].mean():.1f}% du temps "
        f"(indice NDX-100 ≥ {100*INDEX_THRESHOLD:.0f}% de son plus haut {INDEX_LOOKBACK}j).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Leaders 1.0x (référence, cycle #4) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **Leaders + overlay 52w-high indice x{CAP}** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_leaders_index52w_high_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
