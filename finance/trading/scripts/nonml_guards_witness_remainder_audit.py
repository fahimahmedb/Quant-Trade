"""Audit adversarial du #484 — recalcul independant.

Le controle central n'est pas le compte : c'est que **chaque verdict ANODIN
soit verifiable**. Un cycle qui declare anodin ce qu'il ne veut pas compter
masquant serait indetectable par un simple recomptage.

L'audit teste donc chaque motif d'anodin par une route mecanique propre :
- << branche d'if/else >>  -> l'AST montre-t-il un `orelse` non vide ?
- << temoin dans un bloc parent >> -> une ecriture d'un bloc englobant
  mentionne-t-elle la variable ?
- << temoin sous un autre nom >>  -> seul motif NON verifiable mecaniquement,
  et il est signale comme tel.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_guards_witness_remainder_result.md"
OUT = RESULTS / "nonml_guards_witness_remainder_audit.md"
MOI = "guards_witness_remainder"
SECTION = re.compile(r"^### `(nonml_[a-z0-9_]+\.py)` l\.(\d+) — (.+)$", re.M)
VAR = re.compile(r"^if\s+(?:not\s+)?([a-z_][a-z0-9_]*)\s*:\s*$")


def englobe(py, ligne):
    """Le `if` gouvernant la ligne a-t-il un `orelse` non vide ? + sa variable."""
    try:
        src = py.read_text(encoding="utf-8")
        arbre = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError):
        return None, None, None
    lignes = src.splitlines()
    meilleur = None
    for n in ast.walk(arbre):
        if not isinstance(n, ast.If):
            continue
        fins = [x.lineno for x in ast.walk(n) if hasattr(x, "lineno")]
        if n.lineno <= ligne <= max(fins):
            if meilleur is None or n.lineno > meilleur.lineno:
                meilleur = n
    if meilleur is None:
        return None, None, None
    gl = lignes[meilleur.lineno - 1].strip()
    m = VAR.match(gl)
    return bool(meilleur.orelse), (m.group(1) if m else None), meilleur


def temoin_parent(py, noeud, var):
    """Une ecriture d'un bloc ENGLOBANT mentionne-t-elle `var` ?"""
    if noeud is None or var is None:
        return False
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return False
    interne = {id(x) for x in ast.walk(noeud)}
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call) or id(n) in interne:
            continue
        f = n.func
        nom = f.attr if isinstance(f, ast.Attribute) else \
            (f.id if isinstance(f, ast.Name) else "")
        if nom not in ("append", "write", "print", "write_text"):
            continue
        if re.search(rf"\b{re.escape(var)}\b", ast.dump(n)):
            return True
    return False


