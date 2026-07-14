"""Meta-labeling multi-variantes : 3 modeles SECONDAIRES (LogitL2 baseline,
RandomForest, XGBoost) sur le meme primaire deja retenu (LogitL2, Etape B),
sur NDX 40 ans (data/nasdaq100_daily.txt) - protocole EXACT de
scripts/run_etape_b.py (T0=750, refit 21 j, purge/embargo 5 j, triple
barrier H=5/+-1.5*sigma_ewm20, couts 5 bps aller-retour).

Univers des 3 variantes de SECONDAIRE FIGE avant evaluation (cf.
src.meta_labeling.SECONDARY_MODELS) - le primaire ne change pas. Ce n'est
pas un nouvel univers de modeles primaires ; c'est un raffinement (filtrage/
dimensionnement) teste sous 3 formes differentes. Le DSR compte n_trials=3
(les 3 variantes de secondaire), var_trials calcule sur les 3 Sharpe
quotidiens obtenus (dimensionnement continu, la lecture retenue).
"""
import sys
import warnings
from pathlib import Path

import numpy as np

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
from meta_labeling import (  # noqa: E402
    SECONDARY_MODELS,
    build_secondary_features,
    meta_size,
    secondary_labels,
)

# ------------------------------------------------------------------ protocole (identique Etape B, FIGE)
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0

DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "meta_labeling_multi.md")

# References deja etablies (Etape B / meta_labeling simple), REUTILISEES, non refaites.
ETAPE_B_SHARPE_ANN_BUYHOLD_NDX = 0.52
ETAPE_B_DSR_BUYHOLD_NDX = 0.842
LOGITL2_BEFORE_DSR_REF = 0.372  # DSR du LogitL2 brut, n_trials=4 (univers Etape B, cf. CLAUDE.md)


def logistic():
    return SECONDARY_MODELS["LogitL2"]()


print("Chargement NDX 40 ans...")
df = load_ohlc(str(DATA_PATH)).set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = (logp.shift(-1) - logp).values

X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
y.index = df.index
n = len(df)
dates = df.index
oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN

# --- primaire LogitL2, identique Etape B - calcule UNE fois, partage par les 3 variantes
print("Primaire LogitL2 (walk-forward, T0=750, refit 21j)...")
p_up = walk_forward_proba(X, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
pos_before = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)
pnl_before = backtest(pos_before, r_fwd, COST_BPS)[oos]
m_before = trading_metrics(pnl_before)
turn_before = float(np.abs(np.diff(pos_before[oos], prepend=pos_before[oos][0])).mean())

y_sec = secondary_labels(y, pos_before)
X_sec = build_secondary_features(X, p_up)

results = {}
for name, factory in SECONDARY_MODELS.items():
    print(f"Secondaire {name} (walk-forward, T0=750, refit 21j)...")
    p_win = walk_forward_proba(X_sec, y_sec, factory, T0, REFIT_EVERY, EMBARGO, standardize=True)

    size_cont = meta_size(p_win, mode="continuous")
    size_thr = meta_size(p_win, mode="threshold")
    pos_after = pos_before * size_cont
    pos_after_thr = pos_before * size_thr

    pnl_after = backtest(pos_after, r_fwd, COST_BPS)[oos]
    pnl_after_thr = backtest(pos_after_thr, r_fwd, COST_BPS)[oos]
    m_after = trading_metrics(pnl_after)
    m_after_thr = trading_metrics(pnl_after_thr)

    turn_after = float(np.abs(np.diff(pos_after[oos], prepend=pos_after[oos][0])).mean())
    turn_after_thr = float(np.abs(np.diff(pos_after_thr[oos], prepend=pos_after_thr[oos][0])).mean())

    y_sign = np.sign(y.values)

    def acc_on(pos):
        taken = pos[oos] != 0
        if taken.sum() == 0:
            return np.nan
        return float((np.sign(pos[oos][taken]) == y_sign[oos][taken]).mean())

    acc_after_thr = acc_on(pos_after_thr)
    frac_traded = float((pos_after_thr[oos] != 0).mean())

    results[name] = dict(
        m_after=m_after, m_after_thr=m_after_thr,
        turn_after=turn_after, turn_after_thr=turn_after_thr,
        acc_after_thr=acc_after_thr, frac_traded=frac_traded,
    )

