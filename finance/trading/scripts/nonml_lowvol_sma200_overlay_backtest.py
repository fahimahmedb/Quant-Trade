"""Backtest — Low-Volatility Tilt + overlay levé filtre de tendance
SMA200 (spécification pré-enregistrée dans
PREREG_lowvol_sma200_overlay.md, committée avant ce script). Combine les
cycles #15 et #29. n_trials=1, aucune dépendance ML. Règle de succès
renforcée -- référence = Low-Vol 1.0x (cycle #15), pas Buy&Hold.

CORRECTION 05/08/2026 (cycle #257) -- fuite d'exécution « même barre »
(voir `results/nonml_same_bar_execution_audit.md`, patch #166/#167/#253/
#254/#255 appliqué ici, jamais fait avant). `main(causal=True)` décale
désormais les poids d'un jour par défaut ; `causal=False` reproduit le
comportement fautif d'origine, pour l'audit uniquement.
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
VOL_WINDOW = 60
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
SMA_WINDOW = 200


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


def index_trend_series() -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    above = close > sma
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(above, index=dates)


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Correction de la fuite « même barre »
    documentée dans `results/nonml_same_bar_execution_audit.md`."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main(causal=True):
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    exists = np.isfinite(P.values)
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0

    vol = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowvol = np.zeros((T, n_tickers))
    start = VOL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        v = vol[t]
        elig = np.where(np.isfinite(v) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(v[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowvol[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)
    exposure = np.where(trend_aligned, CAP, 1.0)

    weights_base = weights_lowvol
    weights_lev = weights_lowvol * exposure[:, None]
    if causal:
        weights_base = lag_one_day(weights_base)
        weights_lev = lag_one_day(weights_lev)

    pnl_base = (weights_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start:], axis=0, prepend=weights_base[start:start+1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    # Sauvegarde INCONDITIONNELLE du P&L (cycle #427, lot 5) : ce candidat porte
    # un PASS et restait invisible au balayage de doublons. Schema PANIER du #419
    # (le turnover d'un panier n'est pas derivable d'une exposition scalaire).
    # Les P&L stockes sont BRUTS. Aucune ligne de calcul n'est modifiee.
    np.savez(ROOT / "results" / "nonml_lowvol_sma200_overlay_pnl.npz",
             pnl_gross_ov=pnl_lev + turn_lev * (COST_BPS / 1e4),
             pnl_gross_bh=pnl_base + turn_base * (COST_BPS / 1e4),
             turn_ov=turn_lev, turn_bh=turn_base,
             dates=np.asarray(P.index)[start:], cost_bps=COST_BPS)

    me_base = trading_metrics(np.log1p(pnl_base))
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Low-Vol Tilt + overlay levé SMA200 (pré-enregistré, combinaison #15+#29)",
        "",
        f"Référence = portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        f"Overlay actif {100*trend_aligned[start:].mean():.1f}% du temps (indice NDX-100 au-dessus de sa SMA{SMA_WINDOW}).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Low-Vol 1.0x (référence, cycle #15) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **Low-Vol + overlay SMA200 x{CAP}** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_lowvol_sma200_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
