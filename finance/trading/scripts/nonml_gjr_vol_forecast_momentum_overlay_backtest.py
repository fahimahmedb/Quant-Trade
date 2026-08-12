"""Backtest — Direction du changement de la prévision GJR-t, overlay binaire
(cycle #170). Spécification figée dans
`PREREG_gjr_vol_forecast_momentum_overlay.md`, committé AVANT ce script.
n_trials = 1.

    delta(t) = vol_prévue_GJR-t(t) - vol_prévue_GJR-t(t - LAG), LAG=21j
    position(t) = 2.0x  si delta(t) < 0 (décélération)
                = 1.0x  sinon

Réutilisation stricte (Règle 7) de `walk_forward_vol_forecast()` du
#165/#166/#168/#169 (déjà causalement alignée).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402

T0 = 750
REFIT_EVERY = 21
LAG = REFIT_EVERY
CAP = 2.0
FLOOR = 1.0
COST_BPS = 5.0

MARKETS = {
    "ndx": ("NDX (40 ans)", "nasdaq100_daily.txt"),
    "sp500": ("S&P 500", "sp500_daily.txt"),
    "russell2000": ("Russell 2000", "russell2000_daily.txt"),
    "dax": ("DAX", "dax_daily.txt"),
}


def momentum_position(vol_fcst: np.ndarray) -> np.ndarray:
    T = len(vol_fcst)
    pos = np.full(T, np.nan)
    for t in range(T0 + LAG, T):
        delta = vol_fcst[t] - vol_fcst[t - LAG]
        pos[t] = CAP if delta < 0 else FLOOR
    return pos


def main():
    rows = []
    n_success = 0
    per_market = {}

    for key, (name, fname) in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        ser = log_returns_pct(df)
        r_pct = ser.values
        dates = ser.index

        fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
        vol_fcst = fc["vol_fcst"]
        pos_full = momentum_position(vol_fcst)

        start = T0 + LAG
        r_t = r_pct[start:] / 100.0
        pos = pos_full[start:]
        dates_oos = dates[start:]
        assert np.isfinite(pos).all()

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
        ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
        ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        both_ok = sharpe_ok and ret_ok
        n_success += int(both_ok)

        frac_decel = float((pos > FLOOR).mean())
        rows.append((name, len(r_t), me_bh, ret_bh, me_ov, ret_ov, pos, frac_decel,
                     sharpe_ok, ret_ok))
        per_market[key] = dict(pos=pos, r_asset=r_t, dates=pd.to_datetime(dates_oos).values,
                                cost_bps=COST_BPS)

    verdict = n_success >= 3

    lines = [
        "# Résultat — Direction du changement de la prévision GJR-t, overlay binaire (cycle #170)",
        "",
        "Spécification figée dans `PREREG_gjr_vol_forecast_momentum_overlay.md` "
        "(committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t "
        "non validé dessus à l'Étape C).",
        "",
        f"`delta(t) = vol_prévue_GJR-t(t) - vol_prévue_GJR-t(t-{LAG})` ; "
        f"`position(t) = {CAP}x si delta(t) < 0, {FLOOR}x sinon`. "
        f"T0={T0}, REFIT_EVERY={REFIT_EVERY}j, coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | % temps en décélération (2.0x) | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, n, me_bh, ret_bh, me_ov, ret_ov, pos, frac_decel, sharpe_ok, ret_ok in rows:
        lines.append(
            f"| {name} | {n} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*frac_decel:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    lines += [
        "",
        f"**{n_success}/{len(MARKETS)} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
        f"(critère renforcé : ≥3/4).**",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    if verdict:
        lines += [
            "",
            "**PASS de niveau 1 seulement.** Engagement pré-enregistré (§5) : "
            "décomposition Règle 10 (financement DGS3MO réel) à exécuter avant "
            "toute communication comme edge authentique, sur chaque marché PASS.",
        ]

    out = ROOT / "results" / "nonml_gjr_vol_forecast_momentum_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    for key, d in per_market.items():
        np.savez(ROOT / "results" / f"nonml_gjr_vol_forecast_momentum_overlay_{key}_pnl.npz",
                 pos=d["pos"], r_asset=d["r_asset"], dates=d["dates"], cost_bps=d["cost_bps"])

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict, rows


if __name__ == "__main__":
    main()