# --- DSR : n_trials=3 (les 3 variantes de secondaire, dimensionnement continu retenu)
acc_before = float((np.sign(pos_before[oos][pos_before[oos] != 0])
                    == np.sign(y.values[oos][pos_before[oos] != 0])).mean())
sr_by_variant = {name: r["m_after"]["sharpe_daily"] for name, r in results.items()}
n_trials = len(sr_by_variant)
var_trials = float(np.var(list(sr_by_variant.values()), ddof=1))
T_oos = len(oos)

for name, r in results.items():
    r["dsr_after"] = dsr(r["m_after"]["sharpe_daily"], T_oos, var_trials, n_trials,
                         skew=r["m_after"]["skew"], kurt_excess=r["m_after"]["excess_kurt"])

# ------------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Meta-labeling multi-variantes — 3 modèles secondaires sur LogitL2 (NDX 40 ans)\n")

w("## 1. Cadrage\n")
w("Le modèle **primaire ne change pas** : LogitL2 déjà retenu en Étape B "
  "(signal actif le plus prometteur sur NDX, rentable net de coûts mais "
  "encore sous Buy & Hold en DSR — cf. `CLAUDE.md`). On teste ici **3 "
  "variantes de modèle SECONDAIRE**, univers FIGÉ avant évaluation "
  "(`src/meta_labeling.py::SECONDARY_MODELS`) :\n")
w("1. **LogitL2** (baseline, identique à `results/meta_labeling.md`)\n")
w("2. **RandomForest** (sklearn, défauts — `n_estimators=100`, seul "
  "`random_state` fixé, aucun tuning)\n")
w("3. **XGBoost** (défauts `xgboost` — `n_estimators=100`, seul "
  "`random_state` fixé, aucun tuning)\n")
w(f"\nMême protocole que l'Étape B pour le primaire ET pour chacun des 3 "
  f"secondaires : T0={T0}, ré-estimation tous les {REFIT_EVERY} j, "
  f"**purge/embargo {EMBARGO} j** (le label secondaire dépend du même "
  f"triple barrier H={H} j que le primaire), triple barrier "
  f"±{BARRIER_MULT}·σ_ewm{VOL_SPAN}, coûts {COST_BPS:.0f} bps aller-retour. "
  "Position finale = signe(primaire) × taille(confiance secondaire) — "
  "dimensionnement continu (variante à seuil 0.5 également rapportée pour "
  "lecture).\n")
w("**Discipline anti data-snooping** : ceci n'est pas un nouvel univers de "
  "modèles primaires — c'est UN raffinement (filtrage/dimensionnement) du "
  "signal déjà sélectionné (LogitL2), testé sous 3 formes de secondaire. Le "
  f"DSR ci-dessous intègre ces 3 essais : n_trials={n_trials}, var_trials "
  "calculé sur les 3 Sharpe quotidiens obtenus (dimensionnement continu).\n")

label = "NASDAQ-100 (40 ans)"
w(f"## 2. {label} — `nasdaq100_daily.txt`\n")
w(f"OOS = {T_oos} jours ({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}).\n")

w("| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | "
  "Profit factor | Hit rate | Turnover/j |")
w("|---|---|---|---|---|---|---|---|---|")
w(f"| LogitL2 primaire (avant, référence) | {m_before['sharpe_ann']:+.2f} | "
  f"{m_before['sortino_ann']:+.2f} | {m_before['calmar']:+.2f} | "
  f"{m_before['ann_return_pct']:+.1f} % | {m_before['max_drawdown_pct']:.1f} % | "
  f"{m_before['profit_factor']:.2f} | {100*m_before['hit_rate']:.1f} % | {turn_before:.3f} |")
for name, r in results.items():
    ma, mat = r["m_after"], r["m_after_thr"]
    w(f"| **+ Meta {name} (continu)** | **{ma['sharpe_ann']:+.2f}** | {ma['sortino_ann']:+.2f} | "
      f"{ma['calmar']:+.2f} | {ma['ann_return_pct']:+.1f} % | {ma['max_drawdown_pct']:.1f} % | "
      f"{ma['profit_factor']:.2f} | {100*ma['hit_rate']:.1f} % | {r['turn_after']:.3f} |")
    w(f"| + Meta {name} (seuil 0.5) | {mat['sharpe_ann']:+.2f} | {mat['sortino_ann']:+.2f} | "
      f"{mat['calmar']:+.2f} | {mat['ann_return_pct']:+.1f} % | {mat['max_drawdown_pct']:.1f} % | "
      f"{mat['profit_factor']:.2f} | {100*mat['hit_rate']:.1f} % | {r['turn_after_thr']:.3f} |")
