"""Décomposition portage vs effet-prix du gain du #134 (spécification
pré-enregistrée dans PREREG_diversification_bond_carry_price_decomposition.md,
committée avant ce script). PAS un nouveau candidat indépendant --
analyse du mécanisme déjà validé du #134. Cycle #142, aucune dépendance
ML.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10  # noqa: E402

COST_BPS = 5.0


def carry_only_proxy(yield_pct: pd.Series) -> pd.Series:
    """Portage seul : y_lag/252, SANS le terme d'effet-prix -D_mod*(y-y_lag)
    deja committe dans bond_return_proxy() du #134."""
    y = yield_pct.values / 100.0
    y_lag = np.roll(y, 1)
    y_lag[0] = np.nan
    r_carry = y_lag / 252.0
    return pd.Series(r_carry, index=yield_pct.index)


def run(pos_eq_full, r_ndx_full, dates_full, r_bond_aligned):
    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid)) if valid.any() else len(valid)
    pos_eq = pos_eq_full[start:]
    r_ndx = r_ndx_full[start:]
    r_bond = r_bond_aligned.values[start:]

    r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
    ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    return me_ov, ret_ov, calmar_ov, me_bh, ret_bh, calmar_bh, len(r_ndx)


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_diversification_bond_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full = d["pos"], d["r_asset"]
    dates_full = pd.to_datetime(d["dates"])

    dgs10 = load_dgs10()
    r_carry_all = carry_only_proxy(dgs10)
    r_carry_aligned = r_carry_all.reindex(dates_full, method="ffill")

    me_carry, ret_carry, calmar_carry, me_bh, ret_bh, calmar_bh, n = run(
        pos_eq_full, r_ndx_full, dates_full, r_carry_aligned
    )

    lines = [
        "# Décomposition portage vs effet-prix du gain du #134 (cycle #142, analyse -- pas un nouveau candidat)",
        "",
        f"{n} séances (fenêtre identique au #134, NDX ∩ DGS10).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **#134 complet (portage + effet-prix, déjà committé)** | **+0,77** | **+14405,6%** | -50,9% | -- |",
        f"| **Portage SEUL (sans effet-prix)** | **{me_carry['sharpe_ann']:+.2f}** | "
        f"**{100*ret_carry:+.1f}%** | {me_carry['max_drawdown_pct']:.1f}% | {calmar_carry:.3f} |",
        "",
    ]

    sharpe_gap_total = 0.77 - me_bh["sharpe_ann"]
    sharpe_gap_carry = me_carry["sharpe_ann"] - me_bh["sharpe_ann"]
    frac_explained = 100 * sharpe_gap_carry / sharpe_gap_total if sharpe_gap_total != 0 else float("nan")

    mdd_gap_total = me_bh["max_drawdown_pct"] - (-50.9)
    mdd_gap_carry = me_bh["max_drawdown_pct"] - me_carry["max_drawdown_pct"]
    frac_mdd_explained = 100 * mdd_gap_carry / mdd_gap_total if mdd_gap_total != 0 else float("nan")

    lines.append(f"Part du gain de Sharpe (#134 complet vs BH) expliquée par le portage seul : {frac_explained:.0f}%")
    lines.append(f"Part de la réduction de MDD (#134 complet vs BH) expliquée par le portage seul : {frac_mdd_explained:.0f}%")
    lines.append("")

    if frac_explained > 70 and frac_mdd_explained > 70:
        conclusion = (
            "**Hypothèse CONFIRMÉE nettement : le portage seul explique l'essentiel du gain** "
            "(>70% sur les deux métriques). L'effet-prix (flight-to-quality) n'apporte qu'une "
            "contribution marginale. Cohérent avec le #141 (le proxy 3 mois, quasi sans effet-prix, "
            "obtenait un résultat presque identique au proxy 10 ans)."
        )
    elif frac_explained > 50 or frac_mdd_explained > 50:
        conclusion = (
            "**Hypothèse PARTIELLEMENT confirmée : le portage explique une majorité mais pas la "
            "totalité du gain.** L'effet-prix apporte une contribution non négligeable, notamment "
            "sur la métrique où sa part est la plus faible."
        )
    else:
        conclusion = (
            "**Hypothèse RÉFUTÉE : l'effet-prix (flight-to-quality) explique la majorité du gain**, "
            "contrairement à l'intuition suggérée par le #141."
        )
    lines.append(conclusion)
    lines.append("")
    lines.append(
        "Nuance méthodologique : cette décomposition compare le portage SEUL (0% d'effet-prix) au "
        "#134 complet, PAS au proxy 3 mois du #141 (qui a une duration faible mais non nulle, "
        "~0,25 an) -- les deux résultats sont cohérents mais mesurent des choses légèrement "
        "différentes. Ne change AUCUN verdict Règle 9 déjà rendu."
    )

    out = ROOT / "results" / "nonml_diversification_bond_carry_price_decomposition.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
