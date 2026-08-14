"""Extension du critère d'inactivité aux schémas panier (spécification
pré-enregistrée dans `PREREG_empty_pass_basket_extension.md`, committée avant ce
script).

Requalification **documentaire** : aucun verdict recalculé ni annulé.

Le #417 avait appliqué la règle « PASS obtenu par inactivité » aux 158 candidats
au schéma `pos` / `r_asset`. Quinze `.npz` y échappaient, dont 8 portant un PASS :
leur référence est un **portefeuille**, pas Buy & Hold. Le schéma panier stocke
les deux jambes, la comparaison est donc directe.

Règle FIXÉE AVANT EXÉCUTION, reprise du #417 sans assouplissement :
1. le rapport porte un PASS, **et**
2. le P&L net de la jambe candidate est **strictement identique** à celui de la
   jambe de référence, sur toutes les séances **sauf la première**.

Le schéma « deux jambes » est **exclu explicitement** : sa référence n'est pas
stockée dans le fichier.
"""
import sys
from pathlib import Path

import nonml_verdict  # regle unique du depot (#449)

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_empty_pass_basket_extension_result.md"

MARKER = "REQUALIFICATION #422"


def verdict_of(path: Path):
    txt = path.read_text(encoding="utf-8")
    if nonml_verdict.porte_verdict(txt, "PASS"):
        return "PASS"
    if "**FAIL" in txt:
        return "FAIL"
    return "indéterminé"


def classify(npz: Path):
    """Retourne (schema, infos) pour un .npz."""
    try:
        d = np.load(npz, allow_pickle=True)
    except Exception as exc:  # noqa: BLE001
        return "illisible", str(exc)
    f = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in f else 0.0
    if {"pnl_gross_ov", "turn_ov", "pnl_gross_bh", "turn_bh"} <= f:
        ov = np.asarray(d["pnl_gross_ov"], float) - np.asarray(d["turn_ov"], float) * c
        bh = np.asarray(d["pnl_gross_bh"], float) - np.asarray(d["turn_bh"], float) * c
        if ov.shape != bh.shape or ov.size < 2:
            return "panier inexploitable", None
        n_diff = int((np.abs(ov[1:] - bh[1:]) > 1e-15).sum())
        return "panier", {
            "n": len(ov), "n_diff": n_diff,
            "ret_ov": float(np.cumprod(1.0 + ov)[-1] - 1.0),
            "ret_bh": float(np.cumprod(1.0 + bh)[-1] - 1.0),
        }
    if {"pos", "r_asset", "r_alt"} <= f:
        return "deux jambes", None
    if {"pos", "r_asset"} <= f:
        return "indiciel", None
    return "autre", sorted(f)


def warning_block(n_sess: int) -> str:
    return (
        f"\n---\n\n**⚠️ {MARKER} — PASS NON INFORMATIF.**\n\n"
        f"Mesure faite sur le P&L sauvegardé : la jambe candidate produit un P&L "
        f"**strictement identique** à celui de sa jambe de référence sur les {n_sess} "
        f"séances testées (hors première séance). L'overlay ne prend jamais de position "
        f"effective distincte de sa référence.\n\n"
        f"Le verdict PASS ci-dessus n'est pas annulé — le critère pré-enregistré était "
        f"atteint. Mais il mesure une **inactivité**, pas un edge.\n"
    )


