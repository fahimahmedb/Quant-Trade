"""Audit independant du #504.

Le backtest identifie les rapports d'un cycle par le NOM DE STRATEGIE extrait
de sa section. Cet audit les identifie autrement : par la DATE D'INTRODUCTION
GIT. Les rapports d'un cycle sont ceux dont le premier commit tombe entre
celui de la section precedente et celui de la suivante. Meme question, source
d'identification differente -- et c'est le point faible du #504.

Il verifie en outre trois proprietes que le backtest n'enonce pas :
  1. les quatre classes forment une PARTITION ;
  2. l'effectif egale les 13 << valeurs suspectes >> du #503 ;
  3. << confirme au rapport >> implique << present dans un rapport >>.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_suspect_values_reports_result.md"
RAP_503 = RESULTS / "nonml_reference_vs_value_errors_result.md"
BT = SCRIPTS / "nonml_suspect_values_reports_backtest.py"
OUT = RESULTS / "nonml_suspect_values_reports_audit.md"
MOI = "suspect_values_reports"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dates_ajout(prefixe):
    """{nom -> ts du premier ajout} en un seul parcours de l'historique."""
    s = git("log", "--reverse", "--date-order", "--format=@%ct",
            "--name-status", "--diff-filter=A", "--", prefixe)
    out, ts = {}, None
    for l in s.splitlines():
        if l.startswith("@"):
            ts = int(l[1:])
        elif l.startswith("A\t") and ts is not None:
            nom = l.split("\t", 1)[1].strip().split("/")[-1]
            if nom.endswith(".md") and nom not in out:
                out[nom] = ts
    return out


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    bt = module("nonml_suspect_values_reports_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")

    # --- Route independante : rattachement par DATE -----------------------
    d_prereg = {n: t for n, t in
                dates_ajout("finance/trading").items()
                if n.startswith("PREREG_")}
    d_rap = dates_ajout("finance/trading/results/")

    # Ordre des cycles = ordre d'ajout de leur PREREG.
    ordre = sorted(d_prereg.items(), key=lambda x: x[1])
    bornes = {}
    for i, (nom, ts) in enumerate(ordre):
        fin = ordre[i + 1][1] if i + 1 < len(ordre) else float("inf")
        bornes[nom] = (ts, fin)

    # --- Le classement publie --------------------------------------------
    def num(motif, txt=p):
        m = re.search(motif, txt)
        return int(m.group(1)) if m else None
    pub = {
        "total": num(r"valeurs suspectes reclassées : (\d+)"),
        "conf": num(r"\| confirmé au rapport \| (\d+) \|"),
        "sans": num(r"\| présent sans contexte \| (\d+) \|"),
        "abs": num(r"\| absent du rapport \| (\d+) \|"),
        "introuv": num(r"\| rapport introuvable \| (\d+) \|"),
        "residus": num(r"Les résidus — absents des deux sources - effectif : (\d+)"),
    }
    n503 = num(r"\| valeur suspecte \| (\d+) \|", plat(RAP_503.read_text(encoding="utf-8")))
    partition = (pub["conf"] + pub["sans"] + pub["abs"] + pub["introuv"]) == pub["total"]
    effectif_ok = pub["total"] == n503

    # --- Les rapports rattaches par date, compares a ceux par nom ---------
    lignes_corr = re.findall(r"\|\s*`(#\d{3})`\s*\|\s*(?:`([a-z0-9_]+)`|\*\*aucun\*\*)"
                             r"\s*\|\s*\*\*(\d+)\*\*\s*\|", rap)
    accord_nom, desaccord = 0, []
    for cy, nom, n in lignes_corr:
        if not nom:
            desaccord.append((cy, "—", "aucun nom extrait"))
            continue
        pr = f"PREREG_{nom}.md"
        if pr not in bornes:
            desaccord.append((cy, nom, "PREREG absent de l'historique"))
            continue
        a, b = bornes[pr]
        par_date = {f for f, ts in d_rap.items() if a <= ts < b
                    and f.startswith("nonml_")}
        par_nom = {f.name for f in RESULTS.glob(f"nonml_{nom}_*.md")
                   if MOI not in f.name}
        if par_nom and par_nom <= par_date:
            accord_nom += 1
        else:
            manquants = sorted(par_nom - par_date)
            desaccord.append((cy, nom, f"{len(manquants)} rapport(s) hors "
                                       f"fenêtre temporelle"))

    # --- Les residus, revérifiés dans TOUT results/ -----------------------
    bloc = rap.split("## Les résidus", 1)[-1].split("\n## ", 1)[0]
    residus = re.findall(r"\|\s*`([a-z0-9_]+\.py)`\s*\|\s*`(#\d{3})`\s*\|"
                         r"\s*\*\*([\d,\.]+)\*\*\s*\|", bloc)
    ailleurs_total = 0
    for _, _, v in residus:
        trouve = False
        for f in RESULTS.glob("nonml_*.md"):
            if MOI in f.name:
                continue
            try:
                if c502.fenetres(v, f.read_text(encoding="utf-8")):
                    trouve = True
                    break
            except UnicodeDecodeError:
                continue
        if trouve:
            ailleurs_total += 1

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — valeurs suspectes cherchées aux rapports (#504)")
    A("")
    A("Le backtest identifie les rapports d'un cycle par le **nom de stratégie**")
    A("extrait de sa section. Cet audit les identifie par la **date")
    A("d'introduction git** : les rapports d'un cycle sont ceux dont le premier")
    A("commit tombe entre son `PREREG_` et le suivant. **Même question, source")
    A("d'identification différente** — et c'est le point faible du #504.")
    A("")
    A("## Le rattachement, recoupé par les dates")
    A("")
    A(f"- cycles vérifiés : **{len(lignes_corr)}**")
    A(f"- dont les rapports trouvés par **nom** tombent bien dans la **fenêtre")
    A(f"  temporelle** du cycle : **{accord_nom}**")
    A(f"- en désaccord : **{len(desaccord)}**")
    A("")
    A(f"- `PREREG_` datés par cette route : **{len(d_prereg)}** *(un compte nul")
    A("  signalerait que la route ne mesure rien — le premier jet de cet audit")
    A("  passait `finance/trading/PREREG_` à `git log`, qui n'est pas un chemin :")
    A("  il rattachait **0** cycle et le critère l'absolvait quand même.)*")
    A("")
    if desaccord:
        A("| Cycle | Nom | Motif du désaccord |")
        A("|---|---|---|")
        for cy, nom, motif in desaccord:
            A(f"| `{cy}` | `{nom}` | {motif} |")
        A("")
        A("> Un désaccord ici **ne condamne pas** le #504 : un cycle peut")
        A("> régénérer un rapport bien après l'avoir créé, et la fenêtre")
        A("> temporelle le range alors ailleurs. **Le rattachement par nom")
        A("> reste le plus sûr**, et l'écart mesure la marge de l'autre route.")
        A("")
    A("## Trois propriétés que le backtest n'énonce pas")
    A("")
    A(f"- les quatre classes forment une **partition** : "
      f"**{'OUI' if partition else 'NON'}**")
    A(f"- l'effectif (**{pub['total']}**) égale les valeurs suspectes du #503 "
      f"(**{n503}**) : **{'OUI' if effectif_ok else 'NON'}**")
    A(f"- résidus dont le nombre apparaît **quelque part** dans `results/` : "
      f"**{ailleurs_total}** sur **{len(residus)}**")
    A("")
    if ailleurs_total:
        A("> Ces résidus **existent ailleurs dans les rapports**, mais pas dans")
        A("> ceux du cycle qu'ils citent. Cela ne les innocente pas : un nombre")
        A("> qui traîne partout dans un dépôt de cette taille ne prouve rien —")
        A("> c'est exactement la faiblesse que le **#501** avait mesurée.")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Les deux routes partagent la **règle contextuelle** du #502. Leur accord")
    A("valide le **rattachement cycle → rapport**, pas l'idée qu'un recouvrement")
    A("de mots-clés vaut identité de sujet. **Aucun des cinq cycles #500-#504")
    A("n'a établi qu'un seul emprunt soit faux** — ils ont établi ce qu'on ne")
    A("peut pas conclure.")
    A("")
    A("## Inertie et chiffres calculés")
    A("")
    A(f"- fichiers de l'arbre modifiés hors ce cycle : **{len(sales)}**")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; dont **tapés en "
      f"dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("les quatre classes forment une partition", partition),
            ("l'effectif égale les valeurs suspectes du #503", effectif_ok),
            (f"le rattachement par nom est recoupé par les dates "
             f"(**{accord_nom}**/**{len(lignes_corr)}**)",
             bool(lignes_corr) and accord_nom == len(lignes_corr)),
            (f"les **{len(residus)}** résidus sont re-cherchés dans tout "
             "`results/`", len(residus) > 0),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** pour les prix ; la")
    A("datation employée ici est **strictement rétrospective** — premier commit")
    A("d'ajout, jamais l'état courant.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — accord {accord_nom}/{len(lignes_corr)}, "
          f"résidus ailleurs {ailleurs_total}/{len(residus)}")


if __name__ == "__main__":
    main()
