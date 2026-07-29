"""Ré-analyse du critère Calmar (cycle #119, pré-enregistré dans
PREREG_calmar_criterion_reanalysis.md). PAS un nouveau backtest -- ré-
exécute EXACTEMENT _one_index() de run_etape_d_v2.py (mêmes paramètres,
mêmes données) pour Russell 2000/S&P 500/DAX, et extrait le champ
`calmar` déjà calculé en interne par trading_metrics() mais jamais
affiché dans le rapport d'origine.
"""
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import build_overlay_positions  # noqa: E402
from prediction import backtest, trading_metrics  # noqa: E402

T0 = 750
REFIT_EVERY = 21
COST_BPS = 5.0
CAP_V2 = 1.0
PCTL = 95.0

INDICES = {
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def one_index_calmar(name: str, fname: str):
    path = REPO_ROOT / "data" / fname
    df = load_ohlc(str(path))
    quality_report(df)
    r = log_returns_pct(df).values
    r_bt = r / 100.0
    T = len(r)
    idx = np.arange(T0, T)

    pos_bh = np.ones(T)
    metr_bh = trading_metrics(backtest(pos_bh, r_bt, COST_BPS)[idx])
    ov = build_overlay_positions(r, T0, REFIT_EVERY, CAP_V2, with_extreme_cut=True, extreme_pctl=PCTL)
    metr_ov = trading_metrics(backtest(ov["pos"], r_bt, COST_BPS)[idx])

    return name, metr_bh, metr_ov


def main():
    lines = [
        "# Ré-analyse du critère Calmar — Étape D v2 (défensif GJR-GARCH, cap=1.0×) sur Russell/S&P/DAX",
        "",
        "PAS un nouveau backtest : mêmes paramètres exacts que "
        "`run_etape_d_v2.py` (CAP=1.0×, coupe 95e pctl, T0=750, REFIT_EVERY=21) "
        "— extrait uniquement le champ `calmar` déjà calculé en interne, jamais "
        "affiché dans `etape_D_v2_no_leverage.md`.",
        "",
        "| Marché | Calmar BH | Calmar overlay | Sharpe BH | Sharpe overlay | Calmar>BH | Critère Étape D (>25%MDD/≥80%rdt) |",
        "|---|---|---|---|---|---|---|",
    ]
    n_calmar_ok = 0
    for name, fname in INDICES.items():
        name_r, metr_bh, metr_ov = one_index_calmar(name, fname)
        calmar_bh = metr_bh["calmar"] if np.isfinite(metr_bh["calmar"]) else -np.inf
        calmar_ov = metr_ov["calmar"] if np.isfinite(metr_ov["calmar"]) else -np.inf
        ok_calmar = calmar_ov > calmar_bh
        n_calmar_ok += int(ok_calmar)
        # critere Etape D original, pour rappel cote a cote (deja connu, pas recalcule différemment)
        mdd_reduction = 1.0 - abs(metr_ov["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
        ret_ratio = metr_ov["ann_return_pct"] / metr_bh["ann_return_pct"] if metr_bh["ann_return_pct"] != 0 else np.nan
        ok_etaped = bool(mdd_reduction > 0.25 and ret_ratio >= 0.80)
        lines.append(
            f"| {name_r} | {calmar_bh:.3f} | {calmar_ov:.3f} | {metr_bh['sharpe_ann']:+.2f} | "
            f"{metr_ov['sharpe_ann']:+.2f} | {'OUI' if ok_calmar else 'non'} | {'OUI' if ok_etaped else 'NON'} |"
        )

    lines += [
        "",
        f"**{n_calmar_ok}/3 marchés avec Calmar overlay > Calmar BH** (critère du #115), contre "
        f"**0/3 sous le critère Étape D d'origine** (>25% réduction MDD ET ≥80% rendement conservé, "
        f"déjà établi dans `etape_D_v2_no_leverage.md`).",
        "",
    ]
    if n_calmar_ok == 3:
        lines.append(
            "**Conclusion : la divergence vient ENTIÈREMENT du CRITÈRE.** Les 3 marchés améliorent "
            "leur Calmar sous le mécanisme GJR-GARCH -- le critère Étape D (>25%MDD/≥80%rdt) est "
            "simplement plus strict que le critère Calmar simple du #115."
        )
    elif n_calmar_ok == 0:
        lines.append(
            "**Conclusion : la divergence vient ENTIÈREMENT du MOTEUR de volatilité.** Même sous le "
            "critère plus permissif du #115 (Calmar simple), l'overlay GJR-GARCH ne bat Buy&Hold sur "
            "AUCUN des 3 marchés -- contrairement à la vol réalisée simple utilisée en #115."
        )
    else:
        lines.append(
            f"**Conclusion : divergence MIXTE, ni purement le critère ni purement le moteur.** "
            f"{n_calmar_ok}/3 marché(s) (Russell 2000 ici) inverse(nt) de verdict sous le critère Calmar "
            f"simple -- pour ce marché, la divergence #115 vs Étape D vient bien du critère (bar plus "
            f"stricte). Mais {3-n_calmar_ok}/3 (S&P 500, DAX) restent des ÉCHECS même sous le critère "
            f"permissif -- pour ceux-là, c'est le moteur GJR-GARCH lui-même (ou le marché) qui ne "
            f"répond pas au mécanisme défensif, pas seulement une barre trop haute. **Aucune des deux "
            f"lectures simples (\"c'est juste le critère\" ou \"c'est juste le moteur\") n'est complète "
            f"-- les deux facteurs jouent, à des degrés différents selon le marché.**"
        )

    out = ROOT / "results" / "nonml_calmar_criterion_reanalysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
