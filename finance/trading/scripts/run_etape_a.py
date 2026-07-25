"""Etape A - diagnostics preliminaires. Produit results/etape_A_diagnostics.md."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct, parkinson_var_pct, quality_report  # noqa: E402
from diagnostics import (  # noqa: E402
    acf,
    engle_arch_lm,
    fit_student_t,
    ljung_box,
    lo_mackinlay_vr,
    summary_stats,
)

DATA = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "nasdaq_composite_daily.txt")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "results" / "etape_A_diagnostics.md")

df = load_ohlc(DATA)
qr = quality_report(df)
r = log_returns_pct(df).values
rv_p = parkinson_var_pct(df).values

lines = []
w = lines.append
w("# Étape A — Diagnostics préliminaires (NASDAQ Composite, quotidien)\n")

w("## 1. Qualité des données\n")
w(f"- Période : {qr['start']:%d/%m/%Y} → {qr['end']:%d/%m/%Y} — **{qr['n_obs']} séances** "
  f"({qr['n_obs']-1} rendements)")
w(f"- Jours ouvrés manquants vs calendrier : {qr['missing_bdays']} "
  f"(attendu ≈ {round((qr['end']-qr['start']).days/365*9)} fériés US sur la période)")
w(f"- Dates dupliquées : {qr['dup_dates']} | lignes OHLC incohérentes : {qr['bad_ohlc_rows']} "
  f"| écart calendaire max : {qr['max_gap_days']} j")
w(f"- |rendement| max : {qr['max_abs_ret_pct']:.2f} % | rendements >8 % abs. : {qr['n_ret_gt_8pct']}")
w("- Volume = 0 partout → colonne inutilisable, ignorée.\n")

w("## 2. Statistiques descriptives des rendements log quotidiens\n")
s = summary_stats(r)
w("| Statistique | Valeur |")
w("|---|---|")
w(f"| n | {s['n']} |")
w(f"| Moyenne quotidienne | {s['mean_daily_pct']:.4f} % |")
w(f"| Moyenne annualisée | {s['ann_mean_pct']:.2f} % |")
w(f"| Volatilité annualisée | {s['ann_vol_pct']:.2f} % |")
w(f"| Skewness | {s['skew']:.3f} |")
w(f"| Kurtosis en excès | {s['excess_kurtosis']:.3f} |")
w(f"| Min / Max | {s['min_pct']:.2f} % / {s['max_pct']:.2f} % |")
w(f"| Jarque-Bera (p) | {s['jarque_bera']:.1f} ({s['jb_pvalue']:.2e}) |")
w("")

w("## 3. Ratio de variance Lo-MacKinlay (H₀ : random walk)\n")
w("| q | VR(q) | z homoscéd. | p | z* robuste hétéro. | p |")
w("|---|---|---|---|---|---|")
for q in (2, 5, 10):
    v = lo_mackinlay_vr(r, q)
    w(f"| {q} | {v['VR']:.4f} | {v['z_homo']:.2f} | {v['p_homo']:.3f} "
      f"| {v['z_robust']:.2f} | {v['p_robust']:.3f} |")
w("\n*Seule z\\* (robuste) est interprétable en présence de clustering de volatilité "
  "(Lo-MacKinlay 1988). VR<1 = anti-persistance (renversement), VR>1 = momentum.*\n")

w("## 4. Autocorrélations\n")
a_r = acf(r, 10)
a_r2 = acf((r - r.mean()) ** 2, 10)
w("| Lag | ACF rendements | ACF rendements² |")
w("|---|---|---|")
for k in range(10):
    w(f"| {k+1} | {a_r[k]:+.3f} | {a_r2[k]:+.3f} |")
band = 1.96 / np.sqrt(len(r))
w(f"\n*Bande ±1.96/√n = ±{band:.3f} (indicative ; non robuste à l'hétéroscédasticité "
  "pour les rendements bruts).*\n")

lb = ljung_box(r)
w("### Ljung-Box\n")
w("| Lags | Q rendements (p) | Q rendements² (p) |")
w("|---|---|---|")
for l in (5, 10, 22):
    w(f"| {l} | {lb['returns'][l]['Q']:.1f} ({lb['returns'][l]['p']:.3f}) "
      f"| {lb['squared'][l]['Q']:.1f} ({lb['squared'][l]['p']:.2e}) |")
w("")

w("## 5. Test ARCH-LM d'Engle (clustering de volatilité)\n")
e = engle_arch_lm(r, 10)
w(f"- LM({e['nlags']}) = {e['LM']:.1f}, p = {e['p_LM']:.2e} → "
  + ("**effet ARCH massif confirmé**" if e['p_LM'] < 0.01 else "pas d'effet ARCH") + "\n")

w("## 6. Queues de distribution — Student-t non conditionnelle\n")
t = fit_student_t(r)
w(f"- ν estimé (MV) : **{t['nu']:.2f}** | loc {t['loc']:.4f} | scale {t['scale']:.4f}")
w(f"- LR t vs normale : {t['lr_stat_t_vs_normal']:.1f} (χ²(1) ; >6.63 = rejet de la "
  "normale à 1 %)")
w("- NB : ν non conditionnel < ν conditionnel (résidus GARCH), car le clustering "
  "de volatilité explique une partie des queues. Voir Étape C.\n")

w("## 7. Volatilité réalisée range-based (Parkinson)\n")
ratio = ((r - r.mean()) ** 2).mean() / rv_p.mean()
w(f"- Ratio E[ε²] / E[RV_Parkinson] = **{ratio:.3f}** → la variance intra-séance "
  "sous-estime la variance close-to-close (gap overnight non couvert). "
  "Toute utilisation de la RV Parkinson (HAR) est ré-échelonnée par ce ratio, "
  "estimé sur fenêtre d'entraînement uniquement.\n")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
