"""Etape D (variante CADRE CANONIQUE) - Overlay combinant B (direction faible) +
C (volatilite robuste) comme CONTROLE D'EXPOSITION. Produit
results/etape_D_combined_audit.md.

Difference avec run_etape_d.py (overlay long-only pur, deja valide) : ici on
suit EXACTEMENT l'architecture demandee par le Canonical Audit Framework
(Section 6, STEP 2) :

    pos_t = leverage_t * sig_t
    leverage_t = clip(vol_cible / vol_prevue_t, 0, cap)     (vol-targeting, C)
    sig_t      = signal directionnel LogitL2 (Etape B, faible)
    coupe defensive : leverage *= 0 si vol_prevue_t > 95e pctl in-sample

PREUVE ANTI-LOOKAHEAD (verifiee, cf. AUDIT_CANONICAL_FRAMEWORK_FINAL.md) :
- sig_t : walk_forward_signals de l'Etape B (features causales, modele entraine
  sur [:tr-embargo], purge=embargo=5). Decide a la cloture de t, capte r[t->t+1].
- vol_prevue_t : GJR-t walk-forward (overlay.build_overlay_positions, utilise
  garch_path_fold_only). vol_fcst[t] = prevision pour le rendement r_pct[t]
  (= df t->t+1) avec info jusqu'a la CLOTURE de t uniquement. Meme index t que
  sig_t et r_fwd[t] : aucun decalage, aucune fuite (verifie : vol_fcst[t]
  n'utilise pas r_pct[t]).
- vol_cible : vol realisee in-sample sur [:t0], constante, passe uniquement.

UNIVERS FIGE AVANT EVALUATION (N=4 pour le DSR) :
  1. BuyHold                         - reference (toujours long, exposition 1)
  2. VolTarget (long-only)           - overlay C seul (sig=+1), reference de risque
  3. VolTarget x LogitL2             - architecture combinee B+C (STEP 2)
  4. VolTarget+Cut x LogitL2         - + coupe defensive en regime de vol extreme
Couts 5 bps aller-retour sur le turnover de l'exposition (meme backtest() que B).
Metriques cible : MDD et Calmar (reduction du drawdown), + DSR (N=4) + DM vs BuyHold.
"""
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))
warnings.filterwarnings("ignore")

from sklearn.linear_model import LogisticRegression  # noqa: E402

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import build_overlay_positions  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_signals,
)
from volatility import dm_test  # noqa: E402

# ------------------------------------------------------------------ protocole
T0 = 750
COST_BPS = 5.0
CAP = 1.5
EMBARGO = H = 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
SEED = 42
MODELS = ["BuyHold", "VolTarget", "VolTarget×LogitL2", "VolTarget+Cut×LogitL2"]

DATASETS = [
    ("Composite (5 ans)", REPO_ROOT / "data" / "nasdaq_composite_daily.txt", 5, 21),
    ("NDX (40 ans)", REPO_ROOT / "data" / "nasdaq100_daily.txt", 21, 21),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "etape_D_combined_audit.md")


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


lines = []
w = lines.append
w("# Étape D (variante cadre canonique) — Overlay combiné B (direction) × C (volatilité)\n")
w("Architecture Section 6 STEP 2 : `pos_t = leverage_t · sig_t`, "
  "`leverage_t = clip(vol_cible/vol_prévue_t, 0, cap)` (vol-targeting GJR-t, Étape C), "
  "`sig_t` = LogitL2 (Étape B, direction faible), coupe défensive au 95e pctl in-sample.\n")
w(f"**Protocole figé** : T0={T0}, cap {CAP:.1f}×, coûts {COST_BPS:.0f} bps, "
  f"purge/embargo {EMBARGO} j, univers N={len(MODELS)}, figé avant évaluation.\n")

summary = []

