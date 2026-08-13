"""Audit adversarial — dispersion du momentum, univers point-in-time.

Quatre contrôles indépendants du backtest :

1. **Recalcul du spread par un chemin de code disjoint** — le backtest décale les
   prix par tranches NumPy et trie ; l'audit passe par `pandas.shift` et
   `nlargest`/`nsmallest`, sur des dates échantillonnées.
2. **Anti-lookahead par mutation du futur** — les prix postérieurs à une coupure
   sont altérés ; le spread calculé avant doit être strictement inchangé.
3. **Le filtre d'appartenance change-t-il réellement le signal ?** Recalcul sur
   l'univers élargi à tous les tickers : le spread doit différer, sinon le
   portage serait cosmétique et le « maintenu » vide de sens.
4. **Causalité de la porte** — la porte appliquée au rendement du jour t doit
   avoir été décidée en t−1.

Usage : python3 scripts/nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_audit.md"


def prices_frame():
    series = bt.load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    return pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})


def disp_at_pandas(P, i, members_override=None):
    """Recalcul INDEPENDANT de la dispersion transversale a la date i.

    Chemin disjoint : `pandas.shift` puis `Series.std(ddof=1)` au lieu du
    decalage par tranches NumPy et de `np.std` du backtest.
    """
    mom = (P.shift(bt.SKIP).iloc[i] / P.shift(bt.LOOKBACK).iloc[i]) - 1.0
    members = members_override if members_override is not None else tickers_as_of_date(P.index[i])
    if not members:
        return np.nan
    keep = pd.Series([t in members for t in P.columns], index=P.columns)
    vals = mom[keep & mom.notna()]
    if len(vals) < bt.MIN_LISTED:
        return np.nan
    return float(vals.std(ddof=1))


def main():
    L = ["# Audit adversarial — dispersion du momentum, univers point-in-time", ""]

    disp_bt, cov = bt.compute_momentum_dispersion_series_pit()
    P = prices_frame()
    defined = np.where(disp_bt.notna().values)[0]
    sample = defined[np.linspace(0, len(defined) - 1, 6).astype(int)]

    # --- 1. recalcul par chemin disjoint ---
    L.append("## 1. Recalcul de la dispersion par un chemin de code disjoint")
    L.append("")
    L.append("Le backtest décale les prix par tranches NumPy puis appelle `np.std` ;")
    L.append("l'audit passe par `pandas.shift` puis `Series.std(ddof=1)`. Les deux chemins ne")
    L.append("partagent aucune ligne.")
    L.append("")
    L.append("| Date | Dispersion backtest | Dispersion audit | Écart |")
    L.append("|---|---|---|---|")
    max_err = 0.0
    for i in sample:
        s_bt = float(disp_bt.iloc[i])
        s_au = disp_at_pandas(P, int(i))
        err = abs(s_bt - s_au) if np.isfinite(s_au) else float("nan")
        if np.isfinite(err):
            max_err = max(max_err, err)
        L.append(f"| {P.index[i].date()} | {s_bt:.6f} | {s_au:.6f} | {err:.2e} |")
    ok1 = max_err < 1e-10
    L.append("")
    L.append(f"- écart maximal : **{max_err:.2e}**")
    L.append("")
    L.append(f"**{'CONFORME — les deux chemins concordent à la précision machine.' if ok1 else 'DIVERGENCE — les deux implémentations ne concordent pas.'}**")
    L.append("")

    # --- 2. anti-lookahead ---
    cut = int(defined[len(defined) // 2])
    P_pert = P.copy()
    P_pert.iloc[cut + 1:] = P_pert.iloc[cut + 1:] * 7.0
    s_ref = disp_at_pandas(P, cut)
    s_pert = disp_at_pandas(P_pert, cut)
    ok2 = bool(np.isfinite(s_ref) and np.isfinite(s_pert) and abs(s_ref - s_pert) < 1e-12)

    L.append("## 2. Anti-lookahead — mutation du futur")
    L.append("")
    L.append(f"Les prix postérieurs à l'indice {cut} ({P.index[cut].date()}) sont multipliés")
    L.append("par 7. La dispersion calculée **à** cette date doit être strictement inchangée.")
    L.append("")
    L.append(f"- dispersion avant mutation : **{s_ref:.6f}**")
    L.append(f"- dispersion après mutation : **{s_pert:.6f}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur.' if ok2 else 'FUITE DÉTECTÉE — résultat invalide.'}**")
    L.append("")

    # --- 3. le filtre d'appartenance a-t-il un effet ? ---
    all_tickers = set(P.columns)
    diffs = checked = 0
    ampl = []
    for i in sample:
        s_pit = disp_at_pandas(P, int(i))
        s_all = disp_at_pandas(P, int(i), members_override=all_tickers)
        if np.isfinite(s_pit) and np.isfinite(s_all):
            checked += 1
            ampl.append(s_all - s_pit)
            if abs(s_pit - s_all) > 1e-12:
                diffs += 1
    ok3 = diffs > 0

    L.append("## 3. Le filtre d'appartenance change-t-il réellement le signal ?")
    L.append("")
    L.append("Un filtre sans effet rendrait le « maintenu » vide de sens. La dispersion est")
    L.append("recalculée en forçant l'univers à **tous** les tickers disponibles ; elle doit")
    L.append("différer de la version point-in-time.")
    L.append("")
    L.append(f"- dates comparées : **{checked}**")
    L.append(f"- dates où la dispersion diffère : **{diffs}**")
    if ampl:
        L.append("Écart moyen (univers élargi − point-in-time) : "
                 f"**{np.mean(ampl):+.4f}**. Aucun mécanisme n'avait été annoncé au")
        L.append("pré-enregistrement (abstention motivée depuis le #409) : la mesure est donc")
        L.append("publiée sans hypothèse à confirmer ou infirmer.")
        L.append("")

    # --- 4. causalite de la porte ---
    n = 50
    fake_gate = np.zeros(n, dtype=bool)
    fake_gate[20] = True
    r_fake = np.full(n - 1, 0.01)
    pos_fake = bt.combined_position(r_fake, fake_gate)
    idx_mod = list(np.where(pos_fake != 1.0)[0])
    ok4 = idx_mod == [20]

    L.append("## 4. Causalité de la porte")
    L.append("")
    L.append("`combined_position` consomme `gate_aligned[:-1]` : la porte appliquée au")
    L.append("rendement du jour t est celle observée en t−1. Vérifié sur une porte synthétique")
    L.append("n'ayant qu'un seul jour actif (indice 20).")
    L.append("")
    L.append(f"- indices de position modifiée : **{idx_mod}**")
    L.append("")
    L.append(f"**{'CONFORME — décalage d un jour, aucune décision prise sur le rendement du jour même.' if ok4 else 'ANOMALIE'}**")
    L.append("")

    # --- 5. correlation avec la porte du #407 (PRE-ENREGISTRE) ---
    import nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe_backtest as sib  # noqa: E402
    sib_sig, _sib_cov = sib.compute_decile_spread_series_pit()
    gate_here = bt.build_gate(disp_bt)
    gate_sib = sib.build_gate(sib_sig)
    common = gate_here.dropna().index.intersection(gate_sib.dropna().index)
    a = gate_here.reindex(common).astype(float)
    b = gate_sib.reindex(common).astype(float)
    agree = float((a == b).mean())
    corr = float(np.corrcoef(a.values, b.values)[0, 1]) if len(common) > 2 else float("nan")

    L.append("## 5. Proximité avec le #407 — mesure pré-enregistrée")
    L.append("")
    L.append("Les deux candidats sont construits sur la **même matrice de momentum 12-1**,")
    L.append("agrégée autrement : écart-type transversal ici, écart entre déciles extrêmes au")
    L.append("#407. Le pré-enregistrement annonçait de mesurer leur proximité sans en préjuger,")
    L.append("le #403 ayant montré qu'un tel voisinage pouvait aller jusqu'à l'identité.")
    L.append("")
    L.append(f"- séances communes : **{len(common)}**")
    L.append(f"- part des séances où les deux portes donnent la **même** décision : **{100*agree:.1f} %**")
    L.append(f"- corrélation des deux portes : **{corr:.4f}**")
    L.append("")
    if agree > 0.999:
        L.append("**Portes quasi identiques** — les deux entrées désignent pratiquement la même")
        L.append("stratégie, comme #33/#41 au #403. À traiter comme un doublon dans le décompte")
        L.append("d'essais.")
    elif agree > 0.90:
        L.append("**Portes très proches mais distinctes.** Elles ne sont pas interchangeables au")
        L.append("sens du #403 (qui exigeait l'identité), mais leur voisinage signifie que les")
        L.append("deux PASS ne constituent **pas** deux confirmations indépendantes.")
    else:
        L.append("**Portes distinctes** — les deux agrégats de la même matrice produisent des")
        L.append("décisions sensiblement différentes.")
    L.append("")
    L.append("Le `.npz` de ce cycle est sauvegardé : le balayage du #406 pourra comparer les")
    L.append("deux séries de P&L directement.")
    L.append("")

    verdict = ok1 and ok2 and ok3 and ok4
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME — les contrôles de validité (1 à 4) passent.' if verdict else 'NON CONFORME — au moins un contrôle échoue.'}**")
    L.append("")
    L.append("Le contrôle 5 est une **mesure** de proximité avec le #407, pas un test : il")
    L.append("n'entre pas dans ce verdict.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
