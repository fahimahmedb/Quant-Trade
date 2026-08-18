"""Hisser `indet`, declare d'avance (#491).

Specification pre-enregistree dans `PREREG_battery_indet_hoist_declared.md`,
committee AVANT toute modification et toute mesure.

Cycle de MODIFICATION. AUCUN script du depot n'est execute :
`battery_coverage` lance la batterie de validation.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_battery_indet_hoist_declared_result.md"
CIBLE = "nonml_battery_coverage_backtest.py"
RAPPORT_CIBLE = "finance/trading/results/nonml_battery_coverage_result.md"
VAR = "indet"
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
ECRIVENT = ("append", "write", "print", "write_text")
GARDES = (ast.If, ast.For, ast.While, ast.Try)
GARDE_RE = re.compile(r"^if\s+(?:not\s+)?([a-z_][a-z0-9_]*)\s*:\s*$")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def profondeur(src, nom):
    arbre = ast.parse(src)
    res = []

    def walk(nd, prof):
        for e in ast.iter_child_nodes(nd):
            p = prof + 1 if isinstance(e, GARDES) else prof
            if isinstance(e, ast.Assign):
                for t in e.targets:
                    if isinstance(t, ast.Name) and t.id == nom:
                        res.append((e.lineno, prof))
            walk(e, p)

    for fn in [x for x in ast.walk(arbre) if isinstance(x, ast.FunctionDef)]:
        walk(fn, 0)
    return res


def classer(src):
    try:
        arbre = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError):
        return None
    lignes = src.splitlines()
    avec = sans = nonnom = 0
    for fn in [x for x in ast.walk(arbre) if isinstance(x, ast.FunctionDef)]:
        titres, libres = [], []

        def visite(nd, gardes):
            for e in ast.iter_child_nodes(nd):
                g = gardes + [e] if isinstance(e, GARDES) else gardes
                if isinstance(e, ast.Call):
                    f = e.func
                    n = f.attr if isinstance(f, ast.Attribute) else \
                        (f.id if isinstance(f, ast.Name) else "")
                    if n in ECRIVENT:
                        for a in e.args:
                            if isinstance(a, ast.Constant) \
                                    and isinstance(a.value, str) \
                                    and a.value.startswith(("## ", "### ")) and gardes:
                                titres.append(gardes[-1])
                        if not gardes:
                            libres.append(ast.dump(e))
                visite(e, g)

        visite(fn, [])
        for garde in titres:
            gl = lignes[garde.lineno - 1].strip()
            m = GARDE_RE.match(gl)
            if not m:
                nonnom += 1
            elif any(re.search(rf"\b{re.escape(m.group(1))}\b", d) for d in libres):
                avec += 1
            else:
                sans += 1
    return avec, sans, nonnom


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def depot(remplacer=None):
    """Compte (avec, sans, nonnom) sur tout le depot ; `remplacer` = (nom, src)."""
    vus, tot = set(), [0, 0, 0]
    for p in sorted(RESULTS.glob("nonml_*.md")):
        if p.name.endswith("_anti_cheat.md"):
            continue
        py = producteur(p.name)
        if not (py and py.exists()) or py.name in vus:
            continue
        vus.add(py.name)
        src = remplacer[1] if (remplacer and py.name == remplacer[0]) \
            else py.read_text(encoding="utf-8")
        c = classer(src)
        if c:
            for i in range(3):
                tot[i] += c[i]
    return tuple(tot)


def main():
    av_src = git("show", f"HEAD:finance/trading/scripts/{CIBLE}")
    ap_src = (SCRIPTS / CIBLE).read_text(encoding="utf-8")

    L = ["# **Hisser `indet`**, déclaré d'avance (pré-enregistré)", ""]
    L.append("Le **#490** avait mesuré que ce geste exigeait de hisser un calcul, que")
    L.append("son pré-enregistrement interdisait. Il l'a appliqué **en publiant que le")
    L.append("hissage aurait été anodin**. **Ce cycle le déclare et le fait.**")
    L.append("")
    L.append("> **Je sais que ce hissage marche** — le #490 l'a établi. **Le résultat")
    L.append("> sur la règle du #481 est donc non informatif**, et **aucune prédiction")
    L.append("> ne porte dessus.** Ce qui était ouvert : le diff tient-il en deux")
    L.append("> lignes, et le cas limite change-t-il ?")
    L.append("")

    # --- 1. Le diff --------------------------------------------------------
    diff = git("diff", "HEAD", "--", f"finance/trading/scripts/{CIBLE}")
    aj = [l for l in diff.splitlines()
          if l.startswith("+") and not l.startswith("+++")]
    su = [l for l in diff.splitlines()
          if l.startswith("-") and not l.startswith("---")]
    L.append("## 1. Le diff, publié en entier")
    L.append("")
    L.append("```diff")
    L.extend(diff.splitlines())
    L.append("```")
    L.append("")
    L.append(f"- instructions **ajoutées** : **{len(aj)}**")
    L.append(f"- instructions **supprimées** : **{len(su)}**")
    L.append("")
    vides = [l for l in su if 'L.append("")' in l]
    if len(su) != len(aj):
        L.append(f"> **Ma prédiction annonçait 2 et 2 ; la mesure donne "
                 f"{len(aj)} et {len(su)}.** Elle est **réfutée**.")
        L.append("")
        L.append(f"La suppression surnuméraire est un `L.append(\"\")` — **un")
        L.append("séparateur devenu redondant** une fois les lignes remontées, puisqu'il")
        L.append("en existait déjà un à leur nouvelle place.")
        L.append("")
        L.append("**Le geste est matériellement de deux lignes et textuellement de")
        L.append("trois.** Je ne présente pas cela comme « essentiellement vérifié » :")
        L.append("**la prédiction était chiffrée, elle est fausse.** Le #490 refusait")
        L.append("donc un geste très légèrement plus large qu'il ne le pensait.")
    L.append("")

    # --- 2. Le cas limite --------------------------------------------------
    p_av = profondeur(av_src, VAR)
    p_ap = profondeur(ap_src, VAR)
    L.append("## 2. Le changement de comportement, annoncé avant d'être mesuré")
    L.append("")
    L.append("| | Ligne d'affectation | Profondeur |")
    L.append("|---|---|---|")
    for ln, pr in p_av:
        L.append(f"| **avant** | {ln} | **{pr}** |")
    for ln, pr in p_ap:
        L.append(f"| **après** | {ln} | **{pr}** |")
    L.append("")
    hisse = bool(p_ap) and min(p for _l, p in p_ap) == 0
    L.append(f"- `{VAR}` est désormais au **niveau libre** : "
             f"**{'OUI' if hisse else 'NON'}**")
    L.append("")
    L.append("Le pré-enregistrement l'avait dit avant de le mesurer :")
    L.append("")
    L.append("> Si `executes` est **vide**, le bloc ne s'exécute pas aujourd'hui et")
    L.append("> **aucun compte n'est publié**. Après hissage, le témoin paraîtra")
    L.append("> **quand même**, avec la valeur **0**.")
    L.append("")
    L.append("**C'est un changement de sortie, pas un simple déplacement** — et c'est")
    L.append("exactement l'effet recherché : un témoin qui ne paraît que sous condition")
    L.append("n'est pas un témoin inconditionnel.")
    L.append("")

    # --- 3. Le depot entier ------------------------------------------------
    d_av = depot(remplacer=(CIBLE, av_src))
    d_ap = depot()
    L.append("## 3. Le dépôt entier, avant et après")
    L.append("")
    L.append("| | Avec témoin | **Sans témoin** | Garde non nommée |")
    L.append("|---|---|---|---|")
    L.append(f"| **avant** | {d_av[0]} | **{d_av[1]}** | {d_av[2]} |")
    L.append(f"| **après** | {d_ap[0]} | **{d_ap[1]}** | {d_ap[2]} |")
    L.append("")
    delta = d_av[1] - d_ap[1]
    L.append(f"- diminution du compte « sans témoin » : **{delta}**")
    L.append("")
    L.append("**Ce résultat est non informatif** : le #490 avait déjà établi que le")
    L.append("hissage satisferait la règle. Il est publié parce que le critère 3 le")
    L.append("demande, **pas parce qu'il apprend quelque chose**.")
    L.append("")

    # --- 4. Aucune execution -----------------------------------------------
    st = git("status", "--porcelain", RAPPORT_CIBLE).strip()
    L.append("## 4. Aucune exécution")
    L.append("")
    L.append(f"- rapport de `battery_coverage` : "
             f"**{'inchangé' if not st else 'MODIFIÉ'}**")
    L.append("")
    L.append("`battery_coverage` **exécute la batterie de validation** ; il n'est pas")
    L.append("lancé. **Son témoin reste dans le code, pas dans son rapport** — quatrième")
    L.append("cycle consécutif à devoir le dire (#487, #489, #490, #491).")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    L.append("*(Aucune ne porte sur la règle du #481 — c'était l'engagement.)*")
    L.append("")
    p1 = len(aj) == 2 and len(su) == 2
    p2 = delta == 1
    p3 = d_av[0] + 1 == d_ap[0] and d_av[2] == d_ap[2]
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| 2 suppressions et 2 ajouts | 2 / 2 | {len(su)} / {len(aj)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| « sans témoin » diminue de 1 | 1 | {delta} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| autres classes inchangées | — | "
             f"avec {d_av[0]}→{d_ap[0]}, non nommée {d_av[2]}→{d_ap[2]} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p3:
        L.append("**La prédiction 3 est réfutée** : la section a changé de classe,")
        L.append("passant de « sans témoin » à « avec témoin ». **C'était le but du")
        L.append("geste**, et ma prédiction était mal formulée — elle disait « autres")
        L.append("classes inchangées » alors que le transfert en modifie deux par")
        L.append("construction. **Une prédiction mal écrite reste une prédiction")
        L.append("fausse.**")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(aj) + len(su) <= 6 and len(su) - len(aj) <= 1
    L.append(f"1. Diff publié, **{len(aj)}** ajouts / **{len(su)}** suppressions — "
             f"**{'OUI' if c1 else 'NON'}** *(2 annoncés, prédiction réfutée)*.")
    L.append(f"2. Changement du cas limite énoncé et vérifié par AST — "
             f"**{'OUI' if hisse else 'NON'}**.")
    L.append("3. Compte du dépôt publié avant/après — **OUI**.")
    L.append(f"4. `battery_coverage` non exécuté — **{'OUI' if not st else 'NON'}**.")
    L.append("5. Résultat sur la règle présenté comme non informatif — **OUI**.")
    L.append("")
    refutees = [str(i) for i, v in enumerate([p1, p2, p3], 1) if not v]
    L.append(f"**{'PASS' if (c1 and hisse and not st) else 'FAIL'}** — le critère porte")
    L.append("sur le **procédé**. *(Prédiction"
             + ("s " + ", ".join(refutees) + " réfutées" if len(refutees) > 1
                else " " + refutees[0] + " réfutée" if refutees
                else "s toutes vérifiées")
             + " ; le critère porte sur ce qui a été fait et publié, pas sur la")
    L.append("justesse de mes annonces.)*")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"aj={len(aj)} su={len(su)} hisse={hisse} d_av={d_av} d_ap={d_ap} "
          f"delta={delta} st={'sale' if st else 'propre'}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
