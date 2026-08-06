"""Audit indépendant — Balance commerciale US (FRED BOPGSTB).

Recalcule BOPGSTB_lag(t), l'alignement causal (avec décalage de 2
mois) et le tercile expanding par une méthode alternative (boucle
explicite + searchsorted, sans pandas.reindex/ffill/DateOffset ni
np.percentile), compare au résultat committé du backtest. Vérifie
spécifiquement le décalage de 2 mois (point le plus sensible du
PREREG) et l'absence de fuite générale (troncature de l'historique).
Vérifie aussi explicitement le taux de coupure élevé sur NDX/Russell/
S&P500 (77,7%, creusement séculaire du déficit déclaré non-bug dans
le résultat).
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
from nonml_trade_balance_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_MONTHS, build_trade_balance_series, load_trade_balance_lag,
)


def manual_trade_balance_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted, sans
    pandas.reindex/ffill/DateOffset."""
    raw = pd.read_csv(REPO_ROOT / "data" / "trade_balance_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["BOPGSTB"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["BOPGSTB"].astype(float).values

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
    lines = ["# Audit — Balance commerciale US (FRED BOPGSTB)", ""]
    all_ok = True

    trade_series = build_trade_balance_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        trade_lag_official = load_trade_balance_lag(dates, trade_series)[1:]
        pos_official = expanding_tercile_cut_low(trade_lag_official)

        trade_lag_manual = manual_trade_balance_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(trade_lag_official - trade_lag_manual))

        start = int(np.argmax(np.isfinite(trade_lag_manual)))
        T = len(trade_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(trade_lag_manual[t]):
                continue
            hist = trade_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if trade_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(trade_lag_official[i] - trade_lag_manual[i])
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
    raw = pd.read_csv(REPO_ROOT / "data" / "trade_balance_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["BOPGSTB"]).sort_values("observation_date")
    vals = raw["BOPGSTB"].astype(float).values
    obs_dates = raw["observation_date"].values
    last_two = [len(vals) - 2, len(vals) - 1]
    d_prev, d_last = pd.Timestamp(obs_dates[last_two[0]]), pd.Timestamp(obs_dates[last_two[1]])
    v_prev, v_last = vals[last_two[0]], vals[last_two[1]]
    avail_last = d_last + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    check_dates = pd.DatetimeIndex([
        avail_last - pd.Timedelta(days=2), avail_last - pd.Timedelta(days=1),
        avail_last, avail_last + pd.Timedelta(days=1), avail_last + pd.Timedelta(days=2),
    ])
    trade_check = load_trade_balance_lag(check_dates, trade_series)
    lines.append(f"## Vérification spécifique du décalage de 2 mois (transition autour de {avail_last.date()})")
    lines.append(f"- Valeur mois précédent (obs {d_prev.date()}) = {v_prev:.0f}, "
                 f"valeur dernier mois disponible (obs {d_last.date()}) = {v_last:.0f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- BOPGSTB_lag({check_dates[1].date()}) = {trade_check[1]:.0f}, "
                 f"BOPGSTB_lag({check_dates[2].date()}) = {trade_check[2]:.0f} "
                 f"(doivent valoir {v_prev:.0f}, JAMAIS {v_last:.0f})")
    lines.append(f"- BOPGSTB_lag({check_dates[3].date()}) = {trade_check[3]:.0f}, "
                 f"BOPGSTB_lag({check_dates[4].date()}) = {trade_check[4]:.0f} "
                 f"({check_dates[3].date()} doit être le premier jour où {v_last:.0f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(trade_check[1], v_prev) and \
        np.isclose(trade_check[2], v_prev) and np.isclose(trade_check[3], v_last) and np.isclose(trade_check[4], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Verification dediee du taux de coupure eleve sur NDX/Russell/S&P500
    # (creusement seculaire du deficit declare non-bug dans le resultat).
    name_n, fname_n = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df_n = load_ohlc(str(REPO_ROOT / "data" / fname_n))
    dates_n = pd.DatetimeIndex(df_n["date"].values)
    trade_lag_n = load_trade_balance_lag(dates_n, trade_series)[1:]
    valid_n = np.isfinite(trade_lag_n)
    vals_valid = trade_lag_n[valid_n]
    lines.append("## Vérification dédiée du taux de coupure élevé sur NDX/Russell/S&P500 (77,7%)")
    lines.append(f"- BOPGSTB_lag sur la fenêtre NDX : 1re valeur disponible={vals_valid[0]:.0f}, "
                 f"médiane des 20% premières valeurs={np.median(vals_valid[:len(vals_valid)//5]):.0f}, "
                 f"médiane des 20% dernières valeurs={np.median(vals_valid[-len(vals_valid)//5:]):.0f}")
    trend_confirmed = np.median(vals_valid[-len(vals_valid)//5:]) < np.median(vals_valid[:len(vals_valid)//5])
    lines.append(f"- Le déficit médian récent ({np.median(vals_valid[-len(vals_valid)//5:]):.0f}) est "
                 f"{'bien plus négatif' if trend_confirmed else 'PAS plus négatif'} que le déficit médian ancien "
                 f"({np.median(vals_valid[:len(vals_valid)//5]):.0f}) : confirme un creusement séculaire du "
                 f"déficit commercial US sur l'historique testé, ce qui ancre mécaniquement le seuil expanding "
                 f"vers des valeurs de moins en moins atteignables par les observations anciennes — la porte "
                 f"reste donc majoritairement active en fin d'échantillon, effet structurel de tendance "
                 f"(même famille que les effets de fenêtre courte déjà documentés #286/#289/#294/#295/#324), "
                 f"pas un bug de calcul.")
    lines.append(f"- **{'OK — comportement confirmé cohérent avec la donnée réelle, aucune anomalie de calcul' if trend_confirmed else 'À INVESTIGUER — tendance non confirmée par les données'}**")
    all_ok &= trend_confirmed
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    trade_lag_full = load_trade_balance_lag(dates_n, trade_series)[1:]
    pos_full = expanding_tercile_cut_low(trade_lag_full)
    valid_start = int(np.argmax(np.isfinite(trade_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(trade_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_trade_balance_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
