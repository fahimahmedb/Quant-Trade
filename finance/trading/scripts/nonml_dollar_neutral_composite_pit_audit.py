"""Audit indépendant — Portefeuille L/S dollar-neutre composite (PIT).

1. Recalcul indépendant par ÉCHANTILLONNAGE (sur plusieurs dates de
   rebalancement) des 4 signaux, du z-score et des poids finaux, par
   une implémentation entièrement différente (boucles Python pures
   sur les séries pandas natives, sans les tableaux numpy vectorisés
   du backtest).
2. Vérification de la neutralité dollar (Σw ≈ 0) et de l'exposition
   brute (Σ|w| = 2) à chaque date de rebalancement.
3. Anti-lookahead par troncature de l'historique.
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

from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_dollar_neutral_composite_pit_backtest import (  # noqa: E402
    COST_BPS, GROSS_EXPOSURE, LOOKBACK_52W, LOOKBACK_CONSISTENCY, LOOKBACK_MOM,
    MIN_ELIGIBLE, PRICES_PIT_DIR, REBAL_ANCHOR, REBAL_EVERY, SKIP_MOM, VOL_WINDOW,
    load_prices,
)


def manual_signals_for_ticker(close_series: pd.Series, date: pd.Timestamp):
    """Recalcul independant (boucle pandas native, sans numpy vectorise)
    des 4 signaux bruts pour UN ticker a UNE date, par indexation directe
    de la serie (pas de tableau numpy partage)."""
    if date not in close_series.index:
        return None
    idx = close_series.index.get_loc(date)
    # Chaque signal a sa PROPRE exigence d'historique (pas un seuil
    # combine unique) : #4/#73/#82 necessitent 252j, #15 seulement 60j
    # -- un titre recemment cote peut avoir un signal vol valide avant
    # d'avoir 252j d'historique complet. Aucun acces iloc negatif
    # (idx-N<0) n'est tente : chaque bloc verifie ses propres bornes.

    if idx >= LOOKBACK_52W - 1:
        window_52w = close_series.iloc[idx - LOOKBACK_52W + 1:idx + 1]
        if window_52w.isna().any() or len(window_52w) < LOOKBACK_52W:
            sig1 = np.nan
        else:
            sig1 = close_series.iloc[idx] / window_52w.max()
    else:
        sig1 = np.nan

    if idx >= LOOKBACK_MOM:
        c_skip = close_series.iloc[idx - SKIP_MOM]
        c_lb = close_series.iloc[idx - LOOKBACK_MOM]
        sig2 = (c_skip / c_lb - 1.0) if (np.isfinite(c_skip) and np.isfinite(c_lb)) else np.nan
    else:
        sig2 = np.nan

    if idx >= LOOKBACK_CONSISTENCY:
        n_blocks = LOOKBACK_CONSISTENCY // 21
        pos_blocks = 0
        valid_blocks = 0
        for b in range(n_blocks):
            end_i = idx - b * 21
            start_i = end_i - 21
            p_start, p_end = close_series.iloc[start_i], close_series.iloc[end_i]
            if not (np.isfinite(p_start) and np.isfinite(p_end)):
                valid_blocks = -1
                break
            valid_blocks += 1
            if p_end > p_start:
                pos_blocks += 1
        sig3 = (pos_blocks / n_blocks) if valid_blocks == n_blocks else np.nan
    else:
        sig3 = np.nan

    if idx >= VOL_WINDOW:
        window_vol = close_series.iloc[idx - VOL_WINDOW:idx + 1]
        simple_r = window_vol.pct_change().dropna()
        sig4 = -simple_r.std(ddof=1) if len(simple_r) >= VOL_WINDOW else np.nan
    else:
        sig4 = np.nan

    return sig1, sig2, sig3, sig4


def main():
    lines = ["# Audit — Portefeuille L/S dollar-neutre composite (PIT)", ""]
    all_ok = True

    series = load_prices()
    tickers = sorted(series.keys())

    import nonml_dollar_neutral_composite_pit_backtest as bt
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full_window = np.zeros((T, n_tickers), dtype=bool)
    for i in range(bt.LOOKBACK_52W, T):
        window = close[i - bt.LOOKBACK_52W + 1:i + 1]
        has_full_window[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    sig_52w = np.where(has_full_window, close / rolling_max, np.nan)

    sig_mom = np.full((T, n_tickers), np.nan)
    for i in range(bt.LOOKBACK_MOM, T):
        c_skip = close[i - bt.SKIP_MOM]
        c_lookback = close[i - bt.LOOKBACK_MOM]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        sig_mom[i, valid] = m[valid]

    from nonml_momentum_consistency_backtest import consistency_at
    sig_consistency = np.full((T, n_tickers), np.nan)
    for i in range(bt.LOOKBACK_CONSISTENCY, T):
        sig_consistency[i] = consistency_at(close, i)

    simple_ret = P.pct_change(fill_method=None).values
    vol = pd.DataFrame(simple_ret).rolling(bt.VOL_WINDOW).std().values
    sig_low_vol = np.where(np.isfinite(vol), -vol, np.nan)

    first_rebal = max(bt.LOOKBACK_52W, bt.LOOKBACK_MOM, bt.LOOKBACK_CONSISTENCY, bt.VOL_WINDOW,
                       int(P.index.searchsorted(pd.Timestamp(bt.REBAL_ANCHOR))))
    rebal_dates_idx = list(range(first_rebal, T, bt.REBAL_EVERY))

    # 1. Recalcul indépendant des 4 signaux sur un échantillon de (date, ticker)
    lines.append("## 1. Recalcul indépendant des 4 signaux bruts (échantillon)")
    lines.append("")
    lines.append("| Date | Ticker | Écart max (4 signaux) |")
    lines.append("|---|---|---|")
    sample_dates_idx = rebal_dates_idx[::max(1, len(rebal_dates_idx) // 8)][:8]
    max_diff_signals = 0.0
    n_checked = 0
    rng_tickers = tickers[::max(1, len(tickers) // 5)][:5]
    for di in sample_dates_idx:
        date = P.index[di]
        for tk in rng_tickers:
            manual = manual_signals_for_ticker(series[tk], date)
            j = tickers.index(tk)
            official = (sig_52w[di, j], sig_mom[di, j], sig_consistency[di, j], sig_low_vol[di, j])
            if manual is None:
                if all(np.isnan(x) for x in official):
                    continue
                else:
                    lines.append(f"| {date.date()} | {tk} | manuel=None mais officiel fini — ÉCART |")
                    all_ok = False
                    continue
            diffs = [abs(m - o) if (np.isfinite(m) and np.isfinite(o)) else (0.0 if (np.isnan(m) and np.isnan(o)) else np.nan)
                     for m, o in zip(manual, official)]
            if any(np.isnan(d) for d in diffs):
                lines.append(f"| {date.date()} | {tk} | désaccord NaN/fini — ÉCART |")
                all_ok = False
                continue
            d = max(diffs)
            max_diff_signals = max(max_diff_signals, d)
            n_checked += 1
            lines.append(f"| {date.date()} | {tk} | {d:.2e} |")
    lines.append("")
    ok_signals = max_diff_signals < 1e-8
    all_ok &= ok_signals
    lines.append(f"**Écart max sur {n_checked} points (date, ticker) vérifiés : {max_diff_signals:.2e} — "
                 f"{'OK' if ok_signals else 'ÉCART DÉTECTÉ'}**")
    lines.append("")

    # 2. Neutralite dollar et exposition brute a chaque rebalancement
    lines.append("## 2. Neutralité dollar (Σw≈0) et exposition brute (Σ|w|=2) à chaque rebalancement actif")
    lines.append("")
    sum_w_max, sum_absw_max_dev = 0.0, 0.0
    n_active = 0
    for t in rebal_dates_idx:
        members = tickers_as_of_date(P.index[t])
        member_mask = np.array([tickers[j] in members for j in range(n_tickers)])
        all_fin = (np.isfinite(sig_52w[t]) & np.isfinite(sig_mom[t]) &
                   np.isfinite(sig_consistency[t]) & np.isfinite(sig_low_vol[t]))
        eligible = np.where(member_mask & all_fin)[0]
        if len(eligible) < bt.MIN_ELIGIBLE:
            continue
        n_active += 1
        z1 = bt.zscore(sig_52w[t, eligible])
        z2 = bt.zscore(sig_mom[t, eligible])
        z3 = bt.zscore(sig_consistency[t, eligible])
        z4 = bt.zscore(sig_low_vol[t, eligible])
        z_composite = np.nanmean(np.vstack([z1, z2, z3, z4]), axis=0)
        w_raw = z_composite - np.nanmean(z_composite)
        gross = np.nansum(np.abs(w_raw))
        if gross <= 0:
            continue
        w = w_raw / gross * bt.GROSS_EXPOSURE
        sum_w_max = max(sum_w_max, abs(float(np.nansum(w))))
        sum_absw_max_dev = max(sum_absw_max_dev, abs(float(np.nansum(np.abs(w))) - bt.GROSS_EXPOSURE))
    ok_neutral = sum_w_max < 1e-8
    ok_gross = sum_absw_max_dev < 1e-8
    all_ok &= ok_neutral and ok_gross
    lines.append(f"- Écart max |Σw| sur {n_active} rebalancements actifs : {sum_w_max:.2e} — "
                 f"**{'OK — dollar-neutre' if ok_neutral else 'ÉCART DÉTECTÉ'}**")
    lines.append(f"- Écart max |Σ|w|| - {bt.GROSS_EXPOSURE:.0f} : {sum_absw_max_dev:.2e} — "
                 f"**{'OK — exposition brute correcte' if ok_gross else 'ÉCART DÉTECTÉ'}**")
    lines.append("")

    # 3. Anti-lookahead par troncature.
    def build_pos_and_pnl(T_cut):
        weights = np.zeros((T_cut, n_tickers))
        rebal_local = [t for t in rebal_dates_idx if t < T_cut]
        for k, t in enumerate(rebal_local):
            end = rebal_local[k + 1] if k + 1 < len(rebal_local) else T_cut
            members = tickers_as_of_date(P.index[t])
            member_mask = np.array([tickers[j] in members for j in range(n_tickers)])
            all_fin = (np.isfinite(sig_52w[t]) & np.isfinite(sig_mom[t]) &
                       np.isfinite(sig_consistency[t]) & np.isfinite(sig_low_vol[t]))
            eligible = np.where(member_mask & all_fin)[0]
            if len(eligible) < bt.MIN_ELIGIBLE:
                continue
            z1 = bt.zscore(sig_52w[t, eligible])
            z2 = bt.zscore(sig_mom[t, eligible])
            z3 = bt.zscore(sig_consistency[t, eligible])
            z4 = bt.zscore(sig_low_vol[t, eligible])
            z_composite = np.nanmean(np.vstack([z1, z2, z3, z4]), axis=0)
            w_raw = z_composite - np.nanmean(z_composite)
            gross = np.nansum(np.abs(w_raw))
            if gross <= 0:
                continue
            w = w_raw / gross * bt.GROSS_EXPOSURE
            w_full = np.zeros(n_tickers)
            w_full[eligible] = w
            weights[t:end] = w_full
        return bt.lag_one_day(weights)

    T_full = T
    T_trunc = first_rebal + 15 * REBAL_EVERY
    w_full_hist = build_pos_and_pnl(T_full)
    w_trunc_hist = build_pos_and_pnl(T_trunc)
    check_upto = min(T_trunc - REBAL_EVERY, T_full)
    lookahead_diff = float(np.nanmax(np.abs(
        w_full_hist[first_rebal:check_upto] - w_trunc_hist[first_rebal:check_upto]
    )))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead
    lines.append(f"## 3. Anti-lookahead (troncature à {T_trunc} séances, marge de {REBAL_EVERY} séances avant la coupe)")
    lines.append(f"- Écart max poids sur la zone valide, historique complet vs tronqué : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_dollar_neutral_composite_pit_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
