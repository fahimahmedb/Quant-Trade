"""Backtest — Mécanisme hiérarchique gaté (#47) avec volatilité PRÉVUE
GJR-t (cycle #168), au lieu de la volatilité réalisée glissante du #47.

Spécification figée dans `PREREG_gjr_trend_gated_vol_managed.md`, committé
AVANT ce script. n_trials = 1. Réutilisation stricte (Règle 7) de :
- `near_high_mask()` / alignement causal `trend[:-1]` du #47
  (`nonml_trend_vol_targeting_overlay_backtest.py`).
- `walk_forward_vol_forecast()` du #165/#166 (déjà causalement alignée).

    position(t) = clip(20% / vol_prévue_GJR-t(t), 1.0, 2.0x)  si tendance haussière
                = 1.0x                                          sinon

Usage : python3 nonml_gjr_trend_gated_vol_managed_backtest.py
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
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_trend_vol_targeting_overlay_backtest import near_high_mask  # noqa: E402

T0 = 750
REFIT_EVERY = 21
TARGET_VOL_ANNUAL_PCT = 20.0
CAP = 2.0
FLOOR = 1.0
COST_BPS = 5.0

MARKETS = {
    "ndx": ("NDX (40 ans)", "nasdaq100_daily.txt"),
    "sp500": ("S&P 500", "sp500_daily.txt"),
    "russell2000": ("Russell 2000", "russell2000_daily.txt"),
    "dax": ("DAX", "dax_daily.txt"),
}


def build_positions(close: np.ndarray, r_pct: np.ndarray):
    """close : niveaux (longueur T). r_pct : rendements log % (longueur T-1,
    convention `log_returns_pct`, r_pct[k] = log(close[k+1]/close[k])*100)."""
    trend_full = near_high_mask(close)          # longueur T
    trend_r = trend_full[:-1]                    # aligné sur r_pct (longueur T-1)

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst = fc["vol_fcst"]                     # longueur T-1, déjà causal (t-1)

    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL_PCT / vol_fcst
    vt_exposure = np.clip(vt_exposure, FLOOR, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=FLOOR)

    pos = np.where(trend_r, vt_exposure, FLOOR)
    return pos, vol_fcst


def main():
    rows = []
    n_success = 0
    per_market = {}

    for key, (name, fname) in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        close = df["close"].values
        ser = log_returns_pct(df)
        r_pct = ser.values
        dates = ser.index

        pos_full, vol_fcst = build_positions(close, r_pct)

        r_t = r_pct[T0:] / 100.0
        pos = pos_full[T0:]
        dates_oos = dates[T0:]
        assert np.isfinite(pos).all()

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
        ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        both_ok = sharpe_ok and ret_ok
        n_success += int(both_ok)

        rows.append((name, len(r_t), me_bh, ret_bh, me_ov, ret_ov, pos, sharpe_ok, ret_ok, both_ok))
        per_market[key] = dict(pos=pos, r_asset=r_t, dates=pd.to_datetime(dates_oos).values,
                                cost_bps=COST_BPS, name=name)

    verdict = n_success >= 3

    lines = [
        "# Résultat — Mécanisme hiérarchique gaté (#47) avec volatilité PRÉVUE GJR-t (cycle #168)",
        "",
        "Spécification figée dans `PREREG_gjr_trend_gated_vol_managed.md` "
        "(committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t "
        "non validé dessus à l'Étape C).",
        "",
        f"`position(t) = clip({TARGET_VOL_ANNUAL_PCT:.0f}% / vol_prévue_GJR-t(t), {FLOOR}, {CAP}x)` "
        f"si tendance haussière (52w-high indice, seuil 95%), sinon {FLOOR}x. "
        f"T0={T0}, REFIT_EVERY={REFIT_EVERY}j, coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, n, me_bh, ret_bh, me_ov, ret_ov, pos, sharpe_ok, ret_ok, both_ok in rows:
        lines.append(
            f"| {name} | {n} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    lines += [
        "",
        f"**{n_success}/{len(MARKETS)} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
        f"(critère renforcé : ≥3/4, raisonnement au PREREG §4).**",
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

    out = ROOT / "results" / "nonml_gjr_trend_gated_vol_managed_result.md"
    out.write_text("\n".join(lines) + "\n")

    for key, d in per_market.items():
        np.savez(ROOT / "results" / f"nonml_gjr_trend_gated_vol_managed_{key}_pnl.npz",
                 pos=d["pos"], r_asset=d["r_asset"], dates=d["dates"], cost_bps=d["cost_bps"])

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict, rows


if __name__ == "__main__":
    main()
