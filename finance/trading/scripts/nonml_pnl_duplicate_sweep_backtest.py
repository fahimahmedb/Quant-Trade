"""Balayage des doublons de P&L du backlog (spécification pré-enregistrée dans
`PREREG_pnl_duplicate_sweep.md`, committée avant ce script).

Diagnostic, pas une stratégie : reconstruit le P&L net de **tous** les
`results/*_pnl.npz`, puis cherche les paires identiques ou quasi identiques.

Motivation (#403) : `sma200_leaders_overlay` et `leaders_trend_union_overlay`
sont la même stratégie écrite deux fois, et leurs P&L sont bit-à-bit identiques.
Le nombre d'essais du backlog entre dans le DSR ; des doublons le gonflent.

Critères FIXÉS AVANT EXÉCUTION :
- doublon exact      : `np.array_equal` sur le P&L net, à longueur égale ;
- quasi-doublon      : non exact, corrélation de Pearson ≥ 0,9999.

Tout schéma non reconnu est compté et listé, jamais ignoré en silence.
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_pnl_duplicate_sweep_result.md"

CORR_THRESHOLD = 0.9999


def net_pnl(d):
    """Reconstruit le P&L net selon le schema detecte.

    Retourne (serie, nom_du_schema) ou (None, raison) si non reconnu.
    """
    files = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in files else 0.0

    if {"pnl_gross_ov", "turn_ov"} <= files:
        return np.asarray(d["pnl_gross_ov"], dtype=float) - np.asarray(d["turn_ov"], dtype=float) * c, "panier"
    if {"pnl_candidate", "turn_candidate"} <= files:
        return (np.asarray(d["pnl_candidate"], dtype=float)
                - np.asarray(d["turn_candidate"], dtype=float) * c), "candidat+turnover"
    if "pnl_candidate" in files:
        return np.asarray(d["pnl_candidate"], dtype=float), "candidat seul"
    if {"pos", "r_asset"} <= files:
        pos = np.asarray(d["pos"], dtype=float)
        r = np.asarray(d["r_asset"], dtype=float)
        turn = np.abs(np.diff(pos, prepend=1.0))
        if "r_alt" in files:
            r_alt = np.asarray(d["r_alt"], dtype=float)
            return pos * r + (1.0 - pos) * r_alt - turn * c, "deux jambes"
        return pos * r - turn * c, "indiciel"
    return None, "schéma non reconnu"


def main():
    paths = sorted(RESULTS.glob("*_pnl.npz"))
    series, schemas, unknown = {}, {}, []

    for p in paths:
        try:
            d = np.load(p, allow_pickle=True)
        except Exception as exc:  # noqa: BLE001
            unknown.append((p.name, f"illisible : {exc}"))
            continue
        s, tag = net_pnl(d)
        if s is None or s.ndim != 1 or len(s) < 2 or not np.isfinite(s).all():
            unknown.append((p.name, tag if s is None else "série non exploitable"))
            continue
        name = p.name.replace("_pnl.npz", "")
        series[name] = s
        schemas[name] = tag

    exact, quasi = [], []
    names = sorted(series)
    for a, b in combinations(names, 2):
        sa, sb = series[a], series[b]
        if len(sa) != len(sb):
            continue
        if np.array_equal(sa, sb):
            exact.append((a, b))
            continue
        if np.std(sa) == 0 or np.std(sb) == 0:
            continue
        corr = float(np.corrcoef(sa, sb)[0, 1])
        if corr >= CORR_THRESHOLD:
            quasi.append((a, b, corr))

    # groupes de doublons exacts (composantes connexes)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in exact:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups = {}
    for n in names:
        groups.setdefault(find(n), []).append(n)
    dup_groups = [sorted(g) for g in groups.values() if len(g) > 1]
    surnumeraires = sum(len(g) - 1 for g in dup_groups)

    L = ["# Balayage des doublons de P&L du backlog (pré-enregistré)", ""]
    L.append("Diagnostic, pas une stratégie. Reconstruit le P&L net de **tous** les")
    L.append("`results/*_pnl.npz` du dépôt et cherche les paires identiques ou quasi")
    L.append("identiques. Critères fixés avant exécution : égalité exacte")
    L.append(f"(`np.array_equal`) ou corrélation ≥ {CORR_THRESHOLD}.")
    L.append("")
    L.append("## Couverture")
    L.append("")
    L.append(f"- fichiers `*_pnl.npz` trouvés : **{len(paths)}**")
    L.append(f"- P&L reconstruits : **{len(series)}**")
    L.append(f"- schémas non reconnus ou séries inexploitables : **{len(unknown)}**")
    L.append("")
    if unknown:
        L.append("| Fichier | Raison |")
        L.append("|---|---|")
        for n, why in unknown:
            L.append(f"| `{n}` | {why} |")
        L.append("")
        L.append("**Couverture incomplète — rapportée comme telle**, conformément au critère 1")
        L.append("du pré-enregistrement.")
    else:
        L.append("**Couverture 100 %** — critère 1 du pré-enregistrement atteint.")
    L.append("")
    counts = {}
    for tag in schemas.values():
        counts[tag] = counts.get(tag, 0) + 1
    L.append("Répartition par schéma : " + ", ".join(
        f"{k} ({v})" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) + ".")
    L.append("")

    L.append("## Doublons exacts")
    L.append("")
    L.append(f"- paires à P&L **bit-à-bit identique** : **{len(exact)}**")
    L.append(f"- groupes de doublons : **{len(dup_groups)}**")
    L.append(f"- entrées surnuméraires (essais comptés en trop) : **{surnumeraires}**")
    L.append("")
    if dup_groups:
        for g in dup_groups:
            L.append(f"- **groupe de {len(g)}** : " + ", ".join(f"`{x}`" for x in g))
    else:
        L.append("Aucun.")
    L.append("")

    L.append("## Quasi-doublons (corrélation ≥ seuil, non identiques)")
    L.append("")
    L.append(f"- paires signalées : **{len(quasi)}**")
    L.append("")
    if quasi:
        L.append("| Candidat A | Candidat B | Corrélation |")
        L.append("|---|---|---|")
        for a, b, corr in sorted(quasi, key=lambda t: -t[2]):
            L.append(f"| `{a}` | `{b}` | {corr:.8f} |")
        L.append("")
        L.append("Ces paires **ne sont pas comptées comme doublons** à ce stade : le critère 2")
        L.append("du pré-enregistrement impose de les confirmer ou de les rejeter par lecture")
        L.append("des deux scripts. Voir l'audit.")
    else:
        L.append("Aucune.")
    L.append("")

    L.append("## Effet sur le décompte d'essais")
    L.append("")
    L.append(f"Le backlog compte actuellement **372** essais dans le calcul du DSR.")
    L.append(f"Les doublons exacts en rendent **{surnumeraires}** surnuméraires, soit un")
    L.append(f"décompte corrigé de **{372 - surnumeraires}** avant examen des quasi-doublons.")
    L.append("")
    L.append("**Aucune correction n'est appliquée dans ce cycle**, conformément au")
    L.append("pré-enregistrement : rejouer les batteries avec un `n_trials` corrigé après")
    L.append("avoir vu quels candidats en bénéficieraient serait précisément ce que le")
    L.append("protocole interdit. Le décompte corrigé est publié, son usage est un cycle")
    L.append("distinct à déclarer.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return dup_groups, quasi, unknown


if __name__ == "__main__":
    main()
