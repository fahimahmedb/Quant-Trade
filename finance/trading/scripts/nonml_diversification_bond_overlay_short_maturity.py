"""Extension de robustesse du #134 — proxys obligataires COURTS (3 mois,
1 an), vraies séries de taux (pas juste un paramètre de duration
appliqué à DGS10) (spécification pré-enregistrée dans
PREREG_diversification_bond_overlay_short_maturity.md, committée avant
ce script). PAS un nouveau candidat indépendant à sa propre Règle 9 --
extension de la grille de robustesse déjà prévue pour le #134. Cycle
#141, aucune dépendance ML.
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

from prediction import trading_metrics  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import bond_return_proxy  # noqa: E402

COST_BPS = 5.0


def load_short_rate(fname: str, col: str) -> pd.Series:
    df = pd.read_csv(REPO_ROOT / "data" / fname)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df[col] = pd.to_numeric(df[col], errors="coerce")
    s = pd.Series(df[col].values, index=df["observation_date"]).dropna()
    return s[~s.index.duplicated(keep="first")].sort_index()


def run_variant(label, rate_series, maturity_years, pos_eq_full, r_ndx_full, dates_full):
    r_bond_all = bond_return_proxy(rate_series, maturity_years=maturity_years)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
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
    ok_std = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
    ok_calmar = calmar_ov > calmar_bh
    return {
        "label": label, "n": len(r_ndx), "sharpe": me_ov["sharpe_ann"], "ret": ret_ov,
        "mdd": me_ov["max_drawdown_pct"], "calmar": calmar_ov, "sharpe_bh": me_bh["sharpe_ann"],
        "ret_bh": ret_bh, "mdd_bh": me_bh["max_drawdown_pct"], "calmar_bh": calmar_bh,
        "ok_std": ok_std, "ok_calmar": ok_calmar,
    }


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full = d["pos"], d["r_asset"]
    dates_full = pd.to_datetime(d["dates"])

    dgs3mo = load_short_rate("dgs3mo_daily.csv", "DGS3MO")
    dgs1 = load_short_rate("dgs1_daily.csv", "DGS1")

    results = [
        run_variant("3 mois (DGS3MO, duration~0.25an)", dgs3mo, 0.25, pos_eq_full, r_ndx_full, dates_full),
        run_variant("1 an (DGS1, duration~1an)", dgs1, 1.0, pos_eq_full, r_ndx_full, dates_full),
    ]

    lines = [
        "# Extension de robustesse — Diversification obligataire du #134, proxys COURTS (3 mois / 1 an)",
        "",
        "PAS un nouveau candidat indépendant (pas de batterie Règle 9 séparée) -- extension de la grille "
        "de robustesse de maturité déjà prévue pour le #134, avec de VRAIES séries de taux courts (pas "
        "juste un paramètre de duration appliqué à DGS10).",
        "",
        "| Proxy | Séances | Sharpe ann. | Rendement total | MDD | Calmar | vs Buy&Hold (Sharpe/rdt) | vs Buy&Hold (Calmar) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['label']} | {r['n']} | {r['sharpe']:+.2f} | {100*r['ret']:+.1f}% | {r['mdd']:.1f}% | "
            f"{r['calmar']:.3f} | {'PASS' if r['ok_std'] else 'FAIL'} | {'PASS' if r['ok_calmar'] else 'FAIL'} |"
        )
    lines.append(f"| Buy&Hold (référence, fenêtre 3 mois) | {results[0]['n']} | {results[0]['sharpe_bh']:+.2f} | "
                 f"{100*results[0]['ret_bh']:+.1f}% | {results[0]['mdd_bh']:.1f}% | {results[0]['calmar_bh']:.3f} | -- | -- |")
    lines.append(f"| Buy&Hold (référence, fenêtre 1 an) | {results[1]['n']} | {results[1]['sharpe_bh']:+.2f} | "
                 f"{100*results[1]['ret_bh']:+.1f}% | {results[1]['mdd_bh']:.1f}% | {results[1]['calmar_bh']:.3f} | -- | -- |")
    lines.append("")
    lines.append(
        "Rappel #134 (proxy DGS10, 10 ans, fenêtre plus longue car série DGS10 débute avant DGS3MO) : "
        "Sharpe +0,53→+0,77, MDD -82,9%→-50,9%."
    )
    lines.append("")

    both_pass = all(r["ok_std"] or r["ok_calmar"] for r in results)
    if both_pass:
        conclusion = (
            "les proxys courts PASSENT aussi (au moins un critère) -- le mécanisme reste robuste même "
            "en réduisant fortement la duration/le risque de taux, contredisant partiellement "
            "l'intuition d'une protection qui viendrait uniquement de l'effet-prix des obligations longues."
        )
    else:
        conclusion = (
            "au moins un proxy court FAIL -- la protection semble dépendre significativement de la "
            "duration/l'effet-prix, pas seulement du portage, cohérent avec l'intuition d'un effet "
            "flight-to-quality plus fort sur les obligations longues."
        )
    lines.append(f"**Conclusion** : {conclusion}")

    out = ROOT / "results" / "nonml_diversification_bond_overlay_short_maturity.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
