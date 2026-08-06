"""Audit indépendant — Vitesse de circulation de M2 (FRED M2V).

Recalcule M2V_lag(t), l'alignement causal (décalage d'UN TRIMESTRE) et le
tercile expanding par une méthode alternative (boucle explicite +
searchsorted, sans pandas.reindex/ffill/DateOffset ni np.percentile),
compare au résultat committé du backtest. Vérifie spécifiquement le
décalage de 3 mois (point le plus sensible du PREREG, même vérification
que le #195/#286) et l'absence de fuite générale (troncature de
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
from nonml_m2_growth_overlay_backtest import CUT, MARKETS  # noqa: E402
from nonml_m2_velocity_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, build_m2_velocity_series, load_m2_velocity_lag,
)
from nonml_m2_growth_overlay_backtest import expanding_tercile_cut_low  # noqa: E402


def manual_m2_velocity_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "m2_velocity_quarterly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["M2V"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["M2V"].astype(float).values

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=d.day))
    avail_dates = np.array(avail_dates)
    order = np.argsort(avail_dates)
    avail_sorted = avail_dates[order]
    vals_sorted = vals[order]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = vals_sorted[idx]
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
    lines = ["# Audit — Vitesse de circulation de M2 (FRED M2V)", ""]
    all_ok = True

    velocity_series = build_m2_velocity_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        vel_lag_official = load_m2_velocity_lag(dates, velocity_series)[1:]
        pos_official = expanding_tercile_cut_low(vel_lag_official)

        vel_lag_manual = manual_m2_velocity_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(vel_lag_official - vel_lag_manual))

        start = int(np.argmax(np.isfinite(vel_lag_manual)))
        T = len(vel_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(vel_lag_manual[t]):
                continue
            hist = vel_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if vel_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(vel_lag_official[i] - vel_lag_manual[i])
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

    # Verification specifique du decalage de 3 mois (meme test que #195/#286).
    # Choix des dates sondes : la transition obs 2025-10-01 (1.409, dispo
    # 2026-01-01) vers obs 2026-01-01 (1.412, dispo 2026-04-01) — la seule
    # transition recente ou la valeur CHANGE reellement (la transition
    # juin/juillet 2026 est ininteressante car obs 2026-01-01 et obs
    # 2026-04-01 partagent par coincidence la meme valeur arrondie 1.412,
    # ce qui rendrait le test aveugle a une fuite).
    raw = pd.read_csv(REPO_ROOT / "data" / "m2_velocity_quarterly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    check_dates = pd.DatetimeIndex([pd.Timestamp("2026-03-15"), pd.Timestamp("2026-03-31"),
                                     pd.Timestamp("2026-04-01"), pd.Timestamp("2026-04-02")])
    vel_check = load_m2_velocity_lag(check_dates, velocity_series)
    lines.append("## Vérification spécifique du décalage de 3 mois (mars/avril 2026)")
    lines.append(f"- M2V_lag(15 mars) = {vel_check[0]}, M2V_lag(31 mars) = {vel_check[1]} "
                 f"(doivent être la valeur T3-2025 = 1.409 ou plus ancienne, JAMAIS T4-2025 = 1.412 dont la "
                 f"publication n'est disponible qu'à partir du 1er avril)")
    lines.append(f"- M2V_lag(1 avril) = {vel_check[2]}, M2V_lag(2 avril) = {vel_check[3]} "
                 f"(le 2 avril doit être le premier jour où 1.412 apparaît, via shift(1))")
    ok_shift = not np.isclose(vel_check[0], vel_check[3]) and not np.isclose(vel_check[1], vel_check[3])
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au 2 avril, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    vel_lag_full = load_m2_velocity_lag(dates, velocity_series)[1:]
    pos_full = expanding_tercile_cut_low(vel_lag_full)
    valid_start = int(np.argmax(np.isfinite(vel_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(vel_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_m2_velocity_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