def main():
    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    cas = [(m.group(1), int(m.group(2)), m.group(3)) for m in SECTION.finditer(pub)]
    blocs = dict(re.findall(
        r"^### `(nonml_[a-z0-9_]+\.py)` l\.\d+ —[^\n]*\n\n[^\n]*\n\n(.*?)(?=\n### |\n## )",
        pub, re.M | re.S))

    lignes_r = []
    for nom, ln, etiq in cas:
        py = SCRIPTS / nom
        alt, var, noeud = englobe(py, ln)
        motif = blocs.get(nom, "")
        dit_alt = "if/else" in etiq or "branche d'`if/else`" in motif
        dit_parent = "bloc parent" in motif
        dit_autre = "sous un autre nom" in motif
        par = temoin_parent(py, noeud, var) if dit_parent else None
        lignes_r.append({"nom": nom, "ln": ln, "etiq": etiq, "alt": alt,
                         "dit_alt": dit_alt, "dit_parent": dit_parent,
                         "par": par, "dit_autre": dit_autre})

    L = ["# Audit adversarial — les sans témoin non examinés (#484)", ""]
    L.append("**Le contrôle central n'est pas le compte.** Un cycle qui déclarerait")
    L.append("« anodin » ce qu'il ne veut pas compter masquant serait **indétectable**")
    L.append("par un simple recomptage. L'audit teste donc **chaque motif d'anodin**")
    L.append("par une route mécanique propre.")
    L.append("")
    L.append(f"- sections de verdict relues dans le rapport : **{len(cas)}**")
    L.append("")

    L.append("## Motif « branche d'`if/else` » — vérifiable par AST")
    L.append("")
    L.append("Le `if` gouvernant la ligne a-t-il un `orelse` **non vide** ?")
    L.append("")
    L.append("| Cas | Motif invoqué | `orelse` non vide | Verdict |")
    L.append("|---|---|---|---|")
    faux_alt = 0
    for d in lignes_r:
        if not d["dit_alt"]:
            continue
        ok = bool(d["alt"])
        faux_alt += 0 if ok else 1
        L.append(f"| `{d['nom']}` l.{d['ln']} | alternative | "
                 f"**{'oui' if ok else 'NON'}** | "
                 f"{'**confirmé**' if ok else '**INFIRMÉ**'} |")
    L.append("")
    L.append("> **Tous confirmés.**" if not faux_alt else
             f"> **{faux_alt} motif(s) infirmé(s)** — publié tel quel.")
    L.append("")

    L.append("## Motif « témoin dans un bloc parent » — vérifiable par AST")
    L.append("")
    L.append("Une écriture située **hors** du bloc gardé mentionne-t-elle la variable ?")
    L.append("")
    L.append("| Cas | Témoin parent trouvé | Verdict |")
    L.append("|---|---|---|")
    faux_par = 0
    for d in lignes_r:
        if not d["dit_parent"]:
            continue
        ok = bool(d["par"])
        faux_par += 0 if ok else 1
        L.append(f"| `{d['nom']}` l.{d['ln']} | **{'oui' if ok else 'NON'}** | "
                 f"{'**confirmé**' if ok else '**INFIRMÉ**'} |")
    L.append("")
    L.append("> **Tous confirmés.**" if not faux_par else
             f"> **{faux_par} motif(s) infirmé(s)** — publié tel quel.")
    L.append("")

    L.append("## Motif « témoin sous un autre nom » — **non vérifiable mécaniquement**")
    L.append("")
    autres = [d for d in lignes_r if d["dit_autre"]]
    L.append(f"- cas invoquant ce motif : **{len(autres)}**")
    for d in autres:
        L.append(f"  - `{d['nom']}` l.{d['ln']}")
    L.append("")
    L.append("> **Aucune route mécanique ne peut confirmer ce motif** : dire que")
    L.append("> `rappel` témoigne pour `rates`, ou `ok4` pour `idem`, demande de")
    L.append("> comprendre que l'une est le complément de l'autre. **C'est un jugement,")
    L.append("> et l'audit ne peut que le signaler comme tel.**")
    L.append("")
    doubles = [d for d in autres if d["dit_parent"] or d["dit_alt"]]
    if doubles:
        L.append(f"*(**{len(doubles)} de ces cas sont sur-captés** : ma détection de")
        L.append("motif est **textuelle**, et `prereg_convention_coverage` cite dans son")
        L.append("motif la ligne `| le rapport **existe sous un autre nom** |` — qui")
        L.append("parle d'un rapport, pas d'un témoin. **Leur motif réel est le bloc")
        L.append("parent, déjà confirmé ci-dessus.** L'imprécision est de mon audit, et")
        L.append("je la publie plutôt que de la corriger en silence.)*")
        L.append("")
    L.append("**C'est la limite de cet audit, et elle porte sur le motif le plus")
    L.append("fréquent.** Un lecteur qui voudrait contester le cycle devrait commencer")
    L.append("par là — les citations verbatim du rapport sont ce qui le lui permet.")
    L.append("")

    L.append("## Le cycle s'accuse-t-il lui-même ?")
    L.append("")
    miens = [d for d in lignes_r
             if any(k in d["nom"] for k in ("hardcoded_tables_repair",
                                            "citer_451", "conditional_sections"))]
    L.append("| Script de cette série | Verdict reçu |")
    L.append("|---|---|")
    for d in miens:
        L.append(f"| `{d['nom']}` l.{d['ln']} | {d['etiq']} |")
    L.append("")
    if miens:
        L.append("> Le cycle **#482** figure dans la population qu'il mesure, et le")
        L.append("> rapport le dit : *« je viens de le commettre moi-même, dans le cycle")
        L.append("> qui l'a nommé deux fois »*. **L'auteur ne s'exclut pas.**")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / f"nonml_{MOI}_backtest.py").read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess|rm\s|unlink|open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- `subprocess` / `checkout` / suppression : **{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — le script ne fait que lire le disque.**"
             if not dangers else f"**À examiner : {dangers}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    total_v = sum(1 for d in lignes_r if d["dit_alt"] or d["dit_parent"])
    L.append(f"**{'CONCORDANT' if (not faux_alt and not faux_par) else 'DISCORDANT'}**"
             f" — **{total_v - faux_alt - faux_par}/{total_v}** motifs mécaniquement")
    L.append(f"vérifiables sont confirmés ; **{len(autres)}** relèvent d'un jugement que")
    L.append("l'audit **ne peut pas trancher**, et le dit.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
