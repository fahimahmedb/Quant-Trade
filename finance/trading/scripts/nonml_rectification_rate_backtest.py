"""Le taux de rectification des cycles par leurs successeurs (#512).

Specification pre-enregistree dans `PREREG_rectification_rate.md`, committee
AVANT toute mesure -- marqueurs et fenetre compris.

Le depot affirme regulierement qu'un cycle en rectifie un autre. Le TAUX n'a
jamais ete mesure, ni sa TENDANCE. SANS RIEN EXECUTER.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_rectification_rate_result.md"
MOI = "rectification_rate"

MARQUEURS = ["réfut", "rétract", "corrig", "invalid", "fauss", "faux",
             "erron", "sur-affirm", "surestim", "sur-estim", "dissou", "tombe"]
FENETRE = 200          # la fenetre du #502, reprise sans modification
N_RECENTS = 30
N_TRANCHES = 8


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    avant = set(git("status", "--porcelain").splitlines())
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    secs = c501.sections_backlog()
    numeros = sorted(int(k.lstrip("#")) for k in secs)

    # --- Qui rectifie qui -------------------------------------------------
    rect = {n: [] for n in numeros}
    par_marqueur, meme_phrase, fenetre_seule = {}, [], []
    for mmm in numeros:
        txt = secs[f"#{mmm}"].lower()
        for m in re.finditer(r"#(\d{3})", txt):
            nnn = int(m.group(1))
            if nnn >= mmm or nnn not in rect:
                continue                       # que des successeurs, pas soi
            a = max(0, m.start() - FENETRE)
            b = min(len(txt), m.end() + FENETRE)
            fen = txt[a:b]
            touches = [k for k in MARQUEURS if k in fen]
            if touches:
                if mmm not in rect[nnn]:
                    rect[nnn].append(mmm)
                for k in touches:
                    par_marqueur[k] = par_marqueur.get(k, 0) + 1
                # meme PHRASE que la reference, ou seulement dans la fenetre ?
                ph = re.split(r"(?<=[.!?;:])\s+", fen)
                seg = next((x for x in ph if m.group(0) in x), "")
                if any(k in seg for k in MARQUEURS):
                    meme_phrase.append((nnn, mmm))
                else:
                    fenetre_seule.append((nnn, mmm))

    rectifies = [n for n in numeros if rect[n]]
    taux = 100.0 * len(rectifies) / len(numeros) if numeros else 0.0
    recents = numeros[-N_RECENTS:]
    r_rec = [n for n in recents if rect[n]]
    taux_rec = 100.0 * len(r_rec) / len(recents) if recents else 0.0

    delais = sorted(min(rect[n]) - n for n in rectifies)
    med = (delais[len(delais) // 2] if len(delais) % 2
           else (delais[len(delais) // 2 - 1] + delais[len(delais) // 2]) / 2) \
        if delais else None

    top = sorted(rectifies, key=lambda n: (-len(rect[n]), n))[:10]

    taille = max(1, len(numeros) // N_TRANCHES)
    tranches, i = [], 0
    while i < len(numeros):
        bout = (numeros[i:i + taille] if len(numeros) - i >= taille * 2
                else numeros[i:])
        if not bout:
            break
        tranches.append(bout)
        i += len(bout)

    parts = [100.0 * sum(1 for n in b if rect[n]) / len(b) for b in tranches]
    tendance = ("**monte**" if len(parts) >= 2 and parts[-1] > parts[0]
                else "**baisse**" if len(parts) >= 2 and parts[-1] < parts[0]
                else "**stable**")

    L = []
    A = L.append
    A("# Le **taux de rectification** : combien de cycles ont été corrigés ?")
    A("")
    A("Le **#509** a clos la série des emprunts sur ce constat : *treize")
    A("détecteurs successifs et leurs limites*. Le dépôt affirme régulièrement")
    A("qu'un cycle en rectifie un autre — **le taux n'avait jamais été mesuré**.")
    A("")
    A("## La règle, citée verbatim")
    A("")
    A(f"> Un cycle `#NNN` est **rectifié** si une section **postérieure**")
    A(f"> contient `#NNN` avec, dans **±{FENETRE} caractères** *(la fenêtre du")
    A("> #502, reprise sans modification)*, au moins un marqueur :")
    A(">")
    A("> ```")
    A("> " + "   ".join(MARQUEURS))
    A("> ```")
    A(">")
    A("> **Auto-rectification exclue** : seul un successeur compte.")
    A("")
    A("## Ce que cette mesure **ne** mesure **pas**")
    A("")
    A("Elle compte **la fréquence à laquelle une rectification est écrite**,")
    A("pas celle à laquelle une erreur est commise.")
    A("")
    A("> **Un dépôt qui n'avouerait jamais rien obtiendrait un taux de zéro.**")
    A("> Un taux élevé peut signaler beaucoup d'erreurs **ou** beaucoup de")
    A("> franchise, et **cette mesure ne les distingue pas**. Toute lecture qui")
    A("> l'oublierait serait fausse, y compris la mienne.")
    A("")
    A("## Le recensement")
    A("")
    A(f"- sections de backlog : **{len(numeros)}**")
    A(f"- cycles **rectifiés** par au moins un successeur : **{len(rectifies)}**")
    A(f"- **taux global** : " + f"**{taux:.1f} %**".replace(".", ","))
    A(f"- taux sur les **{N_RECENTS} derniers** : "
      + f"**{taux_rec:.1f} %**".replace(".", ","))
    A(f"- délai médian avant première rectification : "
      f"**{med if med is not None else '—'}** cycles")
    A("")
    A("## La tendance, par tranches")
    A("")
    A("| Tranche | Cycles | Rectifiés | Part |")
    A("|---|---|---|---|")
    for b, pt in zip(tranches, parts):
        k = sum(1 for n in b if rect[n])
        A(f"| #{b[0]}–#{b[-1]} | **{len(b)}** | **{k}** | "
          + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- de la première à la dernière tranche, le taux {tendance} "
      + f"(**{parts[0]:.1f} %** → **{parts[-1]:.1f} %**)".replace(".", ",")
      if len(parts) >= 2 else "- une seule tranche : pas de tendance")
    A("")
    if len(parts) >= 2 and parts[-1] > parts[0]:
        A("> **Le taux monte.** Les cycles récents se rectifient les uns les")
        A("> autres plus souvent que les anciens. **Cela ne dit pas qu'ils se")
        A("> trompent davantage** — seulement qu'ils l'écrivent davantage.")
    elif len(parts) >= 2 and parts[-1] < parts[0]:
        A("> **Le taux baisse.** La vague de rectifications récente est donc")
        A("> une **impression** que la mesure dément — et c'est mon propre récit")
        A("> du dépôt qui est en cause.")
    A("")
    A("## La fragilité du détecteur, mesurée")
    A("")
    A("Certains marqueurs sont des **mots courants** de ce registre. Une")
    A(f"fenêtre de ±{FENETRE} caractères peut donc en attraper un qui appartient")
    A("à la **phrase voisine**. Deux mesures pour que le lecteur en juge :")
    A("")
    A("| Marqueur | Déclenchements |")
    A("|---|---|")
    for k, v in sorted(par_marqueur.items(), key=lambda x: (-x[1], x[0])):
        A(f"| `{k}` | **{v}** |")
    A("")
    tot_p = len(meme_phrase) + len(fenetre_seule)
    part_ph = 100.0 * len(meme_phrase) / tot_p if tot_p else 0.0
    A(f"- appariements où le marqueur est dans la **même phrase** que la")
    A(f"  référence : **{len(meme_phrase)}** sur **{tot_p}** ("
      + f"**{part_ph:.1f} %**".replace(".", ",") + ")")
    A(f"- appariements où il n'est **que dans la fenêtre** : "
      f"**{len(fenetre_seule)}**")
    A("")
    n_ph = len({a for a, _ in meme_phrase})
    taux_ph = 100.0 * n_ph / len(numeros) if numeros else 0.0
    A(f"- cycles rectifiés **sous la règle stricte de la phrase** : "
      f"**{n_ph}** — taux " + f"**{taux_ph:.1f} %**".replace(".", ","))
    A("")
    if part_ph < 60:
        A("> **La majorité des appariements ne tiennent qu'à la fenêtre.** Le")
        A("> taux de " + f"**{taux:.1f} %**".replace(".", ",")
          + " annoncé plus haut est donc une **borne")
        A("> supérieure** ; la lecture stricte donne "
          + f"**{taux_ph:.1f} %**".replace(".", ",") + ".")
        A("> **La règle figée reste celle du pré-enregistrement** — je ne la")
        A("> remplace pas après coup — mais publier le seul chiffre large")
        A("> serait le présenter comme plus solide qu'il n'est.")
    else:
        A("> La majorité des appariements tiennent **à la phrase** : le taux")
        A("> annoncé n'est pas porté par des voisinages fortuits.")
    A("")
    A("## Les cycles les plus rectifiés")
    A("")
    if top:
        A("| Cycle | Rectifié par | Successeurs |")
        A("|---|---|---|")
        for n in top:
            liste = ", ".join(f"`#{m}`" for m in sorted(rect[n])[:6])
            if len(rect[n]) > 6:
                liste += f", … (**{len(rect[n]) - 6}** autres)"
            A(f"| `#{n}` | **{len(rect[n])}** | {liste} |")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = taux <= 20.0
    p2 = taux_rec > taux
    p3 = len(rectifies) >= 10
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| taux global ≤ 20 % | ≤ 20 % | " + f"{taux:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| taux des {N_RECENTS} derniers > taux global | > "
      + f"{taux:.1f} %".replace(".", ",") + " | "
      + f"{taux_rec:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| ≥ 10 cycles rectifiés | ≥ 10 | {len(rectifies)} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Auto-exclusion")
    A("")
    A("**Ce cycle ne se compte pas** : sa propre section n'existera qu'après la")
    A("mesure. L'exclusion est **structurelle**, et elle était déclarée au")
    A("pré-enregistrement (règle du #447).")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Le découpage du registre est **importé** du backtest du #501.")
    A("")
    A("## Critères de succès")
    A("")
    c = [(f"Liste de **{len(MARQUEURS)}** marqueurs et fenêtre citées verbatim",
          True),
         (f"Population (**{len(numeros)}**), rectifiés (**{len(rectifies)}**) "
          "et taux publiés", len(numeros) > 0),
         (f"Taux par tranche publié (**{len(tranches)}**) et tendance nommée",
          len(tranches) > 0),
         (f"Cycles les plus rectifiés nommés (**{len(top)}**), délai médian "
          f"(**{med if med is not None else '—'}**)", bool(top)),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état du registre à la")
    A("> date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(numeros)} cycles, {len(rectifies)} rectifiés "
          f"({taux:.1f} %), récents {taux_rec:.1f} %, médiane {med}")


if __name__ == "__main__":
    main()
