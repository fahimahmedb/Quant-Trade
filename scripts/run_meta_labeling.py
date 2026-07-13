"""Meta-labeling sur LogitL2 (meilleur signal actif retenu en Etape B) :
reprend le protocole EXACT de scripts/run_etape_b.py (T0=750, refit 21 j,
purge/embargo 5 j, triple barrier H=5/+-1.5*sigma_ewm20, couts 5 bps
aller-retour) et compare LogitL2 brut vs LogitL2 + meta-labeling, sur les
deux jeux de donnees (Composite 5 ans, NDX 40 ans). Produit
results/meta_labeling.md.

Ce n'est PAS un nouvel univers de N modeles : c'est UN essai supplementaire
sur un signal deja selectionne. Le DSR de la variante meta integre donc
n_trials = 4 (univers original Etape B, deja etabli) + 1 (ce raffinement) = 5,
avec var_trials recalcule sur les 5 Sharpe quotidiens (les 4 premiers sont
REUTILISES depuis results/etape_B_prediction.md et etape_B_ndx100.md, non
refaits - cf. discipline anti data-snooping de CLAUDE.md).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_proba,
)
from meta_labeling import build_secondary_features, meta_size, secondary_labels  # noqa: E402

# ------------------------------------------------------------------ protocole (identique Etape B, FIGE)
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0

# Sharpe quotidiens de l'univers N=4 de l'Etape B - deja ETABLIS, REUTILISES
# tels quels (sources : results/etape_B_prediction.md, results/etape_B_ndx100.md).
ETAPE_B_SHARPE_DAILY = {
    "nasdaq_composite_daily.txt": {
        "BuyHold": 0.0493, "Momentum": -0.0210, "LogitL2": -0.0435, "HistGB": 0.0028,
    },
    "nasdaq100_daily.txt": {
        "BuyHold": 0.0328, "Momentum": -0.0178, "LogitL2": 0.0192, "HistGB": 0.0144,
    },
}
ETAPE_B_SHARPE_ANN_BUYHOLD = {
    "nasdaq_composite_daily.txt": 0.78,
    "nasdaq100_daily.txt": 0.52,
}
ETAPE_B_DSR_BUYHOLD = {  # DSR original (N=4) de BuyHold, pour reference dans le verdict
    "nasdaq_composite_daily.txt": 0.567,
    "nasdaq100_daily.txt": 0.842,
}

DATASETS = [
    ("nasdaq_composite_daily.txt", ROOT / "data" / "nasdaq_composite_daily.txt"),
    ("nasdaq100_daily.txt", ROOT / "data" / "nasdaq100_daily.txt"),
]
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "meta_labeling.md")


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def run_one(key: str, data_path: Path) -> dict:
    df = load_ohlc(str(data_path)).set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values

    X = build_features(df)
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    n = len(df)
    dates = df.index

    # --- primaire LogitL2, identique Etape B
    p_up = walk_forward_proba(X, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
    pos_before = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)

    # --- secondaire : meme purge/embargo (5j), features = primaire + confiance
    y_sec = secondary_labels(y, pos_before)
    X_sec = build_secondary_features(X, p_up)
    p_win = walk_forward_proba(X_sec, y_sec, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)

    size_cont = meta_size(p_win, mode="continuous")
    size_thr = meta_size(p_win, mode="threshold")
    pos_after = pos_before * size_cont       # dimensionnement continu (retenu)
    pos_after_thr = pos_before * size_thr    # filtre seuil (variante de lecture)

    oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN
    pnl_before = backtest(pos_before, r_fwd, COST_BPS)[oos]
    pnl_after = backtest(pos_after, r_fwd, COST_BPS)[oos]
    pnl_after_thr = backtest(pos_after_thr, r_fwd, COST_BPS)[oos]

    m_before = trading_metrics(pnl_before)
    m_after = trading_metrics(pnl_after)
    m_after_thr = trading_metrics(pnl_after_thr)

    turn_before = float(np.abs(np.diff(pos_before[oos], prepend=pos_before[oos][0])).mean())
    turn_after = float(np.abs(np.diff(pos_after[oos], prepend=pos_after[oos][0])).mean())
    turn_after_thr = float(np.abs(np.diff(pos_after_thr[oos], prepend=pos_after_thr[oos][0])).mean())

    # accuracy sur les paris PRIS uniquement (|position|>0), avant vs apres filtre seuil
    y_sign = np.sign(y.values)

    def acc_on(pos):
        taken = pos[oos] != 0
        if taken.sum() == 0:
            return np.nan
        return float((np.sign(pos[oos][taken]) == y_sign[oos][taken]).mean())

    acc_before, acc_after_thr = acc_on(pos_before), acc_on(pos_after_thr)
    frac_traded = float((pos_after_thr[oos] != 0).mean())

    # --- DSR : n_trials = univers Etape B (4, deja etabli) + 1 (ce raffinement) = 5
    base_sr = dict(ETAPE_B_SHARPE_DAILY[key])
    all_sr = dict(base_sr)
    all_sr["LogitL2+Meta"] = m_after["sharpe_daily"]
    n_trials = len(all_sr)
    var_trials = float(np.var(list(all_sr.values()), ddof=1))
    T_oos = len(oos)

    dsr_before = dsr(base_sr["LogitL2"], T_oos, var_trials, n_trials,
                     skew=m_before["skew"], kurt_excess=m_before["excess_kurt"])
    dsr_after = dsr(all_sr["LogitL2+Meta"], T_oos, var_trials, n_trials,
                    skew=m_after["skew"], kurt_excess=m_after["excess_kurt"])

    return dict(
        key=key, dates=dates, oos=oos, T_oos=T_oos,
        m_before=m_before, m_after=m_after, m_after_thr=m_after_thr,
        turn_before=turn_before, turn_after=turn_after, turn_after_thr=turn_after_thr,
        acc_before=acc_before, acc_after_thr=acc_after_thr, frac_traded=frac_traded,
        dsr_before=dsr_before, dsr_after=dsr_after,
        n_trials=n_trials, var_trials=var_trials,
    )


results = [run_one(key, path) for key, path in DATASETS]

# ------------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Meta-labeling — filtre de confiance sur le signal LogitL2 (Étape B)\n")

w("## 1. Cadrage\n")
w("Le modèle **primaire ne change pas** : c'est le LogitL2 déjà retenu en "
  "Étape B (signal actif le plus prometteur, rentable net de coûts sur NDX "
  "mais encore sous Buy & Hold en DSR — cf. `CLAUDE.md`). Un modèle "
  "**secondaire** (même famille, régression logistique L2) apprend, sur les "
  "features causales de `build_features` augmentées de la confiance primaire "
  "(|p_up−0.5|·2), si le pari primaire a des chances d'être gagnant (label = "
  "coïncidence signe(primaire) / signe(triple-barrier)). Position finale = "
  "signe(primaire) × taille(confiance secondaire), taille bornée [0,1] "
  "(dimensionnement continu ; une variante à seuil pur est aussi rapportée).\n")
w(f"Protocole **identique** à l'Étape B : T0={T0}, ré-estimation tous les "
  f"{REFIT_EVERY} j, **purge/embargo {EMBARGO} j sur le primaire ET le "
  f"secondaire** (le label secondaire dépend du même triple barrier, donc de "
  f"la même fenêtre H={H} j), triple barrier ±{BARRIER_MULT}·σ_ewm{VOL_SPAN}, "
  f"coûts {COST_BPS:.0f} bps aller-retour.\n")
w("**Discipline anti data-snooping** : ceci est UN essai supplémentaire sur "
  "un signal déjà sélectionné (LogitL2), pas un nouvel univers de N modèles "
  "— pas de nouveau test SPA. Le DSR ci-dessous intègre néanmoins cet essai : "
  "n_trials = 4 (univers Étape B, déjà établi) + 1 (ce raffinement) = 5, "
  "var_trials recalculé sur les 5 Sharpe quotidiens.\n")

for res in results:
    label = "NASDAQ Composite (5 ans)" if "composite" in res["key"] else "NASDAQ-100 (40 ans)"
    w(f"## 2. {label} — `{res['key']}`\n")
    w(f"OOS = {res['T_oos']} jours ({res['dates'][res['oos'][0]]:%d/%m/%Y} → "
      f"{res['dates'][res['oos'][-1]]:%d/%m/%Y}).\n")
    w("| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | "
      "Profit factor | Hit rate | Turnover/j |")
    w("|---|---|---|---|---|---|---|---|---|")
    mb, ma, mat = res["m_before"], res["m_after"], res["m_after_thr"]
    w(f"| LogitL2 (avant) | {mb['sharpe_ann']:+.2f} | {mb['sortino_ann']:+.2f} | "
      f"{mb['calmar']:+.2f} | {mb['ann_return_pct']:+.1f} % | {mb['max_drawdown_pct']:.1f} % | "
      f"{mb['profit_factor']:.2f} | {100*mb['hit_rate']:.1f} % | {res['turn_before']:.3f} |")
    w(f"| LogitL2 + Meta (seuil 0.5) | {mat['sharpe_ann']:+.2f} | {mat['sortino_ann']:+.2f} | "
      f"{mat['calmar']:+.2f} | {mat['ann_return_pct']:+.1f} % | {mat['max_drawdown_pct']:.1f} % | "
      f"{mat['profit_factor']:.2f} | {100*mat['hit_rate']:.1f} % | {res['turn_after_thr']:.3f} |")
    w(f"| **LogitL2 + Meta (continu)** | **{ma['sharpe_ann']:+.2f}** | {ma['sortino_ann']:+.2f} | "
      f"{ma['calmar']:+.2f} | {ma['ann_return_pct']:+.1f} % | {ma['max_drawdown_pct']:.1f} % | "
      f"{ma['profit_factor']:.2f} | {100*ma['hit_rate']:.1f} % | {res['turn_after']:.3f} |")
    w(f"| *Buy & Hold (référence, Étape B)* | *{ETAPE_B_SHARPE_ANN_BUYHOLD[res['key']]:+.2f}* | "
      "| | | | | | |\n")

    w(f"Accuracy directionnelle sur les paris pris : {100*res['acc_before']:.2f} % (avant) "
      f"→ {100*res['acc_after_thr']:.2f} % (après filtre seuil, {100*res['frac_traded']:.1f} % "
      "des jours OOS tradés — le reste est mis à plat par manque de confiance).\n")

    w("| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** (n_trials=5) |")
    w("|---|---|---|---|---|")
    db, da = res["dsr_before"], res["dsr_after"]
    w(f"| LogitL2 (avant) | {db['sr0_daily']:+.4f} → {res['m_before']['sharpe_daily']:+.4f} | "
      f"{db['sr0_daily']:.4f} | {db['z']:+.2f} | **{db['dsr']:.3f}** |")
    w(f"| LogitL2 + Meta (continu) | {res['m_after']['sharpe_daily']:+.4f} | "
      f"{da['sr0_daily']:.4f} | {da['z']:+.2f} | **{da['dsr']:.3f}** |")
    w(f"\n*σ²(SR, n_trials=5) = {res['var_trials']:.4e}. DSR Buy & Hold de référence "
      f"(Étape B, n_trials=4) = {ETAPE_B_DSR_BUYHOLD[res['key']]:.3f}.*\n")

w("## 3. Verdict honnête\n")
c_res = next(r for r in results if "composite" in r["key"])
n_res = next(r for r in results if "nasdaq100" in r["key"])
for res, name in ((c_res, "Composite"), (n_res, "NDX")):
    sh_gain = res["m_after"]["sharpe_ann"] - res["m_before"]["sharpe_ann"]
    turn_cut = 1 - res["turn_after"] / res["turn_before"] if res["turn_before"] > 0 else np.nan
    beats_bh = res["m_after"]["sharpe_ann"] > ETAPE_B_SHARPE_ANN_BUYHOLD[res["key"]]
    beats_bh_dsr = res["dsr_after"]["dsr"] > 0.95
    w(f"- **{name}** : Sharpe ann. {res['m_before']['sharpe_ann']:+.2f} → "
      f"{res['m_after']['sharpe_ann']:+.2f} ({sh_gain:+.2f}), turnover/j "
      f"{res['turn_before']:.3f} → {res['turn_after']:.3f} "
      f"({100*turn_cut:+.0f} %), DSR {res['dsr_before']['dsr']:.3f} → "
      f"{res['dsr_after']['dsr']:.3f}. "
      + ("Bat désormais Buy & Hold en Sharpe" if beats_bh else "Reste sous Buy & Hold en Sharpe")
      + (" et en DSA (DSR>0.95)." if beats_bh_dsr else f" ; DSR < 0.95 (Buy & Hold reste "
         f"la référence la plus crédible, DSR={ETAPE_B_DSR_BUYHOLD[res['key']]:.3f}).")
    )
w("\nLe meta-labeling filtre/dimensionne les paris du primaire sans changer "
  "de sens : il réduit mécaniquement le turnover (et donc les coûts) en "
  "mettant à plat les jours de faible confiance secondaire, ce qui améliore "
  "généralement le Sharpe net et parfois le drawdown, mais **ne crée pas "
  "d'edge directionnel qui n'existait pas déjà dans le primaire** — un "
  "primaire structurellement mauvais (LogitL2 sur Composite, Sharpe négatif "
  "en Étape B) ne devient pas rentable par simple filtrage de confiance. "
  "Conclusion cohérente avec Étape B : **Buy & Hold reste la stratégie de "
  "référence** sur les deux jeux de données ; le meta-labeling est un "
  "raffinement utile pour la gestion du risque (turnover, drawdown) du "
  "meilleur signal actif, pas une preuve d'edge directionnel nouveau.\n")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
