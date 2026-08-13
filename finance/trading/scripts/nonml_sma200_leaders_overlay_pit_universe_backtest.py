"""Backtest — Leaders 52-semaines + overlay levé filtre de tendance SMA200,
univers de titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_sma200_leaders_overlay_pit_universe.md`, committée avant ce script).

Réutilisation stricte (Règle 7) du cycle d'origine (#33) : **aucun paramètre
modifié**. Seul l'univers de sélection des Leaders change — `data/pead/prices/`
devient `data/pead/prices_pit/`, avec appartenance résolue à chaque date de
rebalancement par `ndx100_membership.tickers_as_of_date`.

Le signal SMA200 porte sur l'INDICE : il ne dépend pas de l'univers titres.

Exécution causale (patch #166/#167, appliqué à ce candidat au #253).
Référence = portefeuille Leaders 1,0×, **pas** Buy & Hold.

Le script mesure et rapporte le nombre de séances où le signal SMA200 diffère du
signal « union SMA200 ∪ 52w-high » du #401, comme pré-enregistré : si ce nombre
est nul, ce cycle est une identité arithmétique du #401 et ne compte pas comme
une observation nouvelle.
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
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
COMPOSITION_START = pd.Timestamp("2015-01-01")

# --- Parametres REPRIS A L'IDENTIQUE du cycle d'origine (Regle 7) ---
LOOKBACK = 252
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
SMA_WINDOW = 200
# Parametres du signal 52w-high, presents UNIQUEMENT pour mesurer la
# coincidence avec le #401. Ils n'entrent dans aucune decision de position.
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95


def load_prices_pit():
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


def index_signals():
    """Retourne (SMA200, union SMA200 U 52w-high) sur l'indice NDX-100.

    Seul le premier pilote la strategie ; le second sert uniquement a mesurer
    la coincidence avec le #401, comme pre-enregistre.
    """
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    above_sma = close > sma
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    idx = pd.to_datetime(df["date"]).values
    return (pd.Series(above_sma, index=idx),
            pd.Series(above_sma | near_high, index=idx))


def lag_one_day(W):
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def build_weights():
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    tickers = list(P.columns)
    close = P.values

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full, close / rolling_max, np.nan)

    n_top = max(1, int(round(n_tickers * TERCILE)))
    W = np.zeros((T, n_tickers))
    # Masque EXPLICITE des dates ou l'appartenance PIT est definie (piege #396).
    investable = np.zeros(T, dtype=bool)
    coverage = []

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        if P.index[t] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        r = ratio[t]
        elig = np.where(np.isfinite(r) & member_cols)[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            W[t:end] = w
            investable[t:end] = True
            coverage.append(len(elig) / max(1, len(members)))

    cov = float(np.mean(coverage)) if coverage else float("nan")
    return P, tickers, W, investable, cov


def main():
    P, tickers, W, investable, cov = build_weights()
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0

    sma_sig, union_sig = index_signals()
    sma_al = sma_sig.reindex(P.index, method="ffill").fillna(False).values.astype(bool)
    union_al = union_sig.reindex(P.index, method="ffill").fillna(False).values.astype(bool)
    exposure = np.where(sma_al, CAP, 1.0)

    W_base = lag_one_day(W)
    W_lev = lag_one_day(W * exposure[:, None])
    inv_lag = np.concatenate(([False], investable[:-1]))
    first = int(np.argmax(inv_lag)) if inv_lag.any() else len(P)
    start = max(LOOKBACK, first)

    n_signal_diff = int((sma_al[start:] != union_al[start:]).sum())

    pnl_base = (W_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (W_lev[start:] * R[start:]).sum(axis=1)
    turn_base = np.abs(np.diff(W_base[start:], axis=0,
                               prepend=W_base[start:start + 1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(W_lev[start:], axis=0,
                              prepend=W_lev[start:start + 1])).sum(axis=1) / 2.0
    pnl_gross_ov_, pnl_gross_bh_ = pnl_lev.copy(), pnl_base.copy()
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(np.log1p(pnl_base))
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok
    active = float(sma_al[start:].mean())

    lines = [
        "# Résultat — Leaders + overlay SMA200, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#33) : **aucun paramètre "
        "modifié**. Seul l'univers de sélection des Leaders change. Exécution causale (#253). "
        "Le signal SMA200 porte sur l'indice et est inchangé.",
        "",
        "Référence = portefeuille Leaders 1,0× (convention du #4), **pas** Buy&Hold.",
        "",
        f"Univers PIT : {len(tickers)} tickers, couverture moyenne {100*cov:.1f}%. "
        f"{len(pnl_base)} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        f"Overlay actif {100*active:.1f}% du temps (indice au-dessus de sa SMA200).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Leaders 1.0x (référence) | {me_base['sharpe_ann']:+.2f} | "
        f"{100*ret_base:+.1f}% | {me_base['max_drawdown_pct']:.1f}% |",
        f"| **Leaders + overlay SMA200 {CAP}x** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
        "## Coïncidence avec le #401 — mesure pré-enregistrée",
        "",
        "Le PREREG annonçait, **avant tout calcul**, que ce cycle pouvait n'être qu'une "
        "identité arithmétique du #401 : l'audit du #41 avait établi que sur 2022-2026 le "
        "signal 52w-high était un sous-ensemble strict du signal SMA200, rendant leur union "
        "identique à SMA200 seul.",
        "",
        f"Séances où le signal SMA200 diffère de l'union SMA200 ∪ 52w-high, sur la fenêtre "
        f"testée ({len(pnl_base)} séances) : **{n_signal_diff}**.",
        "",
    ]
    if n_signal_diff == 0:
        lines += [
            "**L'inclusion tient encore sur 2015-2026.** Ce cycle reproduit donc exactement "
            "le #401 : ce n'est **pas une observation nouvelle** mais la même stratégie sous "
            "un autre nom. Conformément à la règle de comptage fixée d'avance, il n'est "
            "**pas** ajouté au décompte des candidats testés de l'axe.",
        ]
    else:
        lines += [
            f"**L'inclusion est rompue sur cette fenêtre plus longue** ({n_signal_diff} "
            "séances de divergence) : les deux candidats ne coïncident pas, et ce résultat "
            "est une observation propre, comptée comme telle.",
        ]
    lines += [
        "",
        "Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent.",
        "",
    ]

    out = ROOT / "results" / "nonml_sma200_leaders_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(ROOT / "results" / "nonml_sma200_leaders_overlay_pit_universe_pnl.npz",
             pnl_gross_ov=pnl_gross_ov_, pnl_gross_bh=pnl_gross_bh_,
             turn_ov=turn_lev, turn_bh=turn_base,
             dates=np.asarray(P.index)[start:], cost_bps=COST_BPS)

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
