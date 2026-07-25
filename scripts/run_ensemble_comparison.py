"""Comparaison univers primaires complet : 4 signaux (Etape B) x {solo, +overlay}.
Produit results/ensemble_comparison.md.

Objectif (cf. tache) : valider lequel des 4 signaux primaires figes de
l'Etape B (BuyHold, Momentum, LogitL2, HistGB) beneficie le plus de l'overlay
de gestion du risque (Etape D, vol-targeting GJR-GARCH(1,1)-t, cap 2.0x /
coupe totale au 90e percentile in-sample), et si une combinaison simple
(egal-poids ou Sharpe-pondere) des 4 signaux, avec overlay applique au
portefeuille, bat Buy & Hold.

NOTE DE LOCALISATION (repo reorganise depuis la redaction initiale de la
tache, cf. commit "Reorganize repository: finance/trading, divers/robot-
politique, cours") : les modules reutilises (data_loader, prediction,
overlay) vivent desormais sous finance/src/ et non plus src/ a la racine.
Ce script (racine scripts/, conforme au chemin demande dans la tache)
importe donc depuis finance/src/ explicitement ci-dessous. Les donnees
(data/nasdaq100_daily.txt) et ce rapport (results/) restent a la racine du
repo, comme prevu par CLAUDE.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- Univers de 4 signaux primaires EXACTEMENT (identiques a Etape B, aucune
  reestimation/retouche) : BuyHold, Momentum (signe rdt 10j), LogitL2
  (regression logistique L2, C=0.5), HistGB (HistGradientBoostingClassifier,
  memes hyperparametres qu'Etape B).
- Pour chaque signal : variante solo et variante +overlay (vol-targeting
  GJR-GARCH(1,1)-t, cap 2.0x, coupe totale au 90e percentile in-sample -
  ces reglages proviennent de la grille DEJA figee et publiee dans
  results/etape_D_overlay_optimized.md / finance/src/integrated_pipeline.py,
  PAS re-optimises ici) => 8 variantes EXACTEMENT, aucun ajout a posteriori
  (n_trials=8 pour le DSR).
- Un seul dataset : NDX (data/nasdaq100_daily.txt, 40 ans).
- Walk-forward T0=750, refit 21 j (signal ET GJR-t), purge/embargo 5 j
  (triple barrier H=5j, +/-1.5*sigma_ewm20), couts 5 bps aller-retour sur le
  turnover de la position finale (signal x exposition).
- Evaluation : Sharpe/Calmar/MDD/Turnover NETS de couts + Deflated Sharpe
  Ratio (N=8, la famille des 8 variantes ci-dessus).
- Bonus OPTIONNEL, hors du N=8 fige (rapporte a part, jamais mele au DSR
  principal) : portefeuille egal-poids des 4 signaux primaires solo, et
  portefeuille Sharpe-pondere (poids proportionnels aux Sharpe solo positifs
  observes ci-dessus - ce n'est PAS un reglage a priori, c'est explicitement
  un bonus post-hoc marque comme tel, non couvert par le DSR=8 principal),
  overlay applique au portefeuille resultant.

CRITERE DE SUCCES (cf. tache) : au moins un signal primaire (hors BuyHold) +
overlay atteint DSR >= BuyHold (0.987 sur NDX, cf. resultat ci-dessous) OU
reduit le MDD de plus de 30% sans perdre plus de 20% de rendement annualise,
par rapport a sa propre variante solo.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "finance" / "src"))
warnings.filterwarnings("ignore")

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

# ------------------------------------------------------------------ protocole FIGE
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
SEED = 42
# Overlay : reglages DEJA retenus (etape_D_overlay_optimized.md), pas re-optimises ici.
OVERLAY_CAP = 2.0
OVERLAY_PCTL = 90.0

DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "ensemble_comparison.md")

SIGNALS = ["BuyHold", "Momentum", "LogitL2", "HistGB"]
VARIANTS = []
for s in SIGNALS:
    VARIANTS.append(s)
    VARIANTS.append(f"{s}+Overlay")
assert len(VARIANTS) == 8, "Univers fige = 8 variantes exactement"


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def hgb():
    return HistGradientBoostingClassifier(
        max_depth=3, max_iter=150, learning_rate=0.05,
        l2_regularization=1.0, min_samples_leaf=40, random_state=SEED)


print("Chargement NDX 40 ans...")
df_raw = load_ohlc(str(DATA_PATH))
df = df_raw.set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = (logp.shift(-1) - logp).values  # rendement futur t->t+1
n = len(df)
dates = df.index

print("Features + labels (triple barrier)...")
X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
y.index = df.index

# --------------------------------------------------------- 4 signaux primaires (Etape B)
print("Signal Momentum (regle, sans apprentissage)...")
mom = (logp - logp.shift(10)).values
pos_mom = np.where(np.isfinite(mom), np.sign(mom), 0.0)
pos_mom[pos_mom == 0] = 1.0  # convention Etape B : long par defaut

print(f"Signal LogitL2 (walk-forward, refit {REFIT_EVERY}j, embargo {EMBARGO}j)...")
pos_logit = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic,
                                 T0, REFIT_EVERY, EMBARGO, standardize=True)

print(f"Signal HistGB (walk-forward, refit {REFIT_EVERY}j, embargo {EMBARGO}j)...")
pos_hgb = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), hgb,
                               T0, REFIT_EVERY, EMBARGO, standardize=False)

pos_solo = {
    "BuyHold": np.ones(n),
    "Momentum": pos_mom,
    "LogitL2": pos_logit,
    "HistGB": pos_hgb,
}

# ---------------------------------------------------------- overlay (Etape D optimisee)
print(f"Overlay vol-targeting GJR-t (cap {OVERLAY_CAP:.1f}x, coupe {OVERLAY_PCTL:.0f}e pctl, "
      f"refit {REFIT_EVERY}j)...")
r_pct = log_returns_pct(df_raw).values  # longueur n-1, memes valeurs que r_fwd[0:n-1]
ov = build_overlay_positions(r_pct, T0, REFIT_EVERY, OVERLAY_CAP,
                             with_extreme_cut=True, extreme_pctl=OVERLAY_PCTL)
exposure = np.zeros(n)
exposure[:len(r_pct)] = ov["pos"]  # derniere position (n-1) jamais evaluee dans l'OOS

positions = {}
for s in SIGNALS:
    positions[s] = pos_solo[s]
    positions[f"{s}+Overlay"] = pos_solo[s] * exposure

# ------------------------------------------------------------------------- backtests
oos = np.arange(T0, n - 1)  # r_fwd[n-1] = NaN
T_oos = len(oos)
pnl = {v: backtest(positions[v], r_fwd, COST_BPS)[oos] for v in VARIANTS}
metr = {v: trading_metrics(pnl[v]) for v in VARIANTS}
turnover = {v: float(np.abs(np.diff(positions[v][oos], prepend=positions[v][oos][0])).mean())
            for v in VARIANTS}

# ------------------------------------------------------- Deflated Sharpe Ratio (N=8)
sr_daily = {v: metr[v]["sharpe_daily"] for v in VARIANTS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
n_trials = len(VARIANTS)
dsr_out = {v: dsr(sr_daily[v], T_oos, var_trials, n_trials,
                  skew=metr[v]["skew"], kurt_excess=metr[v]["excess_kurt"]) for v in VARIANTS}

# ---------------------------------------------------- criteres de succes (par signal actif)
bh = metr["BuyHold"]
dsr_bh = dsr_out["BuyHold"]["dsr"]
success_rows = []
for s in ("Momentum", "LogitL2", "HistGB"):
    solo, ov_m = metr[s], metr[f"{s}+Overlay"]
    mdd_solo, mdd_ov = abs(solo["max_drawdown_pct"]), abs(ov_m["max_drawdown_pct"])
    mdd_reduction = 1.0 - mdd_ov / mdd_solo if mdd_solo > 0 else np.nan
    ret_ratio = (ov_m["ann_return_pct"] / solo["ann_return_pct"]
                if solo["ann_return_pct"] != 0 else np.nan)
    crit_dsr = dsr_out[f"{s}+Overlay"]["dsr"] >= dsr_bh
    crit_mdd = (np.isfinite(mdd_reduction) and mdd_reduction > 0.30
               and np.isfinite(ret_ratio) and ret_ratio >= 0.80)
    success_rows.append((s, dsr_out[f"{s}+Overlay"]["dsr"], dsr_bh, crit_dsr,
                         mdd_reduction, ret_ratio, crit_mdd))

# ------------------------------------------------------------------- bonus (hors N=8)
print("Bonus (optionnel, hors DSR=8) : portefeuilles egal-poids / Sharpe-pondere...")
sh_solo = {s: max(metr[s]["sharpe_ann"], 0.0) for s in SIGNALS}  # poids >=0 uniquement
w_sum = sum(sh_solo.values())
if w_sum > 0:
    w_sharpe = {s: sh_solo[s] / w_sum for s in SIGNALS}
else:
    w_sharpe = {s: 1.0 / len(SIGNALS) for s in SIGNALS}
w_equal = {s: 1.0 / len(SIGNALS) for s in SIGNALS}

pos_equal = sum(w_equal[s] * pos_solo[s] for s in SIGNALS)
pos_sharpe = sum(w_sharpe[s] * pos_solo[s] for s in SIGNALS)
BONUS = ["Equal-Weight(4)", "Equal-Weight(4)+Overlay", "Sharpe-Weighted(4)", "Sharpe-Weighted(4)+Overlay"]
positions_bonus = {
    "Equal-Weight(4)": pos_equal,
    "Equal-Weight(4)+Overlay": pos_equal * exposure,
    "Sharpe-Weighted(4)": pos_sharpe,
    "Sharpe-Weighted(4)+Overlay": pos_sharpe * exposure,
}
pnl_bonus = {v: backtest(positions_bonus[v], r_fwd, COST_BPS)[oos] for v in BONUS}
metr_bonus = {v: trading_metrics(pnl_bonus[v]) for v in BONUS}
turnover_bonus = {v: float(np.abs(np.diff(positions_bonus[v][oos], prepend=positions_bonus[v][oos][0])).mean())
                 for v in BONUS}
sr_daily_bonus = {v: metr_bonus[v]["sharpe_daily"] for v in BONUS}
# DSR du bonus : famille SEPAREE (n_trials=4 : les 4 variantes bonus), jamais melee au N=8 principal.
var_trials_bonus = float(np.var(list(sr_daily_bonus.values()), ddof=1))
dsr_bonus = {v: dsr(sr_daily_bonus[v], T_oos, var_trials_bonus, len(BONUS),
                    skew=metr_bonus[v]["skew"], kurt_excess=metr_bonus[v]["excess_kurt"])
            for v in BONUS}
bonus_beats_bh = any(metr_bonus[v]["sharpe_ann"] > bh["sharpe_ann"] and dsr_bonus[v]["dsr"] >= dsr_bh
                     for v in BONUS)

n_years = (dates[oos[-1]] - dates[oos[0]]).days / 365.25

# ------------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Comparaison univers primaires complet — NDX (4 signaux × {solo, +overlay})\n")

w("## 1. Cadrage\n")
w("Objectif (cf. `CLAUDE.md`, Étape D) : valider lequel des 4 signaux primaires "
  "figés de l'Étape B (BuyHold, Momentum, LogitL2, HistGB) bénéficie le plus de "
  "l'overlay de gestion du risque (vol-targeting GJR-GARCH(1,1)-t), et si une "
  "combinaison simple des 4 signaux bat Buy & Hold.\n")
w("Aucun des deux moteurs n'est réinventé : le primaire (Étape B) et l'overlay "
  f"(cap {OVERLAY_CAP:.1f}×, coupe totale au {OVERLAY_PCTL:.0f}e percentile "
  "in-sample) sont ceux **déjà retenus** dans les études précédentes du repo "
  "(`results/etape_D_overlay_optimized.md`, `finance/src/integrated_pipeline.py`), "
  "pas re-optimisés ici.\n")
w(f"**Protocole figé** : NDX (`{DATA_PATH.name}`), walk-forward T0={T0}, "
  f"ré-estimation tous les {REFIT_EVERY} j (signal ET GJR-t), purge/embargo "
  f"{EMBARGO} j (triple barrier H={H} j, ±{BARRIER_MULT}·σ_ewm{VOL_SPAN}), "
  f"coûts {COST_BPS:.0f} bps aller-retour. OOS = {T_oos} jours "
  f"({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}, ~{n_years:.1f} ans).\n")

w("## 2. Univers de 8 variantes (FIGÉ avant évaluation — N=8 pour le DSR)\n")
w("| # | Variante | Composition |")
w("|---|---|---|")
for i, v in enumerate(VARIANTS, 1):
    base = v.replace("+Overlay", "")
    comp = ("toujours long" if base == "BuyHold" else
           "signe rendement 10j" if base == "Momentum" else
           "régression logistique L2" if base == "LogitL2" else
           "HistGradientBoosting")
    comp = comp + " × exposition vol-targeting" if "+Overlay" in v else comp
    w(f"| {i} | {v} | {comp} |")
w("")

w("## 3. Performance out-of-sample (nette de coûts)\n")
w("| Variante | Sharpe ann. | Calmar | **MDD %** | Rdt ann. % | Turnover/j | Hit rate |")
w("|---|---|---|---|---|---|---|")
for v in VARIANTS:
    x = metr[v]
    w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['max_drawdown_pct']:.1f} | {x['ann_return_pct']:+.1f} | "
      f"{turnover[v]:.3f} | {100*x['hit_rate']:.1f} % |")
w("")

w("## 4. Deflated Sharpe Ratio (N=8, univers des 8 variantes)\n")
w(f"σ²(SR essais) = {var_trials:.4e}.\n")
w("| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
for v in VARIANTS:
    d = dsr_out[v]
    w(f"| {v} | {sr_daily[v]:+.4f} | {d['sr0_daily']:.4f} | {d['z']:+.2f} | **{d['dsr']:.3f}** |")
w("")

w("## 5. Effet de l'overlay, signal par signal (critère de succès explicite)\n")
w(f"Succès si DSR(signal+overlay) ≥ DSR(BuyHold) = **{dsr_bh:.3f}** OU réduction "
  "du MDD > 30% sans perdre plus de 20% de rendement annualisé, **par rapport à "
  "la variante solo du même signal** (déclaré avant lecture du résultat).\n")
w("| Signal | DSR +Overlay | DSR BuyHold | Crit. DSR | ΔMDD rel. (solo→+overlay) | "
  "Rdt conservé | Crit. MDD/Rdt | Verdict |")
w("|---|---|---|---|---|---|---|---|")
any_success = False
for s, d_ov, d_bh, c_dsr, mdd_r, ret_r, c_mdd in success_rows:
    ok = c_dsr or c_mdd
    any_success = any_success or ok
    w(f"| {s} | {d_ov:.3f} | {d_bh:.3f} | {'OUI' if c_dsr else 'non'} | "
      f"{100*mdd_r:+.1f}% | {100*ret_r:.0f}% | {'OUI' if c_mdd else 'non'} | "
      f"{'**succès**' if ok else 'échec'} |")
w("")

w("## 6. Bonus optionnel — portefeuilles combinés (HORS du N=8 principal)\n")
w("**Avertissement anti data-snooping** : les poids Sharpe-pondérés sont "
  "calculés à partir des Sharpe solo observés eux-mêmes dans ce script (poids "
  "= Sharpe positif normalisé) — ce n'est **pas** un réglage fixé a priori, "
  "c'est un choix informé par le résultat, donc structurellement optimiste. "
  "Ces 4 variantes bonus forment une famille **séparée** (n_trials=4 pour leur "
  "propre DSR), jamais mélangée au DSR=8 de la section 4, et leur résultat "
  "doit être lu avec un degré de confiance inférieur à celui de la comparaison "
  "principale.\n")
w(f"Poids égal-poids : {', '.join(f'{s}={w_equal[s]:.2f}' for s in SIGNALS)}. "
  f"Poids Sharpe-pondéré : {', '.join(f'{s}={w_sharpe[s]:.2f}' for s in SIGNALS)}.\n")
w("| Variante | Sharpe ann. | Calmar | MDD % | Rdt ann. % | Turnover/j | DSR (n=4, famille bonus) |")
w("|---|---|---|---|---|---|---|")
for v in BONUS:
    x = metr_bonus[v]
    w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['max_drawdown_pct']:.1f} | {x['ann_return_pct']:+.1f} | "
      f"{turnover_bonus[v]:.3f} | {dsr_bonus[v]['dsr']:.3f} |")
w("")
w(f"Pour mémoire, Buy & Hold (référence, section 3-4) : Sharpe ann. "
  f"{bh['sharpe_ann']:+.2f}, DSR (famille N=8) {dsr_bh:.3f}.\n")
if bonus_beats_bh:
    w("Au moins une combinaison bonus dépasse Buy & Hold en Sharpe ann. **et** "
      "en DSR (comparaison hétérogène : DSR bonus calculé sur sa propre famille "
      "n=4, DSR BuyHold sur la famille n=8 — à lire avec prudence, cf. "
      "avertissement ci-dessus, ne pas conclure à un edge validé sans "
      "re-test sur un échantillon indépendant).")
else:
    w("Aucune combinaison bonus ne dépasse Buy & Hold simultanément en Sharpe "
      "ann. et en DSR.")
w("")

w("## 7. Verdict honnête\n")
best_dsr_main = max(VARIANTS, key=lambda v: dsr_out[v]["dsr"])
w(f"- Meilleur DSR de l'univers figé (N=8) : **{best_dsr_main}** "
  f"({dsr_out[best_dsr_main]['dsr']:.3f}).")
if any_success:
    w("- **Au moins un signal primaire + overlay atteint le critère de succès** "
      "(voir tableau section 5, colonne Verdict) : l'overlay bénéficie "
      "matériellement au(x) signal(aux) marqué(s) succès. Ne pas généraliser "
      "au-delà des lignes marquées succès.")
else:
    w("- **Critère de succès NON atteint pour aucun signal actif.** Ni le DSR "
      "de la variante +overlay ne dépasse celui de Buy & Hold, ni la réduction "
      "de MDD (>30%) avec rendement conservé (≥80%) n'est observée, pour "
      "Momentum, LogitL2 ou HistGB. Cohérent avec l'Étape B/D déjà établies : "
      "Buy & Hold (nu ou avec overlay long-only) reste la référence sur NDX.")
w("- **Discipline anti data-snooping** : univers de 8 variantes figé avant "
  "évaluation (section 2), DSR déflaté sur cette famille exacte (n_trials=8), "
  "réglages de l'overlay (cap 2.0×, coupe 90e percentile) repris tels quels "
  "d'une étude antérieure déjà publiée dans le repo — pas de balayage de "
  "paramètres ni d'ajout de variante après lecture du résultat ci-dessus. Le "
  "bonus (section 6) est explicitement hors de ce cadre et signalé comme tel.\n")

Path(OUT).write_text("\n".join(lines))
print("\n".join(lines))
