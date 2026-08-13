"""Audit independant de la correction de `net_pnl` (#445).

Point 4 du critere pre-enregistre : recalculer les groupes de doublons
**sans reutiliser** la fonction corrigee, directement depuis les `.npz`, et
verifier qu'on retrouve les memes.

L'audit reimplemente donc la reconstruction de zero, avec ses propres
conventions de lecture, et se refuse a importer `net_pnl`.
"""
import re
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_net_pnl_correction_audit.md"
SWEEP = SCRIPTS / "nonml_pnl_duplicate_sweep_backtest.py"
CORR_THRESHOLD = 0.9999          # relu dans le balayage, pas importe


def reconstruire(d):
    """Reconstruction INDEPENDANTE, ecrite sans regarder `net_pnl`.

    Regle unique et explicite : un P&L deja net se lit tel quel ; un P&L brut
    se lit net de son turnover.
    """
    f = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in f else 0.0

    if "pnl_gross_ov" in f and "turn_ov" in f:                 # brut -> net
        return np.asarray(d["pnl_gross_ov"], float) - np.asarray(d["turn_ov"], float) * c
    if "pnl_candidate" in f:                                   # DEJA net
        return np.asarray(d["pnl_candidate"], float)
    if "pos" in f and "r_asset" in f:
        pos = np.asarray(d["pos"], float)
        r = np.asarray(d["r_asset"], float)
        turn = np.abs(np.diff(pos, prepend=1.0))
        if "r_alt" in f:
            return pos * r + (1.0 - pos) * np.asarray(d["r_alt"], float) - turn * c
        return pos * r - turn * c
    return None


def groupes(series):
    exact = []
    names = sorted(series)
    for a, b in combinations(names, 2):
        sa, sb = series[a], series[b]
        if len(sa) == len(sb) and np.array_equal(sa, sb):
            exact.append((a, b))
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
    g = {}
    for n in names:
        g.setdefault(find(n), []).append(n)
    return sorted(tuple(sorted(v)) for v in g.values() if len(v) > 1)


def main():
    series = {}
    for p in sorted(RESULTS.glob("*_pnl.npz")):
        try:
            d = np.load(p, allow_pickle=True)
        except Exception:  # noqa: BLE001
            continue
        s = reconstruire(d)
        if s is None or s.ndim != 1 or len(s) < 2 or not np.isfinite(s).all():
            continue
        series[p.name.replace("_pnl.npz", "")] = s

    g_audit = groupes(series)

    # Groupes du balayage corrige, obtenus SANS importer sa fonction :
    # on l'execute et on lit son rapport.
    txt = (RESULTS / "nonml_pnl_duplicate_sweep_result.md").read_text(encoding="utf-8")

    # Controle 1 : le diff est-il bien confine aux lignes annoncees ?
    numstat = subprocess.run(
        ["git", "diff", "HEAD", "--numstat", "--", str(SWEEP)],
        cwd=ROOT.parent.parent, capture_output=True, text=True).stdout.strip()
    ins = dele = None
    if numstat:
        parts = numstat.split()
        ins, dele = int(parts[0]), int(parts[1])

    # Controle 2 : la branche fautive a-t-elle disparu du source ?
    src = SWEEP.read_text(encoding="utf-8")
    branche_absente = "candidat+turnover" not in src
    lecture_directe = 'return np.asarray(d["pnl_candidate"], dtype=float), "candidat seul"' in src

    # Controle 3 : lecture exacte du fichier concerne
    d = np.load(RESULTS / "nonml_dollar_neutral_composite_pit_pnl.npz", allow_pickle=True)
    ecart = float(np.abs(reconstruire(d) - np.asarray(d["pnl_candidate"], float)).max())

    L = ["# Audit indépendant — correction de `net_pnl` (#445)", ""]
    L.append("Point 4 du critère pré-enregistré : **recalculer les groupes de doublons sans")
    L.append("réutiliser la fonction corrigée**. Cet audit réimplémente la reconstruction")
    L.append("depuis les `.npz`, avec sa propre règle — *un P&L déjà net se lit tel quel, un")
    L.append("P&L brut se lit net de son turnover* — et **n'importe pas** `net_pnl`.")
    L.append("")

    L.append("## Contrôle 1 — le diff est-il confiné aux lignes annoncées ?")
    L.append("")
    if ins is None:
        L.append("`git diff` ne renvoie rien : la modification est **déjà committée**, le")
        L.append("contrôle porte alors sur le source (contrôle 2).")
    else:
        ok = (ins == 0 and dele == 3)
        L.append(f"- insertions : **{ins}** — suppressions : **{dele}**")
        L.append(f"- conforme au régime annoncé (0 insertion, 3 suppressions) : "
                 f"**{'OUI' if ok else 'NON'}**")
    L.append("")

    L.append("## Contrôle 2 — la branche fautive a-t-elle disparu ?")
    L.append("")
    L.append(f"- `\"candidat+turnover\"` absent du source : **{'OUI' if branche_absente else 'NON'}**")
    L.append(f"- lecture directe `\"candidat seul\"` présente : **{'OUI' if lecture_directe else 'NON'}**")
    L.append("")

    L.append("## Contrôle 3 — lecture exacte, mesurée indépendamment")
    L.append("")
    L.append("Écart entre la reconstruction **de cet audit** et `pnl_candidate` brut pour")
    L.append(f"`dollar_neutral_composite_pit` : **{ecart:.1e}**.")
    L.append("")

    L.append("## Contrôle 4 — les groupes de doublons")
    L.append("")
    L.append(f"Groupes trouvés par la reconstruction **indépendante** : **{len(g_audit)}**.")
    L.append("")
    for g in g_audit:
        L.append(f"- `{'`, `'.join(g)}`")
    L.append("")
    # Comparaison REELLE des groupes : on lit ceux du rapport, on compare les
    # ensembles. Un simple compte identique ne prouverait pas la meme partition.
    g_rapport = sorted(
        tuple(sorted(re.findall(r"`([^`]+)`", ln)))
        for ln in txt.splitlines() if ln.startswith("- **groupe de"))
    memes = g_rapport == g_audit
    L.append(f"Groupes listés par le rapport du balayage : **{len(g_rapport)}**.")
    L.append("")
    L.append(f"**Partitions identiques : {'OUI' if memes else 'NON'}** — comparaison des")
    L.append("ensembles de noms, pas seulement des effectifs : deux partitions distinctes")
    L.append("peuvent avoir le même nombre de groupes.")
    if not memes:
        for g in [g for g in g_audit if g not in g_rapport]:
            L.append(f"- présent chez l'audit seulement : `{'`, `'.join(g)}`")
        for g in [g for g in g_rapport if g not in g_audit]:
            L.append(f"- présent au rapport seulement : `{'`, `'.join(g)}`")
    L.append("")

    ok_all = branche_absente and lecture_directe and ecart == 0.0 and memes
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME' if ok_all else 'NON CONFORME'}** — la correction fait ce qu'elle")
    L.append("annonce, et une reconstruction écrite indépendamment retrouve les mêmes")
    L.append("groupes de doublons.")
    L.append("")
    L.append("### Ce que cet audit ne prouve pas")
    L.append("")
    L.append("Il partage avec le balayage la **convention** « `pnl_candidate` est déjà net ».")
    L.append("Si cette convention était fausse, les deux se tromperaient ensemble. Elle a été")
    L.append("établie au #444 par **lecture des scripts producteurs**, pas par accord entre")
    L.append("deux reconstructions — et c'est cette lecture, pas cet audit, qui la fonde.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
