"""Batterie de validation renforcée (Règle 9) — #258 (momentum 12-1 +
double-tri turnover), ADAPTÉE au format PORTEFEUILLE multi-actifs
(spécification pré-enregistrée dans
`PREREG_momentum_turnover_doublesort_pass_validation_battery.md`,
committée avant ce script).

Première application de la batterie Règle 9 à un candidat
stock-selection (poids répartis sur plusieurs titres) plutôt qu'à un
overlay mono-actif (`pos, r_asset` scalaires) : les 5 contrôles sont
reconstruits à partir de deux paires (rendement BRUT, turnover)
candidat/référence au lieu du format `.npz` (pos, r_asset, dates,
cost_bps) utilisé par `nonml_pass_validation_battery.py`.
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
from volatility import spa_test  # noqa: E402
from nonml_pass_validation_battery import parse_backlog_n_trials, approx_var_trials, CRISIS_WINDOWS, EMBARGO  # noqa: E402
from nonml_momentum_turnover_doublesort_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day,
    LOOKBACK, SKIP, TURNOVER_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
)


def build_raw_series():
    """Reconstruit (rendement brut, turnover, dates) pour le double-tri
    (candidat) et le momentum seul (référence), avant application des
    coûts -- permet de recalculer le PnL à n'importe quel coût sans
    reexecuter tout le backtest."""
    close_series = load_all_prices()
    vol_series = load_all_volume()
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    # Rendements SIMPLES : le rendement d'un panier pondere est somme(w_i*r_simple_i).
    # `.copy()` : sous pandas >= 3, `.values` peut etre en lecture seule.
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
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

    dollar_volume = P.values * V.values
    turnover_avg = pd.DataFrame(dollar_volume).rolling(TURNOVER_WINDOW).mean().values

    weights_double = np.zeros((T, n_tickers))
    weights_mom = np.zeros((T, n_tickers))
    n_top_mom_full = max(1, int(round(n_tickers * TERCILE)))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        tv = turnover_avg[t]
        eligible = np.where(np.isfinite(m) & np.isfinite(tv) & (tv > 0))[0]
        n_top_mom = min(n_top_mom_full, len(eligible))
        if n_top_mom > 0:
            top_mom_idx = eligible[np.argsort(-m[eligible])[:n_top_mom]]
            w = np.zeros(n_tickers)
            w[top_mom_idx] = 1.0 / n_top_mom
            weights_mom[t:end] = w
            n_top_double = max(1, int(round(len(top_mom_idx) * TERCILE)))
            n_top_double = min(n_top_double, len(top_mom_idx))
            if n_top_double > 0:
                low_turnover_idx = top_mom_idx[np.argsort(tv[top_mom_idx])[:n_top_double]]
                w2 = np.zeros(n_tickers)
                w2[low_turnover_idx] = 1.0 / n_top_double
                weights_double[t:end] = w2

    weights_double = lag_one_day(weights_double)
    weights_mom = lag_one_day(weights_mom)

    start = LOOKBACK
    raw_double = (weights_double[start:] * R_safe[start:]).sum(axis=1)
    raw_mom = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    turn_double = np.abs(np.diff(weights_double[start:], axis=0, prepend=weights_double[start:start+1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    dates = P.index[start:]
    return raw_double, turn_double, raw_mom, turn_mom, dates


def pnl_at_cost(raw, turn, cost_bps):
    return raw - turn * (cost_bps / 1e4)


def check_a_cost_stress(raw_c, turn_c, raw_r, turn_r, cost_baseline):
    rows = []
    for mult in (1, 3, 5):
        cost = cost_baseline * mult
        pnl_c = pnl_at_cost(raw_c, turn_c, cost)
        pnl_r = pnl_at_cost(raw_r, turn_r, cost)
        me_c, me_r = trading_metrics(np.log1p(pnl_c)), trading_metrics(np.log1p(pnl_r))
        ret_c = float(np.cumprod(1.0 + pnl_c)[-1] - 1.0)
        ret_r = float(np.cumprod(1.0 + pnl_r)[-1] - 1.0)
        ok = (me_c["sharpe_ann"] > me_r["sharpe_ann"]) and (ret_c > ret_r)
        rows.append((cost, me_c["sharpe_ann"], me_r["sharpe_ann"], ret_c, ret_r, ok))
    return all(r[-1] for r in rows), rows


def check_b_crisis_stress(raw_c, turn_c, raw_r, turn_r, dates, cost_baseline):
    rows = []
    any_window = False
    all_ok = True
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            rows.append((label, n, None, None, None))
            continue
        any_window = True
        pnl_c = pnl_at_cost(raw_c[mask], turn_c[mask], cost_baseline)
        pnl_r = pnl_at_cost(raw_r[mask], turn_r[mask], cost_baseline)
        mdd_c = trading_metrics(np.log1p(pnl_c))["max_drawdown_pct"]
        mdd_r = trading_metrics(np.log1p(pnl_r))["max_drawdown_pct"]
        ok = mdd_c >= mdd_r - 1.0
        all_ok &= ok
        rows.append((label, n, mdd_c, mdd_r, ok))
    return (all_ok and any_window), rows, any_window


def check_c_temporal_stability(raw_c, turn_c, raw_r, turn_r, cost_baseline, n_folds=4):
    T = len(raw_c)
    fold_len = T // n_folds
    rows = []
    n_beat, n_scored = 0, 0
    for k in range(n_folds):
        f0 = k * fold_len
        f1 = (k + 1) * fold_len if k < n_folds - 1 else T
        if k > 0:
            f0 += EMBARGO
        if f1 - f0 < 30:
            continue
        pnl_c = pnl_at_cost(raw_c[f0:f1], turn_c[f0:f1], cost_baseline)
        pnl_r = pnl_at_cost(raw_r[f0:f1], turn_r[f0:f1], cost_baseline)
        s_c = trading_metrics(np.log1p(pnl_c))["sharpe_ann"]
        s_r = trading_metrics(np.log1p(pnl_r))["sharpe_ann"]
        beat = s_c > s_r
        n_beat += int(beat)
        n_scored += 1
        rows.append((k + 1, f1 - f0, s_c, s_r, beat))
    majority_ok = n_scored > 0 and n_beat > n_scored / 2
    return majority_ok, rows, n_beat, n_scored


def check_d_spa(raw_c, turn_c, raw_r, turn_r, cost_baseline):
    pnl_c = pnl_at_cost(raw_c, turn_c, cost_baseline)
    pnl_r = pnl_at_cost(raw_r, turn_r, cost_baseline)
    losses = {"candidat": -np.log1p(pnl_c), "reference": -np.log1p(pnl_r)}
    res = spa_test(losses, bench="reference")
    return res["p_value"] < 0.05, res["p_value"]


def check_e_dsr(raw_c, turn_c, cost_baseline):
    pnl_c = pnl_at_cost(raw_c, turn_c, cost_baseline)
    me = trading_metrics(np.log1p(pnl_c))
    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    if n_trials is None or var_trials_annual is None:
        return None
    var_trials = var_trials_annual / 252.0
    d = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=n_trials,
            skew=me["skew"], kurt_excess=me["excess_kurt"])
    return n_trials, n_extracted, var_trials, d["dsr"]


def main():
    name = "momentum_turnover_doublesort"
    raw_double, turn_double, raw_mom, turn_mom, dates = build_raw_series()
    cost_bps = COST_BPS

    lines = [f"# Batterie de validation renforcée — {name} (adaptée au format portefeuille)",
             "",
             f"Coût pré-enregistré : {cost_bps:.1f} bps. {len(raw_double)} séances. "
             "Candidat = momentum 12-1 + double-tri turnover faible (#258). "
             "Référence = momentum 12-1 seul (#73), PAS Buy&Hold.",
             ""]

    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |")
    lines.append("|---|---|---|---|---|---|")
    ok_a, rows_a = check_a_cost_stress(raw_double, turn_double, raw_mom, turn_mom, cost_bps)
    for cost, s_c, s_r, r_c, r_r, ok in rows_a:
        lines.append(f"| {cost:.1f} | {s_c:+.2f} | {s_r:+.2f} | {100*r_c:+.1f}% | {100*r_r:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    lines.append("## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)")
    lines.append("")
    lines.append("| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, rows_b, any_window = check_b_crisis_stress(raw_double, turn_double, raw_mom, turn_mom, dates, cost_bps)
    for label, n, mdd_c, mdd_r, ok in rows_b:
        if mdd_c is None:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
        else:
            lines.append(f"| {label} | {n} | {mdd_c:.1f}% | {mdd_r:.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible (2022-2026, "
                     "univers NDX-100 prix+volume) : ce contrôle ne peut pas être exécuté, il ne doit PAS "
                     "être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — MDD jamais pire que la référence sur les fenêtres couvertes : {'oui' if ok_b else 'NON'}.**")
    lines.append("")

    lines.append(f"## c. Stabilité temporelle (folds non chevauchants + embargo {EMBARGO}j)")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |")
    lines.append("|---|---|---|---|---|")
    ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(raw_double, turn_double, raw_mom, turn_mom, cost_bps)
    for k, n, s_c, s_r, beat in rows_c:
        lines.append(f"| {k} | {n} | {s_c:+.2f} | {s_r:+.2f} | {'OUI' if beat else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — bat la référence sur {n_beat}/{n_scored} folds "
                 f"(majorité {'atteinte' if ok_c else 'NON atteinte'}).**")
    lines.append("")

    lines.append("## d. SPA à 1 candidat contre la référence")
    lines.append("")
    ok_d, p_spa = check_d_spa(raw_double, turn_double, raw_mom, turn_mom, cost_bps)
    lines.append(f"p-value SPA : {p_spa:.4f}")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — significatif à 5% : {'oui' if ok_d else 'NON'}.**")
    lines.append("")

    lines.append("## e. DSR avec n_trials = taille totale du backlog (jamais 1)")
    lines.append("")
    e_res = check_e_dsr(raw_double, turn_double, cost_bps)
    if e_res is None:
        lines.append("**PENDING — n_trials ou var_trials introuvable dans le backlog.**")
        ok_e = False
    else:
        n_trials, n_extracted, var_trials, d = e_res
        ok_e = d >= 0.95
        lines.append(f"n_trials = {n_trials} (taille du backlog après le #258), "
                     f"Var(Sharpe essais) estimée sur {n_extracted} Sharpe extraits du backlog "
                     f"= {var_trials:.6f} (échelle journalière).")
        lines.append(f"DSR = {d:.4f}")
        lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — DSR ≥ 0.95 : {'oui' if ok_e else 'NON'}.**")
    lines.append("")

    n_ok = sum([ok_a, ok_b, ok_c, ok_d, ok_e])
    lines.append(f"## Verdict global : {n_ok}/5")
    lines.append("")
    lines.append(f"**{'PASS RENFORCÉ (5/5)' if n_ok == 5 else f'PAS de PASS RENFORCÉ ({n_ok}/5)'}.**")

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
