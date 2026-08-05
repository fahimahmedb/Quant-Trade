"""Backtest — Overlay vol-targeting gaté par le ratio vol Parkinson / vol
close-to-close (spécification pré-enregistrée dans
PREREG_parkinson_c2c_ratio_vol_targeting_overlay.md, committée avant ce
script). Combine deux estimateurs déjà validés séparément (#46
close-to-close, #50 Parkinson) en un signal de régime nouveau, distinct
du #216 (gap brut, FAIL 2/5). n_trials=1, aucune dépendance ML. Règle de
succès renforcée.
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

from data_loader import load_ohlc, log_returns_pct, parkinson_var_pct, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
MEDIAN_WINDOW = 252
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def vol_c2c_ann_lagged(r_pct: np.ndarray) -> np.ndarray:
    """Vol close-to-close annualisee (%), fenetre VOL_WINDOW, decalee d'un
    jour (t-1) -- exactement le denominateur du mecanisme #46."""
    vol_ann = pd.Series(r_pct / 100.0).rolling(VOL_WINDOW).std().values * ANNUALIZATION * 100.0
    lagged = np.roll(vol_ann, 1)
    lagged[0] = np.nan
    return lagged


def vol_park_ann_lagged(rv_pct2: np.ndarray) -> np.ndarray:
    """Vol Parkinson annualisee (%), moyenne mobile VOL_WINDOW de la
    variance Parkinson, decalee d'un jour (t-1)."""
    rv_ann = pd.Series(rv_pct2).rolling(VOL_WINDOW).mean().values * (ANNUALIZATION ** 2)
    vol_ann = np.sqrt(np.maximum(rv_ann, 0.0))
    lagged = np.roll(vol_ann, 1)
    lagged[0] = np.nan
    return lagged


def calm_ratio_mask(r_pct: np.ndarray, rv_pct2: np.ndarray) -> np.ndarray:
    """Porte = ratio(vol Parkinson / vol close-to-close, t-1) >= sa
    mediane glissante MEDIAN_WINDOW jours (les deux jambes decalees du
    meme jour, donc le ratio est causal par construction)."""
    vc2c = vol_c2c_ann_lagged(r_pct)
    vpark = vol_park_ann_lagged(rv_pct2)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = vpark / vc2c
    med = pd.Series(ratio).rolling(MEDIAN_WINDOW).median().values
    gate = ratio >= med
    return np.nan_to_num(gate, nan=0.0).astype(bool)


def combined_position(r_pct: np.ndarray, gate: np.ndarray) -> np.ndarray:
    vol_lagged_frac = vol_c2c_ann_lagged(r_pct) / 100.0
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged_frac
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par le ratio vol Parkinson / vol close-to-close "
        "(pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_close-to-close_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si ratio(vol_Parkinson_{VOL_WINDOW}j / vol_close-to-close_{VOL_WINDOW}j)(t-1) est ≥ sa médiane "
        f"glissante {MEDIAN_WINDOW}j, sinon 1.0x. Échantillon testable à partir de la "
        f"{VOL_WINDOW + MEDIAN_WINDOW}e séance.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0
    start = VOL_WINDOW + MEDIAN_WINDOW

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r_pct = log_returns_pct(df).values
        rv_pct2 = parkinson_var_pct(df).values
        assert len(rv_pct2) == len(r_pct), f"Desalignement r/rv : {len(r_pct)} vs {len(rv_pct2)}"
        if len(r_pct) <= start:
            continue

        gate = calm_ratio_mask(r_pct, rv_pct2)
        pos_full = combined_position(r_pct, gate)
        r_t = r_pct[start:] / 100.0
        pos = pos_full[start:]

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

    out = ROOT / "results" / "nonml_parkinson_c2c_ratio_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
