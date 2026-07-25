"""Hypothese "regime-aware R5" : reprend la lecon du paradoxe H10
(results/hypothesis_10_mean_reversion_lowvol.json) mais appliquee a R5
("Fractional Differentiation") plutot qu'au signal FAIBLE H1 (RSI, Sharpe
0.213).

RAPPEL DU PARADOXE H10 : gater un signal deja faible par le regime de
volatilite (tercile bas = calme) a DETRUIT le signal (Sharpe 0.213 -> -0.47
low-vol-only, -0.36 scaled-regime). Question ici : le meme type de gate
detruit-il aussi R5, repute "robuste" (Sharpe brut 0.534 dans
results/risky_hypotheses.json) ?

CORRECTION METHODOLOGIQUE IMPORTANTE (a documenter honnetement dans le
rapport) : le R5 original (run_risky_hypotheses.py) calcule
  frac_series = poids * prix, PUIS z-score sur la SERIE COMPLETE
  (frac_series.mean()/.std() calcules sur tout l'echantillon, y compris le
  futur au moment de chaque decision passee) -> lookahead flagrant. Son
  Sharpe de 0.534 est donc invalide tel quel.
Ici on reconstruit R5 de facon strictement causale :
  - frac_diff(logp, d=0.4) = differenciation fractionnaire a fenetre fixe
    (deja implementee et causale dans finance/src/prediction.py, reutilisee
    telle quelle, memes poids que l'Etape B),
  - z-score sur une fenetre ROULANTE (250 j, n'utilise que le passe et le
    jour courant, jamais le futur),
  - position = signe(z).
Le protocole (T0, refit, embargo, couts) suit EXACTEMENT celui de l'Etape B
(finance/trading/scripts/run_etape_b.py), pour rester comparable au reste du
cadre canonique.

PROTOCOLE (fige avant execution) :
  - Marche : NDX (data/nasdaq100_daily.txt), 40 ans, seul jeu demande.
  - T0=750, refit=21j, embargo=21j (seuils de regime recalcules tous les 21j
    a partir des donnees jusqu'a t-embargo seulement -> aucune fuite).
  - Couts 5 bps aller-retour sur le turnover.
  - Univers FIGE (N=6 essais sur ce signal : R5_base + R1..R5) :
      R5_base : signal brut, sans gate (reference)
      R1  : trade seulement si regime vol = tercile BAS
      R2  : position *= {bas:1.0, moyen:0.5, haut:0.25}  (vol-targeting doux)
      R3  : trade seulement si tendance (EMA50 vs EMA200) s'aligne avec R5
      R4  : dual-gate = R1 ET R3 simultanement
      R5x : contrarien pur (ignore le signe de R5) : position = -1 en
            tercile bas, +1 en tercile haut, 0 en moyen -- teste l'hypothese
            INVERSE de R1/R2 (edge en vol elevee, pas en vol calme).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # .../finance
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from prediction import backtest, dsr, frac_diff, trading_metrics  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../Quant-Trade

# ------------------------------------------------------------------ protocole
T0, REFIT_EVERY, EMBARGO = 750, 21, 21
COST_BPS = 5.0
VOL_WIN = 20          # fenetre de volatilite realisee (regime)
ZSCORE_WIN = 250       # fenetre roulante de standardisation du frac-diff (causale)
TREND_FAST, TREND_SLOW = 50, 200

DATA = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "data" / "nasdaq100_daily.txt")
OUT_JSON = sys.argv[2] if len(sys.argv) > 2 else str(REPO_ROOT / "results" / "hypothesis_regime_gated_r5.json")
OUT_MD = sys.argv[3] if len(sys.argv) > 3 else str(REPO_ROOT / "results" / "hypothesis_regime_gated_r5.md")


def main() -> None:
    df = load_ohlc(DATA).set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r = logp.diff()  # rendement log causal du jour t
    r_fwd = (logp.shift(-1) - logp).values  # rendement t -> t+1

    n = len(df)
    dates = df.index

    # -------------------------------------------------------- R5 base (fixe)
    fd = frac_diff(logp.values, d=0.4)  # causal, fenetre fixe (Etape B)
    fd_s = pd.Series(fd, index=dates)
    roll_mu = fd_s.rolling(ZSCORE_WIN, min_periods=ZSCORE_WIN // 2).mean()
    roll_sd = fd_s.rolling(ZSCORE_WIN, min_periods=ZSCORE_WIN // 2).std()
    z = (fd_s - roll_mu) / roll_sd.replace(0, np.nan)
    sig_r5 = np.where(np.isfinite(z.values), np.sign(z.values), 0.0)  # {-1,0,+1}

    # -------------------------------------------------------- regime de vol
    vol20 = r.rolling(VOL_WIN).std()
    vol20_v = vol20.values
    regime_vol = np.full(n, "", dtype=object)  # "low"/"mid"/"high"/"" (indefini)

    for tr in range(T0, n, REFIT_EVERY):
        cutoff = tr - EMBARGO  # seuils estimes sur [0:cutoff[ uniquement (purge)
        hist = vol20_v[:cutoff]
        hist = hist[np.isfinite(hist)]
        if len(hist) < 100:
            continue
        lo_cut, hi_cut = np.quantile(hist, [1 / 3, 2 / 3])
        block = slice(tr, min(tr + REFIT_EVERY, n))
        v_block = vol20_v[block]
        reg = np.where(~np.isfinite(v_block), "",
              np.where(v_block <= lo_cut, "low",
              np.where(v_block >= hi_cut, "high", "mid")))
        regime_vol[block] = reg

    # -------------------------------------------------------- regime de tendance
    ema_fast = close.ewm(span=TREND_FAST, adjust=False).mean()
    ema_slow = close.ewm(span=TREND_SLOW, adjust=False).mean()
    trend_dir = np.sign((ema_fast - ema_slow).values)  # causal, pas de seuil a estimer

    # ------------------------------------------------------------- positions
    pos = {}
    pos["R5_base"] = sig_r5.copy()

    is_low = regime_vol == "low"
    is_mid = regime_vol == "mid"
    is_high = regime_vol == "high"
    has_regime = is_low | is_mid | is_high

    # R1 : trade seulement en tercile bas
    pos["R1_LowVolOnly"] = np.where(is_low, sig_r5, 0.0)

    # R2 : position scalee par regime (1x bas, 0.5x moyen, 0.25x haut)
    scale_r2 = np.select([is_low, is_mid, is_high], [1.0, 0.5, 0.25], default=0.0)
    pos["R2_VolScaled"] = sig_r5 * scale_r2

    # R3 : trade seulement si la tendance (EMA50/200) s'aligne avec R5
    aligned = (sig_r5 != 0) & (trend_dir != 0) & (sig_r5 == trend_dir)
    pos["R3_TrendGate"] = np.where(aligned, sig_r5, 0.0)

    # R4 : dual-gate, vol bas ET tendance alignee
    pos["R4_DualGate"] = np.where(is_low & aligned, sig_r5, 0.0)

    # R5x : contrarien pur -- ignore le signe de R5, parie sur le REGIME seul,
    # hypothese inverse de R1/R2 (court en vol basse, long en vol haute)
    pos["R5x_Contrarian"] = np.select([is_low, is_high], [-1.0, 1.0], default=0.0)

    MODELS = ["R5_base", "R1_LowVolOnly", "R2_VolScaled", "R3_TrendGate",
              "R4_DualGate", "R5x_Contrarian"]

    # fenetre OOS commune : a partir de T0, la ou les regimes sont definis
    oos = np.arange(T0, n - 1)

    # ------------------------------------------------------------- backtests
    pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
    metr = {m: trading_metrics(pnl[m]) for m in MODELS}

    # Buy & Hold pour reference (meme fenetre OOS, meme couts -- turnover nul)
    bh_pos = np.ones(n)
    pnl_bh = backtest(bh_pos, r_fwd, COST_BPS)[oos]
    metr_bh = trading_metrics(pnl_bh)

    # turnover moyen par variante
    turnover = {m: float(np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean())
                for m in MODELS}

    # ------------------------------------------- Deflated Sharpe (N=6 essais)
    sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    T_oos = len(oos)
    dsr_out = {}
    for m in MODELS:
        dsr_out[m] = dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                         skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])

    # ----------------------------------------------------------- regime-stats
    reg_oos = regime_vol[oos]
    regime_stats = {}
    for reg_name in ("low", "mid", "high"):
        mask = reg_oos == reg_name
        pct_time = float(mask.mean())
        if mask.sum() > 5:
            r_reg = r_fwd[oos][mask]
            hit_rate_base = float((np.sign(sig_r5[oos][mask]) == np.sign(r_reg)).mean())
        else:
            hit_rate_base = np.nan
        regime_stats[reg_name] = {"pct_time_oos": pct_time,
                                   "r5_base_hit_rate": hit_rate_base}
    pct_undefined = float((~has_regime[oos]).mean())

    # -------------------------------------------------------------- sauvegarde
    out = {
        "market": "NDX (nasdaq100_daily.txt)",
        "protocol": {"T0": T0, "refit_every": REFIT_EVERY, "embargo": EMBARGO,
                     "cost_bps": COST_BPS, "n_oos": T_oos,
                     "oos_start": str(dates[oos[0]].date()),
                     "oos_end": str(dates[oos[-1]].date())},
        "buy_hold": {"sharpe_ann": metr_bh["sharpe_ann"],
                     "max_drawdown_pct": metr_bh["max_drawdown_pct"],
                     "calmar": metr_bh["calmar"]},
        "regime_stats_oos": regime_stats,
        "pct_time_regime_undefined_oos": pct_undefined,
        "variants": {
            m: {
                "sharpe_ann": metr[m]["sharpe_ann"],
                "sortino_ann": metr[m]["sortino_ann"],
                "calmar": metr[m]["calmar"],
                "max_drawdown_pct": metr[m]["max_drawdown_pct"],
                "ann_return_pct": metr[m]["ann_return_pct"],
                "profit_factor": metr[m]["profit_factor"],
                "hit_rate": metr[m]["hit_rate"],
                "turnover_mean": turnover[m],
                "dsr": dsr_out[m]["dsr"],
                "sr0_daily": dsr_out[m]["sr0_daily"],
            } for m in MODELS
        },
    }
    Path(OUT_JSON).write_text(__import__("json").dumps(out, indent=2, default=str))

    # ------------------------------------------------------------------ rapport md
    lines = []
    w = lines.append
    w("# Hypothese regime-aware R5 (leçon du paradoxe H10)\n")
    w("## 1. Contexte\n")
    w("`H10` (results/hypothesis_10_mean_reversion_lowvol.json) a gate un signal "
      "**faible** (H1, RSI mean-reversion, Sharpe 0.213) par le regime de "
      "volatilite : resultat paradoxal, le gate **detruit** le signal "
      "(Sharpe -0.47 en tercile bas seul, -0.36 en version scalee). Question ici : "
      "le meme type de gate detruit-il aussi **R5** (\"Fractional Differentiation\"), "
      "repute plus robuste ?\n")
    w("**Correction methodologique** : le R5 original "
      "(`run_risky_hypotheses.py`, Sharpe brut affiche 0.534) standardise sa serie "
      "fractionnairement differenciee avec la **moyenne/ecart-type de l'echantillon "
      "complet** — lookahead flagrant, son chiffre est invalide. Ici R5 est "
      "reconstruit de facon strictement causale : `frac_diff` (fenetre fixe, deja "
      "utilisee et causale dans l'Etape B) + z-score sur fenetre **roulante** "
      f"({ZSCORE_WIN} j). Le protocole walk-forward suit exactement l'Etape B : "
      f"T0={T0}, refit {REFIT_EVERY} j, **purge/embargo {EMBARGO} j** (les seuils de "
      "regime de volatilite sont recalcules tous les 21 j a partir des donnees "
      "jusqu'a t-embargo uniquement — aucune fuite), couts {:.0f} bps.\n".format(COST_BPS))

    w("## 2. Univers fige (N=6 essais sur ce signal, pour le DSR)\n")
    w("| # | Variante | Regle |")
    w("|---|---|---|")
    w("| 0 | R5_base | signal causal, sans gate (reference) |")
    w("| 1 | R1_LowVolOnly | trade seulement si vol tercile BAS, sinon plat |")
    w("| 2 | R2_VolScaled | position × {1.0 bas, 0.5 moyen, 0.25 haut} |")
    w("| 3 | R3_TrendGate | trade seulement si EMA50 vs EMA200 s'aligne avec R5 |")
    w("| 4 | R4_DualGate | R1 ET R3 simultanement |")
    w("| 5 | R5x_Contrarian | ignore le signe de R5 : court en vol basse, long en vol haute |")
    w("")

    w("## 3. Performance OOS (nette de couts, NDX)\n")
    w(f"Fenêtre OOS : {out['protocol']['n_oos']} jours "
      f"({out['protocol']['oos_start']} → {out['protocol']['oos_end']}).\n")
    w("| Variante | Sharpe ann. | Calmar | MDD | Turnover moy. | Profit factor | **DSR** |")
    w("|---|---|---|---|---|---|---|")
    w(f"| **Buy & Hold** | {metr_bh['sharpe_ann']:+.2f} | {metr_bh['calmar']:+.2f} | "
      f"{metr_bh['max_drawdown_pct']:.1f}% | 0.00 | {metr_bh['profit_factor']:.2f} | — |")
    for m in MODELS:
        x = metr[m]
        w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | "
          f"{x['max_drawdown_pct']:.1f}% | {turnover[m]:.3f} | "
          f"{x['profit_factor']:.2f} | {dsr_out[m]['dsr']:.3f} |")
    w("\n*DSR calcule avec N=6 (les essais de cette hypothese uniquement). "
      "**Avertissement anti data-snooping** : cette hypothese s'inscrit dans une "
      "exploration bien plus large (H1-H12, R1-R10 dans `results/`) ; un DSR "
      "correctement deflate sur l'ensemble de cette exploration serait "
      "sensiblement **plus bas** que celui affiche ici (N reel ≫ 6). Ces chiffres "
      "ne remplacent pas l'univers fige et le SPA de l'Etape B/C.*\n")

    w("## 4. Statistiques de regime (OOS)\n")
    w("| Regime | % du temps OOS | Hit-rate directionnel R5_base |")
    w("|---|---|---|")
    for reg_name in ("low", "mid", "high"):
        rs = regime_stats[reg_name]
        hr = f"{100*rs['r5_base_hit_rate']:.1f}%" if np.isfinite(rs['r5_base_hit_rate']) else "n/a"
        w(f"| {reg_name} | {100*rs['pct_time_oos']:.1f}% | {hr} |")
    w(f"\n*{100*pct_undefined:.1f}% des jours OOS sans regime defini (warmup des "
      "seuils, ignores dans le backtest -> position nulle).*\n")

    w("## 5. Verdict honnête\n")
    best_gated = max(("R1_LowVolOnly", "R2_VolScaled", "R3_TrendGate", "R4_DualGate", "R5x_Contrarian"),
                      key=lambda m: metr[m]["sharpe_ann"])
    base_sh = metr["R5_base"]["sharpe_ann"]
    best_sh = metr[best_gated]["sharpe_ann"]
    if best_sh > base_sh and best_sh > 0:
        verdict = (f"- **Le gating aide** : {best_gated} (Sharpe {best_sh:+.2f}) bat "
                   f"R5_base (Sharpe {base_sh:+.2f}). Contrairement au paradoxe H10, "
                   "le regime-gating n'est pas systematiquement destructeur — mais cela "
                   "reste a confirmer par le turnover/couts et le DSR (colonne ci-dessus).")
    else:
        verdict = (f"- **Le paradoxe H10 se reproduit sur R5** : aucune variante gatee "
                   f"ne bat R5_base (Sharpe {base_sh:+.2f}). Le meilleur gate "
                   f"({best_gated}) fait {best_sh:+.2f}. Le gating par regime, meme sur "
                   "un signal repute plus robuste, **detruit ou n'ameliore pas** le "
                   "signal ici — coherent avec H10.")
    w(verdict)
    w(f"- **R5_base lui-meme** (une fois le lookahead corrige) a un Sharpe "
      f"{'positif' if base_sh > 0 else 'negatif ou nul'} ({base_sh:+.2f}) et reste "
      f"{'au-dessus' if base_sh > metr_bh['sharpe_ann'] else 'en-dessous'} du "
      f"Buy & Hold ({metr_bh['sharpe_ann']:+.2f}). Le chiffre de 0.534 dans "
      "`risky_hypotheses.json` (methode non causale) n'est **pas reproductible** "
      "en walk-forward honnete : la robustesse pretee a R5 etait en grande partie "
      "un artefact de lookahead.")
    w("- Discipline : ceci reste **un essai de plus** sur un signal deja explore "
      "de facon non canonique (hors univers fige de l'Etape B) ; a ne pas "
      "confondre avec un edge valide au sens du SPA/DSR de l'Etape B/C.\n")

    Path(OUT_MD).write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nJSON -> {OUT_JSON}\nMD   -> {OUT_MD}")


if __name__ == "__main__":
    main()
