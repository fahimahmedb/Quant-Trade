"""Batterie de validation renforcée (Règle 9) — #48 (vol-targeting 20% +
portefeuille Leaders 52-semaines), ADAPTÉE au format PORTEFEUILLE
multi-actifs (spécification pré-enregistrée dans
`PREREG_leaders_vol_targeting_20_overlay_pass_validation_battery.md`,
committée avant ce script).

Réutilisation stricte (Règle 7) du patron déjà établi au #259/#315 : les
5 fonctions de contrôle sont importées directement (génériques).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr  # noqa: E402
from nonml_pass_validation_battery import parse_backlog_n_trials, approx_var_trials  # noqa: E402
from nonml_momentum_turnover_doublesort_pass_validation_battery import (  # noqa: E402
    check_a_cost_stress, check_b_crisis_stress, check_c_temporal_stability, check_d_spa,
)
from nonml_leaders_vol_targeting_20_overlay_backtest import (  # noqa: E402
    load_prices, vol_target_exposure, lag_one_day,
    LOOKBACK, REBAL_EVERY, COST_BPS, TERCILE, VOL_WINDOW,
)


def build_raw_series():
    """Reconstruit (rendement brut, turnover, dates) pour le candidat
    (Leaders + vol-targeting 20%) et la reference (Leaders seul) --
    identique en structure a build_raw_series() du #315, mais avec le
    mecanisme d'exposition continu du #48 au lieu de la porte SMA200."""
    series = load_prices()
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

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_leaders = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w

    pnl_leaders_raw = (weights_leaders * R).sum(axis=1)
    exposure = vol_target_exposure(pnl_leaders_raw)

    weights_base = lag_one_day(weights_leaders)
    weights_lev = lag_one_day(weights_leaders * exposure[:, None])

    start = LOOKBACK + VOL_WINDOW
    raw_lev = (weights_lev[start:] * R[start:]).sum(axis=1)
    raw_base = (weights_base[start:] * R[start:]).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    turn_base = np.abs(np.diff(weights_base[start:], axis=0, prepend=weights_base[start:start+1])).sum(axis=1) / 2.0
    dates = P.index[start:]
    return raw_lev, turn_lev, raw_base, turn_base, dates


def pnl_at_cost(raw, turn, cost_bps):
    return raw - turn * (cost_bps / 1e4)


def check_e_dsr(raw_c, turn_c, cost_baseline):
    pnl_c = pnl_at_cost(raw_c, turn_c, cost_baseline)
    me = trading_metrics(pnl_c)
    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    if n_trials is None or var_trials_annual is None:
        return None
    var_trials = var_trials_annual / 252.0
    d = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=n_trials,
            skew=me["skew"], kurt_excess=me["excess_kurt"])
    return n_trials, n_extracted, var_trials, d["dsr"]


def main():
    name = "leaders_vol_targeting_20_overlay"
    raw_lev, turn_lev, raw_base, turn_base, dates = build_raw_series()
    cost_bps = COST_BPS

    lines = [f"# Batterie de validation renforcée — {name} (adaptée au format portefeuille)",
             "",
             f"Coût pré-enregistré : {cost_bps:.1f} bps. {len(raw_lev)} séances. "
             "Candidat = Leaders 52-semaines + vol-targeting continu 20% (#48). "
             "Référence = Leaders seul (#4), PAS Buy&Hold.",
             ""]

    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |")
    lines.append("|---|---|---|---|---|---|")
    ok_a, rows_a = check_a_cost_stress(raw_lev, turn_lev, raw_base, turn_base, cost_bps)
    for cost, s_c, s_r, r_c, r_r, ok in rows_a:
        lines.append(f"| {cost:.1f} | {s_c:+.2f} | {s_r:+.2f} | {100*r_c:+.1f}% | {100*r_r:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    lines.append("## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)")
    lines.append("")
    lines.append("| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, rows_b, any_window = check_b_crisis_stress(raw_lev, turn_lev, raw_base, turn_base, dates, cost_bps)
    for label, n, mdd_c, mdd_r, ok in rows_b:
        if mdd_c is None:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
        else:
            lines.append(f"| {label} | {n} | {mdd_c:.1f}% | {mdd_r:.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible (univers "
                     "NDX-100 titre-par-titre, 2021-2026) : ce contrôle ne peut pas être exécuté, il ne doit "
                     "PAS être compté comme un OK silencieux (Règle 5).**")
        ok_b = False
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — MDD jamais pire que la référence sur les fenêtres couvertes : {'oui' if ok_b else 'NON'}.**")
    lines.append("")

    lines.append("## c. Stabilité temporelle (folds non chevauchants + embargo 5j)")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |")
    lines.append("|---|---|---|---|---|")
    ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(raw_lev, turn_lev, raw_base, turn_base, cost_bps)
    for k, n, s_c, s_r, beat in rows_c:
        lines.append(f"| {k} | {n} | {s_c:+.2f} | {s_r:+.2f} | {'OUI' if beat else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — bat la référence sur {n_beat}/{n_scored} folds "
                 f"(majorité {'atteinte' if ok_c else 'NON atteinte'}).**")
    lines.append("")

    lines.append("## d. SPA à 1 candidat contre la référence")
    lines.append("")
    ok_d, p_spa = check_d_spa(raw_lev, turn_lev, raw_base, turn_base, cost_bps)
    lines.append(f"p-value SPA : {p_spa:.4f}")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — significatif à 5% : {'oui' if ok_d else 'NON'}.**")
    lines.append("")

    lines.append("## e. DSR avec n_trials = taille totale du backlog (jamais 1)")
    lines.append("")
    e_res = check_e_dsr(raw_lev, turn_lev, cost_bps)
    if e_res is None:
        lines.append("**PENDING — n_trials ou var_trials introuvable dans le backlog.**")
        ok_e = False
    else:
        n_trials, n_extracted, var_trials, d = e_res
        ok_e = d >= 0.95
        lines.append(f"n_trials = {n_trials} (taille du backlog après le #48), "
                     f"Var(Sharpe essais) estimée sur {n_extracted} Sharpe extraits du backlog "
                     f"= {var_trials:.6f} (échelle journalière).")
        lines.append(f"DSR = {d:.4f}")
        lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — DSR ≥ 0.95 : {'oui' if ok_e else 'NON'}.**")
    lines.append("")

    n_ok = sum([ok_a, ok_b, ok_c, ok_d, ok_e])
    lines.append(f"## Verdict global : {n_ok}/5")
    lines.append("")
    lines.append(f"**{'PASS RENFORCÉ (5/5)' if n_ok == 5 else f'PAS de PASS RENFORCÉ ({n_ok}/5)'}.**")

    out = ROOT / "results" / "nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
