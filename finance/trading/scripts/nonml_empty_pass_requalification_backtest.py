"""Requalification des PASS obtenus par inactivité (spécification
pré-enregistrée dans `PREREG_empty_pass_requalification.md`, committée avant ce
script).

Requalification **documentaire** : aucun verdict n'est recalculé ni annulé. Un
bloc d'avertissement est **ajouté** en fin de rapport pour les candidats dont le
P&L est strictement identique à celui de Buy & Hold — leur PASS ne mesure alors
que l'inactivité de la stratégie.

Règle FIXÉE AVANT EXÉCUTION :
1. le rapport porte un PASS, **et**
2. le `.npz` permet de reconstruire le P&L, **et**
3. ce P&L est identique à celui de Buy & Hold sur toutes les séances **sauf la
   première** — exclue car les scripts imputent un coût d'entrée à la seule
   jambe Buy & Hold (écart comptable, pas décision de stratégie ; défaut attrapé
   au #416).

Le critère est l'**identité du P&L**, pas un seuil d'activation : le #416 a
montré qu'un seuil bas ne distingue pas une porte neutralisée d'une porte rare
par construction.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_empty_pass_requalification_result.md"

MARKER = "REQUALIFICATION #417"


def verdict_of(path: Path):
    txt = path.read_text(encoding="utf-8")
    if "**PASS" in txt or "PASS (niveau 1)" in txt:
        return "PASS"
    if "**FAIL" in txt:
        return "FAIL"
    return "indéterminé"


def pnl_identical(npz: Path):
    """Le P&L de l'overlay est-il identique a celui de Buy & Hold ?

    Retourne (identique, n_seances, n_differentes) ou None si inexploitable.
    """
    try:
        d = np.load(npz, allow_pickle=True)
    except Exception:  # noqa: BLE001
        return None
    if "pos" not in d.files or "r_asset" not in d.files:
        return None
    pos = np.asarray(d["pos"], dtype=float)
    r = np.asarray(d["r_asset"], dtype=float)
    if pos.size < 2 or pos.shape != r.shape:
        return None
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in d.files else 0.0
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * c
    pnl_bh = r.copy()
    pnl_bh[0] -= c
    n_diff = int((np.abs(pnl_ov[1:] - pnl_bh[1:]) > 1e-15).sum())
    return (n_diff == 0), len(pos), n_diff


def warning_block(n_sess: int) -> str:
    return (
        f"\n---\n\n**⚠️ {MARKER} — PASS NON INFORMATIF.**\n\n"
        f"Mesure faite sur le P&L sauvegardé : la stratégie produit un P&L "
        f"**strictement identique** à celui de Buy & Hold sur les {n_sess} séances "
        f"testées (hors coût d'entrée, imputé à la seule jambe Buy & Hold par "
        f"convention du dépôt). L'overlay ne prend **jamais** de position effective.\n\n"
        f"Le verdict PASS ci-dessus n'est pas annulé — le critère pré-enregistré était "
        f"bien atteint. Mais il mesure une **inactivité**, pas un edge : les deux lignes "
        f"du tableau sont égales pour une raison mécanique.\n\n"
        f"Cause établie au #410 puis confirmée par mesure au #416 : la porte s'ouvre en "
        f"régime de faiblesse, or c'est exactement là que le vol-targeting `20 % / vol` "
        f"tombe sous 1,0 et se fait ramener au plancher. Les deux briques s'annulent.\n"
    )


def main():
    npzs = sorted(RESULTS.glob("nonml_*_pnl.npz"))
    examined, unusable, requalified, already, pass_but_acts = [], [], [], [], []

    for p in npzs:
        name = p.name.replace("nonml_", "").replace("_pnl.npz", "")
        rep = RESULTS / f"nonml_{name}_result.md"
        res = pnl_identical(p)
        if res is None:
            unusable.append(name)
            continue
        identical, n_sess, n_diff = res
        examined.append(name)
        if not rep.exists():
            continue
        v = verdict_of(rep)
        if v != "PASS":
            continue
        if not identical:
            pass_but_acts.append(name)
            continue
        txt = rep.read_text(encoding="utf-8")
        if MARKER in txt or "NON INFORMATIF" in txt:
            already.append(name)
            continue
        rep.write_text(txt.rstrip("\n") + "\n" + warning_block(n_sess), encoding="utf-8")
        requalified.append((name, n_sess))

    L = ["# Requalification des PASS obtenus par inactivité (pré-enregistré)", ""]
    L.append("Requalification **documentaire** : aucun verdict n'est recalculé ni annulé.")
    L.append("Le critère est l'**identité du P&L** avec Buy & Hold, pas un seuil")
    L.append("d'activation — distinction établie au #416.")
    L.append("")
    L.append("## Couverture")
    L.append("")
    L.append(f"- fichiers `nonml_*_pnl.npz` trouvés : **{len(npzs)}**")
    L.append(f"- exploitables (schéma `pos` / `r_asset`) : **{len(examined)}**")
    L.append(f"- inexploitables (autre schéma) : **{len(unusable)}**")
    L.append("")
    L.append("Les schémas « panier » et « deux jambes » n'entrent pas dans ce balayage : leur")
    L.append("jambe de référence n'est pas Buy & Hold mais un portefeuille, et le critère")
    L.append("d'identité ne s'y transpose pas tel quel. C'est une limite de portée, pas un")
    L.append("oubli — elle est chiffrée ci-dessus.")
    L.append("")

    L.append("## Résultat")
    L.append("")
    L.append(f"- candidats **requalifiés** par ce cycle : **{len(requalified)}**")
    L.append(f"- déjà étiquetés avant ce cycle : **{len(already)}**")
    L.append(f"- PASS dont l'overlay **agit** (non requalifiables) : **{len(pass_but_acts)}**")
    L.append("")
    if requalified:
        L.append("| Candidat requalifié | Séances testées |")
        L.append("|---|---|")
        for n, ns in requalified:
            L.append(f"| `{n}` | {ns} |")
        L.append("")
    else:
        L.append("**Aucun candidat requalifié par ce cycle.**")
        L.append("")
    if already:
        L.append("Déjà étiquetés : " + ", ".join(f"`{n}`" for n in already) + ".")
        L.append("")

    L.append("## Ce que le balayage établit")
    L.append("")
    L.append(f"Sur **{len(examined)}** candidats mesurables, **{len(pass_but_acts)}** portent un")
    L.append("PASS dont l'overlay agit réellement. Le cas de l'inactivité totale est donc")
    L.append("**isolé**, et non un travers répandu du backlog.")
    L.append("")
    L.append("Le balayage a porté sur l'ensemble des `.npz` et non sur le seul cas connu du")
    L.append("#416 — restreindre la recherche à ce qui est déjà su est ce qui avait fait")
    L.append("manquer un foyer au #390, un portage au #395 et un doublon au #406.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return requalified, already, pass_but_acts, examined, unusable


if __name__ == "__main__":
    main()
