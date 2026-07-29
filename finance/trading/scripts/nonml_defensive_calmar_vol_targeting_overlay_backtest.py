"""Backtest — Vol-targeting DÉFENSIF (jamais de levier), critère de
succès Calmar (rendement annualisé/|MDD|), pas Sharpe+rendement
(spécification pré-enregistrée dans
PREREG_defensive_calmar_vol_targeting_overlay.md, committée avant ce
script). n_trials=1 pour ce critère Calmar. Mécanisme identique au #44
(TARGET_VOL_ANNUAL=20% au lieu de 15%, cf. précédent #46).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 1.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def vol_target_position(r: np.ndarray) -> np.ndarray:
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Vol-targeting défensif, critère Calmar (pré-enregistré, critère DÉLIBÉRÉMENT différent de la règle renforcée standard)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 0.0, {CAP}x) "
        f"— jamais de levier. Critère : Calmar overlay > Calmar BH sur ≥4/5 marchés (PAS "
        f"Sharpe+rendement).",
        "",
        "| Marché | BH Calmar | BH Sharpe | BH Rdt total | BH MDD | Overlay Calmar | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Calmar>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0
    best_pos, best_r, best_start = None, None, None
    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])

        pos_full = vol_target_position(r)
        start = VOL_WINDOW
        r_t = r[start:]
        pos = pos_full[start:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
        calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
        ok = calmar_ov > calmar_bh
        n_markets += 1
        n_success += int(ok)

        lines.append(
            f"| {name} | {calmar_bh:.3f} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | **{calmar_ov:.3f}** | {me_ov['sharpe_ann']:+.2f} | "
            f"{100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | {'OUI' if ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            best_pos, best_r, best_start = pos, r_t, start

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés avec Calmar overlay > Calmar BH.**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} (critère Calmar ≥4/5) — "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 (critère Calmar) seulement -- pas un verdict final. La batterie "
                     "Règle 9 (`nonml_pass_validation_battery.py "
                     "defensive_calmar_vol_targeting_overlay`) sera exécutée à titre informatif, mais "
                     "ses contrôles (a) coûts et (c) stabilité sont bâtis sur le critère Sharpe/rendement "
                     "standard, PAS Calmar -- un échec de ces contrôles précis ne contredit pas "
                     "nécessairement ce succès Calmar (voir PREREG).**")

    out = ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict and best_pos is not None:
        df = load_ohlc(str(REPO_ROOT / "data" / MARKETS["NDX (40 ans)"]))
        dates_idx = pd.to_datetime(df["date"])
        dates_used = dates_idx.values[1:][best_start:]
        np.savez(
            ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz",
            pos=best_pos, r_asset=best_r, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
