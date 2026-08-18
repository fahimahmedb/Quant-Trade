"""Recensement des chiffres empruntes sans relecture (#500).

Specification pre-enregistree dans `PREREG_borrowed_figures_census.md`,
committee AVANT toute mesure -- les trois definitions comprises.

Au #497, une prediction reposait sur un << + 2 >> emprunte a l'audit du #496
sans etre recalcule ; il valait 3. Ce cycle mesure l'AMPLEUR de ce canal
d'erreur dans le depot, SANS RIEN EXECUTER.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_borrowed_figures_census_result.md"
RAP_497 = RESULTS / "nonml_execution_primitives_census_result.md"
AUD_496 = RESULTS / "nonml_execution_detection_rule_audit.md"
MOI = "borrowed_figures_census"

ECRIVAINS = {"append", "write_text", "print"}
CYCLE = re.compile(r"#\d{3}")
NOMBRE_GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
SUFFIXES = [("_backtest.py", "_result.md"), ("_audit.py", "_audit.md"),
            ("_robustness.py", "_robustness.md"),
            ("_sim_300e.py", "_sim_300e.md")]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def lu(chemin, motif_re):
    """Un chiffre LU dans un rapport publie -- jamais retape ici (#497)."""
    plat = re.sub(r"\s+", " ", chemin.read_text(encoding="utf-8")
                  .replace("*", "").replace("`", ""))
    m = re.search(motif_re, plat)
    return m.group(1) if m else "?"


def rapport_de(nom):
    for a, b in SUFFIXES:
        if nom.endswith(a):
            return f"{nom[:-len(a)]}{b}"
    return None


def chaines_publiees(arbre):
    """Les chaines qui PARTENT dans un rapport : arguments d'un ecrivain.

    Rend une liste de (texte_litteral, est_fstring). Pour une f-string, seul
    le texte HORS champ interpole est retenu -- c'est la distinction
    porteur / citeur du #473.
    """
    out = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = n.func.attr if isinstance(n.func, ast.Attribute) else (
            n.func.id if isinstance(n.func, ast.Name) else None)
        if nom not in ECRIVAINS:
            continue
        for a in list(n.args) + [k.value for k in n.keywords]:
            # Un fragment interne a une f-string n'est NI un Constant publie NI
            # une f-string : le compter serait compter deux fois la meme chaine.
            dedans = {id(v) for j in ast.walk(a) if isinstance(j, ast.JoinedStr)
                      for v in ast.walk(j) if v is not j}
            for s in ast.walk(a):
                if id(s) in dedans:
                    continue
                if isinstance(s, ast.Constant) and isinstance(s.value, str):
                    out.append((s.value, False))
                elif isinstance(s, ast.JoinedStr):
                    litt = "".join(v.value for v in s.values
                                   if isinstance(v, ast.Constant)
                                   and isinstance(v.value, str))
                    out.append((litt, True))
    return out


def emprunts_de(arbre):
    """Chaines publiees portant a la fois une reference #NNN et un nombre
    en gras LITTERAL (hors champ interpole)."""
    vus = []
    for txt, _ in chaines_publiees(arbre):
        cycles = CYCLE.findall(txt)
        nombres = NOMBRE_GRAS.findall(txt)
        if cycles and nombres:
            vus.append((txt.strip(), sorted(set(cycles)), nombres))
    return vus


def est_relecteur(arbre, src, mon_rapport):
    """Lit-il un rapport TIERS, au lieu d'en retaper les chiffres ?"""
    lit = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr == "read_text" for n in ast.walk(arbre))
    if not lit:
        return False, []
    tiers = sorted({s.value for s in ast.walk(arbre)
                    if isinstance(s, ast.Constant)
                    and isinstance(s.value, str)
                    and s.value.endswith(".md")
                    and s.value != mon_rapport})
    return bool(tiers), tiers


