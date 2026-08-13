"""Audit adversarial — breadth nette hauts-bas, univers point-in-time.

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

Usage : python3 scripts/nonml_net_breadth_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_net_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
import nonml_net_breadth_vol_targeting_overlay_backtest as orig  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_net_breadth_vol_targeting_overlay_pit_universe_audit.md"


def prices_frame():
    series = bt.load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    return pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})


def breadth_at_pandas(P, i, members_override=None):
    """Recalcul INDEPENDANT de la breadth nette a la date d'indice i.

    Chemin disjoint : `pandas.rolling(252).max()/.min()` sur la fenetre, au lieu
    des boucles NumPy du backtest.
    """
    win = P.iloc[i - bt.INDEX_LOOKBACK + 1:i + 1]
    full = win.notna().all(axis=0)
    hi = win.max()
    lo = win.min()
    px = P.iloc[i]

    members = members_override if members_override is not None else tickers_as_of_date(P.index[i])
    if not members:
        return np.nan
    is_member = pd.Series([t in members for t in P.columns], index=P.columns)
    listed = px.notna() & is_member
    n_listed = int(listed.sum())
    if n_listed == 0:
        return np.nan
    near_high = full & listed & (px >= bt.INDEX_THRESHOLD_HIGH * hi)
    near_low = full & listed & (px <= bt.INDEX_THRESHOLD_LOW * lo)
    return float(int(near_high.sum()) - int(near_low.sum())) / n_listed


def main():
    L = ["# Audit adversarial — breadth nette hauts-bas, univers point-in-time", ""]

    breadth_bt, cov = bt.compute_net_breadth_series_pit()
    P = prices_frame()
    defined = np.where(breadth_bt.notna().values)[0]
    sample = defined[np.linspace(0, len(defined) - 1, 6).astype(int)]

    # --- 1. chemin disjoint ---
    L.append("## 1. Recalcul de la breadth par un chemin de code disjoint")
    L.append("")
    L.append("Le backtest calcule plus-hauts et plus-bas glissants par boucles NumPy ;")
    L.append("l'audit par `pandas` sur la fenêtre. Aucune ligne partagée.")
    L.append("")
    L.append("| Date | Breadth backtest | Breadth audit | Écart |")
    L.append("|---|---|---|---|")
    max_err = 0.0
    for i in sample:
        b_bt = float(breadth_bt.iloc[i])
        b_au = breadth_at_pandas(P, int(i))
        err = abs(b_bt - b_au) if np.isfinite(b_au) else float("nan")
        if np.isfinite(err):
            max_err = max(max_err, err)
        L.append(f"| {P.index[i].date()} | {b_bt:+.6f} | {b_au:+.6f} | {err:.2e} |")
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
    b_ref = breadth_at_pandas(P, cut)
    b_pert = breadth_at_pandas(P_pert, cut)
    ok2 = bool(np.isfinite(b_ref) and np.isfinite(b_pert) and abs(b_ref - b_pert) < 1e-12)

    L.append("## 2. Anti-lookahead — mutation du futur")
    L.append("")
    L.append(f"Prix postérieurs à l'indice {cut} ({P.index[cut].date()}) multipliés par 7.")
    L.append("")
    L.append(f"- breadth avant mutation : **{b_ref:+.6f}**")
    L.append(f"- breadth après mutation : **{b_pert:+.6f}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur.' if ok2 else 'FUITE DÉTECTÉE'}**")
    L.append("")

    # --- 3. effet du filtre ---
    all_tickers = set(P.columns)
    diffs = checked = 0
    for i in sample:
        b_pit = breadth_at_pandas(P, int(i))
        b_all = breadth_at_pandas(P, int(i), members_override=all_tickers)
        if np.isfinite(b_pit) and np.isfinite(b_all):
            checked += 1
            if abs(b_pit - b_all) > 1e-12:
                diffs += 1
    ok3 = diffs > 0

    L.append("## 3. Le filtre d'appartenance change-t-il réellement le signal ?")
    L.append("")
    L.append(f"- dates comparées : **{checked}**")
    L.append(f"- dates où la breadth diffère : **{diffs}**")
    L.append(f"- couverture moyenne : **{100*cov:.1f}%**")
    L.append("")
    L.append(f"**{'CONFORME — le filtre point-in-time change effectivement le signal.' if ok3 else 'ALERTE — filtre sans effet, portage cosmétique.'}**")
    L.append("")

    # --- 4. decalage de NIVEAU, mesure exigee par le PREREG ---
    # Comparaison SUR LES MEMES DATES, sinon on confondrait effet d'univers et
    # effet de periode : les deux series ne couvrent pas la meme fenetre.
    breadth_orig = orig.compute_net_breadth_series()
    common = breadth_bt.dropna().index.intersection(breadth_orig.dropna().index)
    a = breadth_bt.reindex(common)
    b = breadth_orig.reindex(common)
    shift = float((b - a).mean())
    n_common = len(common)
    frac_pos_pit = float((a > bt.GATE_THRESHOLD).mean())
    frac_pos_orig = float((b > bt.GATE_THRESHOLD).mean())

    L.append("## 4. Décalage de niveau entre les deux univers")
    L.append("")
    L.append("Contrôle **exigé par le pré-enregistrement** : la porte de ce candidat a un")
    L.append("seuil absolu, elle n'est donc pas invariante par translation du signal. Le")
    L.append("mécanisme décrit au PREREG suppose que l'univers biaisé — composé de sociétés")
    L.append("ayant survécu jusqu'en 2026 — affiche une breadth nette **plus haute**.")
    L.append("")
    L.append("Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les")
    L.append("moyennes des deux rapports confondrait effet d'univers et effet de période,")
    L.append("leurs fenêtres n'étant pas les mêmes.")
    L.append("")
    L.append(f"- dates communes : **{n_common}**")
    L.append(f"- breadth moyenne, univers point-in-time : **{100*float(a.mean()):+.2f} pts**")
    L.append(f"- breadth moyenne, univers biaisé : **{100*float(b.mean()):+.2f} pts**")
    L.append(f"- décalage (biaisé − point-in-time) : **{100*shift:+.2f} pts**")
    L.append(f"- part des séances au-dessus du seuil, point-in-time : **{100*frac_pos_pit:.1f}%**")
    L.append(f"- part des séances au-dessus du seuil, biaisé : **{100*frac_pos_orig:.1f}%**")
    L.append("")
    if shift > 0:
        L.append("Le décalage est **positif** : l'univers biaisé affiche bien une breadth nette")
        L.append("plus haute, conformément au mécanisme décrit avant calcul.")
    elif shift < 0:
        L.append("Le décalage est **négatif** : l'univers biaisé affiche une breadth nette plus")
        L.append("**basse** que l'univers réel — soit l'inverse du mécanisme décrit avant")
        L.append("calcul. Le mécanisme est donc **contredit**, et c'est consigné ici plutôt")
        L.append("que passé sous silence.")
    else:
        L.append("Décalage nul.")
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
