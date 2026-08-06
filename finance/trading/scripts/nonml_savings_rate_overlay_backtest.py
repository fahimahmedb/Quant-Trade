"""Backtest — Taux d'épargne des ménages US (FRED PSAVERT), overlay
défensif (spécification pré-enregistrée dans
PREREG_savings_rate_overlay.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, TERCILE_PCT, MARKETS et expanding_tercile_cut_high
(niveau brut, tercile le plus haut = défensif) directement du #291
(NFCI), Règle 7. Décalage de publication d'UN MOIS calendaire, même
convention que #195/#203/#323/#324.
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

PUBLICATION_LAG_MONTHS = 1  # rapport BEA "Personal Income and Outlays"


def build_savings_rate_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "savings_rate_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["PSAVERT"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["PSAVERT"].astype(float).values
    obs_dates = raw["observation_date"].values

    # Publication ~1 mois apres la fin du mois (rapport BEA "Personal
    # Income and Outlays"), meme convention conservatrice que le #203.
    available_dates = pd.DatetimeIndex(obs_dates) + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    s = pd.Series(vals, index=available_dates)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_savings_rate_lag(dates: pd.DatetimeIndex, savings_series: pd.Series) -> np.ndarray:
    y = savings_series.reindex(dates, method="ffill")
    return y.shift(1).values


def main():
    savings_series = build_savings_rate_series()

    lines = [
        "# Résultat — Taux d'épargne des ménages US (FRED PSAVERT), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si PSAVERT_lag(t-1) est dans son tercile expanding le plus HAUT "
        f"(taux d'épargne le plus élevé observé à ce jour = comportement de précaution), `1.0x` sinon. "
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

        savings_lag_full = load_savings_rate_lag(dates, savings_series)
        savings_lag = savings_lag_full[1:]
        pos_full = expanding_tercile_cut_high(savings_lag)

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
            np.savez(ROOT / "results" / "nonml_savings_rate_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_savings_rate_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
