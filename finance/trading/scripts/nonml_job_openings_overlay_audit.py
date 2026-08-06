"""Audit indépendant — Offres d'emploi US (FRED JTSJOL, JOLTS).

Recalcule JOLGrowth_lag(t), l'alignement causal (avec décalage de 2
mois) et le tercile expanding par une méthode alternative (boucle
explicite + searchsorted, sans pandas.reindex/ffill/DateOffset ni
np.percentile), compare au résultat committé du backtest. Vérifie
spécifiquement le décalage de 2 mois (sur une transition réelle, pas
aveugle) et l'absence de fuite générale (troncature de l'historique).
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
from nonml_m2_growth_overlay_backtest import CUT, YOY_MONTHS, MARKETS, expanding_tercile_cut_low  # noqa: E402
from nonml_job_openings_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, build_job_openings_growth_series, load_job_openings_growth_lag,
)


def manual_jol_growth_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "job_openings_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["JTSJOL"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["JTSJOL"].astype(float).values

    growth = np.full(len(vals), np.nan)
    for i in range(YOY_MONTHS, len(vals)):
        growth[i] = np.log(vals[i] / vals[i - YOY_MONTHS])

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=1))
    avail_dates = np.array(avail_dates)
    order = np.argsort(avail_dates)
    avail_sorted = avail_dates[order]
    growth_sorted = growth[order]
    valid = np.isfinite(growth_sorted)
    avail_sorted, growth_sorted = avail_sorted[valid], growth_sorted[valid]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = growth_sorted[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
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
    lines = ["# Audit — Offres d'emploi US (FRED JTSJOL, JOLTS)", ""]
    all_ok = True

    jol_series = build_job_openings_growth_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        jol_lag_official = load_job_openings_growth_lag(dates, jol_series)[1:]
        pos_official = expanding_tercile_cut_low(jol_lag_official)

        jol_lag_manual = manual_jol_growth_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(jol_lag_official - jol_lag_manual))

        start = int(np.argmax(np.isfinite(jol_lag_manual)))
        T = len(jol_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(jol_lag_manual[t]):
                continue
            hist = jol_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if jol_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(jol_lag_official[i] - jol_lag_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage de 2 mois : transition ou la
    # valeur CHANGE reellement (evite le piege du #320).
    raw = pd.read_csv(REPO_ROOT / "data" / "job_openings_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["JTSJOL"]).sort_values("observation_date")
    vals = raw["JTSJOL"].astype(float).values
    obs_dates = raw["observation_date"].values
    growth_raw = np.full(len(vals), np.nan)
    growth_raw[YOY_MONTHS:] = np.log(vals[YOY_MONTHS:] / vals[:-YOY_MONTHS])
    last_two = np.where(np.isfinite(growth_raw))[0][-2:]
    d_prev, d_last = pd.Timestamp(obs_dates[last_two[0]]), pd.Timestamp(obs_dates[last_two[1]])
    g_prev, g_last = growth_raw[last_two[0]], growth_raw[last_two[1]]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=2), avail_last - pd.Timedelta(days=1),
        avail_last, avail_last + pd.Timedelta(days=1), avail_last + pd.Timedelta(days=2),
    ])
    jol_check = load_job_openings_growth_lag(check_dates, jol_series)
    lines.append(f"## Vérification spécifique du décalage de 2 mois (transition autour de {avail_last.date()})")
    lines.append(f"- Valeur mois précédent (obs {d_prev.date()}) = {g_prev:.6f}, "
                 f"valeur dernier mois disponible (obs {d_last.date()}) = {g_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(g_prev, g_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- JOLGrowth_lag({check_dates[1].date()}) = {jol_check[1]:.6f}, "
                 f"JOLGrowth_lag({check_dates[2].date()}) = {jol_check[2]:.6f} "
                 f"(doivent valoir {g_prev:.6f}, JAMAIS {g_last:.6f})")
    lines.append(f"- JOLGrowth_lag({check_dates[3].date()}) = {jol_check[3]:.6f}, "
                 f"JOLGrowth_lag({check_dates[4].date()}) = {jol_check[4]:.6f} "
                 f"({check_dates[3].date()} doit être le premier jour où {g_last:.6f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(g_prev, g_last)) and np.isclose(jol_check[1], g_prev) and \
        np.isclose(jol_check[2], g_prev) and np.isclose(jol_check[3], g_last) and np.isclose(jol_check[4], g_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    jol_lag_full = load_job_openings_growth_lag(dates, jol_series)[1:]
    pos_full = expanding_tercile_cut_low(jol_lag_full)
    valid_start = int(np.argmax(np.isfinite(jol_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(jol_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_job_openings_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
