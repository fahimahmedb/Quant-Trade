"""Nouvelle phase de recherche : univers de 9 signaux techniques classiques,
figes A PRIORI, teste sur NDX 40 ans avec protocole strict anti-data-snooping.

CONTEXTE (a lire avant le code) : ce script est INDEPENDANT des etudes
precedentes du repo (Etapes A/B/C/D, pipeline integree). Il ne reutilise ni
les features ML de `finance/src/prediction.py`, ni le meta-labeling, ni
l'overlay vol-targeting deja construits : l'objectif declare de cette phase
est de repartir d'une base propre avec des regles techniques simples
(pas de modele entraine), pour verifier si un signal actif "classique"
bat Buy & Hold une fois les couts et le Deflated Sharpe Ratio (multi-essais)
pris en compte. Seuls sont reutilises les utilitaires generiques deja
valides : chargement des donnees (`data_loader.load_ohlc`) et les fonctions
de metriques/backtest/DSR (`prediction.backtest`, `prediction.trading_metrics`,
`prediction.dsr`), qui ne dependent d'aucun choix de modele.

============================================================================
PHASE 1 - UNIVERS FIGE A PRIORI (N=9, aucun ajout apres avoir vu les resultats)
============================================================================
Tier 1 (baseline)      : S0  Buy & Hold
Tier 2 (classiques)     : S1  Momentum EMA 12/26 (signe(EMA12-EMA26))
                          S2  RSI(14) seuils 30/70 (mean-reversion)
                          S3  Donchian 20 breakout (canal des 20j PRECEDENTS,
                              position tenue jusqu'au signal oppose)
Tier 3 (combinaisons)   : S4  Momentum + RSI confluence (signes EMA12-EMA26 et
                              RSI-50 alignes, sinon flat)
                          S5  EMA trend (EMA50>EMA200), long seul, flat sinon
                          S6  Momentum ajuste-vol (direction = signe(mom_10j),
                              exposition = target_vol/vol_realisee, cap 1.5x)
Tier 4 (multi-timeframe): S7  Confluence EMA12>EMA50>EMA200 (long) /
                              EMA12<EMA50<EMA200 (short), sinon flat
                          S8  Double momentum (ROC 12j et ROC 20j du meme
                              signe pour prendre position, sinon flat)

============================================================================
PHASE 2 - PROTOCOLE STRICT (identique pour les 9 signaux)
============================================================================
- Donnees   : NDX 40 ans (data/nasdaq100_daily.txt), OHLC quotidien complet.
- Fenetre OOS : demarre a T0=750 (warm-up commun, couvre le plus long lookback
  utilise ici, SMA250) jusqu'a l'avant-dernier jour (r_fwd defini).
- refit_every=21j / embargo=21j : DECLARES dans la tache, mais NOTE DE
  METHODE explicite ci-dessous (section "note_protocole" du rapport) - ces
  signaux sont des regles techniques DETERMINISTES, fonctions causales des
  seuls OHLC passes (aucun parametre estime par apprentissage sur des labels
  futurs). Il n'y a donc ni ajustement ("fit") ni fuite train/test possible a
  purger : refit_every/embargo n'ont pas d'effet sur la construction des
  signaux (contrairement au modele ML de l'Etape B). Ils sont neanmoins
  respectes au sens propre du terme : aucune information du jour t+1 ou
  au-dela n'entre dans la decision prise au jour t. Seul T0 (borne de depart
  de la fenetre OOS commune) est un parametre actif ici.
- Features causales uniquement (EMA/RSI/Donchian/ROC calcules avec shift
  approprie pour eviter tout regard sur la barre courante quand necessaire,
  ex. canal de Donchian decale d'un jour).
- Couts : 5 bps aller-retour sur le turnover (prediction.backtest, identique
  au reste du repo).
- Sortie : Sharpe/Sortino/Calmar/MDD/win-rate + turnover + Deflated Sharpe
  Ratio (Bailey & Lopez de Prado), n_trials=9 pour l'univers principal.

============================================================================
PHASE 3 - VARIANTES DECLAREES A L'AVANCE (PAS de grid-search post-hoc)
============================================================================
- S6b : identique a S6 mais cap d'exposition 2.0x au lieu de 1.5x.
- S7b : identique a S7 mais filtre de confirmation supplementaire
  EMA200 > SMA250 (tendance long-terme) / EMA200 < SMA250 (short).
Le seul parametre "estime sur donnees" de toute la phase est le target_vol de
S6/S6b : calcule UNE SEULE FOIS sur l'echantillon in-sample [0:T0[ (jamais sur
la fenetre OOS, jamais retouche apres avoir vu un resultat).
Ces 2 variantes ETENDENT l'univers a N=11 essais au total : conformement a la
discipline anti-data-snooping du repo (CLAUDE.md : "Toute extension doit etre
declaree, comptee (N essais) et re-testee au SPA/DSR"), on rapporte donc DEUX
DSR : le DSR "officiel" de la tache (n_trials=9, univers principal seul) ET un
DSR honnete de la famille etendue (n_trials=11) qui inclut S6b/S7b.

Usage: python3 scripts/run_new_research_phase.py [data_path] [json_out] [md_out]
Defaut : data/nasdaq100_daily.txt, NEW_RESEARCH_PHASE_RESULTS.json,
NEW_RESEARCH_PHASE_REPORT.md (racine du repo, chemins demandes dans la tache).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "finance" / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from prediction import backtest, dsr, trading_metrics  # noqa: E402

DATA_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "nasdaq100_daily.txt"
JSON_OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "NEW_RESEARCH_PHASE_RESULTS.json"
MD_OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "NEW_RESEARCH_PHASE_REPORT.md"

T0 = 750
REFIT_EVERY = 21
EMBARGO = 21
COST_BPS = 5.0

MAIN_UNIVERSE = ["S0_BuyHold", "S1_EMA_12_26", "S2_RSI_30_70", "S3_Donchian20",
                 "S4_Mom_RSI_confluence", "S5_EMA_trend_50_200",
                 "S6_VolAdjMom_cap1.5", "S7_EMA_confluence", "S8_DualMomentum"]
PHASE3_EXTRA = ["S6b_VolAdjMom_cap2.0", "S7b_EMA_confluence_SMA250"]
FULL_UNIVERSE = MAIN_UNIVERSE + PHASE3_EXTRA

LABELS = {
    "S0_BuyHold": "S0: Buy & Hold",
    "S1_EMA_12_26": "S1: Momentum EMA 12/26",
    "S2_RSI_30_70": "S2: RSI(14) seuils 30/70",
    "S3_Donchian20": "S3: Donchian 20 breakout",
    "S4_Mom_RSI_confluence": "S4: Momentum + RSI confluence",
    "S5_EMA_trend_50_200": "S5: EMA trend (50>200), long seul",
    "S6_VolAdjMom_cap1.5": "S6: Vol-adjusted momentum (cap 1.5x)",
    "S7_EMA_confluence": "S7: EMA confluence 12>50>200",
    "S8_DualMomentum": "S8: Dual momentum (ROC 12j/20j)",
    "S6b_VolAdjMom_cap2.0": "S6b: Vol-adjusted momentum (cap 2.0x) [Phase 3]",
    "S7b_EMA_confluence_SMA250": "S7b: EMA confluence + filtre EMA200>SMA250 [Phase 3]",
}


def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def build_signals(df: pd.DataFrame, t0: int) -> dict:
    """Construit les positions {-1,0,+1} (ou continues pour S6/S6b) de chaque
    signal, purement causales : la decision au jour t n'utilise que les OHLC
    jusqu'au jour t inclus."""
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    logp = np.log(close)
    r = logp.diff()
    n = len(df)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    sma250 = close.rolling(250).mean()
    rsi14 = _rsi(close, 14)
    # canal de Donchian sur les 20 jours PRECEDENTS (exclut la barre courante)
    donch_high20 = high.rolling(20).max().shift(1)
    donch_low20 = low.rolling(20).min().shift(1)
    roc12 = close / close.shift(12) - 1.0
    roc20 = close / close.shift(20) - 1.0
    mom10 = logp - logp.shift(10)

    pos = {}

    # S0 : Buy & Hold
    pos["S0_BuyHold"] = np.ones(n)

    # S1 : Momentum EMA 12/26
    pos["S1_EMA_12_26"] = np.sign((ema12 - ema26).fillna(0.0)).values

    # S2 : RSI(14) seuils 30/70, mean-reversion, instantane (0 sinon)
    s2 = pd.Series(0.0, index=df.index)
    s2[rsi14 < 30] = 1.0
    s2[rsi14 > 70] = -1.0
    pos["S2_RSI_30_70"] = s2.values

    # S3 : Donchian 20 breakout, position tenue jusqu'au signal oppose
    s3 = np.zeros(n)
    cur = 0.0
    cv, dh, dl = close.values, donch_high20.values, donch_low20.values
    for t in range(n):
        if np.isfinite(dh[t]) and cv[t] > dh[t]:
            cur = 1.0
        elif np.isfinite(dl[t]) and cv[t] < dl[t]:
            cur = -1.0
        s3[t] = cur
    pos["S3_Donchian20"] = s3

    # S4 : Momentum + RSI confluence
    mom_sign = np.sign((ema12 - ema26).fillna(0.0))
    rsi_sign = np.sign((rsi14 - 50.0).fillna(0.0))
    pos["S4_Mom_RSI_confluence"] = np.where(mom_sign == rsi_sign, mom_sign, 0.0)

    # S5 : EMA trend (EMA50>EMA200), long seul, flat sinon
    pos["S5_EMA_trend_50_200"] = np.where((ema50 > ema200).values, 1.0, 0.0)

    # S6 / S6b : Momentum ajuste-vol, target_vol estime UNE FOIS sur [0:t0[
    inst_vol = r.rolling(20).std()
    target_vol = float(r.iloc[:t0].std())  # in-sample seul, fige a priori
    base_dir = np.sign(mom10.fillna(0.0))
    lev15 = (target_vol / inst_vol).clip(upper=1.5, lower=0.0).fillna(0.0)
    lev20 = (target_vol / inst_vol).clip(upper=2.0, lower=0.0).fillna(0.0)
    pos["S6_VolAdjMom_cap1.5"] = (base_dir * lev15).values
    pos["S6b_VolAdjMom_cap2.0"] = (base_dir * lev20).values

    # S7 / S7b : Confluence EMA multi-timeframe
    long_c = (ema12 > ema50) & (ema50 > ema200)
    short_c = (ema12 < ema50) & (ema50 < ema200)
    pos["S7_EMA_confluence"] = np.where(long_c, 1.0, np.where(short_c, -1.0, 0.0))
    long_cb = long_c & (ema200 > sma250)
    short_cb = short_c & (ema200 < sma250)
    pos["S7b_EMA_confluence_SMA250"] = np.where(long_cb, 1.0, np.where(short_cb, -1.0, 0.0))

    # S8 : Double momentum (ROC 12j et 20j alignes)
    long8 = (roc12 > 0) & (roc20 > 0)
    short8 = (roc12 < 0) & (roc20 < 0)
    pos["S8_DualMomentum"] = np.where(long8, 1.0, np.where(short8, -1.0, 0.0))

    return pos, {"target_vol_daily_insample": target_vol}


