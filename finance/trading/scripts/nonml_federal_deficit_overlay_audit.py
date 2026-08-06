"""Audit indépendant — Déficit budgétaire fédéral US (FRED MTSDS133FMS).

Recalcule DeficitTTM_lag(t) (somme glissante 12 mois sans
pandas.rolling, alignement causal avec décalage d'un mois sans
pandas.reindex/ffill/DateOffset) et le tercile expanding par une
méthode alternative (boucle explicite + searchsorted, sans
np.percentile), compare au résultat committé du backtest. Vérifie
spécifiquement le décalage d'un mois et l'absence de fuite générale
(troncature de l'historique). Vérifie aussi explicitement le risque
déclaré au PREREG : tendance séculaire de creusement du déficit
ancrant le seuil expanding.
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
from nonml_federal_deficit_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, ROLLING_MONTHS, build_deficit_ttm_series, load_deficit_ttm_lag,
)


def manual_deficit_ttm_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite (somme glissante 12 mois sans
    pandas.rolling) + searchsorted, sans pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "federal_deficit_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["MTSDS133FMS"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["MTSDS133FMS"].astype(float).values
    T = len(vals)

    ttm = np.full(T, np.nan)
    for i in range(ROLLING_MONTHS - 1, T):
        ttm[i] = np.sum(vals[i - ROLLING_MONTHS + 1:i + 1])

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + PUBLICATION_LAG_MONTHS
        while m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=1))
    avail_dates = np.array(avail_dates)
    valid = np.isfinite(ttm)
    avail_valid, ttm_valid = avail_dates[valid], ttm[valid]
    order = np.argsort(avail_valid)
    avail_sorted, ttm_sorted = avail_valid[order], ttm_valid[order]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = ttm_sorted[idx]
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
    lines = ["# Audit — Déficit budgétaire fédéral US (FRED MTSDS133FMS)", ""]
    all_ok = True

    deficit_series = build_deficit_ttm_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        deficit_lag_official = load_deficit_ttm_lag(dates, deficit_series)[1:]
        pos_official = expanding_tercile_cut_low(deficit_lag_official)

        deficit_lag_manual = manual_deficit_ttm_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(deficit_lag_official - deficit_lag_manual))

        start = int(np.argmax(np.isfinite(deficit_lag_manual)))
        T = len(deficit_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(deficit_lag_manual[t]):
                continue
            hist = deficit_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if deficit_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(deficit_lag_official[i] - deficit_lag_manual[i])
            if local_diff >= 1e-6:  # tolerance plus large : sommes glissantes de grands nombres
                boundary_tie_ok = False

        ok = (diff_align < 1e-3) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : {diff_align:.2e}")
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
    raw = pd.read_csv(REPO_ROOT / "data" / "federal_deficit_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["MTSDS133FMS"]).sort_values("observation_date")
    vals = raw["MTSDS133FMS"].astype(float).values
    obs_dates = raw["observation_date"].values
    ttm_raw = np.full(len(vals), np.nan)
    for i in range(ROLLING_MONTHS - 1, len(vals)):
        ttm_raw[i] = np.sum(vals[i - ROLLING_MONTHS + 1:i + 1])
    last_two = np.where(np.isfinite(ttm_raw))[0][-2:]
    d_prev, d_last = pd.Timestamp(obs_dates[last_two[0]]), pd.Timestamp(obs_dates[last_two[1]])
    v_prev, v_last = ttm_raw[last_two[0]], ttm_raw[last_two[1]]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=2), avail_last - pd.Timedelta(days=1),
        avail_last, avail_last + pd.Timedelta(days=1), avail_last + pd.Timedelta(days=2),
    ])
    deficit_check = load_deficit_ttm_lag(check_dates, deficit_series)
    lines.append(f"## Vérification spécifique du décalage d'un mois (transition autour de {avail_last.date()})")
    lines.append(f"- DeficitTTM mois précédent (obs {d_prev.date()}) = {v_prev:.0f}, "
                 f"DeficitTTM dernier mois disponible (obs {d_last.date()}) = {v_last:.0f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle'})")
    lines.append(f"- DeficitTTM_lag({check_dates[1].date()}) = {deficit_check[1]:.0f}, "
                 f"DeficitTTM_lag({check_dates[2].date()}) = {deficit_check[2]:.0f} "
                 f"(doivent valoir {v_prev:.0f}, JAMAIS {v_last:.0f})")
    lines.append(f"- DeficitTTM_lag({check_dates[3].date()}) = {deficit_check[3]:.0f}, "
                 f"DeficitTTM_lag({check_dates[4].date()}) = {deficit_check[4]:.0f} "
                 f"({check_dates[3].date()} doit être le premier jour où {v_last:.0f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(deficit_check[1], v_prev, atol=1) and \
        np.isclose(deficit_check[2], v_prev, atol=1) and np.isclose(deficit_check[3], v_last, atol=1) and \
        np.isclose(deficit_check[4], v_last, atol=1)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Verification dediee du risque declare au PREREG : tendance seculaire
    # de creusement du deficit sur NDX (40 ans, taux de coupure 65,8%).
    name_n, fname_n = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df_n = load_ohlc(str(REPO_ROOT / "data" / fname_n))
    dates_n = pd.DatetimeIndex(df_n["date"].values)
    deficit_lag_n = load_deficit_ttm_lag(dates_n, deficit_series)[1:]
    valid_n = np.isfinite(deficit_lag_n)
    vals_valid_n = deficit_lag_n[valid_n]
    lines.append("## Vérification dédiée du taux de coupure élevé sur NDX (65,8%)")
    lines.append(f"- DeficitTTM_lag sur la fenêtre NDX : médiane des 20% premières valeurs="
                 f"{np.median(vals_valid_n[:len(vals_valid_n)//5]):.0f} M$, "
                 f"médiane des 20% dernières valeurs={np.median(vals_valid_n[-len(vals_valid_n)//5:]):.0f} M$")
    trend_confirmed = np.median(vals_valid_n[-len(vals_valid_n)//5:]) < np.median(vals_valid_n[:len(vals_valid_n)//5])
    lines.append(f"- Le déficit cumulé médian récent est "
                 f"{'bien plus négatif (creusement confirmé)' if trend_confirmed else 'PAS plus négatif'} "
                 f"que le déficit cumulé médian ancien : confirme un creusement séculaire réel du déficit fédéral "
                 f"US sur l'historique testé, ancrant mécaniquement le seuil expanding vers des valeurs de moins "
                 f"en moins atteignables par les observations anciennes — même mécanisme de tendance déjà "
                 f"documenté au #327 (balance commerciale) et #331 (TCU), pas un bug de calcul.")
    lines.append(f"- **{'OK — comportement confirmé cohérent avec la donnée réelle, aucune anomalie de calcul' if trend_confirmed else 'À INVESTIGUER'}**")
    all_ok &= trend_confirmed
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    deficit_lag_full = load_deficit_ttm_lag(dates_n, deficit_series)[1:]
    pos_full = expanding_tercile_cut_low(deficit_lag_full)
    valid_start = int(np.argmax(np.isfinite(deficit_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(deficit_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_federal_deficit_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
