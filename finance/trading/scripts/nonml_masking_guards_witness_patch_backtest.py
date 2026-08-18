"""Ajouter un temoin aux 2 sections masquantes (#487).

Specification pre-enregistree dans `PREREG_masking_guards_witness_patch.md`,
committee AVANT toute modification et toute mesure.

Cycle de MODIFICATION. La verification est STATIQUE : les deux scripts vises
ont des effets de bord reels (l'un execute d'autres scripts, l'autre ecrit un
rapport qui n'est pas le sien), et les executer pour << verifier >> la
reparation causerait plus de degats que le defaut repare.

AUCUN script du depot n'est execute par ce cycle.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_masking_guards_witness_patch_result.md"
MOI = "masking_guards_witness_patch"
CIBLES = [("nonml_six_reports_regeneration_backtest.py", "perdus"),
          ("nonml_sweep_pass_prose_fix_backtest.py", "strategies")]
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
ECRIVENT = ("append", "write", "print", "write_text")
GARDES = (ast.If, ast.For, ast.While, ast.Try)
VAR = re.compile(r"^if\s+(?:not\s+)?([a-z_][a-z0-9_]*)\s*:\s*$")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def nomcall(n):
    f = n.func
    return f.attr if isinstance(f, ast.Attribute) else \
        (f.id if isinstance(f, ast.Name) else "")


def classer(src):
    """Regle du #481, reprise SANS modification : avec/sans temoin."""
    try:
        arbre = ast.parse(src)
    except SyntaxError:
        return None
    lignes = src.splitlines()
    avec, sans, nonnom = [], [], []
    for fn in [x for x in ast.walk(arbre) if isinstance(x, ast.FunctionDef)]:
        titres, libres = [], []

        def visite(nd, gardes):
            for e in ast.iter_child_nodes(nd):
                g = gardes + [e] if isinstance(e, GARDES) else gardes
                if isinstance(e, ast.Call) and nomcall(e) in ECRIVENT:
                    for a in e.args:
                        if isinstance(a, ast.Constant) \
                                and isinstance(a.value, str) \
                                and a.value.startswith(("## ", "### ")) and gardes:
                            titres.append((a.lineno, gardes[-1]))
                    if not gardes:
                        libres.append(ast.dump(e))
                visite(e, g)

        visite(fn, [])
        for ln, garde in titres:
            gl = lignes[garde.lineno - 1].strip()
            m = VAR.match(gl)
            if not m:
                nonnom.append(ln)
            elif any(re.search(rf"\b{re.escape(m.group(1))}\b", d) for d in libres):
                avec.append(ln)
            else:
                sans.append(ln)
    return avec, sans, nonnom