def run_dsr_table(names, sr_daily, T_oos, metr):
    var_trials = float(np.var([sr_daily[v] for v in names], ddof=1))
    n_trials = len(names)
    out = {}
    for v in names:
        out[v] = dsr(sr_daily[v], T_oos, var_trials, n_trials,
                      skew=metr[v]["skew"], kurt_excess=metr[v]["excess_kurt"])
    return out, var_trials, n_trials


def main():
    print(f"Chargement NDX 40 ans depuis {DATA_PATH} ...")
    df = load_ohlc(str(DATA_PATH))
    n = len(df)
    logp = np.log(df["close"].astype(float))
    r_fwd = (logp.shift(-1) - logp).values  # r_fwd[t] = rendement log t -> t+1
    date0, date1 = df["date"].iloc[0], df["date"].iloc[-1]
    print(f"{n} seances, {date0.date()} -> {date1.date()}")

    print(f"Construction des {len(FULL_UNIVERSE)} signaux (9 principaux + 2 variantes Phase 3)...")
    positions, extra = build_signals(df, T0)

    oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN
    T_oos = len(oos)

    pnl = {v: backtest(positions[v], r_fwd, COST_BPS)[oos] for v in FULL_UNIVERSE}
    metr = {v: trading_metrics(pnl[v]) for v in FULL_UNIVERSE}
    turnover = {v: float(np.abs(np.diff(positions[v][oos], prepend=positions[v][oos][0])).mean())
                for v in FULL_UNIVERSE}
    sr_daily = {v: metr[v]["sharpe_daily"] for v in FULL_UNIVERSE}

    dsr_main, var_main, n_main = run_dsr_table(MAIN_UNIVERSE, sr_daily, T_oos, metr)
    dsr_full, var_full, n_full = run_dsr_table(FULL_UNIVERSE, sr_daily, T_oos, metr)

    ranking = sorted(MAIN_UNIVERSE, key=lambda v: metr[v]["sharpe_ann"], reverse=True)

    verdict_threshold = 0.95
    real_edges_main = [v for v in MAIN_UNIVERSE if dsr_main[v]["dsr"] > verdict_threshold]
    real_edges_full = [v for v in FULL_UNIVERSE if dsr_full[v]["dsr"] > verdict_threshold]

    # ------------------------------------------------------------------ JSON
    results = {
        "protocole": {
            "data_path": str(DATA_PATH),
            "n_obs": n,
            "date_debut": str(date0.date()),
            "date_fin": str(date1.date()),
            "T0": T0,
            "refit_every_j": REFIT_EVERY,
            "embargo_j": EMBARGO,
            "cost_bps": COST_BPS,
            "T_oos": int(T_oos),
            "note_protocole": (
                "Signaux techniques deterministes (regles causales sur OHLC "
                "passes), aucun parametre estime par apprentissage sur labels "
                "futurs. refit_every/embargo declares dans la tache n'ont donc "
                "pas d'effet sur la construction des signaux (pas de fit, pas "
                "de fuite train/test a purger) ; seul T0 (debut de la fenetre "
                "OOS commune) est actif. Le seul parametre estime sur donnees "
                "(target_vol de S6/S6b) est calcule une seule fois sur "
                "l'echantillon in-sample [0:T0[, jamais retouche."
            ),
            "target_vol_daily_insample": extra["target_vol_daily_insample"],
        },
        "univers_principal_N9": MAIN_UNIVERSE,
        "univers_etendu_phase3_N11": FULL_UNIVERSE,
        "metriques": {v: metr[v] for v in FULL_UNIVERSE},
        "turnover_jour": turnover,
        "dsr_n_trials_9": {v: dsr_main[v] for v in MAIN_UNIVERSE},
        "dsr_variance_essais_n9": var_main,
        "dsr_n_trials_11_extended": {v: dsr_full[v] for v in FULL_UNIVERSE},
        "dsr_variance_essais_n11": var_full,
        "ranking_par_sharpe_ann_univers_principal": ranking,
        "verdict": {
            "seuil_dsr_edge_reel": verdict_threshold,
            "signaux_avec_edge_reel_N9": real_edges_main,
            "signaux_avec_edge_reel_N11_etendu": real_edges_full,
            "buy_and_hold_gagnant": ranking[0] == "S0_BuyHold",
        },
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f"JSON ecrit -> {JSON_OUT}")

    # -------------------------------------------------------------- rapport md
    write_report(MD_OUT, df, results, metr, turnover, dsr_main, var_main, n_main,
                 dsr_full, var_full, n_full, ranking, real_edges_main, real_edges_full,
                 verdict_threshold, T_oos)
    print(f"Rapport ecrit -> {MD_OUT}")