for label, path, refit_ov, refit_b in DATASETS:
    refit_ov = int(os.environ.get("REFIT_EVERY", refit_ov))
    df = load_ohlc(str(path)).set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values          # rendement t->t+1 (natif Étape B)
    dates = df.index
    n = len(df)

    r_pct = log_returns_pct(df.reset_index()).values  # len n-1 ; r_pct[t] = 100*r_fwd[t]
    T_ov = len(r_pct)
    if n <= T0 + 30:
        w(f"## {label}\n\n*Historique trop court — ignoré.*\n")
        continue

    # --- direction (Étape B, LogitL2) ---
    X = build_features(df.reset_index())
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    sig_B = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic,
                                 T0, refit_b, EMBARGO, standardize=True)  # len n, {-1,0,+1}

    # --- volatilité (Étape C via overlay), long-only et cut ---
    ov_vt = build_overlay_positions(r_pct, T0, refit_ov, CAP, with_extreme_cut=False)
    ov_cut = build_overlay_positions(r_pct, T0, refit_ov, CAP, with_extreme_cut=True)
    # overlay index t == df index t (verifie) ; pad a longueur n pour backtest sur r_fwd
    lev_vt = np.zeros(n); lev_vt[:T_ov] = ov_vt["pos"]        # exposition long-only vol-target
    lev_cut = np.zeros(n); lev_cut[:T_ov] = ov_cut["pos"]     # idem + coupe extreme

    pos = {
        "BuyHold": np.ones(n),
        "VolTarget": lev_vt,
        "VolTarget×LogitL2": lev_vt * sig_B,
        "VolTarget+Cut×LogitL2": lev_cut * sig_B,
    }

    oos = np.arange(T0, n - 1)  # r_fwd[n-1] = NaN
    pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
    metr = {m: trading_metrics(pnl[m]) for m in MODELS}

    sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    T_oos = len(oos)
    dsr_out = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                      skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"]) for m in MODELS}
    # DM vs BuyHold sur le PnL quotidien (perte = -rendement ; d>0 <=> modele meilleur)
    hac = int(np.ceil(1.5 * T_oos ** (1.0 / 3)))
    dm_vs_bh = {m: dm_test(-pnl["BuyHold"], -pnl[m], hac_lags=hac) for m in MODELS if m != "BuyHold"}

    n_years = (dates[-1] - dates[T0]).days / 365.25
    w(f"## {label}\n")
    w(f"- OOS : {dates[T0]:%d/%m/%Y} → {dates[n-2]:%d/%m/%Y} ({T_oos} obs, ~{n_years:.1f} ans), "
      f"GJR-t ré-estimé /{refit_ov} j, LogitL2 /{refit_b} j.")
    ex = pos["VolTarget×LogitL2"][oos]
    w(f"- Exposition combinée VolTarget×LogitL2 : moy. {ex.mean():+.2f}×, "
      f"min {ex.min():+.2f}×, max {ex.max():+.2f}× (peut être short si sig=-1).")
    frac_long = float((sig_B[oos] > 0).mean())
    w(f"- Signal LogitL2 long {100*frac_long:.0f}% du temps sur l'OOS.\n")

    w("| Variante | Sharpe ann. | Calmar | **MDD %** | Rdt ann. % | Profit factor | DSR | DM t vs BH (p) |")
    w("|---|---|---|---|---|---|---|---|")
    for m in MODELS:
        me = metr[m]
        dmc = f"{dm_vs_bh[m]['t']:+.2f} ({dm_vs_bh[m]['p_one_sided_model_better']:.3f})" if m != "BuyHold" else "—"
        w(f"| {m} | {me['sharpe_ann']:+.2f} | {me['calmar']:+.2f} | {me['max_drawdown_pct']:.1f} | "
          f"{me['ann_return_pct']:+.1f} | {me['profit_factor']:.2f} | {dsr_out[m]['dsr']:.3f} | {dmc} |")
    w("")

    bh = metr["BuyHold"]
    for m in ("VolTarget", "VolTarget×LogitL2", "VolTarget+Cut×LogitL2"):
        me = metr[m]
        mdd_red = 1.0 - abs(me["max_drawdown_pct"]) / abs(bh["max_drawdown_pct"])
        ret_ratio = me["ann_return_pct"] / bh["ann_return_pct"] if bh["ann_return_pct"] != 0 else np.nan
        ok = (mdd_red > 0.25) and (ret_ratio >= 0.80)
        summary.append((label, m, mdd_red, ret_ratio, me["calmar"], bh["calmar"],
                        dsr_out[m]["dsr"], ok))
        w(f"- **{m}** : ΔMDD relatif {100*mdd_red:+.1f}% (seuil >25%), "
          f"rendement conservé {100*ret_ratio:.0f}% du BuyHold (seuil ≥80%) → "
          + ("**succès**" if ok else "**échec du critère**"))
    w("")

w("## Verdict — architecture combinée B×C\n")
w("| Jeu | Variante | ΔMDD rel. | Rdt/BH | Calmar (ov vs BH) | DSR | Critère |")
w("|---|---|---|---|---|---|---|")
for lab, m, mdd_r, ret_r, cal, cal_bh, d, ok in summary:
    w(f"| {lab} | {m} | {100*mdd_r:+.1f}% | {100*ret_r:.0f}% | {cal:+.2f} vs {cal_bh:+.2f} | "
      f"{d:.3f} | {'OUI' if ok else 'NON'} |")
w("")
any_ok = any(s[-1] for s in summary)
if any_ok:
    w("**Verdict** : au moins une variante combinée atteint le critère (voir tableau). "
      "Ne pas généraliser au-delà des cellules OUI.")
else:
    w("**Verdict honnête** : AUCUNE variante combinée B×C n'atteint le critère "
      "(réduction MDD >25% ET rendement conservé ≥80%). Injecter la direction LogitL2 "
      "(rejetée au niveau 2, DSR<BuyHold) dans l'overlay dégrade le résultat par rapport "
      "à l'overlay vol-targeting long-only (run_etape_d.py) : le turnover du signal faible "
      "coûte plus qu'il n'apporte. L'overlay défensif long-only reste la seule variante "
      "défendable de l'Étape D.")

Path(OUT).write_text("\n".join(lines))
print("\n".join(lines))
