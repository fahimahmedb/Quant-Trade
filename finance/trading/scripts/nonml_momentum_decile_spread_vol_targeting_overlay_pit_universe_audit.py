"""Audit adversarial — spread décile de momentum, univers point-in-time.

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

Usage : python3 scripts/nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe_audit.md"


def prices_frame():
    series = bt.load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    return pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})


def spread_at_pandas(P, i, members_override=None):
    """Recalcul INDEPENDANT du spread decile a la date d'indice i.

    Chemin disjoint : `pandas.shift` et `nlargest`/`nsmallest` au lieu du
    decalage par tranches NumPy et du tri complet.
    """
    mom = (P.shift(bt.SKIP).iloc[i] / P.shift(bt.LOOKBACK).iloc[i]) - 1.0
    members = members_override if members_override is not None else tickers_as_of_date(P.index[i])
    if not members:
        return np.nan
    keep = pd.Series([t in members for t in P.columns], index=P.columns)
    vals = mom[keep & mom.notna()]
    n = len(vals)
    if n < bt.MIN_LISTED:
        return np.nan
    k = max(1, round(n * bt.DECILE_FRACTION))
    return float(vals.nlargest(k).mean() - vals.nsmallest(k).mean())


def main():
    L = ["# Audit adversarial — spread décile de momentum, univers point-in-time", ""]

    spread_bt, cov = bt.compute_decile_spread_series_pit()
    P = prices_frame()
    defined = np.where(spread_bt.notna().values)[0]
    sample = defined[np.linspace(0, len(defined) - 1, 6).astype(int)]

    # --- 1. recalcul par chemin disjoint ---
    L.append("## 1. Recalcul du spread par un chemin de code disjoint")
    L.append("")
    L.append("Le backtest décale les prix par tranches NumPy puis trie la colonne entière ;")
    L.append("l'audit passe par `pandas.shift` et `nlargest`/`nsmallest`. Les deux chemins ne")
    L.append("partagent aucune ligne.")
    L.append("")
    L.append("| Date | Spread backtest | Spread audit | Écart |")
    L.append("|---|---|---|---|")
    max_err = 0.0
    for i in sample:
        s_bt = float(spread_bt.iloc[i])
        s_au = spread_at_pandas(P, int(i))
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
    s_ref = spread_at_pandas(P, cut)
    s_pert = spread_at_pandas(P_pert, cut)
    ok2 = bool(np.isfinite(s_ref) and np.isfinite(s_pert) and abs(s_ref - s_pert) < 1e-12)

    L.append("## 2. Anti-lookahead — mutation du futur")
    L.append("")
    L.append(f"Les prix postérieurs à l'indice {cut} ({P.index[cut].date()}) sont multipliés")
    L.append("par 7. Le spread calculé **à** cette date doit être strictement inchangé.")
    L.append("")
    L.append(f"- spread avant mutation : **{s_ref:.6f}**")
    L.append(f"- spread après mutation : **{s_pert:.6f}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur.' if ok2 else 'FUITE DÉTECTÉE — résultat invalide.'}**")
    L.append("")

    # --- 3. le filtre d'appartenance a-t-il un effet ? ---
    all_tickers = set(P.columns)
    diffs = checked = 0
    ampl = []
    for i in sample:
        s_pit = spread_at_pandas(P, int(i))
        s_all = spread_at_pandas(P, int(i), members_override=all_tickers)
        if np.isfinite(s_pit) and np.isfinite(s_all):
            checked += 1
            ampl.append(s_all - s_pit)
            if abs(s_pit - s_all) > 1e-12:
                diffs += 1
    ok3 = diffs > 0

    L.append("## 3. Le filtre d'appartenance change-t-il réellement le signal ?")
    L.append("")
    L.append("Un filtre sans effet rendrait le « maintenu » vide de sens. Le spread est")
    L.append("recalculé en forçant l'univers à **tous** les tickers disponibles ; il doit")
    L.append("différer de la version point-in-time.")
    L.append("")
    L.append(f"- dates comparées : **{checked}**")
    L.append(f"- dates où le spread diffère : **{diffs}**")
    if ampl:
        L.append(f"- écart moyen (univers élargi − point-in-time) : **{np.mean(ampl):+.4f}**")
    L.append(f"- couverture moyenne rapportée par le backtest : **{100*cov:.1f}%**")
    L.append("")
    L.append(f"**{'CONFORME — le filtre point-in-time change effectivement le signal.' if ok3 else 'ALERTE — le filtre ne change rien, le portage serait cosmétique.'}**")
    L.append("")
    if ampl:
        # Ce commentaire est ecrit dans les DEUX sens. Un rapport qui ne commente
        # que lorsque la mesure confirme l'hypothese est biaise par construction.
        L.append("Le pré-enregistrement décrivait un mécanisme possible : retirer")
        L.append("rétroactivement les sociétés sorties de l'indice amputerait surtout le décile")
        L.append("**faible**, donc l'univers élargi devrait produire un spread **plus large**.")
        L.append("")
        if np.mean(ampl) > 0:
            L.append("L'écart mesuré est **positif** : la mesure va dans le sens du mécanisme")
            L.append("proposé.")
        else:
            L.append("L'écart mesuré est **négatif** : l'univers élargi produit un spread plus")
            L.append("**étroit**, soit l'inverse de ce que le mécanisme proposé prédisait. Le")
            L.append("mécanisme écrit au pré-enregistrement est donc **contredit** par cette")
            L.append("mesure — c'est consigné plutôt que passé sous silence.")
        L.append("")
        L.append("Dans les deux cas, six dates ne constituent pas une mesure mais une")
        L.append("indication : ce contrôle sert à établir que le filtre agit, pas à quantifier")
        L.append("son sens.")
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

    verdict = ok1 and ok2 and ok3 and ok4
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME — les quatre contrôles passent.' if verdict else 'NON CONFORME — au moins un contrôle échoue.'}**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
