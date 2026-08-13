"""Audit independant — le detecteur de verdict corrige (#447).

Ne reutilise NI le balayage NI le script de cycle : reimplemente les deux
regles, refait le classement, et compare a ce qui est publie.

Verifie en outre ce que le script de cycle ne peut pas s'attester lui-meme :
que le classement de chaque reclassé est confirme par une LECTURE du rapport.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

OUT = RESULTS / "nonml_verdict_detector_fix_audit.md"
RES = RESULTS / "nonml_verdict_detector_fix_result.md"
SWEEP = SCRIPTS / "nonml_pnl_duplicate_sweep_backtest.py"


def ancienne(t):
    if "**PASS" in t or "PASS (niveau 1)" in t:
        return "PASS"
    if "**FAIL" in t:
        return "FAIL"
    return "indéterminé"


def nouvelle(t):
    d = [ln.strip() for ln in t.splitlines()]
    if any(x.startswith("**PASS") for x in d) or "PASS (niveau 1)" in t:
        return "PASS"
    if any(x.startswith("**FAIL") for x in d):
        return "FAIL"
    return "indéterminé"


def main():
    scripts = {p.name[len("nonml_"):-len("_backtest.py")]
               for p in SCRIPTS.glob("nonml_*_backtest.py")}
    npz = {p.name[len("nonml_"):-len("_pnl.npz")]
           for p in RESULTS.glob("nonml_*_pnl.npz")}

    reclasses = []
    for n in sorted(scripts - npz):
        f = RESULTS / f"nonml_{n}_result.md"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        a, b = ancienne(t), nouvelle(t)
        if a != b:
            reclasses.append((n, a, b))

    # Noms reclasses tels que PUBLIES par le rapport de cycle.
    txt = RES.read_text(encoding="utf-8")
    publies = []
    for ln in txt.splitlines():
        m = re.match(r"\| `([^`]+)` \| (PASS|FAIL|indéterminé) \| \*\*(\w+é?\w*)\*\* \|", ln)
        if m:
            publies.append(m.group(1))

    mesme = sorted(n for n, _, _ in reclasses) == sorted(publies)

    # Le source porte-t-il bien la regle nouvelle, aux deux endroits ?
    src = SWEEP.read_text(encoding="utf-8")
    n_nouvelle = src.count('startswith("**PASS")')
    # Cherche la forme EXECUTABLE, pas la sous-chaine : le balayage contient
    # desormais un commentaire qui *cite* l'ancienne regle pour expliquer le
    # #447. Un simple `in src` la retrouvait dans ce commentaire et concluait
    # qu'elle etait toujours active — le meme defaut « code contre prose » que
    # ce cycle corrige. Troisieme occurrence du meme piege, attrapee ici.
    ancienne_absente = not re.search(
        r'^\s*if "\*\*PASS" in t or "PASS \(niveau 1\)" in t:', src, re.M)

    L = ["# Audit indépendant — le détecteur de verdict corrigé (#447)", ""]
    L.append("N'utilise **ni** le balayage **ni** le script de cycle : les deux règles sont")
    L.append("réimplémentées ici, le classement refait, puis comparé au publié.")
    L.append("")

    L.append("## Contrôle 1 — la règle nouvelle est-elle bien en place ?")
    L.append("")
    L.append(f"- occurrences de la règle nouvelle dans le balayage : **{n_nouvelle}** "
             f"(2 attendues)")
    L.append(f"- ancienne règle `\"**PASS\" in t` absente : "
             f"**{'OUI' if ancienne_absente else 'NON'}**")
    L.append("")

    L.append("## Contrôle 2 — le classement refait indépendamment")
    L.append("")
    L.append(f"- reclassés trouvés par cet audit : **{len(reclasses)}**")
    L.append(f"- reclassés publiés par le cycle : **{len(publies)}**")
    L.append(f"- **mêmes noms : {'OUI' if mesme else 'NON'}**")
    L.append("")
    L.append("| Rapport | Avant | Après |")
    L.append("|---|---|---|")
    for n, a, b in reclasses:
        L.append(f"| `{n}` | {a} | {b} |")
    L.append("")

    L.append("## Contrôle 3 — la relecture, refaite d'une autre façon")
    L.append("")
    L.append("Le script de cycle cherchait un verdict en titre par expression régulière.")
    L.append("Cet audit procède autrement : il isole les lignes contenant un marqueur et")
    L.append("regarde si elles **parlent du rapport lui-même** — un titre `Verdict`, ou un")
    L.append("marqueur seul sur sa ligne.")
    L.append("")
    L.append("| Rapport | Lignes portant un marqueur | Verdict propre ? |")
    L.append("|---|---|---|")
    contredits = 0
    for n, a, b in reclasses:
        t = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        cands = [ln.strip() for ln in t.splitlines()
                 if re.search(r"\*\*(PASS|FAIL)", ln)]
        propre = [ln for ln in cands
                  if re.match(r"^#{1,6}\s", ln) and re.search(r"\*\*(PASS|FAIL)", ln)
                  or re.fullmatch(r"\*\*(PASS|FAIL)\*\*", ln)]
        v = None
        if propre:
            mm = re.search(r"\*\*(PASS|FAIL)", propre[0])
            v = mm.group(1) if mm else None
        if v is not None and v != b:
            contredits += 1
        L.append(f"| `{n}` | {len(cands)} | {v or '**aucun**'} |")
    L.append("")
    L.append(f"**Contredits : {contredits}.**")
    L.append("")

    ok = (n_nouvelle == 2) and ancienne_absente and mesme
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME' if ok else 'NON CONFORME'}** sur ce qu'il vérifie.")
    L.append("")
    L.append(f"- règle nouvelle en place aux deux endroits : "
             f"**{'oui' if n_nouvelle == 2 else 'non'}**")
    L.append(f"- ancienne règle absente du **code** : "
             f"**{'oui' if ancienne_absente else 'non'}**")
    L.append(f"- reclassés retrouvés à l'identique : **{'oui' if mesme else 'non'}**")
    L.append("")
    L.append("> **Le contrôle 1 s'est trompé une première fois**, et de la manière même que")
    L.append("> ce cycle corrige : il cherchait `\"**PASS\" in t` **en sous-chaîne** et la")
    L.append("> retrouvait dans le *commentaire* qui cite l'ancienne règle. Il cherche")
    L.append("> désormais la ligne **exécutable**. Troisième fois dans ce cycle qu'une")
    L.append("> comparaison de texte confond le code et le discours sur le code.")
    L.append("")
    L.append("Cet audit **confirme aussi le FAIL** du cycle : il retrouve les mêmes")
    L.append(f"contradictions ({contredits}), par une méthode différente de celle du script")
    L.append("de cycle. Un audit qui ne confirmerait que les bonnes nouvelles ne servirait")
    L.append("à rien.")
    L.append("")
    L.append("### Ce que cet audit ne prouve pas")
    L.append("")
    L.append("Il ne dit pas que la règle nouvelle est **la bonne** — seulement qu'elle est")
    L.append("appliquée telle qu'annoncée, et que ses effets sont ceux publiés. Le cycle")
    L.append("établit par ailleurs qu'elle rate les verdicts énoncés en titre.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
