"""Batterie de validation renforcée (Règle 9) — #350 (sleeve
dollar-neutre composite redimensionné par sa vol), ADAPTÉE au format
PORTEFEUILLE multi-actifs (spécification pré-enregistrée dans
PREREG_dollar_neutral_composite_vol_targeted_pass_validation_battery.md,
committée avant ce script).

Réutilise STRICTEMENT (Règle 7) les fonctions de contrôle a-e déjà
écrites et validées (nonml_momentum_turnover_doublesort_pass_validation_battery.py),
aucune modification. Reconstruit le pipeline COMPLET (sleeve #349 →
vol-targeting #350) en (rendement BRUT, turnover) pour permettre au
contrôle (a) de recalculer le P&L à différents niveaux de coût --
décomposition algébrique exacte de la formule déjà committée du #350
(r_vt = pos*raw_sleeve - [pos*turn_sleeve + |Δpos|]*cost_bps/1e4), pas
une nouvelle stratégie.
"""
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
from nonml_momentum_consistency_backtest import consistency_at  # noqa: E402
from nonml_momentum_turnover_doublesort_pass_validation_battery import (  # noqa: E402
    check_a_cost_stress, check_b_crisis_stress, check_c_temporal_stability,
    check_d_spa, check_e_dsr,
)
from nonml_vol_targeting_overlay_backtest import (  # noqa: E402
    CAP, TARGET_VOL_ANNUAL, VOL_WINDOW as VT_WINDOW, ANNUALIZATION, vol_target_position,
)
import nonml_dollar_neutral_composite_pit_backtest as bt  # noqa: E402


