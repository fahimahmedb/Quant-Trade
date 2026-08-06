"""Backtest — Volume RELATIF de l'indice (ratio au volume moyen
glissant 252j) comme porte défensive (spécification pré-enregistrée
dans PREREG_relative_index_volume_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès sur 4
marchés (≥3/4) — Composite exclu, volume=0 documenté.

Réutilisation STRICTE de load_volume (#308) et
expanding_tercile_gate_high (#296), Règle 7. Corrige la non-
stationnarité identifiée au #308 par normalisation au volume moyen
glissant.
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
from prediction import trading_metrics  # noqa: E402
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    expanding_tercile_gate_high,
)
from nonml_index_volume_overlay_backtest import MARKETS, load_volume  # noqa: E402

COST_BPS = 5.0
CUT = 0.5
MA_WINDOW = 252


def volume_ratio(vol: pd.Series) -> pd.Series:
    ma = vol.rolling(MA_WINDOW).mean()
    return vol / ma


def main():
    lines = [
        "# Résultat — Volume RELATIF de l'indice (ratio à MA252) comme porte défensive (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si VolRatio(t-1) = Vol(t-1)/MA_252(Vol)(t-1) est dans son "
        f"tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps. "
        "Composite EXCLU (volume=0 documenté). Critère ajusté à ≥3/4 marchés.",
        "",
        "| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
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
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        vol_series = load_volume(str(path))
        ratio_series = volume_ratio(vol_series)
        ratio_aligned = ratio_series.reindex(dates).values
        ratio_shifted = pd.Series(ratio_aligned).shift(1).values  # decalage causal reel
        ratio_lag = ratio_shifted[1:]  # ratio_lag[k] = ratio_aligned[k] = connu a la cloture de t

        gate = expanding_tercile_gate_high(ratio_lag)
        valid = np.isfinite(ratio_lag)
        start = int(np.argmax(valid))
        gate_t = gate[start:]
        valid_t = valid[start:]
        bh_t = bh_full[start:]
        assert valid_t.all(), "le ratio de volume doit etre valide sur toute la fenetre testable"

        pos = np.where(gate_t, CUT, 1.0)
        frac_cut = float(gate_t.mean())

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
            f"| {name} | {len(bh_t)} | {100*frac_cut:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_relative_index_volume_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 3
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère ajusté : ≥3/4, Composite exclu — volume=0).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_relative_index_volume_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