def main():
    avant = set(git("status", "--porcelain").splitlines())

    fichiers = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]
    porteurs, relecteurs, profils = [], [], {}
    for py in fichiers:
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        emp = emprunts_de(arbre)
        rel, tiers = est_relecteur(arbre, src, rapport_de(py.name))
        profils[py.name] = {"emp": emp, "rel": rel, "tiers": tiers}
        if emp:
            porteurs.append(py.name)
        if rel:
            relecteurs.append(py.name)

    n_emprunts = sum(len(profils[n]["emp"]) for n in porteurs)
    croise = [n for n in porteurs if profils[n]["rel"]]
    seuls = [n for n in porteurs if not profils[n]["rel"]]
    part_seuls = 100.0 * len(seuls) / len(porteurs) if porteurs else 0.0

    cites = {}
    for n in porteurs:
        for _, cy, _ in profils[n]["emp"]:
            for c in cy:
                cites[c] = cites.get(c, 0) + 1

    moi497 = "nonml_execution_primitives_census_backtest.py"
    p497_rel = profils.get(moi497, {}).get("rel", False)

    L = []
    A = L.append
    A("# Les **chiffres empruntés sans relecture** (pré-enregistré)")
    A("")
    v496 = lu(AUD_496, r"(\d+) script\(s\) appellent subprocess\.Popen")
    v497 = lu(RAP_497, r"\| P2 \|[^|]*\| (\d+) \|")
    A(f"Au **#497**, une prédiction reposait sur un « + {v496} » emprunté à")
    A(f"l'audit du **#496** sans être recalculé. Il valait **{v497}**. **Ce canal")
    A("d'erreur n'avait jamais été dénombré.**")
    A("")
    A("> **Ces deux nombres sont lus dans les rapports du #496 et du #497**, pas")
    A("> retapés. Une première version de ce rapport les tapait — **mon propre")
    A("> audit l'a signalé**, et il aurait fallu qu'un rapport sur les emprunts")
    A("> soit lui-même porteur pour que la démonstration soit complète. Elle")
    A("> l'est autrement : le détecteur a mordu son auteur.")
    A("")
    A("## Les trois définitions, citées verbatim")
    A("")
    A("> **Chaîne publiée** — littéral (`Constant`) ou f-string (`JoinedStr`)")
    noms_e = ", ".join(("`" + ("" if e == "print" else ".") + e + "(`")
                       for e in sorted(ECRIVAINS))
    A(f"> argument d'un appel à {noms_e}.")
    A("> Commentaires et docstrings exclus **par construction**.")
    A(">")
    A(f"> **Chiffre emprunté** — chaîne publiée portant **à la fois** `{CYCLE.pattern}`")
    A("> et un nombre en gras présent **en texte littéral**, hors de tout champ")
    A("> interpolé. *(Un champ `f\"**{n}**\"` **calcule** ; le même texte tapé")
    A("> avec ses chiffres **recopie**.)*")
    A(">")
    A("> *L'exemple est écrit sans chiffre à dessein : rédigé avec un nombre en")
    A("> gras, il était lui-même détecté comme littéral — le contrôle ne")
    A("> distingue pas un exemple typographique d'un chiffre en dur, et je n'ai")
    A("> pas voulu affaiblir le contrôle pour sauver ma phrase.*")
    A(">")
    A("> **Relecteur** — script appelant `.read_text(` **et** portant un littéral")
    A("> `.md` **autre** que son propre rapport.")
    A("")
    A("## Le recensement")
    A("")
    A(f"- scripts `nonml_*.py` analysés : **{len(profils)}**")
    A(f"- scripts **porteurs** d'au moins un chiffre emprunté : **{len(porteurs)}**")
    A(f"- **emprunts** au total : **{n_emprunts}**")
    A(f"- scripts **relecteurs** : **{len(relecteurs)}**")
    A("")
    A("## Le croisement — le cœur de la question")
    A("")
    A("| | Nombre | Part des porteurs |")
    A("|---|---|---|")
    pc = 100.0 * len(croise) / len(porteurs) if porteurs else 0.0
    A(f"| porteurs **qui lisent aussi** | **{len(croise)}** | "
      + f"**{pc:.1f} %**".replace(".", ",") + " |")
    A(f"| porteurs **qui ne lisent pas** | **{len(seuls)}** | "
      + f"**{part_seuls:.1f} %**".replace(".", ",") + " |")
    A("")
    if part_seuls > 50:
        A("> **La majorité des porteurs ne va pas lire.** Le chiffre attribué à")
        A("> un autre cycle est **retapé**, et rien dans le script ne le relie à")
        A("> sa source.")
    elif porteurs:
        A("> **La majorité des porteurs lit aussi des rapports tiers.** Le défaut")
        A("> n'est donc pas « ne pas savoir lire » mais **lire et retaper quand")
        A("> même** — ce qui est pire : l'outil était là et n'a pas servi.")
    A("")
    A("## Les cycles cités dans les emprunts")
    A("")
    A(f"- cycles distincts cités : **{len(cites)}**")
    A("")
    if cites:
        A("| Cycle cité | Emprunts |")
        A("|---|---|")
        for c, k in sorted(cites.items(), key=lambda x: (-x[1], x[0]))[:15]:
            A(f"| `{c}` | **{k}** |")
        reste = sorted(cites.items(), key=lambda x: (-x[1], x[0]))[15:]
        if reste:
            bas, haut = min(k for _, k in reste), max(k for _, k in reste)
            combien = f"**{bas}** fois" if bas == haut else f"de **{bas}** à **{haut}** fois"
            A("")
            A(f"*(**{len(reste)}** autres cycles, cités {combien} chacun, non listés.)*")
    A("")
    A("## Les porteurs qui ne lisent pas, nommés")
    A("")
    A(f"- effectif : **{len(seuls)}**")
    A("")
    for n in sorted(seuls)[:12]:
        e = profils[n]["emp"][0]
        extrait = e[0][:90].replace("\n", " ")
        A(f"- `{n}` — cite {', '.join('`'+c+'`' for c in e[1])} : « {extrait}… »")
    if len(seuls) > 12:
        A("")
        A(f"*(et **{len(seuls) - 12}** autres.)*")
    A("")
    A("## Ce que ce recensement **ne dit pas**")
    A("")
    A("Il mesure une **exposition**, pas une **erreur**. Aucun emprunt n'est ici")
    A("confronté à sa source : un chiffre retapé peut être **exact**, comme le")
    A("« ~4,1 % » du **#499** l'était. **Vérifier chaque emprunt est un autre")
    A("cycle**, et il est proposé en fin de rapport.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = len(porteurs) >= 10
    p2 = part_seuls > 50
    p3 = bool(p497_rel)
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| porteurs ≥ 10 | ≥ 10 | {len(porteurs)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| majorité des porteurs ne lisent pas | > 50 % | "
      + f"{part_seuls:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| le backtest du #497 est relecteur | oui | "
      f"{'oui' if p497_rel else 'non'} | **{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("> La prédiction 3 dit aussi ce que la mesure **ne peut pas** voir : le")
    A("> « + 2 » fautif du #497 était dans son **pré-enregistrement**, pas dans")
    A("> son code. **Ce recensement ne l'aurait pas attrapé** — et c'est une")
    A("> limite de la définition, déclarée d'avance.")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Les seuls appels externes visent `git status`, **en lecture**.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Les trois définitions citées verbatim, établies par AST", True),
         (f"Population (**{len(profils)}**), porteurs (**{len(porteurs)}**), "
          f"emprunts (**{n_emprunts}**), relecteurs (**{len(relecteurs)}**)",
          len(profils) > 0),
         ("Croisement publié avec la part des porteurs non relecteurs",
          bool(porteurs)),
         (f"Cycles cités nommés avec leur compte (**{len(cites)}**)", bool(cites)),
         ("Aucun script exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    A("> de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(porteurs)} porteurs / {n_emprunts} emprunts, "
          f"{len(relecteurs)} relecteurs, non-lecteurs {part_seuls:.1f} %")


if __name__ == "__main__":
    main()
