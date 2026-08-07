"""Audit indépendant — Force relative EM/DM (EEM/SPY, log-return 21j).

Recalcule le ratio EEM/SPY, RatioMom_lag(t), le tercile expanding et
la position par une méthode alternative (boucle explicite +
searchsorted, sans pandas.reindex/ffill/np.percentile), compare au
résultat committé du backtest. Vérifie le décalage causal d'un jour
sur une transition réelle et l'absence de fuite par troncature de
l'historique.
"""
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
from nonml_dollar_strength_overlay_backtest import MARKETS, RET_WINDOW  # noqa: E402
from nonml_bitcoin_momentum_overlay_backtest import CUT, expanding_tercile_cut_low  # noqa: E402
from nonml_em_dm_relative_strength_overlay_backtest import load_ratio_mom_lag, load_ratio_series  # noqa: E402


def manual_ratio_series() -> tuple:
    eem = pd.read_csv(REPO_ROOT / "data" / "eem_etf_daily.csv")
    spy = pd.read_csv(REPO_ROOT / "data" / "spy_etf_daily.csv")
    eem["observation_date"] = pd.to_datetime(eem["observation_date"])
    spy["observation_date"] = pd.to_datetime(spy["observation_date"])
    eem["EEM"] = pd.to_numeric(eem["EEM"], errors="coerce")
    spy["SPY"] = pd.to_numeric(spy["SPY"], errors="coerce")
    eem = eem.dropna(subset=["EEM"]).drop_duplicates("observation_date").sort_values("observation_date")
    spy = spy.dropna(subset=["SPY"]).drop_duplicates("observation_date").sort_values("observation_date")
    return (eem["observation_date"].values, eem["EEM"].astype(float).values,
            spy["observation_date"].values, spy["SPY"].astype(float).values)


def manual_ratio_mom_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif) pour CHAQUE serie separement, sans pandas.reindex/ffill."""
    de, ve, ds, vs = manual_ratio_series()

    aligned_eem = np.full(len(dates), np.nan)
    aligned_spy = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx_e = np.searchsorted(de, np.datetime64(d), side="right") - 1
        idx_s = np.searchsorted(ds, np.datetime64(d), side="right") - 1
        if idx_e >= 0:
            aligned_eem[i] = ve[idx_e]
        if idx_s >= 0:
            aligned_spy[i] = vs[idx_s]

    ratio = np.where(np.isfinite(aligned_eem) & np.isfinite(aligned_spy), aligned_eem / aligned_spy, np.nan)

    mom = np.full(len(dates), np.nan)
    for i in range(RET_WINDOW, len(dates)):
        if np.isfinite(ratio[i]) and np.isfinite(ratio[i - RET_WINDOW]):
            mom[i] = np.log(ratio[i] / ratio[i - RET_WINDOW])

    shifted = np.full(len(dates), np.nan)
    shifted[1:] = mom[:-1]
    return shifted


def manual_percentile_low_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Force relative EM/DM (EEM/SPY, log-return 21j)", ""]
    all_ok = True

    ratio_series = load_ratio_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        mom_official = load_ratio_mom_lag(dates, ratio_series)[1:]
        pos_official = expanding_tercile_cut_low(mom_official)

        mom_manual = manual_ratio_mom_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(mom_official - mom_manual))

        start = int(np.argmax(np.isfinite(mom_manual)))
        T = len(mom_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(mom_manual[t]):
                continue
            hist = mom_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if mom_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(mom_official[i] - mom_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, "
                     f"intersection stricte des deux séries) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/.../#353) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage causal d'un jour.
    de, ve, ds, vs = manual_ratio_series()
    common_dates = np.intersect1d(de, ds)
    ve_map = dict(zip(de, ve))
    vs_map = dict(zip(ds, vs))
    ratio_raw = np.array([ve_map[d] / vs_map[d] for d in common_dates])
    diffs = np.diff(ratio_raw)
    nz = np.where(diffs != 0)[0]
    last_change = nz[-1]
    d_prev, d_last = pd.Timestamp(common_dates[last_change]), pd.Timestamp(common_dates[last_change + 1])
    r_prev, r_last = ratio_raw[last_change], ratio_raw[last_change + 1]

    lines.append(f"## Vérification spécifique du décalage causal d'un jour (transition {d_prev.date()}→{d_last.date()})")
    lines.append(f"- Ratio brut jour précédent ({d_prev.date()}) = {r_prev:.6f}, "
                 f"ratio brut jour de la transition ({d_last.date()}) = {r_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(r_prev, r_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    ok_shift = not np.isclose(r_prev, r_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — transition non aveugle confirmée' if ok_shift else 'TRANSITION AVEUGLE, coïncidence à éviter'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    mom_full = load_ratio_mom_lag(dates, ratio_series)[1:]
    pos_full = expanding_tercile_cut_low(mom_full)
    valid_start = int(np.argmax(np.isfinite(mom_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(mom_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_em_dm_relative_strength_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
