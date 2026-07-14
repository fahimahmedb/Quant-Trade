"""Comparaison univers primaires complet : 4 signaux (Etape B) x {solo, +overlay}.
Produit results/ensemble_comparison.md.

Objectif (cf. CLAUDE.md, Etape D "en cours") : jusqu'ici l'overlay (vol-targeting
GJR-GARCH(1,1)-t, cap 2.0x / coupe 90e percentile - meilleure combinaison du
grid-search fige, cf. results/etape_D_overlay_optimized.md) n'a ete verifie
QUE sur Buy & Hold (Etape D) et sur LogitL2 seul (results/integrated_pipeline.md,
via src/integrated_pipeline.py). Ce script etend la meme question aux 4 signaux
PRIMAIRES de l'Etape B simultanement, pour savoir lequel benefice le plus de
l'overlay, et si une combinaison simple des 4 (egal-poids ou Sharpe-pondere)
bat Buy & Hold.

Ne reinvente aucun moteur : reutilise tels quels
  - src/prediction.py : build_features, triple_barrier_labels,
                        walk_forward_signals (signaux primaires, Etape B),
                        backtest, trading_metrics, dsr
  - src/overlay.py    : walk_forward_vol_forecast, vol_target_exposure,
                        extreme_cut, EXTREME_CUT_FRAC (GJR-t, meme cap/pctl
                        DEJA retenus dans etape_D_overlay_optimized.md - PAS
                        re-optimises ici)

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- Un seul dataset : NDX (data/nasdaq100_daily.txt, 40 ans, plusieurs cycles).
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j (triple barrier H=5j,
  +/-1.5*sigma_ewm20), couts 5 bps aller-retour.
- Overlay : cap 2.0x, coupe totale (EXTREME_CUT_FRAC=0.0) au 90e percentile
  in-sample de la vol GJR-t annualisee - reglage DEJA retenu, pas retouche ici.
- Univers de 8 variantes EXACTEMENT, aucun ajout a posteriori (N=8 pour le
  DSR) :
    1. BuyHold                 5. BuyHold + overlay
    2. Momentum                6. Momentum + overlay
    3. LogitL2                 7. LogitL2 + overlay
    4. HistGB                  8. HistGB + overlay
  position "+overlay" = signal primaire (-1/0/+1, ou +1 pour BuyHold) x
  exposition vol-targeting (jamais un nouveau modele).
- Evaluation : Sharpe/Calmar/MDD/Turnover NETS de couts + Deflated Sharpe
  Ratio (N=8, la famille des 8 variantes ci-dessus).

CRITERE DE SUCCES (declare avant lecture du resultat, cf. tache) : au moins un
signal primaire actif (Momentum, LogitL2 ou HistGB) + overlay atteint soit
  (a) un DSR >= celui de BuyHold seul (repere indicatif : 0.987 sur NDX, cf.
      results/integrated_pipeline.md - recalcule ici sous n_trials=8, donc pas
      forcement identique), soit
  (b) une reduction de MDD > 30% (relatif, +overlay vs le meme signal seul)
      SANS perdre plus de 20% de son rendement annualise (ret conserve >= 80%).

BONUS (hors protocole fige N=8, EXPLORATOIRE UNIQUEMENT - cf. section dediee
du rapport) : portefeuille egal-poids et Sharpe-pondere des 4 signaux
primaires, overlay applique au portefeuille. Le poids Sharpe-pondere est
calcule a partir du Sharpe OOS de la MEME fenetre evaluee ci-dessus (ce n'est
donc PAS un test out-of-sample independant : resultat illustratif, non compte
dans le DSR, ne remplace pas un protocole a poids fixes a priori).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import EXTREME_CUT_FRAC, extreme_cut, vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
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
OVERLAY_CAP = 2.0          # deja retenu, cf. results/etape_D_overlay_optimized.md
OVERLAY_PCTL = 90.0        # idem
SEED = 42

DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "ensemble_comparison.md")

# Seuils de succes DECLARES AVANT lecture du resultat (cf. docstring).
MDD_REDUCTION_THRESHOLD = 0.30
RET_KEEP_THRESHOLD = 0.80

PRIMARY = ["BuyHold", "Momentum", "LogitL2", "HistGB"]
VARIANTS = []
for p in PRIMARY:
    VARIANTS.append(p)
    VARIANTS.append(f"{p}+Overlay")
ACTIVE_PRIMARY = ["Momentum", "LogitL2", "HistGB"]  # signaux actifs (hors BuyHold)


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
r_fwd = (logp.shift(-1) - logp).values  # rendement log t -> t+1
n = len(df)
dates = df.index

# ------------------------------------------------------- 1) signaux primaires (Etape B)
print("Signaux primaires (walk-forward purge/embargo)...")
X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
y.index = df.index

pos = {}
pos["BuyHold"] = np.ones(n)
mom = (logp - logp.shift(10)).values
pos["Momentum"] = np.where(np.isfinite(mom), np.sign(mom), 0.0)
pos["Momentum"][pos["Momentum"] == 0] = 1.0  # convention Etape B : long par defaut
pos["LogitL2"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic,
                                      T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["HistGB"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), hgb,
                                     T0, REFIT_EVERY, EMBARGO, standardize=False)

# ------------------------------------------------------- 2) overlay GJR-t (deja retenu)
print(f"Overlay vol-targeting GJR-t (cap {OVERLAY_CAP:.1f}x, coupe {OVERLAY_PCTL:.0f}e pctl)...")
r_pct = log_returns_pct(df_raw).values  # longueur n-1 ; r_pct[t] == r_fwd[t] (meme convention
# causale que src/integrated_pipeline.py : r_pct[t] utilise l'info jusqu'a t-1 pour son sigma).
fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY, extreme_pctl=OVERLAY_PCTL)
expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], OVERLAY_CAP)
expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"], EXTREME_CUT_FRAC)
exposure = np.nan_to_num(expo, nan=0.0)
exposure = np.concatenate([exposure, [0.0]])  # aligne sur n (derniere position jamais evaluee)

# ------------------------------------------------------- 3) 8 variantes figees
for p in PRIMARY:
    pos[f"{p}+Overlay"] = pos[p] * exposure

# fenetre OOS commune (a partir de T0, la ou tous les modeles decident)
oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN (pas de lendemain)
T_oos = len(oos)

pnl = {v: backtest(pos[v], r_fwd, COST_BPS)[oos] for v in VARIANTS}
metr = {v: trading_metrics(pnl[v]) for v in VARIANTS}
turnover = {v: float(np.abs(np.diff(pos[v][oos], prepend=pos[v][oos][0])).mean()) for v in VARIANTS}

# ------------------------------------------------------- Deflated Sharpe Ratio (N=8)
sr_daily = {v: metr[v]["sharpe_daily"] for v in VARIANTS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
n_trials = len(VARIANTS)
dsr_out = {}
for v in VARIANTS:
    dsr_out[v] = dsr(sr_daily[v], T_oos, var_trials, n_trials,
                     skew=metr[v]["skew"], kurt_excess=metr[v]["excess_kurt"])

# ------------------------------------------------------- critere de succes par signal
per_signal = {}
for p in ACTIVE_PRIMARY:
    solo, ov = metr[p], metr[f"{p}+Overlay"]
    mdd_solo, mdd_ov = abs(solo["max_drawdown_pct"]), abs(ov["max_drawdown_pct"])
    mdd_reduction = 1.0 - mdd_ov / mdd_solo if mdd_solo > 0 else np.nan
    ret_ratio = (ov["ann_return_pct"] / solo["ann_return_pct"]
                if solo["ann_return_pct"] != 0 else np.nan)
    dsr_ok = dsr_out[f"{p}+Overlay"]["dsr"] >= dsr_out["BuyHold"]["dsr"]
    mdd_ok = bool(np.isfinite(mdd_reduction) and mdd_reduction > MDD_REDUCTION_THRESHOLD
                  and np.isfinite(ret_ratio) and ret_ratio >= RET_KEEP_THRESHOLD)
    per_signal[p] = dict(mdd_reduction=mdd_reduction, ret_ratio=ret_ratio,
                         dsr_ok=dsr_ok, mdd_ok=mdd_ok, success=dsr_ok or mdd_ok)
overall_success = any(v["success"] for v in per_signal.values())

# ------------------------------------------------------- bonus : portefeuilles (exploratoire)
w_ew = {p: 0.25 for p in PRIMARY}
sharpe_pos = {p: max(metr[p]["sharpe_ann"], 0.0) for p in PRIMARY}
s = sum(sharpe_pos.values())
w_sw = {p: (sharpe_pos[p] / s if s > 0 else 0.25) for p in PRIMARY}

pos_ew = sum(w_ew[p] * pos[p] for p in PRIMARY)
pos_sw = sum(w_sw[p] * pos[p] for p in PRIMARY)
pos_ew_ov = pos_ew * exposure
pos_sw_ov = pos_sw * exposure

PORT_VARIANTS = ["EqualWeight", "EqualWeight+Overlay", "SharpeWeighted", "SharpeWeighted+Overlay"]
port_pos = {"EqualWeight": pos_ew, "EqualWeight+Overlay": pos_ew_ov,
           "SharpeWeighted": pos_sw, "SharpeWeighted+Overlay": pos_sw_ov}
port_pnl = {v: backtest(port_pos[v], r_fwd, COST_BPS)[oos] for v in PORT_VARIANTS}
port_metr = {v: trading_metrics(port_pnl[v]) for v in PORT_VARIANTS}
port_turnover = {v: float(np.abs(np.diff(port_pos[v][oos], prepend=port_pos[v][oos][0])).mean())
                 for v in PORT_VARIANTS}
best_port = max(PORT_VARIANTS, key=lambda v: port_metr[v]["sharpe_ann"])
port_beats_bh = port_metr[best_port]["sharpe_ann"] > metr["BuyHold"]["sharpe_ann"]

# ------------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Comparaison univers primaires complet — 4 signaux × {solo, +overlay} (NDX)\n")

w("## 1. Cadrage\n")
w("Objectif (cf. `CLAUDE.md`, Étape D) : l'overlay vol-targeting GJR-GARCH(1,1)-t "
  "(cap, coupe extrême — réglage **déjà retenu**, cf. `results/etape_D_overlay_optimized.md`, "
  "pas re-optimisé ici) n'avait été vérifié que sur Buy & Hold (Étape D) et sur "
  "LogitL2 seul (`results/integrated_pipeline.md`). Ce script étend la même "
  "question aux **4 signaux primaires de l'Étape B simultanément** : quel signal "
  "bénéficie le plus de l'overlay, et une combinaison simple des 4 bat-elle "
  "Buy & Hold ?\n")
w(f"**Protocole figé** : NDX (`{DATA_PATH.name}`), walk-forward T0={T0}, "
  f"ré-estimation tous les {REFIT_EVERY} j, purge/embargo {EMBARGO} j (triple "
  f"barrier H={H} j, ±{BARRIER_MULT}·σ_ewm{VOL_SPAN}), coûts {COST_BPS:.0f} bps "
  f"aller-retour. Overlay : cap {OVERLAY_CAP:.1f}×, coupe totale au "
  f"{OVERLAY_PCTL:.0f}e percentile in-sample. OOS = {T_oos} jours "
  f"({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}).\n")

w("## 2. Univers de 8 variantes (FIGÉ avant évaluation — N=8 pour le DSR)\n")
w("| # | Variante | Composition |")
w("|---|---|---|")
descr = {
    "BuyHold": "toujours long, benchmark",
    "Momentum": "signe du rendement 10 j",
    "LogitL2": "régression logistique L2 (Étape B)",
    "HistGB": "gradient boosting (Étape B)",
}
for i, v in enumerate(VARIANTS, 1):
    base = v.replace("+Overlay", "")
    comp = descr[base] + (" × exposition vol-targeting GJR-t" if "+Overlay" in v else "")
    w(f"| {i} | {v} | {comp} |")
w("")

w("## 3. Performance out-of-sample (nette de coûts)\n")
w("| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | "
  "Profit factor | Hit rate | Turnover/j |")
w("|---|---|---|---|---|---|---|---|---|")
for v in VARIANTS:
    x = metr[v]
    w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | "
      f"{x['calmar']:+.2f} | {x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{x['profit_factor']:.2f} | {100*x['hit_rate']:.1f} % | {turnover[v]:.3f} |")
w("")

w("## 4. Deflated Sharpe Ratio (N=8, univers des 8 variantes)\n")
w(f"σ²(SR essais) = {var_trials:.4e}.\n")
w("| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
for v in VARIANTS:
    d = dsr_out[v]
    w(f"| {v} | {sr_daily[v]:+.4f} | {d['sr0_daily']:.4f} | {d['z']:+.2f} | "
      f"**{d['dsr']:.3f}** |")
w("")

w("## 5. Effet de l'overlay, signal par signal\n")
w(f"Seuils de succès déclarés avant lecture : DSR(+overlay) ≥ DSR(BuyHold), "
  f"OU réduction de MDD > {100*MDD_REDUCTION_THRESHOLD:.0f} % (relatif, +overlay "
  f"vs le même signal seul) sans perdre plus de "
  f"{100*(1-RET_KEEP_THRESHOLD):.0f} % de rendement annualisé.\n")
w("| Signal | ΔMDD relatif (+overlay) | Rdt ann. conservé | DSR(+overlay) ≥ DSR(BuyHold) ? | Critère MDD/rdt ? | **Succès** |")
w("|---|---|---|---|---|---|")
for p in ACTIVE_PRIMARY:
    d = per_signal[p]
    w(f"| {p} | {100*d['mdd_reduction']:+.1f} % | {100*d['ret_ratio']:.1f} % | "
      f"{'OUI' if d['dsr_ok'] else 'non'} | {'OUI' if d['mdd_ok'] else 'non'} | "
      f"{'**OUI**' if d['success'] else 'non'} |")
w("")

w("## 6. Bonus — portefeuilles combinés (EXPLORATOIRE, hors protocole figé N=8)\n")
w("**Avertissement anti data-snooping** : les poids Sharpe-pondérés sont "
  "calculés à partir du Sharpe OOS de la **même fenêtre** évaluée ci-dessous "
  "(pas de split train/test séparé pour les poids). Ce n'est donc **pas** un "
  "test out-of-sample indépendant — résultat illustratif uniquement, non "
  "compté dans le DSR (N=8) ci-dessus, ne remplace pas un protocole à poids "
  "fixés a priori.\n")
w(f"Poids égal-poids : {', '.join(f'{p}={w_ew[p]:.2f}' for p in PRIMARY)}. "
  f"Poids Sharpe-pondéré : {', '.join(f'{p}={w_sw[p]:.2f}' for p in PRIMARY)}.\n")
w("| Portefeuille | Sharpe ann. | Calmar | Rdt ann. | MDD | Turnover/j |")
w("|---|---|---|---|---|---|")
for v in PORT_VARIANTS:
    x = port_metr[v]
    w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | {port_turnover[v]:.3f} |")
w(f"\n*Pour référence, BuyHold seul (protocole figé, section 3) : Sharpe ann. "
  f"{metr['BuyHold']['sharpe_ann']:+.2f}, Calmar {metr['BuyHold']['calmar']:+.2f}, "
  f"MDD {metr['BuyHold']['max_drawdown_pct']:.1f} %.*\n")
w(f"- Meilleur portefeuille (Sharpe ann.) : **{best_port}** — "
  + ("bat" if port_beats_bh else "ne bat pas")
  + " BuyHold en Sharpe (résultat exploratoire, cf. avertissement ci-dessus).\n")

w("## 7. Verdict honnête\n")
best_dsr = max(VARIANTS, key=lambda v: dsr_out[v]["dsr"])
w(f"Meilleur DSR de l'univers figé (N=8) : **{best_dsr}** ({dsr_out[best_dsr]['dsr']:.3f}). "
  f"DSR BuyHold seul (référence) : **{dsr_out['BuyHold']['dsr']:.3f}**.\n")
if overall_success:
    winners = [p for p in ACTIVE_PRIMARY if per_signal[p]["success"]]
    w(f"**Critère de succès atteint** pour {', '.join(winners)} : au moins un "
      "signal primaire actif + overlay satisfait le critère déclaré en section 5 "
      "(DSR ≥ BuyHold, ou réduction de MDD matérielle sans perte excessive de "
      "rendement). Détail par signal : voir tableau section 5.")
else:
    w("**Critère de succès NON atteint** pour aucun des 3 signaux actifs "
      "(Momentum, LogitL2, HistGB) + overlay : ni DSR ≥ BuyHold, ni réduction "
      "de MDD matérielle sans perte excessive de rendement. Rapporté tel quel, "
      "sans le présenter comme un succès — cohérent avec les Étapes B/D : "
      "l'overlay réduit le risque des signaux qu'il pilote (cf. section 3) mais "
      "ne suffit pas à les faire dépasser Buy & Hold sur ce protocole.")
w(f"\nDiscipline anti data-snooping : 8 variantes figées avant évaluation, DSR "
  f"déflaté sur cette famille (n_trials=8) ; aucun paramètre de l'overlay "
  f"(cap {OVERLAY_CAP:.1f}×, percentile {OVERLAY_PCTL:.0f}e) n'a été retouché "
  "après avoir vu ce résultat — il provient d'une recherche antérieure déjà "
  "publiée dans le repo. La section 6 (portefeuilles) est explicitement "
  "exploratoire et exclue de ce compte N=8.\n")

Path(OUT).write_text("\n".join(lines))
print("\n".join(lines))