def main():
    npzs = sorted(RESULTS.glob("nonml_*_pnl.npz"))
    baskets, two_leg, indexed, other, unusable = [], [], [], [], []
    requalified, already, pass_but_acts = [], [], []

    for p in npzs:
        name = p.name.replace("nonml_", "").replace("_pnl.npz", "")
        schema, info = classify(p)
        if schema == "panier":
            baskets.append((name, info))
        elif schema == "deux jambes":
            two_leg.append(name)
        elif schema == "indiciel":
            indexed.append(name)
        elif schema in ("illisible", "panier inexploitable"):
            unusable.append((name, schema))
        else:
            other.append(name)

    for name, info in baskets:
        rep = RESULTS / f"nonml_{name}_result.md"
        if not rep.exists():
            continue
        if verdict_of(rep) != "PASS":
            continue
        if info["n_diff"] > 0:
            pass_but_acts.append((name, info))
            continue
        txt = rep.read_text(encoding="utf-8")
        if MARKER in txt or "NON INFORMATIF" in txt:
            already.append(name)
            continue
        rep.write_text(txt.rstrip("\n") + "\n" + warning_block(info["n"]), encoding="utf-8")
        requalified.append((name, info))

    L = ["# Extension du critère d'inactivité aux schémas panier (pré-enregistré)", ""]
    L.append("Requalification **documentaire** : aucun verdict recalculé. La règle du #417 est")
    L.append("transposée sans assouplissement — identité du P&L entre la jambe candidate et sa")
    L.append("**propre** jambe de référence, hors première séance.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- fichiers `nonml_*_pnl.npz` : **{len(npzs)}**")
    L.append(f"- schéma **panier**, traités par ce cycle : **{len(baskets)}**")
    L.append(f"- schéma **deux jambes**, exclus explicitement : **{len(two_leg)}**")
    L.append(f"- schéma indiciel, déjà traités au #417 : **{len(indexed)}**")
    L.append(f"- autres / inexploitables : **{len(other) + len(unusable)}**")
    L.append("")
    if two_leg:
        L.append("Exclus (schéma « deux jambes », référence non stockée dans le fichier) :")
        L.append("")
        for n in two_leg:
            L.append(f"- `{n}`")
        L.append("")
        L.append("Définir ce que « ne rien faire » signifie pour ces candidats demanderait une")
        L.append("convention inventée pour l'occasion. Ils sont comptés et listés, pas dissous.")
        L.append("")

    L.append("## Résultat")
    L.append("")
    L.append(f"- candidats panier **requalifiés** : **{len(requalified)}**")
    L.append(f"- déjà étiquetés : **{len(already)}**")
    L.append(f"- PASS panier dont la jambe candidate **agit** : **{len(pass_but_acts)}**")
    L.append("")
    if requalified:
        L.append("| Candidat requalifié | Séances |")
        L.append("|---|---|")
        for n, i in requalified:
            L.append(f"| `{n}` | {i['n']} |")
    else:
        L.append("**Aucun candidat requalifié.**")
    L.append("")

    if pass_but_acts:
        L.append("### PASS panier dont la jambe candidate agit")
        L.append("")
        L.append("| Candidat | Séances de P&L différent | Rendement candidat | Rendement référence |")
        L.append("|---|---|---|---|")
        for n, i in sorted(pass_but_acts):
            L.append(f"| `{n}` | {i['n_diff']} / {i['n']} | {100*i['ret_ov']:+.1f} % | "
                     f"{100*i['ret_bh']:+.1f} % |")
        L.append("")

    L.append("## Lecture")
    L.append("")
    L.append("Le pré-enregistrement annonçait **0 requalification**, en s'appuyant sur les")
    L.append("rendements déjà publiés : deux jambes affichant des rendements différents ne")
    L.append("peuvent pas avoir des P&L identiques.")
    L.append("")
    if not requalified:
        L.append("**Attente confirmée.** La dernière dette actionnable du protocole est fermée")
        L.append("sans avoir rien trouvé — ce qui était l'issue annoncée, et reste un résultat :")
        L.append("le PASS obtenu par inactivité demeure un cas isolé, désormais vérifié sur")
        L.append("**tous** les schémas où la question est décidable.")
    else:
        L.append("**Attente démentie** — un rapport publié affiche donc deux rendements")
        L.append("différents pour deux séries identiques. Contradiction interne à instruire")
        L.append("avant toute autre conclusion.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return requalified, already, pass_but_acts, baskets, two_leg


if __name__ == "__main__":
    main()
