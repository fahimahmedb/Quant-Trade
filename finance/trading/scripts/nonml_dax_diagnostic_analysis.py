"""Analyse diagnostique — pourquoi DAX est-il systématiquement le marché
le plus difficile de la lignée de portes #216-242 ? (spécification
pré-enregistrée dans PREREG_dax_diagnostic_analysis.md, committée avant
ce script). PAS un backtest : calcule les diagnostics déjà implémentés à
l'Étape A sur les 5 marchés standards du backlog, à titre de comparaison
descriptive.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from diagnostics import (  # noqa: E402
    summary_stats, lo_mackinlay_vr, ljung_box, engle_arch_lm, fit_student_t,
)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    rows = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r = log_returns_pct(df).values

        ss = summary_stats(r)
        vr = lo_mackinlay_vr(r, q=5)
        lb = ljung_box(r, lags=(5, 10, 22))
        arch = engle_arch_lm(r, nlags=10)
        st = fit_student_t(r)

        rows[name] = {
            "n": ss["n"],
            "sharpe_bh_ann": ss["ann_mean_pct"] / ss["ann_vol_pct"] if ss["ann_vol_pct"] else float("nan"),
            "ann_vol_pct": ss["ann_vol_pct"],
            "skew": ss["skew"],
            "excess_kurtosis": ss["excess_kurtosis"],
            "vr5": vr["VR"],
            "vr5_p_robust": vr["p_robust"],
            "lb22_squared_p": lb["squared"][22]["p"],
            "arch_lm_p": arch["p_LM"],
            "nu": st["nu"],
        }

    lines = [
        "# Diagnostic structurel — pourquoi DAX est-il systématiquement le marché le plus "
        "difficile de la lignée de portes #216-242 ?",
        "",
        "Analyse diagnostique (pas un backtest, pas de critère PASS/FAIL) : diagnostics déjà "
        "implémentés à l'Étape A, calculés sur l'échantillon complet de chaque marché.",
        "",
        "| Marché | n séances | Sharpe BH ann. | Vol ann. | Skew | Kurtosis excès | VR(5) | "
        "VR(5) p robuste | Ljung-Box Q(22) rdt² p | ARCH-LM p | ν Student-t |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, d in rows.items():
        lines.append(
            f"| {name} | {d['n']} | {d['sharpe_bh_ann']:+.2f} | {d['ann_vol_pct']:.1f}% | "
            f"{d['skew']:+.2f} | {d['excess_kurtosis']:+.2f} | {d['vr5']:.3f} | "
            f"{d['vr5_p_robust']:.4f} | {d['lb22_squared_p']:.4f} | {d['arch_lm_p']:.4f} | "
            f"{d['nu']:.2f} |"
        )

    lines.append("")
    lines.append("## Lecture comparative DAX vs les 4 autres marchés")
    lines.append("")

    dax = rows.get("DAX")
    others = {k: v for k, v in rows.items() if k != "DAX"}
    if dax and others:
        for metric, label in [
            ("sharpe_bh_ann", "Sharpe Buy&Hold annualisé"),
            ("ann_vol_pct", "Volatilité annualisée"),
            ("skew", "Asymétrie (skew)"),
            ("excess_kurtosis", "Excès de kurtosis"),
            ("vr5", "Ratio de variance VR(5)"),
            ("nu", "ν Student-t (épaisseur des queues, non conditionnel)"),
        ]:
            dax_val = dax[metric]
            other_vals = [v[metric] for v in others.values()]
            lo, hi = min(other_vals), max(other_vals)
            outside_range = not (lo <= dax_val <= hi)
            lines.append(
                f"- **{label}** : DAX = {dax_val:.3f}, autres marchés ∈ [{lo:.3f}, {hi:.3f}] — "
                f"{'DAX HORS de la plage des 4 autres' if outside_range else 'DAX dans la plage des 4 autres'}"
            )

    lines.append("")
    lines.append(
        "**Lecture honnête** : ce diagnostic est purement descriptif et comparatif, sans "
        "critère de succès pré-défini au-delà de la question posée. Voir le corps du texte "
        "pour l'interprétation qualitative des écarts constatés."
    )

    out = ROOT / "results" / "nonml_dax_diagnostic_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
