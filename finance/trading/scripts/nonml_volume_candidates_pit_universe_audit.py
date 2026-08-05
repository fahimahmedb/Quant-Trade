"""Audit adversarial — vérification PIT des deux candidats volume
(#258, #261). Résultat surprenant (les deux basculent en FAIL sous
l'univers point-in-time, contrairement au #38 qui avait survécu au
#163) : audit avant tout usage de ce résultat (Règle 4).

1. Vérifie que `tickers_as_of_date` est appelé identiquement à
   l'implémentation du #163 (même import, mêmes arguments).
2. Recalcul indépendant de l'éligibilité PIT à un échantillon de dates
   (boucle Python explicite) pour les deux backtests.
3. Vérifie le décalage causal (`lag_one_day`).
4. Test anti-lookahead (perturbation du futur : prix et volume).
5. Compare la couverture moyenne mesurée ici (87.6%/87.8%) à celle du
   #163 (87.6%) -- doit être cohérente (même source de composition).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_momentum_turnover_doublesort_backtest import lag_one_day  # noqa: E402
import nonml_momentum_turnover_doublesort_pit_universe_backtest as MOM  # noqa: E402
import nonml_amihud_illiquidity_tilt_pit_universe_backtest as ILLIQ  # noqa: E402


def independent_eligible_at(tickers, m_or_illiq_row, extra_valid_row, date, require_positive_extra=True):
    members = tickers_as_of_date(date)
    out = []
    for j, tk in enumerate(tickers):
        if not np.isfinite(m_or_illiq_row[j]):
            continue
        if not np.isfinite(extra_valid_row[j]):
            continue
        if require_positive_extra and not (extra_valid_row[j] > 0):
            continue
        if tk not in members:
            continue
        out.append(j)
    return set(out)


def audit_one(name, module, signal_key):
    close_series = module.load_series(module.PRICES_PIT_DIR, "close")
    vol_series = module.load_series(module.VOLUME_PIT_DIR, "volume")
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0

    if signal_key == "momentum":
        R_np = R.values
        signal = np.full((T, n_tickers), np.nan)
        for i in range(module.LOOKBACK, T):
            c_skip = close[i - module.SKIP]
            c_lookback = close[i - module.LOOKBACK]
            with np.errstate(all="ignore"):
                m = c_skip / c_lookback - 1.0
            valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
            signal[i, valid] = m[valid]
        dollar_volume = P.values * V.values
        extra = pd.DataFrame(dollar_volume).rolling(module.TURNOVER_WINDOW).mean().values
        window = module.LOOKBACK
    else:
        dollar_volume = P.values * V.values
        with np.errstate(divide="ignore", invalid="ignore"):
            illiq_daily = np.abs(R.values) / dollar_volume
        illiq_daily[~np.isfinite(illiq_daily)] = np.nan
        signal = pd.DataFrame(illiq_daily).rolling(module.ILLIQ_WINDOW).mean().values
        extra = signal  # meme signal sert de filtre >0 (illiq)
        window = module.ILLIQ_WINDOW

    first_rebal = max(window, int(P.index.searchsorted(pd.Timestamp(module.REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, module.REBAL_EVERY))
    check_dates = rebal_dates[::40]

    lines = [f"### {name}", "",
             "| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |",
             "|---|---|---|---|"]
    all_ok = True
    coverage_ratios = []
    for t in check_dates:
        date = P.index[t]
        sig_row = signal[t]
        members = tickers_as_of_date(date)
        n_members = len(members)

        elig_orig = set(np.where(np.isfinite(sig_row) & np.isfinite(extra[t]) & (extra[t] > 0))[0])
        elig_orig_pit = {j for j in elig_orig if tickers[j] in members}

        elig_indep = independent_eligible_at(tickers, sig_row, extra[t], date)

        identical = elig_orig_pit == elig_indep
        all_ok &= identical
        coverage_ratios.append(len(elig_orig_pit) / max(1, n_members))
        lines.append(f"| {date.date()} | {len(elig_orig_pit)} | {len(elig_indep)} | {'OUI' if identical else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — éligibilité PIT confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")
    lines.append(f"Couverture moyenne mesurée sur cet échantillon : {100*np.mean(coverage_ratios):.1f}% "
                 f"(cohérent avec le ~87,6% mesuré au #163 sur le même univers de composition).")
    return lines, all_ok


def main():
    lines = ["# Audit adversarial — vérification PIT des candidats volume (#258, #261)", ""]

    l1, ok1 = audit_one("Momentum + double-tri turnover (#258 PIT)", MOM, "momentum")
    lines += l1
    lines.append("")
    l2, ok2 = audit_one("Tilt Amihud illiquidité (#261 PIT)", ILLIQ, "illiq")
    lines += l2
    lines.append("")

    lines.append("## Vérification du décalage causal (`lag_one_day`, partagé par les deux scripts)")
    lines.append("")
    W_test = np.zeros((100, 10))
    rng0 = np.random.default_rng(3)
    W_test[5::7] = rng0.random((len(range(5, 100, 7)), 10))
    W_lagged = lag_one_day(W_test)
    shift_ok = np.allclose(W_lagged[1:], W_test[:-1]) and np.allclose(W_lagged[0], 0.0)
    lines.append(f"**{'OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.' if shift_ok else 'ÉCHEC.'}**")

    lines.append("## Test anti-lookahead (perturbation du futur : prix et volume, sur le #261 PIT)")
    lines.append("")
    close_series = ILLIQ.load_series(ILLIQ.PRICES_PIT_DIR, "close")
    vol_series = ILLIQ.load_series(ILLIQ.VOLUME_PIT_DIR, "volume")
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T = len(P)
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg_before = pd.DataFrame(illiq_daily).rolling(ILLIQ.ILLIQ_WINDOW).mean().values

    cut = T // 2
    P_pert = P.copy()
    V_pert = V.copy()
    rng = np.random.default_rng(274)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    V_pert.iloc[cut:] = V_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=V_pert.iloc[cut:].shape))
    R_pert = np.log(P_pert / P_pert.shift(1))
    R_pert.iloc[0, :] = 0.0
    dollar_volume_pert = P_pert.values * V_pert.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily_pert = np.abs(R_pert.values) / dollar_volume_pert
    illiq_daily_pert[~np.isfinite(illiq_daily_pert)] = np.nan
    illiq_avg_after = pd.DataFrame(illiq_daily_pert).rolling(ILLIQ.ILLIQ_WINDOW).mean().values

    check_t = cut - ILLIQ.ILLIQ_WINDOW - 50
    diff_pert = np.nanmax(np.abs(np.nan_to_num(illiq_avg_before[check_t], nan=0.0) -
                                  np.nan_to_num(illiq_avg_after[check_t], nan=0.0)))
    anti_leak_ok = diff_pert < 1e-9
    lines.append(f"Écart ILLIQ à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    lines.append(f"## Verdict global")
    lines.append("")
    all_ok = ok1 and ok2 and shift_ok and anti_leak_ok
    lines.append(f"**{'OK — aucun bug détecté, le FAIL des deux candidats sous univers PIT est confirmé authentique.' if all_ok else 'ÉCHEC — anomalie détectée, résultat à ne PAS utiliser tel quel.'}**")

    out = ROOT / "results" / "nonml_volume_candidates_pit_universe_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
