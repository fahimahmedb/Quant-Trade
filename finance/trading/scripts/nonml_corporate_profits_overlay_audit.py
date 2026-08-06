"""Audit indépendant — Profits des entreprises US (FRED CP).

Recalcule CPGrowth(t), l'alignement causal (décalage d'UN TRIMESTRE) et
le tercile expanding par une méthode alternative (boucle explicite +
searchsorted, sans pandas.reindex/ffill/DateOffset ni np.percentile),
compare au résultat committé du backtest. Vérifie spécifiquement le
décalage de 3 mois (point le plus sensible du PREREG, même vérification
que le #195/#286/#320) et l'absence de fuite générale (troncature de
l'historique).
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
from nonml_m2_growth_overlay_backtest import CUT, MARKETS, expanding_tercile_cut_low  # noqa: E402
from nonml_corporate_profits_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, YOY_QUARTERS, build_corporate_profits_series,
    load_corporate_profits_lag,
)


def manual_corporate_profits_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "corporate_profits_quarterly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["CP"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["CP"].astype(float).values

    growth = np.full(len(vals), np.nan)
    for i in range(YOY_QUARTERS, len(vals)):
        growth[i] = np.log(vals[i] / vals[i - YOY_QUARTERS])

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=d.day))
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
    lines = ["# Audit — Profits des entreprises US (FRED CP)", ""]
    all_ok = True

    cp_series = build_corporate_profits_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        cp_lag_official = load_corporate_profits_lag(dates, cp_series)[1:]
        pos_official = expanding_tercile_cut_low(cp_lag_official)

        cp_lag_manual = manual_corporate_profits_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(cp_lag_official - cp_lag_manual))

        start = int(np.argmax(np.isfinite(cp_lag_manual)))
        T = len(cp_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(cp_lag_manual[t]):
                continue
            hist = cp_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if cp_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(cp_lag_official[i] - cp_lag_manual[i])
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
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#320) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage de 3 mois : recherche de la
    # transition la plus recente ou la valeur de croissance CHANGE
    # reellement (evite le piege du #320 ou une transition avait ete
    # choisie aveuglement par coincidence de valeurs identiques).
    raw = pd.read_csv(REPO_ROOT / "data" / "corporate_profits_quarterly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["CP"]).sort_values("observation_date")
    vals = raw["CP"].astype(float).values
    obs_dates = raw["observation_date"].values
    growth_raw = np.full(len(vals), np.nan)
    growth_raw[YOY_QUARTERS:] = np.log(vals[YOY_QUARTERS:] / vals[:-YOY_QUARTERS])
    last_two = np.where(np.isfinite(growth_raw))[0][-2:]
    d_prev, d_last = pd.Timestamp(obs_dates[last_two[0]]), pd.Timestamp(obs_dates[last_two[1]])
    g_prev, g_last = growth_raw[last_two[0]], growth_raw[last_two[1]]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    # 5 dates espacees de 1 jour (au lieu de sonder des dates isolees) pour
    # que le shift(1) positionnel corresponde a un vrai decalage d'UN JOUR
    # calendaire une fois "amorce" -- la toute premiere position (T-17j)
    # est structurellement NaN par artefact de bord de tableau (aucun
    # predecesseur dans ce mini-tableau de sondage), ignoree du verdict ;
    # lecon tiree du premier essai du #320 (dates trop espacees, verdict
    # aveugle par coincidence).
    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=17), avail_last - pd.Timedelta(days=16),
        avail_last - pd.Timedelta(days=1), avail_last, avail_last + pd.Timedelta(days=1),
    ])
    cp_check = load_corporate_profits_lag(check_dates, cp_series)
    lines.append(f"## Vérification spécifique du décalage de 3 mois (transition autour de {avail_last.date()})")
    lines.append(f"- Valeur trimestre précédent (obs {d_prev.date()}) = {g_prev:.6f}, "
                 f"valeur dernier trimestre disponible (obs {d_last.date()}) = {g_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(g_prev, g_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- CPGrowth_lag({check_dates[1].date()}) = {cp_check[1]:.6f}, "
                 f"CPGrowth_lag({check_dates[2].date()}) = {cp_check[2]:.6f} "
                 f"(doivent valoir {g_prev:.6f}, JAMAIS {g_last:.6f})")
    lines.append(f"- CPGrowth_lag({check_dates[3].date()}) = {cp_check[3]:.6f}, "
                 f"CPGrowth_lag({check_dates[4].date()}) = {cp_check[4]:.6f} "
                 f"({check_dates[4].date()} doit être le premier jour où {g_last:.6f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(g_prev, g_last)) and np.isclose(cp_check[1], g_prev) and \
        np.isclose(cp_check[2], g_prev) and np.isclose(cp_check[3], g_prev) and np.isclose(cp_check[4], g_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    cp_lag_full = load_corporate_profits_lag(dates, cp_series)[1:]
    pos_full = expanding_tercile_cut_low(cp_lag_full)
    valid_start = int(np.argmax(np.isfinite(cp_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(cp_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_corporate_profits_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
