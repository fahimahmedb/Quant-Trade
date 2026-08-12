"""Backtest — Bilan de la Réserve fédérale (FRED WALCL, croissance
glissante 52 semaines), overlay défensif (spécification pré-enregistrée
dans PREREG_fed_balance_sheet_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5
marchés (≥4/5).

Réutilise CUT=0,5, TERCILE_PCT et expanding_tercile_cut_low (tercile
le plus BAS = défensif) du #203 (M2 growth, Règle 7, direction
identique), décalage de publication de 7 jours réutilisé du #204/#291
(rapport hebdomadaire de la Fed, même convention).
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

YOY_WEEKS = 52
PUBLICATION_LAG_DAYS = 7


def build_walcl_growth_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "fed_balance_sheet_weekly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["WALCL"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["WALCL"].astype(float).values
    obs_dates = raw["observation_date"].values

    growth = np.full(len(vals), np.nan)
    growth[YOY_WEEKS:] = np.log(vals[YOY_WEEKS:] / vals[:-YOY_WEEKS])

    # Publication ~7 jours apres la date de reference (rapport H.4.1),
    # meme convention que l'ICSA #204 / NFCI #291.
    available_dates = pd.DatetimeIndex(obs_dates) + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    s = pd.Series(growth, index=available_dates).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_walcl_growth_lag(dates: pd.DatetimeIndex, walcl_series: pd.Series) -> np.ndarray:
    y = walcl_series.reindex(dates, method="ffill")
    return y.shift(1).values


def main():
    walcl_series = build_walcl_growth_series()

    lines = [
        "# Résultat — Bilan de la Réserve fédérale (WALCL, croissance 52 semaines), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si WALCLGrowth_lag(t)=log(WALCL(t)/WALCL(t-{YOY_WEEKS})) est dans son tercile "
        f"expanding le plus BAS (contraction du bilan la plus marquée, régime QT actif), `1.0x` sinon. "
        f"Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        walcl_lag_full = load_walcl_growth_lag(dates, walcl_series)
        walcl_lag = walcl_lag_full[1:]
        pos_full = expanding_tercile_cut_low(walcl_lag)

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
            np.savez(ROOT / "results" / "nonml_fed_balance_sheet_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_fed_balance_sheet_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
