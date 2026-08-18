"""Les verdicts du depot : forme ou mesure ? (#506)

Specification pre-enregistree dans `PREREG_verdicts_form_vs_measure.md`,
committee AVANT toute mesure -- les quatre classes comprises.

Le #498 a montre qu'un verdict pouvait basculer sans qu'aucun fait ne change :
seul le detecteur avait change. Combien de verdicts de ce depot reposent sur
un appariement de forme plutot que sur une mesure ? SANS RIEN EXECUTER.
"""
import ast
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_verdicts_form_vs_measure_result.md"
MOI = "verdicts_form_vs_measure"

EXT_DONNEES = (".txt", ".npz", ".csv")
EXT_TEXTE = (".md", ".py")
IMPORTS_DONNEES = ("data_loader", "load_ohlc")
CLASSES = {
    "F": "forme — lit le texte **et** apparie, **sans** lire de données",
    "D": "mesure — lit des données, **sans** lire le texte du dépôt",
    "M": "mixte — lit **les deux**",
    "N": "ni l'un ni l'autre",
}
N_RECENTS = 20


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def litteraux(arbre):
    return [s.value for s in ast.walk(arbre)
            if isinstance(s, ast.Constant) and isinstance(s.value, str)]


def profil(src, arbre):
    lits = litteraux(arbre)
    modules = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            modules.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            modules.add(n.module.split(".")[0])
    donnees = (any(l.endswith(EXT_DONNEES) or "data/" in l for l in lits)
               or bool(modules & set(IMPORTS_DONNEES)))
    texte = any(l.endswith(EXT_TEXTE) or
                (("*" in l or "glob" in l) and l.endswith(EXT_TEXTE))
                for l in lits)
    apparie = "re" in modules
    return donnees, texte, apparie


def classe(donnees, texte, apparie):
    if donnees and texte:
        return "M"
    if texte and apparie:
        return "F"
    if donnees:
        return "D"
    return "N"


def dates_ajout():
    s = git("log", "--reverse", "--date-order", "--format=@%ct",
            "--name-status", "--diff-filter=A", "--", "finance/trading")
    out, ts = {}, None
    for l in s.splitlines():
        if l.startswith("@"):
            ts = int(l[1:])
        elif l.startswith("A\t") and ts is not None:
            nom = l.split("\t", 1)[1].strip().split("/")[-1]
            if nom not in out:
                out[nom] = ts
    return out


