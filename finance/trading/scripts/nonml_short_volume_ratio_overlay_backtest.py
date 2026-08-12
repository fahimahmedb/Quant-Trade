"""Backtest — Ratio de volume vendu à découvert sur QQQ (FINRA Reg SHO,
ShortVolume/TotalVolume), overlay défensif (spécification
pré-enregistrée dans PREREG_short_volume_ratio_overlay.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, COST_BPS, MARKETS et expanding_tercile_cut_high
(tercile le plus HAUT = défensif) du #291 (NFCI, Règle 7). Décalage de
publication conservateur de 2 jours (FINRA publie le fichier "en date
du" jour J le lendemain matin au plus tard), Règle 7.
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
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, expanding_tercile_cut_high,
)

PUBLICATION_LAG_DAYS = 2


def build_short_vol_ratio_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "qqq_short_volume_daily.csv")
    raw["date"] = pd.to_datetime(raw["date"])
    raw["short_volume"] = pd.to_numeric(raw["short_volume"], errors="coerce")
    raw["total_volume"] = pd.to_numeric(raw["total_volume"], errors="coerce")
    raw = raw.dropna(subset=["short_volume", "total_volume"])
    raw = raw[raw["total_volume"] > 0]
    raw = raw.drop_duplicates("date").sort_values("date")

    ratio = raw["short_volume"] / raw["total_volume"]
    available_dates = raw["date"] + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    s = pd.Series(ratio.values, index=available_dates)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_short_vol_ratio_lag(dates: pd.DatetimeIndex, ratio_series: pd.Series) -> np.ndarray:
    y = ratio_series.reindex(dates, method="ffill")
    return y.shift(1).values


def main():
    ratio_series = build_short_vol_ratio_series()

    lines = [
        "# Résultat — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si ShortVolRatio_lag(t) (QQQ, ShortVolume/TotalVolume) est dans son "
        f"tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps. "
        f"Décalage de publication {PUBLICATION_LAG_DAYS}j + alignement causal quotidien standard.",
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

        ratio_lag_full = load_short_vol_ratio_lag(dates, ratio_series)
        ratio_lag = ratio_lag_full[1:]
        pos_full = expanding_tercile_cut_high(ratio_lag)

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
            np.savez(ROOT / "results" / "nonml_short_volume_ratio_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_short_volume_ratio_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
