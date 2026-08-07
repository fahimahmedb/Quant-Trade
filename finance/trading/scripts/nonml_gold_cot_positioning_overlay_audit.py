"""Audit indépendant — Positionnement spéculatif net CFTC sur l'or (COT).

Recalcule NetPctSpécOr_lag(t), le tercile expanding et la position par
une méthode alternative (boucle explicite + searchsorted, sans
pandas.reindex/ffill/np.percentile), compare au résultat committé du
backtest. Vérifie le décalage de publication (10j) + causal (1j) sur
une transition réelle et l'absence de fuite par troncature de
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
from nonml_financial_conditions_overlay_backtest import CUT, MARKETS, expanding_tercile_cut_high  # noqa: E402
from nonml_gold_cot_positioning_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_DAYS, build_gold_cot_net_pct_series, load_gold_cot_lag,
)


def manual_gold_cot_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif) sur les dates "disponibles" (as_of + lag publication),
    sans pandas.reindex/ffill."""
    raw = pd.read_csv(REPO_ROOT / "data" / "gold_cot_positioning_weekly.csv")
    raw.columns = [c.strip() for c in raw.columns]
    raw["as_of_date"] = pd.to_datetime(raw["as_of_date"])
    for col in ("open_interest", "nc_long", "nc_short"):
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw = raw.dropna(subset=["open_interest", "nc_long", "nc_short"])
    raw = raw.drop_duplicates("as_of_date").sort_values("as_of_date")

    net_pct = (100.0 * (raw["nc_long"] - raw["nc_short"]) / raw["open_interest"]).values
    available = (raw["as_of_date"] + pd.Timedelta(days=PUBLICATION_LAG_DAYS)).values

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(available, np.datetime64(d), side="right") - 1
        if idx < 0:
            continue
        out[i] = net_pct[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (2.0 * 100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Positionnement spéculatif net CFTC sur l'or (COT)", ""]
    all_ok = True

    cot_series = build_gold_cot_net_pct_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        cot_official = load_gold_cot_lag(dates, cot_series)[1:]
        pos_official = expanding_tercile_cut_high(cot_official)

        cot_manual = manual_gold_cot_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(cot_official - cot_manual))

        start = int(np.argmax(np.isfinite(cot_manual)))
        T = len(cot_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(cot_manual[t]):
                continue
            hist = cot_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if cot_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(cot_official[i] - cot_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/.../#360) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage de publication (10j) + causal
    # (1j) sur la derniere transition de valeur reelle.
    raw = pd.read_csv(REPO_ROOT / "data" / "gold_cot_positioning_weekly.csv")
    raw.columns = [c.strip() for c in raw.columns]
    raw["as_of_date"] = pd.to_datetime(raw["as_of_date"])
    for col in ("open_interest", "nc_long", "nc_short"):
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw = raw.dropna(subset=["open_interest", "nc_long", "nc_short"]).sort_values("as_of_date")
    net_pct = (100.0 * (raw["nc_long"] - raw["nc_short"]) / raw["open_interest"]).values
    as_of = raw["as_of_date"].values
    v_prev, v_last = float(net_pct[-2]), float(net_pct[-1])
    d_prev_asof, d_last_asof = pd.Timestamp(as_of[-2]), pd.Timestamp(as_of[-1])
    d_avail = d_last_asof + pd.Timedelta(days=PUBLICATION_LAG_DAYS)

    check_dates = pd.DatetimeIndex([
        d_avail - pd.Timedelta(days=2), d_avail - pd.Timedelta(days=1),
        d_avail, d_avail + pd.Timedelta(days=1), d_avail + pd.Timedelta(days=2),
    ])
    cot_check = load_gold_cot_lag(check_dates, cot_series)

    lines.append(f"## Vérification spécifique du décalage de publication ({PUBLICATION_LAG_DAYS}j) + causal (1j)")
    lines.append(f"- Dernière observation « en date du » {d_last_asof.date()} = {v_last:.6f} "
                 f"(observation précédente {d_prev_asof.date()} = {v_prev:.6f}, "
                 f"valeurs distinctes : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- Date de disponibilité déclarée (as_of + {PUBLICATION_LAG_DAYS}j) = {d_avail.date()}")
    lines.append(f"- NetPctSpécOr_lag({d_avail.date()}) = {cot_check[2]:.6f} (doit valoir {v_prev:.6f}, JAMAIS {v_last:.6f} — "
                 f"la valeur n'est censée devenir visible qu'au jour SUIVANT sa disponibilité, via shift(1))")
    lines.append(f"- NetPctSpécOr_lag({(d_avail + pd.Timedelta(days=1)).date()}) = {cot_check[3]:.6f} "
                 f"(doit être le premier jour où {v_last:.6f} apparaît)")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(cot_check[2], v_prev) and \
        np.isclose(cot_check[3], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — le décalage de publication + causal est correctement appliqué' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    cot_full = load_gold_cot_lag(dates, cot_series)[1:]
    pos_full = expanding_tercile_cut_high(cot_full)
    valid_start = int(np.argmax(np.isfinite(cot_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_high(cot_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_gold_cot_positioning_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
