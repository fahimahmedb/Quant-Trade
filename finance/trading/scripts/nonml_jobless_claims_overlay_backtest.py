"""Backtest — Demandes initiales d'allocations chômage (ICSA), overlay
défensif (spécification pré-enregistrée dans
PREREG_jobless_claims_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5
marchés (≥4/5).

Réutilise CUT=0,5 et la technique de tercile expanding déjà établie aux
#169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202/#203,
et le principe de décalage causal de publication déjà validé aux
#195/#203 (adapté ici à un délai de 7 jours pour une série
hebdomadaire), Règle 7.
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
CUT = 0.5
TERCILE_PCT = 100.0 / 3.0
MA_WEEKS = 4
YOY_WEEKS = 52
PUBLICATION_LAG_DAYS = 7

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def build_claims_yoy_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "icsa_weekly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["ICSA"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["ICSA"].astype(float).values
    obs_dates = raw["observation_date"].values

    ma4 = pd.Series(vals).rolling(MA_WEEKS).mean().values
    yoy = np.full(len(ma4), np.nan)
    yoy[YOY_WEEKS:] = np.log(ma4[YOY_WEEKS:] / ma4[:-YOY_WEEKS])

    # Convention de publication : la semaine se terminant le samedi
    # "obs_dates[i]" n'est publiee que le jeudi SUIVANT (~5j) -- decalage
    # conservateur de 7j calendaires (PREREG S2).
    available_dates = pd.DatetimeIndex(obs_dates) + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    s = pd.Series(yoy, index=available_dates).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_claims_yoy_lag(dates: pd.DatetimeIndex, claims_series: pd.Series) -> np.ndarray:
    y = claims_series.reindex(dates, method="ffill")
    return y.shift(1).values


def expanding_tercile_cut_high(claims_yoy: np.ndarray) -> np.ndarray:
    T = len(claims_yoy)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(claims_yoy)))
    for t in range(start, T):
        if not np.isfinite(claims_yoy[t]):
            continue
        hist = claims_yoy[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = CUT if claims_yoy[t] >= thresh else 1.0
    return pos


def main():
    claims_series = build_claims_yoy_series()

    lines = [
        "# Résultat — Demandes initiales d'allocations chômage (ICSA), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si ClaimsYoY(t)=log(MA4(t)/MA4(t-52)) est dans son tercile "
        f"expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        claims_lag_full = load_claims_yoy_lag(dates, claims_series)
        claims_lag = claims_lag_full[1:]
        pos_full = expanding_tercile_cut_high(claims_lag)

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

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_jobless_claims_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
