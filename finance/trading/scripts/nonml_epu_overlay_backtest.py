"""Backtest — Indice d'incertitude de politique économique US (FRED
USEPUINDXD), overlay défensif (spécification pré-enregistrée dans
PREREG_epu_overlay.md, committée avant ce script). n_trials=1, aucune
dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5, TERCILE_PCT, MARKETS et expanding_tercile_cut_high
(niveau brut, tercile le plus haut = défensif) directement du #291
(NFCI), Règle 7. Alignement causal quotidien sans décalage calendaire
additionnel (reindex+ffill+shift(1)), convention déjà utilisée pour
les séries quotidiennes disponibles en temps quasi réel (VIX #130,
pétrole #283, cuivre #284, dollar #198).
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


def build_epu_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "epu_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")["USEPUINDXD"].astype(float).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_epu_lag(dates: pd.DatetimeIndex, epu_series: pd.Series) -> np.ndarray:
    y = epu_series.reindex(dates, method="ffill")
    return y.shift(1).values


def main():
    epu_series = build_epu_series()

    lines = [
        "# Résultat — Indice d'incertitude de politique économique US (FRED USEPUINDXD), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si EPU_lag(t-1) est dans son tercile expanding le plus HAUT "
        f"(incertitude de politique économique la plus élevée observée à ce jour), `1.0x` sinon. "
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

        epu_lag_full = load_epu_lag(dates, epu_series)
        epu_lag = epu_lag_full[1:]
        pos_full = expanding_tercile_cut_high(epu_lag)

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
            np.savez(ROOT / "results" / "nonml_epu_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_epu_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