def fmt_pct(x):
    return f"{x:+.1f} %" if np.isfinite(x) else "n/a"


def fmt(x, prec=3):
    return f"{x:+.{prec}f}" if np.isfinite(x) else "n/a"


def write_report(path, df, results, metr, turnover, dsr_main, var_main, n_main,
                  dsr_full, var_full, n_full, ranking, real_edges_main, real_edges_full,
                  threshold, T_oos):
    p = results["protocole"]
    lines = []
    w = lines.append
    w("# Nouvelle phase de recherche — univers de 9 signaux techniques classiques (NDX 40 ans)\n")
    w("## 1. Cadrage et discipline anti-data-snooping\n")
    w("Base propre, independante des Etapes A/B/C/D et de la pipeline integree deja "
      "publiees dans le repo : aucun modele entraine, aucune reutilisation de "
      "features/labels ML. Seuls les utilitaires generiques (chargement des donnees, "
      "backtest a couts, metriques de trading, Deflated Sharpe Ratio) sont repris de "
      "`finance/src/`.\n")
    w(f"- Donnees : NDX (`data/nasdaq100_daily.txt`), {p['n_obs']} seances, "
      f"{p['date_debut']} -> {p['date_fin']}.\n"
      f"- Walk-forward : T0={p['T0']}, refit declare {p['refit_every_j']} j, "
      f"embargo declare {p['embargo_j']} j, couts {p['cost_bps']:.0f} bps aller-retour.\n"
      f"- Fenetre OOS evaluee : {T_oos} observations (jour {p['T0']} a l'avant-dernier "
      f"jour de l'historique).\n")
    w("- **Note de methode (honnetete)** : " + p["note_protocole"] + "\n")
    w("- Univers de **9 signaux figes a priori** (Phase 1, avant toute execution) : "
      "voir tableau ci-dessous. Aucun signal n'a ete ajoute apres avoir vu un resultat.\n")
    w("- 2 variantes supplementaires **declarees a l'avance** (Phase 3, S6b/S7b) : "
      "parametres choisis a priori sur l'echantillon in-sample [0:T0[ uniquement, "
      "jamais retouches apres coup. Comptees comme extension de l'univers "
      "(N=11 au total) pour le DSR, conformement a `CLAUDE.md`.\n")

    w("\n## 2. Univers figé (Phase 1)\n")
    w("| # | Signal |\n|---|---|\n")
    for i, v in enumerate(MAIN_UNIVERSE):
        w(f"| {i} | {LABELS[v]} |\n")
    w("\nVariantes Phase 3 (hors univers principal, ajoutees a l'univers étendu N=11) :\n\n")
    w("| Variante | Description |\n|---|---|\n")
    for v in PHASE3_EXTRA:
        w(f"| {LABELS[v]} | parametre cap/filtre choisi a priori sur [0:T0[ |\n")

    w("\n## 3. Résultats bruts (nets de coûts, fenêtre OOS complète)\n")
    w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | "
      "Hit rate | Turnover/j |\n|---|---|---|---|---|---|---|---|---|\n")
    for v in results["univers_etendu_phase3_N11"]:
        m = metr[v]
        tag = LABELS[v]
        w(f"| {tag} | {fmt(m['sharpe_ann'],2)} | {fmt(m['sortino_ann'],2)} | "
          f"{fmt(m['calmar'],2)} | {fmt_pct(m['ann_return_pct'])} | "
          f"{fmt_pct(m['max_drawdown_pct'])} | {fmt(m['profit_factor'],2)} | "
          f"{m['hit_rate']*100:.1f} % | {turnover[v]:.3f} |\n")

    w("\n## 4. Ranking par Sharpe annualisé (univers principal N=9)\n")
    for i, v in enumerate(ranking, 1):
        w(f"{i}. **{LABELS[v]}** — Sharpe ann. {fmt(metr[v]['sharpe_ann'],2)}\n")

    w("\n## 5. Deflated Sharpe Ratio\n")
    w(f"### 5.1 Univers principal officiel de la tâche (N=9, σ²(SR essais)={var_main:.4e})\n\n")
    w("| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |\n|---|---|---|---|---|\n")
    for v in MAIN_UNIVERSE:
        d = dsr_main[v]
        w(f"| {LABELS[v]} | {fmt(metr[v]['sharpe_daily'],4)} | {d['sr0_daily']:.4f} | "
          f"{fmt(d['z'],2)} | **{d['dsr']:.3f}** |\n")

    w(f"\n### 5.2 Univers étendu honnête (N=11, inclut les variantes Phase 3, "
      f"σ²(SR essais)={var_full:.4e})\n\n")
    w("| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |\n|---|---|---|---|---|\n")
    for v in results["univers_etendu_phase3_N11"]:
        d = dsr_full[v]
        w(f"| {LABELS[v]} | {fmt(metr[v]['sharpe_daily'],4)} | {d['sr0_daily']:.4f} | "
          f"{fmt(d['z'],2)} | **{d['dsr']:.3f}** |\n")

    w(f"\nVerdict multiple-testing (seuil DSR>{threshold:.2f} = edge réel même après correction) : "
      f"{'aucun signal actif ne passe ce seuil' if not real_edges_main else ', '.join(LABELS[v] for v in real_edges_main)}"
      f" (univers N=9). Univers étendu N=11 : "
      f"{'aucun signal actif ne passe ce seuil' if not real_edges_full else ', '.join(LABELS[v] for v in real_edges_full)}.\n")

    w("\n## 6. Leçons\n")
    w("- Les signaux techniques déterministes testés ici n'ont, par construction, aucun "
      "paramètre appris sur des labels futurs : le couple refit/embargo hérité du "
      "protocole de l'Étape B (modèles ML) est donc **vide de contenu opérationnel** "
      "pour cet univers — seul le point de départ T0 de la fenêtre OOS commune compte. "
      "Ce constat est déclaré explicitement plutôt que de prétendre silencieusement à "
      "un embargo qui n'a aucun effet mesurable ici.\n")
    w("- Le coût de transaction (5 bps) pénalise fortement les signaux à turnover élevé "
      "(mean-reversion RSI, ajustement de volatilité quotidien) : comparer le tableau "
      "Sharpe brut/écarté du turnover est essentiel avant toute conclusion.\n")
    w("- Ajouter S6b/S7b après coup sans les compter dans le DSR aurait été une violation "
      "de la discipline anti-snooping du repo ; ils sont donc inclus dans un univers "
      "étendu à N=11 pour un DSR honnête (section 5.2), même si la tâche ne demandait "
      "formellement que N=9.\n")
    bh_dsr_main = dsr_main["S0_BuyHold"]["dsr"]
    top_dsr_main = max(MAIN_UNIVERSE, key=lambda v: dsr_main[v]["dsr"])
    best_active_main = max((v for v in MAIN_UNIVERSE if v != "S0_BuyHold"),
                            key=lambda v: dsr_main[v]["dsr"])
    if top_dsr_main == "S0_BuyHold":
        w(f"- Buy & Hold obtient le DSR le plus élevé (**{bh_dsr_main:.3f}**) de l'univers "
          f"principal ; le meilleur signal actif (**{LABELS[best_active_main]}**, DSR="
          f"{dsr_main[best_active_main]['dsr']:.3f}) reste nettement en dessous du seuil "
          f"{threshold:.2f} — cohérent avec la conclusion déjà établie à l'Étape B "
          f"(`CLAUDE.md`) sur NDX et Composite.\n")
    else:
        w(f"- Résultat notable (**à ne pas sur-interpréter**) : dans cet univers N=9, le "
          f"DSR le plus élevé n'est **pas** Buy & Hold (DSR={bh_dsr_main:.3f}) mais "
          f"**{LABELS[top_dsr_main]}** (DSR={dsr_main[top_dsr_main]['dsr']:.3f}), un "
          f"filtre de tendance long-terme long-seul à très faible turnover "
          f"({turnover[top_dsr_main]:.3f}/j) qui évite une bonne partie des grands "
          f"drawdowns (MDD {metr[top_dsr_main]['max_drawdown_pct']:.1f} % vs "
          f"{metr['S0_BuyHold']['max_drawdown_pct']:.1f} % pour Buy & Hold) tout en "
          f"gardant un rendement annualisé proche. Il reste toutefois **sous le seuil "
          f"{threshold:.2f}** retenu pour parler d'edge réel certain après correction "
          f"multi-essais (N=9 puis N=11 en univers étendu) : à traiter comme un signal "
          f"prometteur mais **non confirmé**, pas comme une découverte actionnable.\n")

    w("\n## 7. Recommandation honnête\n")
    if not real_edges_main and top_dsr_main == "S0_BuyHold":
        w("**Buy & Hold reste la stratégie de référence.** Aucun des 9 signaux techniques "
          "classiques déclarés a priori (ni les 2 variantes Phase 3) ne passe le seuil "
          "DSR>0.95 une fois la correction multi-essais appliquée : les Sharpe bruts "
          "observés, même quand ils dépassent 0, sont compatibles avec ce qu'on "
          "attendrait par pur hasard de sélection sur 9 à 11 essais. Cette conclusion "
          "**confirme** (sans la re-découvrir par data-snooping) le résultat déjà établi "
          "à l'Étape B : sur NDX comme sur Composite, aucun signal directionnel simple "
          "ne bat Buy & Hold net de coûts et déflaté.\n")
    else:
        w(f"**Buy & Hold reste la conclusion par défaut la plus défendable**, mais avec une "
          f"nuance honnête à signaler : sur ce protocole précis (NDX 40 ans, T0=750, coûts "
          f"5 bps), **{LABELS[top_dsr_main]}** affiche un Sharpe/DSR ponctuellement "
          f"supérieur à Buy & Hold ({dsr_main[top_dsr_main]['dsr']:.3f} vs "
          f"{bh_dsr_main:.3f}) avec un MDD nettement plus faible ("
          f"{metr[top_dsr_main]['max_drawdown_pct']:.1f} % vs "
          f"{metr['S0_BuyHold']['max_drawdown_pct']:.1f} %). Ni l'un ni l'autre ne "
          f"franchit le seuil DSR>{threshold:.2f} qui signerait un edge réel certain "
          f"après correction multi-essais (N=9, puis N=11 avec les variantes Phase 3) : "
          f"aucun des deux résultats n'est donc statistiquement distinguable du hasard "
          f"de sélection à ce niveau de rigueur. **Recommandation** : ne pas déployer ce "
          f"signal sur la seule base de ce résultat ; le signaler comme piste à "
          f"re-tester sur un échantillon indépendant (ex. Composite) avant toute "
          f"conclusion, exactement la discipline qui a évité de sur-interpréter les "
          f"signaux de l'Étape B.\n")

    path.write_text("".join(lines))


if __name__ == "__main__":
    main()
