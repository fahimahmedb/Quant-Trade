"""Backtest — Overlay de vol-targeting avec estimateur Parkinson
(spécification pré-enregistrée dans
PREREG_parkinson_vol_targeting_overlay.md, committée avant ce script).
Variante du #46 (écart-type close-to-close). n_trials=1, aucune
dépendance ML. Règle de succès renforcée.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report, parkinson_var_pct  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
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


def parkinson_vol_position(df) -> np.ndarray:
    """Renvoie la position continue clip(vol_cible / vol_parkinson(t-1),
    0, CAP), alignee sur les rendements clot-a-clot r = log(close[1:]/close[:-1])
    (meme longueur, meme convention causale que le #46)."""
    var_pct = parkinson_var_pct(df)  # index = df["date"].iloc[1:], longueur T-1, en %^2
    var_roll = var_pct.rolling(VOL_WINDOW).mean().values  # moyenne roulante causale, %^2
    vol_ann = np.sqrt(var_roll) * ANNUALIZATION / 100.0  # %->fraction, annualise
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay de vol-targeting estimateur Parkinson (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_Parkinson_{VOL_WINDOW}j(t-1), 0.0, {CAP}x) "
        f"— variante du #46 (écart-type close-to-close). Échantillon testable = à partir de la {VOL_WINDOW+1}e séance.",
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
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])  # longueur T-1, r[i] = close[i+1]/close[i]

        pos_full = parkinson_vol_position(df)  # longueur T-1, aligne sur bh_full
        start = VOL_WINDOW
        bh_t = bh_full[start:]
        pos = pos_full[start:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
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
            f"| {name} | {len(bh_t)} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
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

    out = ROOT / "results" / "nonml_parkinson_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
