"""Audit indépendant — Règle de Sahm en temps réel (FRED SAHMREALTIME).

Recalcule SahmRule_lag(t) et la porte à seuil fixe par une méthode
alternative (boucle explicite + searchsorted, sans
pandas.reindex/ffill/DateOffset), compare au résultat committé du
backtest. Vérifie le décalage d'un mois sur une transition réelle et
l'absence de fuite générale (troncature de l'historique).
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
from nonml_m2_growth_overlay_backtest import MARKETS  # noqa: E402
from nonml_sahm_rule_overlay_backtest import (  # noqa: E402
    CUT, PUBLICATION_LAG_MONTHS, SAHM_THRESHOLD, build_sahm_series,
    fixed_threshold_gate, load_sahm_lag,
)


def manual_sahm_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "sahm_rule_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["SAHMREALTIME"] = pd.to_numeric(raw["SAHMREALTIME"], errors="coerce")
    raw = raw.dropna(subset=["SAHMREALTIME"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["SAHMREALTIME"].astype(float).values

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=1))
    avail_dates = np.array(avail_dates)
    order = np.argsort(avail_dates)
    avail_sorted, vals_sorted = avail_dates[order], vals[order]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = vals_sorted[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def main():
    lines = ["# Audit — Règle de Sahm en temps réel (FRED SAHMREALTIME)", ""]
    all_ok = True

    sahm_series = build_sahm_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        sahm_official = load_sahm_lag(dates, sahm_series)[1:]
        pos_official = fixed_threshold_gate(sahm_official)

        sahm_manual = manual_sahm_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(sahm_official - sahm_manual))

        T = len(sahm_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(T):
            if not np.isfinite(sahm_manual[t]):
                continue
            pos_manual[t] = CUT if sahm_manual[t] >= SAHM_THRESHOLD else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff = float(np.max(np.abs(pos_official[mask] - pos_manual[mask]))) if mask.any() else 0.0

        ok = (diff_align < 1e-8) and (pos_diff < 1e-9)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        lines.append(f"- Écart max position (seuil fixe recalculé indépendamment) : {pos_diff:.2e}")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage d'un mois : transition ou la
    # valeur brute CHANGE reellement, 5 dates consecutives (evite l'artefact
    # de bord positionnel de shift(1) deja documente au #320/#321/#340/#341).
    raw = pd.read_csv(REPO_ROOT / "data" / "sahm_rule_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["SAHMREALTIME"] = pd.to_numeric(raw["SAHMREALTIME"], errors="coerce")
    raw = raw.dropna(subset=["SAHMREALTIME"]).sort_values("observation_date")
    vals = raw["SAHMREALTIME"].astype(float).values
    obs_dates = raw["observation_date"].values
    diffs = np.diff(vals)
    nz = np.where(diffs != 0)[0]
    last_change = nz[-1]
    d_prev, d_last = pd.Timestamp(obs_dates[last_change]), pd.Timestamp(obs_dates[last_change + 1])
    v_prev, v_last = vals[last_change], vals[last_change + 1]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)

    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=2), avail_last - pd.Timedelta(days=1),
        avail_last, avail_last + pd.Timedelta(days=1), avail_last + pd.Timedelta(days=2),
    ])
    sahm_check = load_sahm_lag(check_dates, sahm_series)
    lines.append(f"## Vérification spécifique du décalage d'un mois (transition autour de {avail_last.date()})")
    lines.append(f"- Valeur mois précédent (obs {d_prev.date()}) = {v_prev:.6f}, "
                 f"valeur dernier mois disponible (obs {d_last.date()}) = {v_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- SahmRule_lag({check_dates[1].date()}) = {sahm_check[1]:.6f}, "
                 f"SahmRule_lag({check_dates[2].date()}) = {sahm_check[2]:.6f} "
                 f"(doivent valoir {v_prev:.6f}, JAMAIS {v_last:.6f})")
    lines.append(f"- SahmRule_lag({check_dates[3].date()}) = {sahm_check[3]:.6f}, "
                 f"SahmRule_lag({check_dates[4].date()}) = {sahm_check[4]:.6f} "
                 f"({check_dates[3].date()} doit être le premier jour où {v_last:.6f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(sahm_check[1], v_prev) and \
        np.isclose(sahm_check[2], v_prev) and np.isclose(sahm_check[3], v_last) and np.isclose(sahm_check[4], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    sahm_lag_full = load_sahm_lag(dates, sahm_series)[1:]
    pos_full = fixed_threshold_gate(sahm_lag_full)
    valid_start = int(np.argmax(np.isfinite(sahm_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = fixed_threshold_gate(sahm_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_sahm_rule_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