def main():
    L = ["# **Ajouter un témoin** aux 2 sections masquantes (pré-enregistré)", ""]
    L.append("**Cycle de MODIFICATION.** Les #481 et #484 ont établi **4 sections")
    L.append("masquantes** — dont la garde peut être fausse sans qu'aucun compte publié")
    L.append("hors garde ne signale l'absence. **Deux sont réparées ici**, par l'ajout")
    L.append("d'une ligne chacune.")
    L.append("")

    # --- 1. Le diff, publie en entier --------------------------------------
    diff = git("diff", "HEAD", "--", "finance/trading/scripts/")
    ajouts = [l for l in diff.splitlines()
              if l.startswith("+") and not l.startswith("+++")]
    supprs = [l for l in diff.splitlines()
              if l.startswith("-") and not l.startswith("---")]
    contenu = [l for l in ajouts if l.strip() != "+"]

    L.append("## Le diff, publié en entier")
    L.append("")
    L.append("```diff")
    for l in diff.splitlines():
        L.append(l)
    L.append("```")
    L.append("")
    L.append(f"- lignes **ajoutées** : **{len(ajouts)}** — dont **{len(contenu)}** de")
    L.append("  contenu et le reste des séparateurs vides")
    L.append(f"- lignes **supprimées ou modifiées** : **{len(supprs)}**")
    L.append("")
    if len(contenu) == 2 and not supprs:
        L.append("> **Exactement deux instructions ajoutées, rien de retiré.** Le")
        L.append("> pré-enregistrement annonçait « une ligne par cas, et rien d'autre » ;")
        L.append(f"> `git diff` compte **{len(ajouts)}** insertions parce qu'il compte")
        L.append("> aussi les lignes vides de séparation. **Je publie les deux chiffres")
        L.append("> plutôt que celui qui colle à mon annonce.**")
    L.append("")

    # --- 2. La regle du #481, avant et apres --------------------------------
    L.append("## La règle du #481, ré-appliquée avant et après")
    L.append("")
    L.append("| Script | Sans témoin **avant** | Sans témoin **après** | Total titres |")
    L.append("|---|---|---|---|")
    ok_deplace = True
    tot_avant = tot_apres = 0
    for nom, var in CIBLES:
        rel = f"finance/trading/scripts/{nom}"
        av = git("show", f"HEAD:{rel}")
        ap = (SCRIPTS / nom).read_text(encoding="utf-8")
        ca, cp = classer(av), classer(ap)
        if ca is None or cp is None:
            L.append(f"| `{nom}` | *illisible* | *illisible* | — |")
            ok_deplace = False
            continue
        n_av, n_ap = len(ca[1]), len(cp[1])
        t_av = sum(len(x) for x in ca)
        t_ap = sum(len(x) for x in cp)
        tot_avant += t_av
        tot_apres += t_ap
        if n_ap >= n_av:
            ok_deplace = False
        L.append(f"| `{nom}` | **{n_av}** | **{n_ap}** | {t_av} → {t_ap} |")
    L.append("")
    L.append(f"- titres conditionnels, **total avant** : **{tot_avant}** — "
             f"**après** : **{tot_apres}**")
    L.append("")
    if ok_deplace:
        L.append("> **Les deux cas passent de « sans témoin » à « avec témoin ».** La")
        L.append("> règle qui les avait dénoncés les reconnaît maintenant réparés — et")
        L.append("> c'est **la même règle, non modifiée**, qui rend les deux verdicts.")
    else:
        L.append("> **Le déplacement n'a pas eu lieu.** Ma forme de témoin ne satisfait")
        L.append("> pas ma propre règle. **Le patch est publié comme insuffisant plutôt")
        L.append("> que retouché jusqu'à passer** — c'était l'engagement 1.")
    L.append("")

    # --- 3. Aucune execution, et pourquoi -----------------------------------
    L.append("## Aucune exécution — et ce n'est pas une facilité")
    L.append("")
    L.append("| Script | Effet de bord constaté |")
    L.append("|---|---|")
    for nom, _v in CIBLES:
        src = (SCRIPTS / nom).read_text(encoding="utf-8")
        exe = bool(re.search(r"subprocess\.run\(\[sys\.executable", src))
        n_w = src.count("write_text")
        L.append(f"| `{nom}` | "
                 + ("**exécute d'autres scripts du dépôt**" if exe
                    else f"**écrit {n_w} fichiers**, dont un qui n'est pas le sien")
                 + " |")
    L.append("")
    L.append("> **Les exécuter pour « vérifier » la réparation causerait plus de dégâts")
    L.append("> que le défaut réparé.** Le #482 avait déjà refusé d'exécuter le premier")
    L.append("> pour cette raison exacte.")
    L.append("")
    L.append("**Conséquence, qu'il faut dire sans l'atténuer : les rapports publiés de")
    L.append("ces deux cycles ne portent PAS encore le témoin.** Ils le porteront à leur")
    L.append("prochaine exécution légitime. **La réparation est dans le code, pas encore")
    L.append("dans les rapports** — et un lecteur qui ouvrirait ces rapports aujourd'hui")
    L.append("ne verrait aucun changement.")
    L.append("")

    # --- 4. Perimetre : rien d'autre n'a bouge ------------------------------
    sale = git("status", "--porcelain")
    touches = [l[3:].strip() for l in sale.splitlines()
               if l.strip() and MOI not in l]
    L.append("## Le périmètre — rien d'autre n'a bougé")
    L.append("")
    L.append(f"- fichiers modifiés hors ceux de ce cycle : **{len(touches)}**")
    for t in touches[:10]:
        L.append(f"  - `{t}`")
    L.append("")
    attendus = {f"finance/trading/scripts/{n}" for n, _v in CIBLES}
    hors = [t for t in touches if t not in attendus]
    if not hors:
        L.append("> **Seuls les deux scripts visés sont modifiés**, et aucun rapport")
        L.append("> n'est régénéré.")
    else:
        L.append(f"> **{len(hors)} fichier(s) hors périmètre** — publié tel quel.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = ok_deplace
    p2 = tot_avant == tot_apres
    p3 = not hors
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| les 2 passent « avec témoin » | 2 | "
             f"{'2' if ok_deplace else 'non'} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| total de titres conditionnels inchangé | {tot_avant} | {tot_apres} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| aucun autre cas ne change | 0 | {len(hors)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if p1:
        L.append("**Le compte de masquants passe de 4 à 2.** Les deux qui restent sont")
        L.append("`battery_coverage` l.159 et `net_pnl_correction` l.279, établis au")
        L.append("#481 et **non touchés ici** — leur garde ne porte pas sur une liste de")
        L.append("résultats, et la même recette ne s'y applique pas telle quelle.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(contenu) == 2 and not supprs
    c3 = True   # aucune execution : verifiable dans le code de ce script
    L.append(f"1. Diff publié en entier, **{len(contenu)}** instructions ajoutées, "
             f"**{len(supprs)}** supprimée(s) — **{'OUI' if c1 else 'NON'}**.")
    L.append(f"2. Règle du #481 ré-appliquée avant/après — "
             f"**{'OUI' if ok_deplace else 'NON'}**.")
    L.append("3. Aucune exécution des deux scripts — **OUI**.")
    L.append(f"4. Aucun autre fichier modifié, aucun rapport régénéré — "
             f"**{'OUI' if p3 else 'NON'}**.")
    L.append("5. Le fait que les rapports ne portent pas encore le témoin, écrit — "
             "**OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and ok_deplace and c3 and p3) else 'FAIL'}** — le")
    L.append("critère porte sur le **procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"ajouts={len(ajouts)} contenu={len(contenu)} supprs={len(supprs)} "
          f"deplace={ok_deplace} tot={tot_avant}->{tot_apres} hors={len(hors)}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
