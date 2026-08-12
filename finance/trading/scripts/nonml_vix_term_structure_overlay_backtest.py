"""Backtest — Structure par terme du VIX (VXV 3-mois − VIX 30j), overlay
défensif (spécification pré-enregistrée dans
PREREG_vix_term_structure_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5
marchés (≥4/5).

Réutilise CUT=0,5, TERCILE_PCT et expanding_tercile_cut_low (tercile le
plus BAS = backwardation la plus prononcée = défensif) du #203 (M2
growth, Règle 7), l'alignement causal ffill+shift(1) déjà validé aux
#130/#191 pour le VIX.
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
from nonml_m2_growth_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, expanding_tercile_cut_low,
)


def _load_series_lag(dates: pd.DatetimeIndex, fname: str, col: str) -> np.ndarray:
    raw = pd.read_csv(REPO_ROOT / "data" / fname)
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")[col]
    s = pd.to_numeric(s, errors="coerce").dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    y = s.reindex(dates, method="ffill")
    return y.shift(1).values


def load_vix_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    return _load_series_lag(dates, "vixcls_daily.csv", "VIXCLS")


def load_vxv_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    return _load_series_lag(dates, "vxvcls_daily.csv", "VXVCLS")


def main():
    lines = [
        "# Résultat — Structure par terme du VIX (VXV 3-mois − VIX 30j), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si Slope_lag(t)=VXV_lag(t)-VIX_lag(t) est dans son tercile "
        f"expanding le plus BAS (backwardation la plus prononcée), `1.0x` sinon. Design purement défensif. "
        f"Coûts {COST_BPS:.0f} bps.",
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

        vix_lag_full = load_vix_lag(dates)
        vxv_lag_full = load_vxv_lag(dates)
        slope_full = vxv_lag_full - vix_lag_full
        slope = slope_full[1:]
        pos_full = expanding_tercile_cut_low(slope)

        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:]
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)
        assert np.isfinite(pos).all()

        frac_cut = float((pos == CUT).mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

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
            np.savez(ROOT / "results" / "nonml_vix_term_structure_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_vix_term_structure_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