w(f"| *Buy & Hold (référence, Étape B)* | *{ETAPE_B_SHARPE_ANN_BUYHOLD_NDX:+.2f}* | | | | | | | |\n")

w(f"Accuracy directionnelle du primaire sur les paris pris (avant filtre) : "
  f"{100*acc_before:.2f} %.\n")
w("| Variante | Accuracy après filtre seuil | % jours tradés |")
w("|---|---|---|")
for name, r in results.items():
    w(f"| {name} | {100*r['acc_after_thr']:.2f} % | {100*r['frac_traded']:.1f} % |")
w("")

w(f"\n### DSR (n_trials={n_trials}, univers des 3 variantes de secondaire)\n")
w("| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
w(f"| *LogitL2 primaire (avant, référence externe, n_trials=4 Étape B)* | "
  f"*{m_before['sharpe_daily']:+.4f}* | | | *{LOGITL2_BEFORE_DSR_REF:.3f}* |")
for name, r in results.items():
    d = r["dsr_after"]
    w(f"| + Meta {name} (continu) | {r['m_after']['sharpe_daily']:+.4f} | "
      f"{d['sr0_daily']:.4f} | {d['z']:+.2f} | **{d['dsr']:.3f}** |")
w(f"\n*σ²(SR, n_trials={n_trials}) = {var_trials:.4e}. DSR Buy & Hold de référence "
  f"(Étape B, n_trials=4) = {ETAPE_B_DSR_BUYHOLD_NDX:.3f}.*\n")

w("## 3. Verdict honnête\n")
best_name = max(results, key=lambda k: results[k]["m_after"]["sharpe_ann"])
worst_name = min(results, key=lambda k: results[k]["m_after"]["sharpe_ann"])
for name, r in results.items():
    ma = r["m_after"]
    sh_gain = ma["sharpe_ann"] - m_before["sharpe_ann"]
    turn_cut = 1 - r["turn_after"] / turn_before if turn_before > 0 else np.nan
    beats_bh = ma["sharpe_ann"] > ETAPE_B_SHARPE_ANN_BUYHOLD_NDX
    beats_bh_dsr = r["dsr_after"]["dsr"] > 0.95
    tag = " (meilleure variante)" if name == best_name else (" (pire variante)" if name == worst_name else "")
    w(f"- **{name}{tag}** : Sharpe ann. {m_before['sharpe_ann']:+.2f} → {ma['sharpe_ann']:+.2f} "
      f"({sh_gain:+.2f}), turnover/j {turn_before:.3f} → {r['turn_after']:.3f} "
      f"({100*turn_cut:+.0f} %), DSR (n_trials=3) = {r['dsr_after']['dsr']:.3f}. "
      + ("Bat désormais Buy & Hold en Sharpe" if beats_bh else "Reste sous Buy & Hold en Sharpe")
      + (" et en DSR (>0.95)." if beats_bh_dsr else f" ; DSR < 0.95 (Buy & Hold reste la "
         f"référence la plus crédible, DSR={ETAPE_B_DSR_BUYHOLD_NDX:.3f}).")
    )

w(f"\nLes 3 variantes de secondaire filtrent/dimensionnent le même primaire "
  f"sans changer de sens : leur effet principal est la réduction du turnover "
  f"(donc des coûts) via la mise à plat des jours de faible confiance. "
  f"**{best_name}** est la variante la plus favorable au Sharpe net ici, "
  f"**{worst_name}** la moins favorable"
  + (" (peut dégrader le Sharpe net du primaire si le secondaire, plus "
     "flexible/non-linéaire, sur-apprend le bruit du label triple-barrier "
     "sur un historique encore restreint en early walk-forward)"
     if results[worst_name]["m_after"]["sharpe_ann"] < m_before["sharpe_ann"] else "")
  + f". Aucune des 3 variantes ne crée d'edge directionnel qui n'existait "
  "pas déjà dans le primaire : le meta-labeling reste un raffinement de "
  "gestion du risque (turnover, drawdown), **pas une preuve de battre "
  "Buy & Hold** — cohérent avec `results/meta_labeling.md` et la conclusion "
  "de l'Étape B. Buy & Hold demeure la stratégie de référence sur NDX.\n")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
