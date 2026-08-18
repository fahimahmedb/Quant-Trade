"""Audit independant du #500 -- recalcul par une AUTRE mecanique.

Le backtest reconstruit le texte litteral d'une f-string en concatenant ses
`Constant` (les champs `{...}` disparaissent). Cet audit part du SEGMENT DE
SOURCE BRUT du meme noeud (`ast.get_source_segment`) et en retire les champs
`{...}` a la main. Meme definition, mecanique differente : c'est exactement
la ou un faux positif porteur/citeur se cacherait.

Il verifie en outre trois choses que le backtest n'enonce pas : que chaque
chaine detectee existe VERBATIM dans le fichier, qu'aucune n'est une
docstring, et que l'arithmetique du croisement ferme.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_borrowed_figures_census_result.md"
BT = SCRIPTS / "nonml_borrowed_figures_census_backtest.py"
OUT = RESULTS / "nonml_borrowed_figures_census_audit.md"
MOI = "borrowed_figures_census"

ECRIVAINS = {"append", "write_text", "print"}
CYCLE = re.compile(r"#\d{3}")
NOMBRE_GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
CHAMP = re.compile(r"\{[^{}]*\}")
GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def docstrings(arbre):
    """Les noeuds Constant qui sont des docstrings -- a exclure."""
    ids = set()
    for n in ast.walk(arbre):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                          ast.ClassDef)) and n.body:
            p = n.body[0]
            if isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant) \
                    and isinstance(p.value.value, str):
                ids.add(id(p.value))
    return ids


def emprunts_bruts(src, arbre):
    """Meme definition, depuis le SEGMENT BRUT : les champs {...} retires."""
    docs = docstrings(arbre)
    out = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = n.func.attr if isinstance(n.func, ast.Attribute) else (
            n.func.id if isinstance(n.func, ast.Name) else None)
        if nom not in ECRIVAINS:
            continue
        for a in list(n.args) + [k.value for k in n.keywords]:
            # En 3.11 les noeuds internes d'une f-string portent la position de
            # la f-string entiere : leur segment brut la redonne en entier, d'ou
            # un double comptage. On ne descend donc jamais dedans.
            dedans = {id(v) for j in ast.walk(a) if isinstance(j, ast.JoinedStr)
                      for v in ast.walk(j) if v is not j}
            for s in ast.walk(a):
                if id(s) in dedans:
                    continue
                if not isinstance(s, (ast.Constant, ast.JoinedStr)):
                    continue
                if isinstance(s, ast.Constant):
                    if not isinstance(s.value, str) or id(s) in docs:
                        continue
                seg = ast.get_source_segment(src, s)
                if seg is None:
                    continue
                nu = CHAMP.sub("", seg)           # les champs interpolés sautent
                if CYCLE.search(nu) and NOMBRE_GRAS.search(nu):
                    out.append((seg, sorted(set(CYCLE.findall(nu))),
                                NOMBRE_GRAS.findall(nu)))
    return out


def relecteur_regex(src, mon_md):
    """Meme definition, par expressions regulieres sur le texte."""
    if not re.search(r"\.read_text\s*\(", src):
        return False
    tiers = {m for m in re.findall(r"[\"']([^\"']+\.md)[\"']", src) if m != mon_md}
    return bool(tiers)


def rapport_de(nom):
    for a, b in (("_backtest.py", "_result.md"), ("_audit.py", "_audit.md"),
                 ("_robustness.py", "_robustness.md"),
                 ("_sim_300e.py", "_sim_300e.md")):
        if nom.endswith(a):
            return f"{nom[:-len(a)]}{b}"
    return None


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)

    porteurs, relecteurs, absents, docs_vus = [], [], [], []
    n_emp = 0
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if MOI in py.name:
            continue
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        emp = emprunts_bruts(src, arbre)
        if emp:
            porteurs.append(py.name)
            n_emp += len(emp)
            for seg, _, _ in emp:
                if seg not in src:               # verbatim dans le fichier ?
                    absents.append(py.name)
        if relecteur_regex(src, rapport_de(py.name)):
            relecteurs.append(py.name)

    croise = sorted(set(porteurs) & set(relecteurs))
    seuls = sorted(set(porteurs) - set(relecteurs))

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {
        "porteurs": num(r"porteurs d'au moins un chiffre emprunté : (\d+)"),
        "emprunts": num(r"emprunts au total : (\d+)"),
        "relecteurs": num(r"scripts relecteurs : (\d+)"),
        "croise": num(r"porteurs qui lisent aussi \| (\d+)"),
        "seuls": num(r"porteurs qui ne lisent pas \| (\d+)"),
    }
    somme_ok = (pub["croise"] is not None and pub["seuls"] is not None
                and pub["porteurs"] == pub["croise"] + pub["seuls"])

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — chiffres empruntés sans relecture (#500)")
    A("")
    A("Le backtest **reconstruit** le texte d'une f-string en concaténant ses")
    A("`Constant`. Cet audit part du **segment de source brut** du même nœud et")
    A("retire les champs `{…}` à la main. **Même définition, mécanique")
    A("différente** — c'est là qu'un faux positif porteur/citeur se cacherait.")
    A("")
    A("## Le recomptage")
    A("")
    A("| Grandeur | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    lignes = [("porteurs", pub["porteurs"], len(porteurs)),
              ("emprunts", pub["emprunts"], n_emp),
              ("relecteurs", pub["relecteurs"], len(relecteurs)),
              ("porteurs qui lisent aussi", pub["croise"], len(croise)),
              ("porteurs qui ne lisent pas", pub["seuls"], len(seuls))]
    for nom, a, b in lignes:
        A(f"| {nom} | **{a}** | **{b}** | "
          f"{'**oui**' if a == b else '**NON**'} |")
    A("")
    ecarts = [x for x in lignes if x[1] != x[2]]
    A(f"- grandeurs en désaccord : **{len(ecarts)}**")
    if ecarts:
        A("")
        for nom, a, b in ecarts:
            A(f"  - **{nom}** : rapport **{a}**, audit **{b}** — écart "
              f"**{abs((a or 0) - (b or 0))}**")
    A("")
    A("## Trois contrôles que le backtest n'énonce pas")
    A("")
    A(f"- chaînes détectées **absentes verbatim** de leur fichier : "
      f"**{len(absents)}**")
    A("- docstrings comptées comme chaînes publiées : **0** *(exclues par")
    A("  construction : cet audit les identifie explicitement et les écarte)*")
    A(f"- l'arithmétique du croisement ferme (**{pub['croise']}** + "
      f"**{pub['seuls']}** = **{pub['porteurs']}**) : "
      f"**{'OUI' if somme_ok else 'NON'}**")
    A("")
    if not ecarts:
        A("> Les deux mécaniques **concordent sur les cinq grandeurs**. La")
        A("> distinction porteur / citeur tient donc aussi bien depuis le texte")
        A("> reconstruit que depuis la source brute — ce qui n'allait pas de soi :")
        A("> les #496 et #497 ont tous deux vu une route se tromper.")
    A("")
    A("## Ce que cet audit ne vérifie pas non plus")
    A("")
    A("**Aucun emprunt n'est confronté à sa source.** Le rapport le disait ; je")
    A("le redis, parce qu'un audit qui concorde sur cinq comptes peut donner")
    A("l'illusion d'avoir validé les **valeurs**. Il n'a validé que le")
    A("**dénombrement**.")
    A("")
    A("## Inertie et chiffres calculés")
    A("")
    A(f"- fichiers de l'arbre modifiés hors ce cycle : **{len(sales)}**")
    A(f"- nombres en gras dans le rapport : **{len(GRAS.findall(rap))}** ; "
      f"dont **tapés en dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("les deux mécaniques donnent les mêmes cinq comptes", not ecarts),
            ("chaque chaîne détectée existe verbatim dans son fichier",
             not absents),
            ("l'arithmétique du croisement ferme", bool(somme_ok)),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("Son équivalent ici est **l'inertie**, vérifiée ci-dessus.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(ecarts)} écart(s)")


if __name__ == "__main__":
    main()
