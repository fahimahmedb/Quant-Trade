"""Backtest — Diversification obligataire (#134) sur DAX avec taux
allemand (spécification pré-enregistrée dans
PREREG_diversification_bond_overlay_dax.md, committée avant ce script).
LIMITE RECONNUE : taux allemand disponible seulement en fréquence
MENSUELLE (contrairement à DGS10 quotidien), forward-fillé -- résultat
moins probant qu'une vraie série quotidienne, interprété avec cette
réserve. n_trials=1, aucune dépendance ML. Règle de succès renforcée
niveau 1 -- SI PASS, résultat PAS final, voir Règle 9.
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
from nonml_defensive_calmar_vol_targeting_overlay_backtest import vol_target_position, VOL_WINDOW  # noqa: E402

COST_BPS = 5.0
MATURITY_YEARS = 10


def load_de10y_monthly() -> pd.Series:
    df = pd.read_csv(REPO_ROOT / "data" / "de10y_monthly.csv")
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["IRLTLT01DEM156N"] = pd.to_numeric(df["IRLTLT01DEM156N"], errors="coerce")
    s = pd.Series(df["IRLTLT01DEM156N"].values, index=df["observation_date"]).dropna()
    return s[~s.index.duplicated(keep="first")].sort_index()


def bund_return_proxy(yield_pct_daily_ffilled: pd.Series, maturity_years: int = MATURITY_YEARS) -> pd.Series:
    y = yield_pct_daily_ffilled.values / 100.0
    y_lag = np.roll(y, 1)
    y_lag[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        d_mac = (1 + y_lag) / y_lag * (1 - 1 / (1 + y_lag) ** maturity_years)
    d_mod = d_mac / (1 + y_lag)
    r_bund = y_lag / 252.0 - d_mod * (y - y_lag)
    return pd.Series(r_bund, index=yield_pct_daily_ffilled.index)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "dax_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_full = np.log(close[1:] / close[:-1])

    pos_eq_full = vol_target_position(r_full)

    de10y = load_de10y_monthly()
    de10y_daily = de10y.reindex(dates_full, method="ffill")
    r_bund_all = bund_return_proxy(de10y_daily)

    valid = r_bund_all.notna().values
    start = max(VOL_WINDOW, int(np.argmax(valid)) if valid.any() else len(valid))

    pos_eq = pos_eq_full[start:]
    r_dax = r_full[start:]
    r_bund = r_bund_all.values[start:]
    dates_used = dates_full.values[start:]

    r_combined = pos_eq * r_dax + (1.0 - pos_eq) * r_bund
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_dax.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_ok = calmar_ov > calmar_bh
    verdict = verdict_standard or calmar_ok

    lines = [
        "# Résultat — Diversification obligataire sur DAX, taux allemand (pré-enregistré, deux critères, LIMITE DONNÉES reconnue)",
        "",
        "**Limite reconnue** : taux allemand (FRED IRLTLT01DEM156N) disponible seulement en fréquence "
        "MENSUELLE, forward-fillé au calendrier DAX -- résultat moins probant qu'une vraie série "
        "quotidienne comme DGS10 (#134/#136). Interprété avec cette réserve, PASS ou FAIL.",
        "",
        f"{len(r_dax)} séances (fenêtre commune DAX ∩ taux allemand disponible).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (DAX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **Diversification obligataire (taux allemand)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | {calmar_ov:.3f} |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Critère standard (1 ET 2) : {'PASS' if verdict_standard else 'FAIL'}",
        f"4. Critère Calmar (overlay > BH) : {'PASS' if calmar_ok else 'FAIL'}",
        "",
        f"**{'PASS (niveau 1, au moins un critère)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9), ET fragilisé par la "
                     "limite de données mensuelle ci-dessus. Doit encore passer "
                     "`nonml_pass_validation_battery.py diversification_bond_overlay_dax`.**")

    out = ROOT / "results" / "nonml_diversification_bond_overlay_dax_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_diversification_bond_overlay_dax_pnl.npz",
            pos=pos_eq, r_asset=r_dax, r_alt=r_bund, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
