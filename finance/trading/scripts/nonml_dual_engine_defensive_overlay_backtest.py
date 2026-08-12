"""Backtest — Overlay défensif combiné : moyenne simple des expositions
de #115 (vol réalisée 20j) et de l'overlay GJR-GARCH corrigé du #118,
deux estimateurs INDÉPENDANTS de la volatilité future de NDX
(spécification pré-enregistrée dans
PREREG_dual_engine_defensive_overlay.md, committée avant ce script).
n_trials=1 pour cette combinaison précise. Deux critères rapportés
(standard Sharpe+rendement, et Calmar) -- ni l'un ni l'autre n'est un
verdict final, voir Règle 9.
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


def main():
    d1 = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    d2 = np.load(ROOT / "results" / "nonml_etape_d_garch_defensive_overlay_pnl.npz", allow_pickle=True)

    dates1 = pd.to_datetime(d1["dates"])
    dates2 = pd.to_datetime(d2["dates"])
    s_pos1 = pd.Series(d1["pos"], index=dates1)
    s_r1 = pd.Series(d1["r_asset"], index=dates1)
    s_pos2 = pd.Series(d2["pos"], index=dates2)
    s_r2 = pd.Series(d2["r_asset"], index=dates2)

    common = dates1.intersection(dates2).sort_values()
    pos1 = s_pos1.reindex(common).values
    pos2 = s_pos2.reindex(common).values
    r1 = s_r1.reindex(common).values
    r2 = s_r2.reindex(common).values
    # les deux composants utilisent le meme actif sous-jacent (NDX log-retour) ;
    # verification de coherence (ecart residuel = arrondis differents des deux pipelines)
    max_r_diff = float(np.nanmax(np.abs(r1 - r2)))

    pos_combined = 0.5 * (pos1 + pos2)
    r = r1  # identique a r2 aux arrondis pres, verifie ci-dessus

    turn = np.abs(np.diff(pos_combined, prepend=1.0))
    pnl_ov = pos_combined * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
    calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
    verdict_calmar = calmar_ov > calmar_bh

    lines = [
        "# Résultat — Overlay défensif combiné (moyenne #115 + GJR-GARCH corrigé du #118) (pré-enregistré)",
        "",
        f"Position(t) = (Position_#115(t) + Position_GARCH(t)) / 2, fenêtre commune "
        f"{len(common)} séances ({common[0].date()} → {common[-1].date()}). Écart max "
        f"résiduel entre les deux séries de rendement NDX sous-jacentes (vérif. cohérence, "
        f"arrondis des deux pipelines) : {max_r_diff:.2e}.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **Overlay combiné (#115+GARCH)/2** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | **{calmar_ov:.3f}** |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Calmar overlay > BH : {'OUI' if verdict_calmar else 'non'}",
        "",
        f"**Critère standard (Sharpe ET rendement) : {'PASS' if verdict_standard else 'FAIL'}.**",
        f"**Critère Calmar : {'PASS' if verdict_calmar else 'FAIL'}.**",
    ]
    verdict_any = verdict_standard or verdict_calmar
    if verdict_any:
        lines.append("")
        lines.append("**PASS niveau 1 sur au moins un critère seulement -- pas un verdict final (Règle 9). "
                     "Doit encore passer `nonml_pass_validation_battery.py "
                     "dual_engine_defensive_overlay` (stress coûts/crise, stabilité temporelle, SPA, "
                     "DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_dual_engine_defensive_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict_any:
        np.savez(
            ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz",
            pos=pos_combined, r_asset=r, dates=common.values, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