def build_raw_series():
    """Reconstruit (raw, turnover) candidat/reference du pipeline
    COMPLET (sleeve dollar-neutre #349 -> vol-targeting #350),
    identiquement aux formules deja committees des deux cycles."""
    series = bt.load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)
    simple_ret = P.pct_change(fill_method=None).values

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

    sig_consistency = np.full((T, n_tickers), np.nan)
    for i in range(bt.LOOKBACK_CONSISTENCY, T):
        sig_consistency[i] = consistency_at(close, i)

    vol = pd.DataFrame(simple_ret).rolling(bt.VOL_WINDOW).std().values
    sig_low_vol = np.where(np.isfinite(vol), -vol, np.nan)

    weights = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    first_rebal = max(bt.LOOKBACK_52W, bt.LOOKBACK_MOM, bt.LOOKBACK_CONSISTENCY, bt.VOL_WINDOW,
                       int(P.index.searchsorted(pd.Timestamp(bt.REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, bt.REBAL_EVERY))

    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        members = tickers_as_of_date(P.index[t])
        member_mask = np.array([tickers[j] in members for j in range(n_tickers)])
        all_fin = (np.isfinite(sig_52w[t]) & np.isfinite(sig_mom[t]) &
                   np.isfinite(sig_consistency[t]) & np.isfinite(sig_low_vol[t]))
        eligible = np.where(member_mask & all_fin)[0]
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)
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

    weights = bt.lag_one_day(weights)
    weights_bh = bt.lag_one_day(weights_bh)

    start = first_rebal
    raw_sleeve = (weights[start:] * R_safe[start:]).sum(axis=1)
    raw_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_sleeve = np.abs(np.diff(weights[start:], axis=0, prepend=weights[start:start + 1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start + 1])).sum(axis=1) / 2.0
    dates_sleeve = P.index[start:]

    # Couche vol-targeting (#350) : pos(t) calcule sur le rendement DEJA
    # net des couts de rebalancement du sleeve (meme entree que le #350).
    pnl_sleeve_net_at_cost = raw_sleeve - turn_sleeve * (bt.COST_BPS / 1e4)
    pos_full = vol_target_position(pnl_sleeve_net_at_cost)
    vt_start = VT_WINDOW

    raw_candidate = pos_full[vt_start:] * raw_sleeve[vt_start:]
    turn_candidate = (pos_full[vt_start:] * turn_sleeve[vt_start:] +
                       np.abs(np.diff(pos_full[vt_start:], prepend=pos_full[vt_start:vt_start + 1])))
    raw_ref = raw_bh[vt_start:]
    turn_ref = turn_bh[vt_start:]
    dates = dates_sleeve[vt_start:]

    return raw_candidate, turn_candidate, raw_ref, turn_ref, dates


def main():
    name = "dollar_neutral_composite_vol_targeted"
    raw_c, turn_c, raw_r, turn_r, dates = build_raw_series()
    cost_bps = bt.COST_BPS

    # Verification de regression : le pnl reconstruit a cost_bps=5.0
    # doit reproduire exactement le resultat deja committe du #350.
    pnl_check = raw_c - turn_c * (cost_bps / 1e4)
    me_check = trading_metrics(pnl_check)
    sharpe_daily_check = pnl_check.mean() / pnl_check.std() if pnl_check.std() > 0 else float("nan")
    tstat_check = sharpe_daily_check * np.sqrt(len(pnl_check))

    lines = [f"# Batterie de validation renforcée — {name} (adaptée au format portefeuille)",
             "",
             f"Coût pré-enregistré : {cost_bps:.1f} bps. {len(raw_c)} séances. "
             "Candidat = sleeve dollar-neutre composite redimensionné par sa vol (#350). "
             "Référence = Buy&Hold équipondéré (univers PIT, #349).",
             "",
             f"**Vérification de régression (doit reproduire le #350 déjà committé)** : "
             f"Sharpe ann. reconstruit = {me_check['sharpe_ann']:+.2f} (#350 committé : +0.61), "
             f"t-stat reconstruit = {tstat_check:+.2f} (#350 committé : +2.08).",
             ""]

    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |")
    lines.append("|---|---|---|---|---|---|")
    ok_a, rows_a = check_a_cost_stress(raw_c, turn_c, raw_r, turn_r, cost_bps)
    for cost, s_c, s_r, r_c, r_r, ok in rows_a:
        lines.append(f"| {cost:.1f} | {s_c:+.2f} | {s_r:+.2f} | {100*r_c:+.1f}% | {100*r_r:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    lines.append("## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)")
    lines.append("")
    lines.append("| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, rows_b, any_window = check_b_crisis_stress(raw_c, turn_c, raw_r, turn_r, dates, cost_bps)
    for label, n, mdd_c, mdd_r, ok in rows_b:
        if mdd_c is None:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
        else:
            lines.append(f"| {label} | {n} | {mdd_c:.1f}% | {mdd_r:.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible (2015-2026, "
                     "univers PIT NDX-100) : ce contrôle ne peut pas être exécuté, il ne doit PAS "
                     "être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — MDD jamais pire que la référence sur les fenêtres couvertes : {'oui' if ok_b else 'NON'}.**")
    lines.append("")

    lines.append("## c. Stabilité temporelle (folds non chevauchants + embargo 5j)")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |")
    lines.append("|---|---|---|---|---|")
    ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(raw_c, turn_c, raw_r, turn_r, cost_bps)
    for k, n, s_c, s_r, beat in rows_c:
        lines.append(f"| {k} | {n} | {s_c:+.2f} | {s_r:+.2f} | {'OUI' if beat else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — bat la référence sur {n_beat}/{n_scored} folds "
                 f"(majorité {'atteinte' if ok_c else 'NON atteinte'}).**")
    lines.append("")

    lines.append("## d. SPA à 1 candidat contre la référence")
    lines.append("")
    ok_d, p_spa = check_d_spa(raw_c, turn_c, raw_r, turn_r, cost_bps)
    lines.append(f"p-value SPA : {p_spa:.4f}")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — significatif à 5% : {'oui' if ok_d else 'NON'}.**")
    lines.append("")

    lines.append("## e. DSR avec n_trials = taille totale du backlog (jamais 1)")
    lines.append("")
    e_res = check_e_dsr(raw_c, turn_c, cost_bps)
    if e_res is None:
        lines.append("**PENDING — n_trials ou var_trials introuvable dans le backlog.**")
        ok_e = False
    else:
        n_trials, n_extracted, var_trials, d = e_res
        ok_e = d >= 0.95
        lines.append(f"n_trials = {n_trials} (taille du backlog), "
                     f"Var(Sharpe essais) estimée sur {n_extracted} Sharpe extraits du backlog "
                     f"= {var_trials:.6f} (échelle journalière).")
        lines.append(f"DSR = {d:.4f}")
        lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — DSR ≥ 0.95 : {'oui' if ok_e else 'NON'}.**")
    lines.append("")

    n_ok = sum([ok_a, ok_b, ok_c, ok_d, ok_e])
    lines.append(f"## Verdict global : {n_ok}/5")
    lines.append("")
    lines.append(f"**{'PASS RENFORCÉ (5/5)' if n_ok == 5 else f'PAS de PASS RENFORCÉ ({n_ok}/5)'}.**")

    out = ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
