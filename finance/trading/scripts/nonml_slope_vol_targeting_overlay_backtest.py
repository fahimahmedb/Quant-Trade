"""Backtest — Overlay vol-targeting gaté par la pente de la SMA200
(spécification pré-enregistrée dans PREREG_slope_vol_targeting_overlay.md,
committée avant ce script). Combine les cycles #66 (porte) et #46/#47
(mécanisme vol-targeting). n_trials=1, aucune dépendance ML. Règle de
succès renforcée.
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
CAP = 2.0
SMA_WINDOW = 200
SLOPE_LAG = 20
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


def sma_slope_positive_mask(close: np.ndarray) -> np.ndarray:
    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    sma_lagged = np.roll(sma, SLOPE_LAG)
    sma_lagged[:SLOPE_LAG] = np.nan
    with np.errstate(invalid="ignore"):
        slope_up = sma > sma_lagged
    return np.nan_to_num(slope_up, nan=0.0).astype(bool)


def combined_position(close: np.ndarray, r: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (meme longueur que close[1:]).
    Renvoie la position pour chaque rendement de r : clip(vol_cible /
    vol_realisee(t-1), 1.0, CAP) si pente SMA200 positive, 1.0 sinon."""
    slope = sma_slope_positive_mask(close)  # aligne sur close (longueur T)
    # meme convention causale que #47/#67 : slope[i] connu a la cloture
    # du jour i (jour de decision) s'applique a r[i]=log(close[i+1]/close[i])
    # -> slope[:-1], PAS slope[1:] (fuite d'un jour)
    slope_r = slope[:-1]

    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(slope_r, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par la pente SMA200 (pré-enregistré, combinaison #66+#46)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si SMA{SMA_WINDOW}(t) > SMA{SMA_WINDOW}(t-{SLOPE_LAG}) (pente positive), sinon 1.0x. "
        f"Échantillon testable = à partir de la {SMA_WINDOW+SLOPE_LAG+1}e séance.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
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
        bh_full = np.log(close[1:] / close[:-1])

        pos_full = combined_position(close, bh_full)
        start = SMA_WINDOW + SLOPE_LAG
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

        gate_active = (pos > 1.0)
        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*gate_active.mean():.1f}% | {pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_slope_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
