"""Backtest — Règle de Sahm en temps réel (FRED SAHMREALTIME), overlay
défensif (spécification pré-enregistrée dans
PREREG_sahm_rule_overlay.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Réutilise CUT=0,5 et COST_BPS du #203 (M2 growth, Règle 7), décalage
de publication d'un mois réutilisé à l'identique du #324 (PAYEMS,
même rapport BLS mensuel sous-jacent). AUCUN tercile expanding ici :
seuil FIXE externe (Sahm 2019, 0,50 point de pourcentage), jamais
estimé sur les données de ce backlog (voir PREREG, section 4).
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
from nonml_m2_growth_overlay_backtest import COST_BPS, CUT, MARKETS  # noqa: E402

PUBLICATION_LAG_MONTHS = 1
SAHM_THRESHOLD = 0.50  # Sahm (2019), seuil fixe externe, non estime


def build_sahm_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "sahm_rule_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["SAHMREALTIME"] = pd.to_numeric(raw["SAHMREALTIME"], errors="coerce")
    raw = raw.dropna(subset=["SAHMREALTIME"]).drop_duplicates("observation_date").sort_values("observation_date")
    vals = raw["SAHMREALTIME"].astype(float).values
    obs_dates = raw["observation_date"].values

    available_dates = pd.DatetimeIndex(obs_dates) + pd.DateOffset(months=PUBLICATION_LAG_MONTHS)
    s = pd.Series(vals, index=available_dates)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_sahm_lag(dates: pd.DatetimeIndex, sahm_series: pd.Series) -> np.ndarray:
    y = sahm_series.reindex(dates, method="ffill")
    return y.shift(1).values


def fixed_threshold_gate(sahm_lag: np.ndarray) -> np.ndarray:
    """position(t) = CUT si sahm_lag(t) >= SAHM_THRESHOLD (seuil fixe
    externe, jamais estime sur ces donnees), 1.0x sinon."""
    T = len(sahm_lag)
    pos = np.full(T, np.nan)
    for t in range(T):
        if not np.isfinite(sahm_lag[t]):
            continue
        pos[t] = CUT if sahm_lag[t] >= SAHM_THRESHOLD else 1.0
    return pos


def main():
    sahm_series = build_sahm_series()

    lines = [
        "# Résultat — Règle de Sahm en temps réel (FRED SAHMREALTIME), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si SahmRule_lag(t) >= {SAHM_THRESHOLD} (seuil FIXE externe, Sahm 2019, "
        f"jamais estimé sur ces données), `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
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

        sahm_lag_full = load_sahm_lag(dates, sahm_series)
        sahm_lag = sahm_lag_full[1:]
        pos_full = fixed_threshold_gate(sahm_lag)

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
            np.savez(ROOT / "results" / "nonml_sahm_rule_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_sahm_rule_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
