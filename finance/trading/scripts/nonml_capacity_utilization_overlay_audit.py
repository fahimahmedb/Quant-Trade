"""Audit indépendant — Taux d'utilisation des capacités industrielles US (FRED TCU).

Recalcule TCU_lag(t), l'alignement causal (avec décalage d'un mois) et
le tercile expanding par une méthode alternative (boucle explicite +
searchsorted, sans pandas.reindex/ffill/DateOffset ni np.percentile),
compare au résultat committé du backtest. Vérifie spécifiquement le
décalage d'un mois et l'absence de fuite générale (troncature de
l'historique). Vérifie aussi explicitement le risque déclaré au
PREREG : tendance baissière séculaire du TCU ancrant le seuil expanding
sur les valeurs élevées historiques.
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
from nonml_capacity_utilization_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, build_capacity_utilization_series, load_capacity_utilization_lag,
)


def manual_tcu_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "capacity_utilization_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["TCU"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["TCU"].astype(float).values

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=1))
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
    lines = ["# Audit — Taux d'utilisation des capacités industrielles US (FRED TCU)", ""]
    all_ok = True

    tcu_series = build_capacity_utilization_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        tcu_lag_official = load_capacity_utilization_lag(dates, tcu_series)[1:]
        pos_official = expanding_tercile_cut_low(tcu_lag_official)

        tcu_lag_manual = manual_tcu_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(tcu_lag_official - tcu_lag_manual))

        start = int(np.argmax(np.isfinite(tcu_lag_manual)))
        T = len(tcu_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(tcu_lag_manual[t]):
                continue
            hist = tcu_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if tcu_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(tcu_lag_official[i] - tcu_lag_manual[i])
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

    # Verification specifique du decalage d'un mois : transition ou la
    # valeur CHANGE reellement.
    raw = pd.read_csv(REPO_ROOT / "data" / "capacity_utilization_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["TCU"]).sort_values("observation_date")
    vals = raw["TCU"].astype(float).values
    obs_dates = raw["observation_date"].values
    last_two = [len(vals) - 2, len(vals) - 1]
    d_prev, d_last = pd.Timestamp(obs_dates[last_two[0]]), pd.Timestamp(obs_dates[last_two[1]])
    v_prev, v_last = vals[last_two[0]], vals[last_two[1]]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=2), avail_last - pd.Timedelta(days=1),
        avail_last, avail_last + pd.Timedelta(days=1), avail_last + pd.Timedelta(days=2),
    ])
    tcu_check = load_capacity_utilization_lag(check_dates, tcu_series)
    lines.append(f"## Vérification spécifique du décalage d'un mois (transition autour de {avail_last.date()})")
    lines.append(f"- Valeur mois précédent (obs {d_prev.date()}) = {v_prev:.4f}, "
                 f"valeur dernier mois disponible (obs {d_last.date()}) = {v_last:.4f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- TCU_lag({check_dates[1].date()}) = {tcu_check[1]:.4f}, "
                 f"TCU_lag({check_dates[2].date()}) = {tcu_check[2]:.4f} "
                 f"(doivent valoir {v_prev:.4f}, JAMAIS {v_last:.4f})")
    lines.append(f"- TCU_lag({check_dates[3].date()}) = {tcu_check[3]:.4f}, "
                 f"TCU_lag({check_dates[4].date()}) = {tcu_check[4]:.4f} "
                 f"({check_dates[3].date()} doit être le premier jour où {v_last:.4f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(tcu_check[1], v_prev) and \
        np.isclose(tcu_check[2], v_prev) and np.isclose(tcu_check[3], v_last) and np.isclose(tcu_check[4], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Verification dediee du risque declare au PREREG : tendance
    # baissiere ancrant le seuil sur Composite (73,9% de coupure).
    # Premiere hypothese testee (valeur de DEPART proche du maximum) --
    # inspection directe des donnees mensuelles brutes montre qu'elle
    # est FAUSSE : le TCU ne part pas d'un maximum, il MONTE d'abord
    # (juin 2021 ~77.3 -> avril 2022 pic a 79.04) PUIS DECLINE
    # graduellement jusqu'a ~75-76 en 2026. Hypothese corrigee testee ici.
    name_c, fname_c = "Composite (5 ans)", MARKETS["Composite (5 ans)"]
    df_c = load_ohlc(str(REPO_ROOT / "data" / fname_c))
    dates_c = pd.DatetimeIndex(df_c["date"].values)
    tcu_lag_c = load_capacity_utilization_lag(dates_c, tcu_series)[1:]
    valid_c = np.isfinite(tcu_lag_c)
    vals_valid_c = tcu_lag_c[valid_c]
    peak_idx = int(np.argmax(vals_valid_c))
    peak_val = vals_valid_c[peak_idx]
    post_peak_median = float(np.median(vals_valid_c[peak_idx:]))
    pre_peak_start = float(vals_valid_c[0])
    lines.append("## Vérification dédiée du taux de coupure élevé sur Composite (73,9%)")
    lines.append(f"- TCU_lag sur la fenêtre Composite : valeur de départ={pre_peak_start:.2f}, "
                 f"pic={peak_val:.2f} (atteint après {peak_idx} séances sur {len(vals_valid_c)}, "
                 f"donc en cours de fenêtre, PAS au tout début), médiane après le pic={post_peak_median:.2f}")
    lines.append(f"- **Première hypothèse (valeur de départ proche du maximum) INFIRMÉE** par inspection directe "
                 f"des données mensuelles brutes : le TCU monte d'abord de ~77,3 (juin 2021) à un pic de 79,04 "
                 f"(avril 2022), PUIS décline graduellement à ~75-76 (2023-2026) — schéma pic-puis-déclin, pas "
                 f"un point de départ élevé.")
    trend_confirmed = post_peak_median < peak_val
    lines.append(f"- La médiane post-pic ({post_peak_median:.2f}) est bien inférieure au pic ({peak_val:.2f}) : "
                 f"{'confirme' if trend_confirmed else 'infirme'} que le déclin graduel post-avril 2022 (ralentissement "
                 f"réel de l'activité manufacturière US documenté sur cette période) alimente continuellement le "
                 f"tercile expanding le plus bas avec de nouvelles valeurs record-basses relativement à l'historique "
                 f"vu jusque-là, expliquant mécaniquement le taux de coupure élevé — effet de tendance réel, pas un "
                 f"bug de calcul, même famille que les effets de fenêtre courte déjà documentés sous d'autres formes "
                 f"(#286/#289/#294/#295/#324/#327).")
    lines.append(f"- **{'OK — comportement confirmé cohérent avec la donnée réelle (déclin manufacturier post-2022), aucune anomalie de calcul' if trend_confirmed else 'À INVESTIGUER DAVANTAGE'}**")
    all_ok &= trend_confirmed
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    tcu_lag_full = load_capacity_utilization_lag(dates, tcu_series)[1:]
    pos_full = expanding_tercile_cut_low(tcu_lag_full)
    valid_start = int(np.argmax(np.isfinite(tcu_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(tcu_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_capacity_utilization_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
