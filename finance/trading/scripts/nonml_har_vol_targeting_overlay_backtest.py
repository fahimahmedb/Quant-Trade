"""Backtest — Overlay de vol-targeting avec estimateur HAR-P (Corsi 2009,
Étape C) (spécification pré-enregistrée dans PREREG_har_vol_targeting_overlay.md,
committée avant ce script). Réutilise `volatility.py::fit_har`/`har_forecast`
(RV Parkinson rééchelonnée close-to-close, jamais exploité dans le backlog
non-ML) comme 8e estimateur de la lignée #46/#50/#215/#221/#222/#231/#233.
Wrapper walk-forward écrit pour ce cycle (aucun équivalent HAR dans
`overlay.py`), même convention de mise à jour des retards que
`run_etape_c.py` (Règle 7 : refit tous les REFIT_EVERY jours, prévision
recalculée à chaque pas avec les retards les plus récents disponibles,
sans réestimer les coefficients entre deux refits).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, parkinson_var_pct, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from volatility import ANNUALIZE, fit_har, har_forecast  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
TARGET_VOL_ANNUAL_PCT = 20.0
T0 = 750
REFIT_EVERY = 21

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def har_vol_forecast(r_pct: np.ndarray, rv_pct2: np.ndarray, t0: int, refit_every: int) -> np.ndarray:
    """Prevision HAR-P walk-forward de la vol annualisee (%, echelle
    close-to-close via c2c_scale de fit_har). NaN avant t0. Convention
    identique a run_etape_c.py : coefficients fixes par bloc de refit,
    prevision recalculee a chaque pas avec rv[:t] (info < t, causale)."""
    T = len(r_pct)
    vol_fcst = np.full(T, np.nan)
    for tr in range(t0, T, refit_every):
        block = range(tr, min(tr + refit_every, T))
        mod = fit_har(rv_pct2[:tr], r_pct[:tr])
        for t in block:
            hf = har_forecast(rv_pct2[:t], mod, 1)
            vol_fcst[t] = ANNUALIZE * np.sqrt(hf[0])
    return vol_fcst


def har_vol_position(df) -> np.ndarray:
    """Position clip(TARGET_VOL_ANNUAL_PCT / vol_prevue_HAR-P(t), 0, CAP),
    alignee sur r_pct = log_returns_pct(df) (longueur T-1)."""
    r_pct = log_returns_pct(df).values
    rv_pct2 = parkinson_var_pct(df).values
    assert len(rv_pct2) == len(r_pct), (
        f"Desalignement r/rv : {len(r_pct)} vs {len(rv_pct2)}")
    vol_fcst = har_vol_forecast(r_pct, rv_pct2, T0, REFIT_EVERY)
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL_PCT / vol_fcst
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = [
        "# Résultat — Overlay de vol-targeting estimateur HAR-P (Corsi 2009) "
        "(pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL_PCT:.0f}% / vol_prévue_HAR-P(t), 0.0, {CAP}x) "
        f"— HAR-P fit sur la RV Parkinson (retards j/5j/22j), rééchelonné en variance "
        f"close-to-close (`c2c_scale`), walk-forward T0={T0}, REFIT_EVERY={REFIT_EVERY}j "
        f"(réutilisé de l'Étape C, Règle 7). Échantillon testable à partir de la "
        f"{T0}e séance.",
        "",
        "| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r_pct = log_returns_pct(df).values
        if len(r_pct) <= T0 + REFIT_EVERY:
            continue

        pos_full = har_vol_position(df)
        r_t = r_pct[T0:] / 100.0
        pos = pos_full[T0:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(r_t)} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_har_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
