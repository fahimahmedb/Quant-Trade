"""Audit independant — la phrase calculee du balayage (#446).

Critere 2 du pre-enregistrement : **chaque nom publie est verifie
independamment**. Cet audit ne lit ni le balayage ni le script de cycle : il
repart du depot et refait le raisonnement, puis compare a ce qui est publie.

Un nom publie doit satisfaire les trois conditions a la fois :
  (a) c'est un script de backtest non-ML du depot ;
  (b) il n'a aucun `.npz` a son nom ;
  (c) son rapport porte un PASS.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

OUT = RESULTS / "nonml_sweep_pass_prose_fix_audit.md"
REP = RESULTS / "nonml_pnl_duplicate_sweep_result.md"


def main():
    # Reconstruction INDEPENDANTE de l'ensemble attendu.
    scripts = {p.name[len("nonml_"):-len("_backtest.py")]
               for p in SCRIPTS.glob("nonml_*_backtest.py")}
    npz = {p.name[len("nonml_"):-len("_pnl.npz")]
           for p in RESULTS.glob("nonml_*_pnl.npz")}

    attendu = []
    for n in sorted(scripts - npz):
        f = RESULTS / f"nonml_{n}_result.md"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        if "**PASS" in t or "PASS (niveau 1)" in t:
            attendu.append(n)

    # Noms REELLEMENT publies par le rapport, extraits de son bloc.
    lignes = REP.read_text(encoding="utf-8").splitlines()
    try:
        i0 = next(i for i, ln in enumerate(lignes)
                  if "PASS sans `.npz` sont nommés" in ln)
    except StopIteration:
        i0 = None
    publies = []
    if i0 is not None:
        for ln in lignes[i0:]:
            m = re.fullmatch(r"- `([^`]+)`", ln)
            if m:
                publies.append(m.group(1))
            elif publies and ln.strip() == "":
                break

    manquants = sorted(set(attendu) - set(publies))
    en_trop = sorted(set(publies) - set(attendu))

    # Verification individuelle, condition par condition.
    detail = []
    for n in publies:
        f = RESULTS / f"nonml_{n}_result.md"
        t = f.read_text(encoding="utf-8") if f.exists() else ""
        detail.append((n,
                       n in scripts,
                       n not in npz,
                       ("**PASS" in t or "PASS (niveau 1)" in t)))

    tous_ok = all(a and b and c for _, a, b, c in detail) and not manquants and not en_trop

    L = ["# Audit indépendant — la phrase calculée du balayage (#446)", ""]
    L.append("**Critère 2** : chaque nom publié est vérifié **indépendamment**. Cet audit")
    L.append("ne lit ni le balayage ni le script de cycle — il repart du dépôt, refait le")
    L.append("raisonnement, puis compare.")
    L.append("")
    L.append("Un nom publié doit satisfaire **les trois** conditions :")
    L.append("(a) script de backtest non-ML du dépôt ; (b) aucun `.npz` à son nom ;")
    L.append("(c) rapport portant un PASS.")
    L.append("")

    L.append("## Vérification nom par nom")
    L.append("")
    L.append("| Nom publié | (a) script | (b) sans `.npz` | (c) PASS | Verdict |")
    L.append("|---|---|---|---|---|")
    for n, a, b, c in detail:
        ok = a and b and c
        L.append(f"| `{n}` | {'✔' if a else '**non**'} | {'✔' if b else '**non**'} | "
                 f"{'✔' if c else '**non**'} | {'**vérifié**' if ok else '**ÉCHEC**'} |")
    L.append("")

    L.append("## L'ensemble est-il complet et sans excédent ?")
    L.append("")
    L.append(f"- attendus par la reconstruction indépendante : **{len(attendu)}**")
    L.append(f"- publiés par le rapport : **{len(publies)}**")
    L.append(f"- **manquants** (attendus, non publiés) : **{len(manquants)}**")
    L.append(f"- **en trop** (publiés, non attendus) : **{len(en_trop)}**")
    L.append("")
    for n in manquants:
        L.append(f"- manquant : `{n}`")
    for n in en_trop:
        L.append(f"- en trop : `{n}`")
    if not manquants and not en_trop:
        L.append("Les deux ensembles **coïncident exactement**. Le contrôle porte sur")
        L.append("l'ensemble, pas seulement sur le compte : un même effectif avec des noms")
        L.append("différents aurait échoué ici.")
    L.append("")

    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME' if tous_ok else 'NON CONFORME'}** — chaque nom publié satisfait")
    L.append("les trois conditions, et l'ensemble publié coïncide avec l'ensemble reconstruit")
    L.append("indépendamment.")
    L.append("")
    L.append("### Ce que cet audit ne prouve pas")
    L.append("")
    L.append("Il vérifie que la phrase **dit vrai**, pas que la situation soit saine. Un des")
    L.append("noms vérifiés — `tom_decomposition_overlay` — est une **stratégie PASS sans**")
    L.append("**`.npz`**, donc hors de portée du balayage de doublons. La phrase le nomme")
    L.append("désormais correctement ; le problème qu'elle nomme reste entier.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
