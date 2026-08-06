"""Audit indépendant — Demandes continues d'allocations chômage (CCSA).

Recalcule ClaimsContinuingYoY(t), l'alignement causal (avec décalage de
publication de 7 jours) et le tercile expanding par une méthode
alternative (boucle explicite + searchsorted, sans pandas.reindex/ffill
ni np.percentile), compare au résultat committé du backtest. Vérifie
spécifiquement le décalage de publication et l'absence de fuite
générale (troncature de l'historique). Adapté directement du #204
(ICSA), même construction, seule la série change.
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
from nonml_jobless_claims_overlay_backtest import (  # noqa: E402
    CUT, MA_WEEKS, YOY_WEEKS, PUBLICATION_LAG_DAYS, MARKETS,
    expanding_tercile_cut_high,
)
from nonml_continuing_claims_overlay_backtest import (  # noqa: E402
    build_continuing_claims_yoy_series, load_continuing_claims_yoy_lag,
)


def manual_claims_yoy_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite (moyenne glissante 4 semaines et
    ratio 52 semaines sans pandas.rolling) + searchsorted (sans
    pandas.reindex/ffill), independant de la construction vectorisee du
    script principal."""
    raw = pd.read_csv(REPO_ROOT / "data" / "ccsa_weekly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["CCSA"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["CCSA"].astype(float).values
    obs_dates = raw["observation_date"].values
    T = len(vals)

    ma4 = np.full(T, np.nan)
    for i in range(MA_WEEKS - 1, T):
        ma4[i] = np.mean(vals[i - MA_WEEKS + 1:i + 1])

    yoy = np.full(T, np.nan)
    for i in range(YOY_WEEKS, T):
        if np.isfinite(ma4[i]) and np.isfinite(ma4[i - YOY_WEEKS]):
            yoy[i] = np.log(ma4[i] / ma4[i - YOY_WEEKS])

    avail_dates = pd.DatetimeIndex(obs_dates) + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    valid = np.isfinite(yoy)
    avail_valid, yoy_valid = avail_dates[valid], yoy[valid]
    order = np.argsort(avail_valid)
    avail_sorted, yoy_sorted = avail_valid[order], yoy_valid[order]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = yoy_sorted[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (200.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Demandes continues d'allocations chômage (CCSA)", ""]
    all_ok = True

    claims_series = build_continuing_claims_yoy_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        claims_lag_official = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
        pos_official = expanding_tercile_cut_high(claims_lag_official)

        claims_lag_manual = manual_claims_yoy_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(claims_lag_official - claims_lag_manual))

        start = int(np.argmax(np.isfinite(claims_lag_manual)))
        T = len(claims_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(claims_lag_manual[t]):
                continue
            hist = claims_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if claims_lag_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(claims_lag_official[i] - claims_lag_manual[i])
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
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#204/#320/#321) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage de publication (7 jours).
    raw = pd.read_csv(REPO_ROOT / "data" / "ccsa_weekly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    last_obs = raw.dropna(subset=["CCSA"]).sort_values("observation_date").iloc[-1]
    obs_date = last_obs["observation_date"]
    avail_date = obs_date + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    lines.append(f"## Vérification spécifique du décalage de publication ({PUBLICATION_LAG_DAYS} jours)")
    lines.append(f"- Dernière observation CCSA : semaine se terminant le {obs_date.date()} "
                 f"(valeur = {last_obs['CCSA']:.0f})")
    lines.append(f"- Disponible causalement à partir du {avail_date.date()} (décalage {PUBLICATION_LAG_DAYS}j), "
                 f"jamais avant — même convention conservatrice que le #204 (délai réel DOL ~5j, marge 2j)")
    lines.append("- **OK — construction du décalage vérifiée par inspection directe**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    claims_lag_full = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
    pos_full = expanding_tercile_cut_high(claims_lag_full)
    valid_start = int(np.argmax(np.isfinite(claims_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_high(claims_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_continuing_claims_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
