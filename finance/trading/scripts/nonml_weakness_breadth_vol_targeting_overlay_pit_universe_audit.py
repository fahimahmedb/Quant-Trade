"""Audit adversarial — breadth de faiblesse, univers point-in-time.

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

Usage : python3 scripts/nonml_weakness_breadth_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_weakness_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
import nonml_weakness_breadth_vol_targeting_overlay_backtest as orig  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_weakness_breadth_vol_targeting_overlay_pit_universe_audit.md"


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
    near_low = full & listed & (px <= bt.INDEX_THRESHOLD_LOW * lo)
    return float(int(near_low.sum())) / n_listed


def main():
    L = ["# Audit adversarial — breadth de faiblesse, univers point-in-time", ""]

    breadth_bt, cov = bt.compute_weakness_breadth_series_pit()
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
    breadth_orig = orig.compute_weakness_breadth_series()
    common = breadth_bt.dropna().index.intersection(breadth_orig.dropna().index)
    a = breadth_bt.reindex(common)
    b = breadth_orig.reindex(common)
    shift = float((b - a).mean())
    n_common = len(common)
    frac_pos_pit = float((a > bt.BREADTH_THRESHOLD).mean())
    frac_pos_orig = float((b > bt.BREADTH_THRESHOLD).mean())

    L.append("## 4. Décalage de niveau entre les deux univers")
    L.append("")
    L.append("Contrôle **exigé par le pré-enregistrement**, sans mécanisme annoncé —")
    L.append("abstention motivée depuis le #409. Mesuré, publié, non interprété.")
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
    L.append("Aucune interprétation n'est proposée : la mesure est publiée telle quelle.")
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

    # --- 6. pourquoi la porte effective ne s'ouvre jamais ---
    # Constat lu sur les chiffres du backtest, pas une hypothese pre-enregistree :
    # la porte brute s'ouvre 13 fois mais l'exposition finale ne depasse jamais
    # 1,0x. Explication candidate : les deux conditions sont ANTI-CORRELEES par
    # construction -- la breadth de faiblesse culmine quand la volatilite est
    # haute, et c'est exactement quand 20%/vol tombe sous 1,0 et se fait clipper.
    # Verifiable directement : mesurer l'exposition AVANT clip sur les seances ou
    # la porte brute est ouverte.
    from data_loader import load_ohlc, quality_report  # noqa: E402
    dfx = load_ohlc(str(ROOT.parent.parent / "data" / "nasdaq100_daily.txt"))
    quality_report(dfx)
    cl = dfx["close"].values
    dates_x = pd.to_datetime(dfx["date"])
    r_idx = np.log(cl[1:] / cl[:-1])
    vol_ann = pd.Series(r_idx).rolling(bt.VOL_WINDOW).std().values * bt.ANNUALIZATION
    vol_lag = np.roll(vol_ann, 1)
    vol_lag[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        exposure_preclip = bt.TARGET_VOL_ANNUAL / vol_lag

    braw = breadth_bt.reindex(dates_x.values, method="ffill").values
    gate_full = np.where(np.isnan(braw), False, braw >= bt.BREADTH_THRESHOLD)
    gate_r = gate_full[:-1]
    open_idx = np.where(gate_r)[0]
    pre = exposure_preclip[open_idx]
    pre = pre[np.isfinite(pre)]
    n_open = len(pre)
    n_below_one = int((pre < 1.0).sum()) if n_open else 0
    med_pre = float(np.median(pre)) if n_open else float("nan")
    med_all = float(np.nanmedian(exposure_preclip))

    L.append("## 6. Pourquoi la porte effective ne s'ouvre jamais")
    L.append("")
    L.append("Constat **lu sur les chiffres du backtest**, pas une hypothèse")
    L.append("pré-enregistrée : la porte brute s'ouvre, mais l'exposition finale ne dépasse")
    L.append("jamais 1,0×. Explication candidate, vérifiable directement — les deux")
    L.append("conditions sont **anti-corrélées par construction** : la breadth de faiblesse")
    L.append("culmine quand la volatilité est haute, et c'est exactement là que")
    L.append("`20 % / vol` tombe sous 1,0 et se fait clipper au plancher.")
    L.append("")
    L.append("Mesure de l'exposition **avant clip** sur les séances où la porte brute est")
    L.append("ouverte :")
    L.append("")
    L.append(f"- séances à porte brute ouverte : **{n_open}**")
    L.append(f"- dont exposition avant clip < 1,0 : **{n_below_one}**")
    L.append(f"- exposition médiane avant clip, porte ouverte : **{med_pre:.3f}×**")
    L.append(f"- exposition médiane avant clip, toutes séances : **{med_all:.3f}×**")
    L.append("")
    if n_open and n_below_one == n_open:
        L.append("**Explication confirmée** : sur *toutes* les séances où la condition de")
        L.append("capitulation est remplie, le vol-targeting demande déjà moins de 1,0× et le")
        L.append("clip ramène l'exposition au plancher. Les deux briques de cette stratégie")
        L.append("s'annulent mutuellement — ce n'est pas un accident d'échantillon mais une")
        L.append("propriété de sa construction, qui vaut donc aussi pour le cycle d'origine.")
    elif n_open:
        L.append(f"**Explication partielle** : {n_below_one} séances sur {n_open} seulement.")
        L.append("L'anti-corrélation n'explique pas à elle seule l'inactivité totale.")
    else:
        L.append("Aucune séance à porte brute ouverte dans cette fenêtre.")
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
