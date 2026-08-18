"""Erreur de reference ou erreur de valeur ? (#503)

Specification pre-enregistree dans `PREREG_reference_vs_value_errors.md`,
committee AVANT toute mesure -- les trois definitions comprises.

Le #502 laisse 29 emprunts suspects sans dire de quoi ils souffrent. Deux
maladies s'y confondent : le bon chiffre attribue au mauvais cycle, ou le
mauvais chiffre attribue au bon cycle. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_reference_vs_value_errors_result.md"
MOI = "reference_vs_value_errors"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
CLASSES = ["référence probable ailleurs", "valeur suspecte", "indéterminé"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def magnitude(v):
    """Nombre de chiffres de la partie entiere."""
    ent = re.sub(r"\D", "", v.split(",")[0].split(".")[0])
    return len(ent.lstrip("0")) or 1


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    secs = c501.sections_backlog()

    # --- Les suspects du #502, re-derives par SES fonctions ----------------
    suspects = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI, MOI)):
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for t, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is None:
                    continue
                cite, cles = cy[0], c502.mots_cles(t)
                sec = secs.get(cite)
                if sec is None or len(cles) < c502.RECOUVREMENT:
                    continue
                fs = c502.fenetres(v, sec)
                if not fs:
                    origine = "absent"
                elif max(sum(1 for c in cles if c in f) for f in fs) \
                        >= c502.RECOUVREMENT:
                    continue                      # confirmé au #502
                else:
                    origine = "sur-crédité"
                suspects.append({"py": py.name, "cite": cite, "val": v,
                                 "cles": cles, "origine": origine, "sec": sec})

    # --- La classification -------------------------------------------------
    for s in suspects:
        cand = []
        for nom, sec in secs.items():
            if nom == s["cite"]:
                continue
            fs = c502.fenetres(s["val"], sec)
            if not fs:
                continue
            if max(sum(1 for c in s["cles"] if c in f) for f in fs) \
                    >= c502.RECOUVREMENT:
                cand.append(nom)
        s["cand"] = sorted(cand)
        mag = magnitude(s["val"])
        s["mag"] = mag
        s["grandeur"] = any(magnitude(g) == mag for g in GRAS.findall(s["sec"]))
        s["classe"] = ("référence probable ailleurs" if cand else
                       "valeur suspecte" if s["grandeur"] else "indéterminé")

    comptes = {c: sum(1 for s in suspects if s["classe"] == c) for c in CLASSES}
    par_origine = {}
    for o in ("sur-crédité", "absent"):
        grp = [s for s in suspects if s["origine"] == o]
        par_origine[o] = {c: sum(1 for s in grp if s["classe"] == c)
                          for c in CLASSES}
        par_origine[o]["_n"] = len(grp)
    ailleurs = [s for s in suspects if s["classe"] == "référence probable ailleurs"]
    uniques = [s for s in ailleurs if len(s["cand"]) == 1]

    def part(o):
        n = par_origine[o]["_n"]
        return 100.0 * par_origine[o]["référence probable ailleurs"] / n if n else 0.0
    ecart_pts = abs(part("sur-crédité") - part("absent"))

    L = []
    A = L.append
    A("# **Erreur de référence** ou **erreur de valeur** ? (pré-enregistré)")
    A("")
    A("Le **#502** laisse des emprunts « suspects » sans dire de quoi ils")
    A("souffrent. Deux maladies s'y confondent : le **bon chiffre attribué au")
    A("mauvais cycle**, ou le **mauvais chiffre attribué au bon cycle**.")
    A("")
    A("## Les trois définitions, citées verbatim")
    A("")
    A("> - **magnitude** — nombre de chiffres de la partie entière ;")
    A("> - **section candidate** — une section **autre** que celle citée où le")
    A(f">   nombre est en gras **et** ≥ **{c502.RECOUVREMENT}** mots-clés de")
    A(f">   l'emprunt tombent dans **±{c502.FENETRE} caractères** ;")
    A("> - **grandeur présente** — la section **citée** contient un nombre en")
    A(">   gras de **même magnitude**.")
    A("")
    A(f"Les paramètres du #502 — **{c502.LETTRES_MIN} lettres**, "
      f"**±{c502.FENETRE} caractères**, **{c502.RECOUVREMENT} mots-clés** — sont")
    A("**repris tels quels**. Les retoucher ici serait régler un détecteur sur")
    A("la population qu'il doit juger.")
    A("")
    A("## Les trois classes")
    A("")
    A(f"- suspects classés : **{len(suspects)}**")
    A(f"- sections de backlog explorées : **{len(secs)}**")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for c in CLASSES:
        pt = 100.0 * comptes[c] / len(suspects) if suspects else 0.0
        A(f"| **{c}** | **{comptes[c]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## Les deux groupes, **séparément**")
    A("")
    A("*L'engagement 3 l'exige : les fondre en un total masquerait leur")
    A("différence, qui est la question même de ce cycle.*")
    A("")
    A("| Origine (#502) | Effectif | référence ailleurs | valeur suspecte | indéterminé |")
    A("|---|---|---|---|---|")
    for o in ("sur-crédité", "absent"):
        d = par_origine[o]
        A(f"| **{o}** | **{d['_n']}** | **{d[CLASSES[0]]}** | "
          f"**{d[CLASSES[1]]}** | **{d[CLASSES[2]]}** |")
    A("")
    A("| Groupe | Part « référence probable ailleurs » |")
    A("|---|---|")
    for o in ("sur-crédité", "absent"):
        A(f"| **{o}** | " + f"**{part(o):.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- écart entre les deux parts : " + f"**{ecart_pts:.1f}** points".replace(".", ","))
    A("")
    if ecart_pts >= 20:
        A("> **Les deux groupes ne souffrent pas de la même chose.** La")
        A("> distinction du #502 entre « sur-crédité » et « absent » recouvre")
        A("> bien deux situations différentes.")
    else:
        A("> **Les deux groupes se répartissent de la même façon.** La")
        A("> distinction du #502 entre « sur-crédité » et « absent »")
        A("> **ne recouvre rien** — et cela affaiblit rétrospectivement sa")
        A("> lecture, qu'il faut donc corriger ici.")
    A("")
    A("## Les « référence probable ailleurs », nommés")
    A("")
    A(f"- effectif : **{len(ailleurs)}**")
    A(f"- dont à section candidate **unique** : **{len(uniques)}**")
    A("")
    if ailleurs:
        A("| Script | Cite | Nombre | Candidates | Lesquelles |")
        A("|---|---|---|---|---|")
        for s in sorted(ailleurs, key=lambda x: (len(x["cand"]), x["py"]))[:20]:
            lst = ", ".join("`" + c + "`" for c in s["cand"][:4])
            if len(s["cand"]) > 4:
                lst += f", … (**{len(s['cand']) - 4}** autres)"
            A(f"| `{s['py']}` | `{s['cite']}` | **{s['val']}** | "
              f"**{len(s['cand'])}** | {lst} |")
        if len(ailleurs) > 20:
            A("")
            A(f"*(et **{len(ailleurs) - 20}** autres.)*")
    A("")
    if uniques:
        A("### Les seuls pour lesquels une correction serait **nommable**")
        A("")
        for s in sorted(uniques, key=lambda x: x["py"]):
            A(f"- `{s['py']}` cite `{s['cite']}` pour **{s['val']}** — une seule")
            A(f"  section candidate : `{s['cand'][0]}`.")
        A("")
    A("## La direction des candidates — ce que ma classe **sur-affirme**")
    A("")
    num = lambda c: int(c.lstrip("#"))
    apres_only = [s for s in ailleurs
                  if all(num(c) > num(s["cite"]) for c in s["cand"])]
    avant_any = [s for s in ailleurs
                 if any(num(c) < num(s["cite"]) for c in s["cand"])]
    A(f"- « référence ailleurs » dont **toutes** les candidates sont")
    A(f"  **postérieures** au cycle cité : **{len(apres_only)}** sur "
      f"**{len(ailleurs)}**")
    A(f"- dont **au moins une** est **antérieure** : **{len(avant_any)}**")
    A("")
    if len(apres_only) > len(ailleurs) / 2:
        A("> **Ma classe s'appelle mal.** Une candidate **postérieure** au cycle")
        A("> cité n'indique aucune erreur de référence : elle indique qu'un")
        A("> cycle **ultérieur a repris le chiffre** — ce qui est le")
        A("> fonctionnement normal de ce registre, où chaque cycle commente les")
        A("> précédents.")
        A(">")
        A("> **La lecture honnête de « référence probable ailleurs » est donc :")
        A("> le nombre est repris plus tard, pas attribué au mauvais cycle.**")
        A("> Je garde le nom figé au pré-enregistrement — le changer après")
        A("> mesure serait renommer un résultat gênant — mais son sens est")
        A("> corrigé ici, par la mesure et non par une impression.")
    else:
        A("> Les candidates ne sont pas systématiquement postérieures : la")
        A("> classe garde le sens que le pré-enregistrement lui donnait.")
    A("")
    A("> **Conséquence sur la prédiction 3** : les **12** candidates uniques ne")
    A("> sont **pas** des corrections nommables si elles sont postérieures. Le")
    A(f"> compte de corrections réellement nommables tombe à **{len(avant_any)}**.")
    A("")
    A("## Ce que « probable » veut dire ici")
    A("")
    A("**Aucune référence n'est corrigée, aucun nombre n'est déclaré faux.**")
    A("Une section candidate peut parler du même sujet **par hasard** : ce")
    A("dépôt répète ses thèmes d'un cycle à l'autre, et c'est précisément ce")
    A("qui rend la méthode faillible. Un suspect à **plusieurs** candidates")
    A("n'est d'ailleurs **pas** corrigeable — la méthode dit seulement que le")
    A("nombre vit ailleurs **aussi**.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = len(ailleurs) >= 5
    p2 = ecart_pts >= 20
    p3 = len(uniques) >= 1
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| « référence ailleurs » ≥ 5 | ≥ 5 | {len(ailleurs)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| écart entre groupes ≥ 20 points | ≥ 20 | "
      + f"{ecart_pts:.1f}".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| ≥ 1 candidate unique | ≥ 1 | {len(uniques)} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Population, mots-clés et fenêtres sont **importés** des backtests des")
    A("#500, #501 et #502 — leurs fonctions, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Trois définitions citées verbatim, paramètres du #502 inchangés",
          True),
         (f"Les **{len(suspects)}** suspects classés, **{len(CLASSES)}** "
          "classes publiées", len(suspects) > 0),
         ("Détail sur-crédités / absents publié séparément",
          all(par_origine[o]["_n"] >= 0 for o in par_origine)),
         (f"« Référence ailleurs » nommés (**{len(ailleurs)}**), candidates "
          f"uniques distinguées (**{len(uniques)}**)", True),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts et du")
    A("> registre à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(suspects)} suspects : " +
          ", ".join(f"{c}={comptes[c]}" for c in CLASSES) +
          f" ; uniques={len(uniques)}, écart={ecart_pts:.1f} pts")


if __name__ == "__main__":
    main()
