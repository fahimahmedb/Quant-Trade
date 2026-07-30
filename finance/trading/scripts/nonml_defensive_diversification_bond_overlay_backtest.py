"""Backtest — Diversification défensive vers un proxy obligataire (au lieu
de cash) pour la fraction dé-risquée du mécanisme #115 (spécification
pré-enregistrée dans PREREG_defensive_diversification_bond_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée niveau 1 -- SI PASS, ce résultat n'est PAS final, voir
Règle 9 (`scripts/nonml_pass_validation_battery.py`).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
MATURITY_YEARS = 10


def load_dgs10() -> pd.Series:
    df = pd.read_csv(REPO_ROOT / "data" / "dgs10_daily.csv")
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["DGS10"] = pd.to_numeric(df["DGS10"], errors="coerce")  # "." (jours fériés) -> NaN
    s = pd.Series(df["DGS10"].values, index=df["observation_date"]).dropna()
    return s[~s.index.duplicated(keep="first")].sort_index()


def bond_return_proxy(yield_pct: pd.Series, maturity_years: int = MATURITY_YEARS) -> pd.Series:
    """Rendement quotidien approché d'une obligation au pair de maturité
    `maturity_years`, duration modifiee calculee en formule fermee a
    partir du taux lui-meme (aucun parametre libre)."""
    y = yield_pct.values / 100.0
    y_lag = np.roll(y, 1)
    y_lag[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        d_mac = (1 + y_lag) / y_lag * (1 - 1 / (1 + y_lag) ** maturity_years)
    d_mod = d_mac / (1 + y_lag)
    r_bond = y_lag / 252.0 - d_mod * (y - y_lag)
    return pd.Series(r_bond, index=yield_pct.index)


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full, cost_bps_src = d["pos"], d["r_asset"], float(d["cost_bps"])
    dates_full = pd.to_datetime(d["dates"])
    assert cost_bps_src == COST_BPS

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid)) if valid.any() else len(valid)

    pos_eq = pos_eq_full[start:]
    r_ndx = r_ndx_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full.values[start:]

    pos_bond = 1.0 - pos_eq
    r_combined = pos_eq * r_ndx + pos_bond * r_bond

    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_ok = calmar_ov > calmar_bh
    verdict = verdict_standard or calmar_ok

    lines = [
        "# Résultat — Diversification défensive vers un proxy obligataire, #115+DGS10 (pré-enregistré, deux critères)",
        "",
        f"Fraction dé-risquée de la position #115 (jamais >1.0x) allouée à un proxy obligataire "
        f"(duration modifiée, DGS10) au lieu du cash. {len(r_ndx)} séances "
        f"(fenêtre commune #115 ∩ DGS10, {pd.Timestamp(dates_used[0]).date()}→{pd.Timestamp(dates_used[-1]).date()}).",
        "",
        f"Position équity moyenne (#115, inchangée) : {pos_eq.mean():.2f}x — "
        f"position obligataire moyenne : {pos_bond.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **#115 + proxy obligataire (au lieu de cash)** | **{me_ov['sharpe_ann']:+.2f}** | "
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
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py defensive_diversification_bond_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_defensive_diversification_bond_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_defensive_diversification_bond_overlay_pnl.npz",
            pos=pos_eq, r_asset=r_ndx, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