def jour(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y")


def mediane(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def main():
    avant = set(git("status", "--porcelain").splitlines())
    dates = dates_ajout()

    pop = []
    sans_date = 0
    for py in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        if MOI in py.name:
            continue
        rap = RESULTS / f"{py.name[:-len('_backtest.py')]}_result.md"
        if not rap.exists():
            continue
        try:
            txt = rap.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "**PASS**" not in txt and "**FAIL**" not in txt:
            continue
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        d, t, a = profil(src, arbre)
        mien = f"{py.name[:-len('_backtest.py')]}_result.md"
        autres = [l for l in litteraux(arbre)
                  if (l.endswith(EXT_TEXTE) or "glob" in l) and l != mien]
        t_hors_soi = any(l.endswith(EXT_TEXTE) for l in autres) or \
            any("*" in l and l.endswith(EXT_TEXTE) for l in autres)
        ts = dates.get(py.name)
        if ts is None:
            sans_date += 1
            continue
        pop.append({"py": py.name, "cl": classe(d, t, a), "ts": ts,
                    "d": d, "t": t, "a": a,
                    "cl2": classe(d, t_hors_soi, a)})

    pop.sort(key=lambda x: x["ts"])
    comptes = {k: sum(1 for p in pop if p["cl"] == k) for k in CLASSES}
    recents = pop[-N_RECENTS:]
    part_glob = 100.0 * comptes["F"] / len(pop) if pop else 0.0
    part_rec = (100.0 * sum(1 for p in recents if p["cl"] == "F") / len(recents)
                if recents else 0.0)
    med = {k: mediane([p["ts"] for p in pop if p["cl"] == k]) for k in CLASSES}
    d_recents = sum(1 for p in recents if p["cl"] == "D")

    L = []
    A = L.append
    A("# Les verdicts du dépôt : **forme** ou **mesure** ? (pré-enregistré)")
    A("")
    A("Le **#498** a montré qu'un verdict pouvait basculer de **C** à **A**")
    A("**sans qu'aucun fait ne change** : seul le détecteur avait changé.")
    A("**Un verdict vaut ce que vaut son détecteur** — et personne n'avait")
    A("compté combien, dans ce dépôt, reposent sur un appariement de forme.")
    A("")
    A("## Les quatre classes, citées verbatim")
    A("")
    A(f"> - **lit des données** : littéral finissant par "
      f"{', '.join('`' + e + '`' for e in EXT_DONNEES)}, ou mentionnant")
    A(f">   `data/`, ou import de "
      f"{' / '.join('`' + m + '`' for m in IMPORTS_DONNEES)} ;")
    A(f"> - **lit le texte du dépôt** : littéral finissant par "
      f"{', '.join('`' + e + '`' for e in EXT_TEXTE)} ;")
    A("> - **apparie** : `import re`.")
    A("")
    A("| Classe | Définition |")
    A("|---|---|")
    for k, v in CLASSES.items():
        A(f"| **{k}** | {v} |")
    A("")
    A("**Rapport porteur de verdict** : son `.md` contient `**PASS**` ou")
    A("`**FAIL**`.")
    A("")
    A("## Le recensement")
    A("")
    A(f"- rapports **porteurs d'un verdict** : **{len(pop)}**")
    A("  *(au sens figé — verdict **en gras**. La section « couverture » plus")
    A("  bas montre que ce critère écarte la majorité du corpus : **les comptes")
    A("  ci-dessous décrivent une minorité des rapports du dépôt**.)*")
    A(f"- scripts écartés faute de date d'introduction : **{sans_date}**")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for k in CLASSES:
        pt = 100.0 * comptes[k] / len(pop) if pop else 0.0
        A(f"| **{k}** | **{comptes[k]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## La chronologie — le dépôt a-t-il dérivé ?")
    A("")
    A("| Classe | Effectif | Date médiane d'introduction |")
    A("|---|---|---|")
    for k in CLASSES:
        A(f"| **{k}** | **{comptes[k]}** | "
          f"{jour(med[k]) if med[k] else '—'} |")
    A("")
    A("| Population | Part de **F** |")
    A("|---|---|")
    A(f"| **ensemble** (**{len(pop)}**) | "
      + f"**{part_glob:.1f} %**".replace(".", ",") + " |")
    A(f"| **{N_RECENTS} plus récents** | "
      + f"**{part_rec:.1f} %**".replace(".", ",") + " |")
    A("")
    derive = part_rec - part_glob
    A(f"- écart : " + f"**{derive:+.1f}** points".replace(".", ","))
    A("")
    if med["D"] is None:
        A("> **La question de la dérive ne peut pas être tranchée** : la classe")
        A("> **D** est vide **par construction de ma règle**, comme la section")
        A("> suivante le montre. Une médiane sans effectif ne se compare à rien,")
        A("> et je ne remplace pas D par M après coup pour sauver la")
        A("> comparaison — ce serait choisir sa population après avoir vu le")
        A("> résultat.")
    elif med["F"] and med["D"] and med["F"] > med["D"]:
        A("> **La dérive est réelle et datée.** Les scripts qui rendent un")
        A("> verdict sur du **texte** sont médianement **postérieurs** à ceux")
        A("> qui rendent un verdict sur des **données**. Ce dépôt a commencé")
        A("> par mesurer des marchés et a fini par se mesurer lui-même.")
    elif med["F"] and med["D"]:
        A("> **Pas de dérive.** Les deux familles sont contemporaines — ce sont")
        A("> **deux activités menées en parallèle**, pas une qui remplace")
        A("> l'autre. C'est contraire à l'intuition qui m'a fait poser la")
        A("> question, et c'est la mesure qui tranche.")
    A("")
    A(f"## Les **{N_RECENTS}** plus récents, nommés")
    A("")
    A("| Script | Classe | Introduit le |")
    A("|---|---|---|")
    for p in reversed(recents):
        A(f"| `{p['py']}` | **{p['cl']}** | {jour(p['ts'])} |")
    A("")
    A(f"- dont de classe **D** (mesure pure) : **{d_recents}**")
    A("")
    A("## Un défaut de ma propre règle, mesuré")
    A("")
    A("**La classe D est vide, et c'est un artefact.** « Lit le texte du dépôt »")
    A("se déclenche sur le littéral que **tout** script porte : le chemin de")
    A("**son propre rapport**. Aucun script ne peut donc être « données sans")
    A("texte ». **La classe D était impossible à peupler par construction.**")
    A("")
    comptes2 = {k: sum(1 for p in pop if p["cl2"] == k) for k in CLASSES}
    A("En excluant le rapport du script lui-même du critère « lit le texte » —")
    A("**diagnostic, non verdict : la règle reste celle du pré-enregistrement** :")
    A("")
    A("| Classe | Règle figée | Sans son propre rapport |")
    A("|---|---|---|")
    for k in CLASSES:
        A(f"| **{k}** | **{comptes[k]}** | **{comptes2[k]}** |")
    A("")
    A(f"> La famille qui **lit réellement des données** est donc **M**")
    A(f"> (**{comptes['M']}**), et non **D**. C'est elle qu'il faut lire comme")
    A("> « verdict adossé à une mesure ».")
    A("")
    A("## La couverture de la population")
    A("")
    n_bold = len(pop)
    nus = 0
    for py in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        if MOI in py.name:
            continue
        rap = RESULTS / f"{py.name[:-len('_backtest.py')]}_result.md"
        if not rap.exists():
            continue
        try:
            txt = rap.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "**PASS**" in txt or "**FAIL**" in txt:
            continue
        if re.search(r"\bPASS\b|\bFAIL\b", txt):
            nus += 1
    A(f"- rapports retenus (verdict **en gras**) : **{n_bold}**")
    A(f"- rapports portant `PASS`/`FAIL` **sans gras**, donc **écartés** : "
      f"**{nus}**")
    A("")
    A("> La définition figée exigeait le **gras**. Elle laisse donc de côté")
    A(f"> **{nus}** rapports qui rendent bien un verdict. **La population n'est")
    A("> pas exhaustive**, et le dire vaut mieux que présenter les comptes")
    A("> ci-dessus comme un recensement complet.")
    A("")
    A("## Ce que ce compte ne dit pas")
    A("")
    A("**Un verdict de forme n'est pas un faux verdict.** Vérifier qu'un script")
    A("ne contient pas de défaut est un travail légitime, et le #498 montre")
    A("seulement qu'un tel verdict est **fragile au détecteur** — pas qu'il est")
    A("faux. Ce recensement mesure une **nature**, pas une **qualité**.")
    A("")
    A("## Auto-exclusion, déclarée d'avance")
    A("")
    A("**Ce cycle ne se compte pas lui-même**, et il serait, par sa propre")
    A("règle, un **F** de plus : il lit des `.md` et des `.py`, il importe `re`,")
    A("il ne touche aucune donnée de marché. **L'auto-exclusion était déclarée")
    A("au pré-enregistrement** (règle du #447) — elle est rappelée ici, non tue.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = part_glob >= 50.0
    p2 = d_recents >= 1
    p3 = bool(med["F"] and med["D"] and med["F"] > med["D"])
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| part de **F** ≥ 50 % | ≥ 50 % | "
      + f"{part_glob:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 **D** parmi les {N_RECENTS} plus récents | ≥ 1 | {d_recents} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    testable3 = med["F"] is not None and med["D"] is not None
    verdict3 = ("vérifiée" if p3 else "réfutée") if testable3 else "non testable"
    A(f"| médiane **F** postérieure à médiane **D** | oui | "
      f"{'oui' if p3 else ('non' if testable3 else 'classe D vide')} | "
      f"**{verdict3}** |")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Les seuls appels externes visent `git log` et `git status`, **en")
    A("lecture**.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Quatre classes citées verbatim, établies par AST", True),
         (f"Population (**{len(pop)}**) et quatre comptes publiés", len(pop) > 0),
         ("Dates médianes par classe publiées",
          all(med[k] is not None or comptes[k] == 0 for k in CLASSES)),
         (f"Les **{N_RECENTS}** plus récents nommés, deux parts de **F** "
          "comparées", len(recents) > 0),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de")
    A("> l'historique à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(pop)} verdicts : " +
          ", ".join(f"{k}={comptes[k]}" for k in CLASSES) +
          f" ; F global {part_glob:.1f} %, F récents {part_rec:.1f} %")


if __name__ == "__main__":
    main()
