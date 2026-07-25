"""Pipeline integree B -> meta-labeling -> overlay : walk-forward complet NDX.
Produit results/integrated_pipeline.md.

Objectif (cf. CLAUDE.md, Etape D) : verifier que la COMBINAISON des 3
composantes deja construites reduit le max drawdown du SIGNAL ACTIF LogitL2
lui-meme (Etape D "premiere passe"/"optimisee" avaient deja verifie l'effet
de l'overlay sur Buy & Hold ; ici on verifie l'effet sur le signal directionnel).

NOTE DE LOCALISATION (repo reorganise depuis la redaction initiale du script,
cf. commit "Reorganize repository: finance/trading, divers/robot-politique,
cours") : les modules reutilises (data_loader, prediction, meta_labeling,
overlay, integrated_pipeline) vivent desormais sous finance/src/ et non plus
src/ a la racine. Ce script (racine scripts/, conforme au chemin demande
dans la tache) importe donc depuis finance/src/ explicitement ci-dessous.
Les donnees (data/nasdaq100_daily.txt) et ce rapport (results/) restent a la
racine du repo, comme prevu par CLAUDE.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- Univers de 5 variantes EXACTEMENT, aucun ajout a posteriori (N=5 pour le DSR) :
    1. Buy & Hold                          - benchmark de reference
    2. LogitL2 seul                        - Etape B (signal actif retenu)
    3. LogitL2 + meta-labeling             - Etape B + filtre (secondaire LogitL2,
                                             meilleure variante, DSR=0.866, cf.
                                             results/meta_labeling_multi.md)
    4. LogitL2 + overlay                   - Etape B + gestion du risque (GJR-t
                                             vol-targeting, cap 2.0x, coupe 90e
                                             pctl, meilleure combo, cf.
                                             results/etape_D_overlay_optimized.md)
    5. LogitL2 + meta-labeling + overlay   - pipeline complete
  Aucun des 3 reglages (secondaire meta, cap/pctl overlay) n'est re-optimise
  ici : ce sont ceux DEJA retenus dans les etudes precedentes (declarees dans
  finance/src/integrated_pipeline.py, pas retouchees apres avoir vu le
  resultat combine ci-dessous).
- Un seul dataset : NDX (data/nasdaq100_daily.txt, 40 ans, plusieurs cycles).
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j (labels triple barrier
  H=5j +/-1.5*sigma_ewm20), couts 5 bps aller-retour.
- Evaluation : Sharpe/Sortino/Calmar/MDD/Turnover NETS de couts + Deflated
  Sharpe Ratio (N=5, la famille des 5 variantes ci-dessus).

CRITERE DE SUCCES (cf. tache) : la pipeline complete (variante 5) reduit le
MDD de la variante 2 (LogitL2 seul) de facon MATERIELLE (repere indicatif :
reduction relative > 25 %, coherent avec le seuil deja utilise en Etape D)
sans perdre l'essentiel du rendement (repere indicatif : rendement annualise
conserve >= 50 % de celui de la variante 2 - le signal LogitL2 seul degage
deja peu de rendement, cf. Etape B, donc un seuil moins strict que pour
Buy & Hold est raisonnable et declare ici, avant de lire le resultat).
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "finance" / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from integrated_pipeline import (  # noqa: E402
    BARRIER_MULT,
    COST_BPS,
    EMBARGO,
    H,
    OVERLAY_CAP,
    OVERLAY_PCTL,
    REFIT_EVERY,
    T0,
    VARIANTS,
    VOL_SPAN,
    build_pipeline,
)
from prediction import backtest, dsr, trading_metrics  # noqa: E402

DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "integrated_pipeline.md")

# Seuils de succes DECLARES AVANT lecture du resultat (cf. docstring).
MDD_REDUCTION_THRESHOLD = 0.25   # reduction relative du MDD, variante 5 vs variante 2
RET_KEEP_THRESHOLD = 0.50        # rendement annualise conserve (variante 5 / variante 2)

print("Chargement NDX 40 ans...")
df_raw = load_ohlc(str(DATA_PATH))

print(f"Pipeline integree (walk-forward, T0={T0}, refit {REFIT_EVERY}j, "
      f"embargo {EMBARGO}j, overlay cap {OVERLAY_CAP:.1f}x / coupe {OVERLAY_PCTL:.0f}e pctl)...")
out = build_pipeline(df_raw)
positions, r_fwd, dates, n = out["positions"], out["r_fwd"], out["dates"], out["n"]

oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN (pas de lendemain)
T_oos = len(oos)

pnl = {v: backtest(positions[v], r_fwd, COST_BPS)[oos] for v in VARIANTS}
metr = {v: trading_metrics(pnl[v]) for v in VARIANTS}
turnover = {v: float(np.abs(np.diff(positions[v][oos], prepend=positions[v][oos][0])).mean())
            for v in VARIANTS}

# ------------------------------------------------------- Deflated Sharpe Ratio (N=5)
sr_daily = {v: metr[v]["sharpe_daily"] for v in VARIANTS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
n_trials = len(VARIANTS)
dsr_out = {}
for v in VARIANTS:
    dsr_out[v] = dsr(sr_daily[v], T_oos, var_trials, n_trials,
                     skew=metr[v]["skew"], kurt_excess=metr[v]["excess_kurt"])

# ------------------------------------------------------------- critere de succes
base = metr["LogitL2"]           # variante 2 : signal actif seul
combo = metr["LogitL2+Meta+Overlay"]  # variante 5 : pipeline complete
mdd_base, mdd_combo = abs(base["max_drawdown_pct"]), abs(combo["max_drawdown_pct"])
mdd_reduction = 1.0 - mdd_combo / mdd_base if mdd_base > 0 else np.nan
ret_ratio = (combo["ann_return_pct"] / base["ann_return_pct"]
            if base["ann_return_pct"] != 0 else np.nan)
success = bool(np.isfinite(mdd_reduction) and mdd_reduction > MDD_REDUCTION_THRESHOLD
              and np.isfinite(ret_ratio) and ret_ratio >= RET_KEEP_THRESHOLD)

# ------------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Pipeline intégrée B → meta-labeling → overlay (NDX 40 ans)\n")

w("## 1. Cadrage\n")
w("Objectif (cf. `CLAUDE.md`, Étape D) : vérifier que la **combinaison** des "
  "trois composantes déjà construites — signal primaire (Étape B), filtre "
  "meta-labeling, overlay de gestion du risque (Étape D optimisée) — réduit "
  "le max drawdown du **signal actif LogitL2 lui-même**, pas seulement celui "
  "de Buy & Hold (déjà traité dans `finance/trading/results/etape_D_overlay_optimized.md`).\n")
w("Aucun des trois moteurs n'est réinventé : le primaire, le secondaire du "
  "meta-labeling et les paramètres de l'overlay sont ceux **déjà retenus** "
  "dans les études précédentes du repo (`meta_labeling_multi.md` : "
  "secondaire LogitL2, DSR=0.866 ; `etape_D_overlay_optimized.md` : "
  f"cap {OVERLAY_CAP:.1f}×, coupe au {OVERLAY_PCTL:.0f}e percentile), pas "
  "re-optimisés ici.\n")
w("Position finale générique (chaque variante est un cas particulier, "
  "composante absente = neutre) :\n")
w("```\npos_final = signe(LogitL2) × confiance_meta_labeling × exposition_overlay\n```\n")
w(f"**Protocole figé** : NDX (`{DATA_PATH.name}`), walk-forward T0={T0}, "
  f"ré-estimation tous les {REFIT_EVERY} j, purge/embargo {EMBARGO} j "
  f"(triple barrier H={H} j, ±{BARRIER_MULT}·σ_ewm{VOL_SPAN}), coûts "
  f"{COST_BPS:.0f} bps aller-retour. OOS = {T_oos} jours "
  f"({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}).\n")

w("## 2. Univers de 5 variantes (FIGÉ avant évaluation — N=5 pour le DSR)\n")
w("| # | Variante | Composition |")
w("|---|---|---|")
w("| 1 | Buy & Hold | benchmark, toujours long |")
w("| 2 | LogitL2 seul | signal primaire (Étape B) |")
w("| 3 | LogitL2 + meta-labeling | primaire × confiance secondaire LogitL2 |")
w("| 4 | LogitL2 + overlay | primaire × exposition vol-targeting |")
w("| 5 | LogitL2 + meta-labeling + overlay | pipeline complète |")
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

w("## 4. Deflated Sharpe Ratio (N=5, univers des 5 variantes)\n")
w(f"σ²(SR essais) = {var_trials:.4e}.\n")
w("| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
for v in VARIANTS:
    d = dsr_out[v]
    w(f"| {v} | {sr_daily[v]:+.4f} | {d['sr0_daily']:.4f} | {d['z']:+.2f} | "
      f"**{d['dsr']:.3f}** |")
w("")

w("## 5. Effet sur le drawdown du signal actif (LogitL2 seul vs pipeline complète)\n")
w(f"- LogitL2 seul (variante 2) : MDD **{base['max_drawdown_pct']:.1f} %**, "
  f"rendement annualisé {base['ann_return_pct']:+.1f} %, Sharpe ann. "
  f"{base['sharpe_ann']:+.2f}.")
w(f"- LogitL2 + meta-labeling + overlay (variante 5) : MDD "
  f"**{combo['max_drawdown_pct']:.1f} %**, rendement annualisé "
  f"{combo['ann_return_pct']:+.1f} %, Sharpe ann. {combo['sharpe_ann']:+.2f}.")
w(f"- Réduction relative du MDD : **{100*mdd_reduction:+.1f} %** "
  f"(seuil de succès déclaré : > {100*MDD_REDUCTION_THRESHOLD:.0f} %).")
w(f"- Rendement annualisé conservé : **{100*ret_ratio:.1f} %** de la variante 2 "
  f"(seuil de succès déclaré : ≥ {100*RET_KEEP_THRESHOLD:.0f} %).\n")

w("## 6. Verdict honnête\n")
if success:
    w(f"**Succès** : la pipeline complète (variante 5) réduit le MDD du "
      f"signal LogitL2 de {100*mdd_reduction:.1f} % (relatif), au-dessus du "
      f"seuil de {100*MDD_REDUCTION_THRESHOLD:.0f} %, tout en conservant "
      f"{100*ret_ratio:.1f} % de son rendement annualisé (≥ "
      f"{100*RET_KEEP_THRESHOLD:.0f} % requis). La combinaison des trois "
      "composantes réduit donc matériellement le risque du signal actif "
      "lui-même, pas seulement celui de Buy & Hold.")
else:
    reasons = []
    if not (np.isfinite(mdd_reduction) and mdd_reduction > MDD_REDUCTION_THRESHOLD):
        reasons.append(f"réduction du MDD ({100*mdd_reduction:+.1f} %) sous le seuil "
                       f"de {100*MDD_REDUCTION_THRESHOLD:.0f} %")
    if not (np.isfinite(ret_ratio) and ret_ratio >= RET_KEEP_THRESHOLD):
        reasons.append(f"rendement conservé ({100*ret_ratio:.1f} %) sous le seuil "
                       f"de {100*RET_KEEP_THRESHOLD:.0f} %")
    w(f"**Critère de succès non atteint** ({' ; '.join(reasons)}). Rapporté tel "
      "quel, sans le présenter comme un succès.")
best_dsr = max(VARIANTS, key=lambda v: dsr_out[v]["dsr"])
w(f"\nMeilleur DSR de l'univers : **{best_dsr}** ({dsr_out[best_dsr]['dsr']:.3f}). "
  "Rappel (cf. `CLAUDE.md`, Étape B/D) : Buy & Hold reste la stratégie de "
  "référence sur NDX en Sharpe/DSR brut ; l'objet de cette pipeline n'est pas "
  "de la battre en rendement mais de vérifier si la combinaison des trois "
  "composantes améliore le **profil risque du signal actif lui-même** — "
  "conclusion à lire à la lumière du tableau ci-dessus, pas en absolu.\n")
w("Discipline anti data-snooping : 5 variantes figées avant évaluation, DSR "
  "déflaté sur cette famille (n_trials=5) ; aucun paramètre (secondaire meta, "
  "cap/percentile overlay) n'a été retouché après avoir vu ce résultat combiné "
  "- ils proviennent de recherches antérieures déjà publiées dans le repo "
  "(finance/src/meta_labeling.py, finance/src/overlay.py).\n")

Path(OUT).write_text("\n".join(lines))
print("\n".join(lines))
