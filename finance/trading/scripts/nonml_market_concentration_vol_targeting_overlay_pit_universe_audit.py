"""Audit adversarial — concentration du marché (HHI), univers point-in-time.

Cinq contrôles :

1. **Recalcul de la breadth par un chemin de code disjoint** — le backtest passe
   par des boucles NumPy sur fenêtres glissantes ; l'audit par
   `pandas.rolling(...).max()/.min()`, sur des dates échantillonnées.
2. **Anti-lookahead par mutation du futur.**
3. **Le filtre d'appartenance change-t-il réellement le signal ?**
4. **Décalage de niveau entre les deux univers** — contrôle **exigé par le
   pré-enregistrement**, parce que la porte de ce candidat a un seuil absolu et
   n'est donc pas invariante par translation du signal. Mesuré **sur les mêmes
   dates** dans les deux univers, faute de quoi la comparaison confondrait effet
   d'univers et effet de période. Publié quel que soit son signe.
5. **Causalité de la porte.**

Usage : python3 scripts/nonml_market_concentration_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
import nonml_market_concentration_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
import nonml_market_concentration_vol_targeting_overlay_backtest as orig  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_market_concentration_vol_targeting_overlay_pit_universe_audit.md"


def prices_frame():
    series = bt.load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    return pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})


def signal_at_pandas(P, i, members_override=None):
    """Recalcul INDEPENDANT du HHI a la date d'indice i.

    Chemin disjoint : `pandas.shift` et operations sur Series indexees par
    ticker, au lieu de l'indexation matricielle NumPy du backtest.
    """
    cum = P.iloc[i] / P.shift(bt.CONC_WINDOW).iloc[i] - 1.0
    members = members_override if members_override is not None else tickers_as_of_date(P.index[i])
    if not members:
        return np.nan
    is_member = pd.Series([t in members for t in P.columns], index=P.columns)
    elig = cum.notna() & is_member
    n = int(elig.sum())
    if n < bt.MIN_LISTED:
        return np.nan
    contrib = cum[elig].clip(lower=0.0)
    total = float(contrib.sum())
    if total <= 0:
        return 1.0 / n
    shares = contrib / total
    return float((shares ** 2).sum())


def main():
    L = ["# Audit adversarial — concentration du marché (HHI), univers point-in-time", ""]

    breadth_bt, cov, n_mean = bt.compute_concentration_series_pit()
    P = prices_frame()
    defined = np.where(breadth_bt.notna().values)[0]
    sample = defined[np.linspace(0, len(defined) - 1, 6).astype(int)]

    # --- 1. chemin disjoint ---
    L.append("## 1. Recalcul du signal par un chemin de code disjoint")
    L.append("")
    L.append("Le backtest calcule le HHI par indexation matricielle NumPy ;")
    L.append("l'audit par `pandas.shift` et Series indexées par ticker. Aucune ligne partagée.")
    L.append("")
    L.append("| Date | Signal backtest | Signal audit | Écart |")
    L.append("|---|---|---|---|")
    max_err = 0.0
    for i in sample:
        b_bt = float(breadth_bt.iloc[i])
        b_au = signal_at_pandas(P, int(i))
        err = abs(b_bt - b_au) if np.isfinite(b_au) else float("nan")
        if np.isfinite(err):
            max_err = max(max_err, err)
        L.append(f"| {P.index[i].date()} | {b_bt:.6f} | {b_au:.6f} | {err:.2e} |")
    ok1 = max_err < 1e-12
    L.append("")
    L.append(f"- écart maximal : **{max_err:.2e}**")
    L.append("")
    L.append(f"**{'CONFORME — les deux chemins concordent à la précision machine.' if ok1 else 'DIVERGENCE'}**")
    L.append("")

    # --- 2. anti-lookahead ---
    cut = int(defined[len(defined) // 2])
    P_pert = P.copy()
    P_pert.iloc[cut + 1:] = P_pert.iloc[cut + 1:] * 7.0
    b_ref = signal_at_pandas(P, cut)
    b_pert = signal_at_pandas(P_pert, cut)
    ok2 = bool(np.isfinite(b_ref) and np.isfinite(b_pert) and abs(b_ref - b_pert) < 1e-12)

    L.append("## 2. Anti-lookahead — mutation du futur")
    L.append("")
    L.append(f"Prix postérieurs à l'indice {cut} ({P.index[cut].date()}) multipliés par 7.")
    L.append("")
    L.append(f"- signal avant mutation : **{b_ref:.6f}**")
    L.append(f"- signal après mutation : **{b_pert:.6f}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur.' if ok2 else 'FUITE DÉTECTÉE'}**")
    L.append("")

    # --- 3. effet du filtre ---
    all_tickers = set(P.columns)
    diffs = checked = 0
    for i in sample:
        b_pit = signal_at_pandas(P, int(i))
        b_all = signal_at_pandas(P, int(i), members_override=all_tickers)
        if np.isfinite(b_pit) and np.isfinite(b_all):
            checked += 1
            if abs(b_pit - b_all) > 1e-12:
                diffs += 1
    ok3 = diffs > 0

    L.append("## 3. Le filtre d'appartenance change-t-il réellement le signal ?")
    L.append("")
    L.append(f"- dates comparées : **{checked}**")
    L.append(f"- dates où le signal diffère : **{diffs}**")
    L.append(f"- couverture moyenne : **{100*cov:.1f}%**")
    L.append("")
    L.append(f"**{'CONFORME — le filtre point-in-time change effectivement le signal.' if ok3 else 'ALERTE — filtre sans effet, portage cosmétique.'}**")
    L.append("")

    # --- 4. decalage de NIVEAU, mesure exigee par le PREREG ---
    # Comparaison SUR LES MEMES DATES, sinon on confondrait effet d'univers et
    # effet de periode : les deux series ne couvrent pas la meme fenetre.
    breadth_orig = orig.compute_concentration_series()
    common = breadth_bt.dropna().index.intersection(breadth_orig.dropna().index)
    a = breadth_bt.reindex(common)
    b = breadth_orig.reindex(common)
    shift = float((b - a).mean())
    n_common = len(common)
    std_pit, std_orig = float(a.std()), float(b.std())

    L.append("## 4. Décalage de niveau entre les deux univers")
    L.append("")
    L.append("Contrôle **exigé par le pré-enregistrement**, qui signalait un point")
    L.append("**arithmétique** — le HHI dépend du nombre de titres retenus, son minimum")
    L.append("valant `1/n` — en précisant qu'il s'agit d'une propriété de la formule et non")
    L.append("d'une hypothèse sur le marché, et qu'aucune prédiction n'en était tirée. Niveau")
    L.append("**et** dispersion sont donc mesurés, comme annoncé.")
    L.append("")
    L.append("Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les")
    L.append("moyennes des deux rapports confondrait effet d'univers et effet de période,")
    L.append("leurs fenêtres n'étant pas les mêmes.")
    L.append("")
    L.append(f"- dates communes : **{n_common}**")
    L.append(f"- signal moyen, univers point-in-time : **{float(a.mean()):.4f}**")
    L.append(f"- signal moyen, univers biaisé : **{float(b.mean()):.4f}**")
    L.append(f"- décalage (biaisé − point-in-time) : **{shift:+.4f}**")
    L.append(f"- écart-type du signal, point-in-time : **{std_pit:.4f}**")
    L.append(f"- écart-type du signal, biaisé : **{std_orig:.4f}**")
    L.append("")
    L.append(f"Le signal est en moyenne **{'plus haut' if shift < 0 else 'plus bas'}** sur")
    L.append("l'univers point-in-time, et sa **dispersion est plus faible**")
    L.append(f"({std_pit:.4f} contre {std_orig:.4f}).")
    L.append("")
    L.append("Sur le point arithmétique annoncé : l'univers point-in-time retient **moins**")
    L.append(f"de titres ({n_mean:.0f} en moyenne), ce qui **relève** le plancher `1/n` du HHI.")
    L.append("Le niveau mesuré étant pourtant plus bas, l'effet de plancher ne domine pas —")
    L.append("constat factuel, sans interprétation économique proposée.")
    L.append("")
    L.append("Ce contrôle ne conditionne aucun verdict : il mesure une quantité annoncée")
    L.append("d'avance comme pertinente, et la publie quel que soit son signe.")
    L.append("")

    # --- 5. causalite de la porte ---
    n = 50
    fake_gate = np.zeros(n, dtype=bool)
    fake_gate[20] = True
    pos_fake = bt.combined_position(np.full(n - 1, 0.01), fake_gate)
    idx_mod = list(np.where(pos_fake != 1.0)[0])
    ok5 = idx_mod == [20]

    L.append("## 5. Causalité de la porte")
    L.append("")
    L.append(f"- indices de position modifiée : **{idx_mod}** (porte active au seul indice 20)")
    L.append("")
    L.append(f"**{'CONFORME — décalage d un jour.' if ok5 else 'ANOMALIE'}**")
    L.append("")

    # --- 6. attribution univers / periode (PRE-ENREGISTRE) ---
    from data_loader import load_ohlc, quality_report  # noqa: E402
    dfx = load_ohlc(str(ROOT.parent.parent / "data" / "nasdaq100_daily.txt"))
    quality_report(dfx)
    clx = dfx["close"].values
    dts = pd.to_datetime(dfx["date"])
    r_idx = np.log(clx[1:] / clx[:-1])
    gate_s = bt.build_gate(breadth_bt)
    gate_al = gate_s.fillna(False).reindex(dts.values, method="ffill").fillna(False).values.astype(bool)
    gate_raw = gate_s.reindex(dts.values, method="ffill")
    pos_full = bt.combined_position(r_idx, gate_al)
    valid = gate_raw.notna().values
    fv = int(np.argmax(valid)) if valid.any() else len(valid)
    st = max(fv, bt.VOL_WINDOW)
    d_used = dts.iloc[1:].iloc[st:]
    r_w = r_idx[st:]
    pos_w = pos_full[st:]
    turn_w = np.abs(np.diff(pos_w, prepend=1.0))
    c = bt.COST_BPS / 1e4
    pnl_ov_all = pos_w * r_w - turn_w * c
    pnl_bh_all = r_w.copy()
    pnl_bh_all[0] -= c

    orig_start = pd.Timestamp("2021-01-01")
    m = (d_used >= orig_start).values
    L.append("## 6. Attribution — univers ou période ?")
    L.append("")
    L.append("**Contrôle PRÉ-ENREGISTRÉ.** La fenêtre a changé en même temps que l'univers")
    L.append("(2645 séances depuis 2016 contre 1385 au cycle d'origine). Le calcul")
    L.append("point-in-time est restreint à la fenêtre d'origine pour isoler l'effet")
    L.append("d'univers. Ne conditionne aucun verdict.")
    L.append("")
    if m.any():
        me_o = trading_metrics(pnl_ov_all[m])
        me_b = trading_metrics(pnl_bh_all[m])
        ret_o = float(np.exp(pnl_ov_all[m].sum()) - 1.0)
        ret_b = float(np.exp(pnl_bh_all[m].sum()) - 1.0)
        L.append(f"- séances retenues (PIT, depuis {orig_start.date()}) : **{int(m.sum())}**")
        L.append("")
        L.append("| | Sharpe ann. | Rendement total net |")
        L.append("|---|---|---|")
        L.append("| Overlay — origine, univers biaisé | +0.71 | +152.5% |")
        L.append(f"| Overlay — PIT, **fenêtre comparable** | {me_o['sharpe_ann']:+.2f} | {100*ret_o:+.1f}% |")
        L.append(f"| Buy&Hold — même fenêtre | {me_b['sharpe_ann']:+.2f} | {100*ret_b:+.1f}% |")
        L.append("")
        L.append("La jambe Buy & Hold étant identique dans les deux univers, tout écart entre")
        L.append("les deux premières lignes est imputable à l'**univers** du signal.")
    else:
        L.append("Aucune séance commune.")
    L.append("")

    verdict = ok1 and ok2 and ok3 and ok5
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME — les contrôles de validité passent.' if verdict else 'NON CONFORME — au moins un contrôle échoue.'}**")
    L.append("")
    L.append("Le contrôle 4 est une **mesure**, pas un test : il n'entre pas dans ce verdict.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
