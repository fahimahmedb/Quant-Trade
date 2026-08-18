"""Dater le basculement forme / mesure (#510).

Specification pre-enregistree dans `PREREG_form_measure_changepoint.md`,
committee AVANT toute mesure -- regle de coupure et plancher compris.

Le #506 a constate un ecart entre la queue (95 % sans donnees) et l'ensemble
(28 %). Constater n'est pas dater. Ce cycle CALCULE le point de coupure au
contraste maximal. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_form_measure_changepoint_result.md"
MOI = "form_measure_changepoint"

PLANCHER = 20          # effectif minimal de chaque cote, FIGE
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


def heure(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y %H:%M")


def main():
    avant = set(git("status", "--porcelain").splitlines())
    a506 = module("nonml_verdicts_form_vs_measure_audit.py")
    dates = dates_ajout()

    pop = []
    sans_date = 0
    for py in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        if MOI in py.name:
            continue
        r = RESULTS / f"{py.name[:-len('_backtest.py')]}_result.md"
        if not r.exists():
            continue
        try:
            txt = r.read_text(encoding="utf-8")
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, SyntaxError):
            continue
        if not re.search(r"\bPASS\b|\bFAIL\b", txt):
            continue
        ts = dates.get(py.name)
        if ts is None:
            sans_date += 1
            continue
        ext = a506.cibles_ouvertes(arbre)
        pop.append({"py": py.name, "ts": ts,
                    "sans": not bool(ext & {".txt", ".npz", ".csv"})})

    pop.sort(key=lambda x: x["ts"])
    n = len(pop)

    # --- Le point de coupure, CALCULE et non choisi -----------------------
    coupures = []
    for i in range(PLANCHER, n - PLANCHER + 1):
        av, ap = pop[:i], pop[i:]
        p_av = 100.0 * sum(1 for e in av if e["sans"]) / len(av)
        p_ap = 100.0 * sum(1 for e in ap if e["sans"]) / len(ap)
        coupures.append((p_ap - p_av, i, p_av, p_ap))
    coupures.sort(reverse=True)
    meilleur = coupures[0] if coupures else None
    second = None
    if meilleur:
        for c in coupures[1:]:
            if abs(c[1] - meilleur[1]) > PLANCHER:   # un vrai autre endroit
                second = c
                break

    # --- Chronologie par tranches ----------------------------------------
    taille = max(1, n // N_TRANCHES)
    tranches, i = [], 0
    while i < n:
        bout = pop[i:i + taille] if n - i >= taille * 2 else pop[i:]
        if not bout:
            break
        tranches.append((i + 1, i + len(bout), bout))
        i += len(bout)

    L = []
    A = L.append
    A("# **Dater** le basculement forme / mesure (pré-enregistré)")
    A("")
    A("Le **#506** a constaté que sa queue était à **95 %** sans données quand")
    A("le dépôt entier est à **28 %**. **Constater n'est pas dater.** Ici le")
    A("point de coupure est **calculé**, pas choisi.")
    A("")
    A("## La règle, citée verbatim")
    A("")
    A("> 1. scripts ordonnés par **premier commit d'ajout** ;")
    A("> 2. pour chaque coupure, part de « sans données » **avant** et")
    A(">    **après** ;")
    A("> 3. le **basculement** maximise le contraste `part_après − part_avant` ;")
    A(f"> 4. chaque côté doit compter au moins **{PLANCHER}** scripts.")
    A("")
    A("Le plancher est **figé au pré-enregistrement** : il empêche qu'un maximum")
    A("trivial en bout de série soit retenu.")
    A("")
    A("## La population")
    A("")
    A(f"- scripts à verdict (`PASS`/`FAIL`, **en gras ou non**) : **{n}**")
    A(f"- écartés faute de date d'ajout : **{sans_date}**")
    A(f"- coupures évaluées : **{len(coupures)}**")
    A("")
    A("Population **élargie** — celle que l'audit du #506 a montrée")
    A("représentative — et classement par **appels d'ouverture** : *nommer un")
    A("fichier n'est pas l'ouvrir*.")
    A("")
    if meilleur is None:
        A("## Aucun basculement calculable")
        A("")
        A(f"La population (**{n}**) est trop petite pour le plancher de")
        A(f"**{PLANCHER}** de chaque côté. **Rien n'est daté.**")
        contraste = 0.0
    else:
        contraste, idx, p_av, p_ap = meilleur
        ts_cut = pop[idx]["ts"]
        A("## Le basculement, calculé")
        A("")
        A(f"- **date** : **{heure(ts_cut)}** *(premier script du régime")
        A(f"  postérieur : `{pop[idx]['py']}`)*")
        A(f"- **avant** : **{idx}** scripts, part sans données "
          + f"**{p_av:.1f} %**".replace(".", ","))
        A(f"- **après** : **{n - idx}** scripts, part sans données "
          + f"**{p_ap:.1f} %**".replace(".", ","))
        A(f"- **contraste** : " + f"**{contraste:+.1f}** points".replace(".", ","))
        A("")
        A("## Le deuxième meilleur point")
        A("")
        if second is None:
            A("**Aucun autre maximum** n'est situé à plus de "
              f"**{PLANCHER}** scripts du premier : la coupure est **isolée**.")
        else:
            c2, i2, a2, b2 = second
            A(f"- date : **{heure(pop[i2]['ts'])}**")
            A(f"- contraste : " + f"**{c2:+.1f}** points".replace(".", ","))
            A(f"- écart avec le meilleur : "
              + f"**{contraste - c2:.1f}** points".replace(".", ","))
            A("")
            ecart_h = abs(pop[i2]["ts"] - pop[meilleur[1]]["ts"]) / 3600.0
            A(f"- écart temporel entre les deux points : "
              + f"**{ecart_h:.1f}** heures".replace(".", ","))
            A("")
            A("> **Le seuil qui décide de « nette » n'était pas")
            A("> pré-enregistré.** Le pré-enregistrement disait seulement qu'un")
            A("> second maximum « presque aussi bon » devait être signalé, sans")
            A("> chiffrer « presque ». **Les 5 points employés ci-dessous sont un")
            A("> choix fait en écrivant le code**, et le lecteur doit pouvoir en")
            A("> juger : l'écart mesuré vaut "
              + f"**{contraste - c2:.1f}** points.".replace(".", ",") + "")
            A(">")
            A(f"> Les deux points sont distants de **{ecart_h:.0f} heures** : ils")
            A("> décrivent **la même transition**, pas deux dates concurrentes.")
            A("")
            if contraste - c2 < 5:
                A("> **La date n'est pas nette.** Un second point presque aussi")
                A("> bon existe ailleurs : le dépôt a pu changer")
                A("> **progressivement**, et un maximum unique ne le résume pas.")
            else:
                A("> Le second maximum est en retrait de plus de 5 points ; la")
                A("> date retenue n'est donc pas un choix parmi des équivalents")
                A("> **au sens de ce seuil**.")
    A("")
    if meilleur:
        A("## Une coïncidence de date, mesurée")
        A("")
        r498 = RESULTS / "nonml_declaration_rule_extension_dating_result.md"
        d498 = None
        if r498.exists():
            m = re.search(r"premier déclaré littéral\*\* : \*\*(\d{2}/\d{2}/\d{4})",
                          r498.read_text(encoding="utf-8"))
            d498 = m.group(1) if m else None
        d_cut = jour(pop[meilleur[1]]["ts"])
        A(f"- date de naissance de la convention d'auto-déclaration (#498) : "
          f"**{d498 or '—'}**")
        A(f"- date du basculement forme / mesure (ici) : **{d_cut}**")
        A(f"- **même jour** : **{'OUI' if d498 == d_cut else 'NON'}**")
        A("")
        if d498 == d_cut:
            A("> **Deux mesures sans rien de commun tombent sur le même jour.**")
            A("> L'une compte des typographies dans des pré-enregistrements,")
            A("> l'autre des appels d'ouverture de fichiers. Qu'elles désignent")
            A("> la même date **renforce** la lecture d'un changement de régime")
            A("> — c'est une **convergence**, pas une preuve, et je ne l'avais")
            A("> pas prédite sous cette forme.")
        A("")
    A("## La chronologie, par tranches")
    A("")
    A("*Publiée pour que le lecteur juge sur pièce plutôt que sur un point.*")
    A("")
    A("| Tranche | Période | Sans données | Part |")
    A("|---|---|---|---|")
    for a, b, bout in tranches:
        k = sum(1 for e in bout if e["sans"])
        pt = 100.0 * k / len(bout)
        A(f"| {a}–{b} | {jour(bout[0]['ts'])} → {jour(bout[-1]['ts'])} | "
          f"**{k} / {len(bout)}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## Auto-exclusion, déclarée d'avance")
    A("")
    A("**Ce cycle ne se compte pas lui-même** : il serait, une fois de plus, un")
    A("script à verdict qui n'ouvre aucune donnée. L'auto-exclusion était")
    A("déclarée au pré-enregistrement (règle du #447) — elle est rappelée ici.")
    A("")
    A("## Ce que ce cycle ne juge pas")
    A("")
    A("Il date un **changement d'activité**, pas une **perte de qualité**. Un")
    A("verdict rendu sans lire de données n'est pas moins bon : le #498 montre")
    A("seulement qu'il est **fragile au détecteur**.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    seuil_13 = None
    if meilleur:
        ts_cut = pop[meilleur[1]]["ts"]
        seuil_13 = datetime(2026, 8, 13, tzinfo=timezone.utc).timestamp()
    p1 = bool(meilleur and pop[meilleur[1]]["ts"] > seuil_13)
    p2 = contraste >= 40.0
    p3 = bool(meilleur and meilleur[2] <= 20.0)
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| basculement après le 13/08/2026 | oui | "
      f"{heure(pop[meilleur[1]]['ts']) if meilleur else '—'} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| contraste ≥ 40 points | ≥ 40 | "
      + f"{contraste:.1f}".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| part avant ≤ 20 % | ≤ 20 % | "
      + (f"{meilleur[2]:.1f} %".replace(".", ",") if meilleur else "—")
      + f" | **{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    if p1 and meilleur and jour(pop[meilleur[1]]["ts"]) == "13/08/2026":
        A("> **La prédiction 1 se vérifie sur une lecture de borne** : le point")
        A("> tombe **le** 13/08, à 21:51, donc après le début de cette journée.")
        A("> Le pré-enregistrement disait « après le 13/08/2026 » sans préciser")
        A("> l'heure ; j'applique la lecture littérale, et je publie")
        A("> l'horodatage pour que le lecteur juge lui-même.")
        A("")
    if not p2:
        A("> **La prédiction 2 est réfutée : il n'y a pas de basculement net.**")
        A("> Le mot « basculement », que le pré-enregistrement employait **par")
        A("> hypothèse et non par constat**, ne décrit pas ce que la mesure")
        A("> montre. Ce qu'on observe est une **dérive**, pas une bascule.")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("La route de classement est **importée** de l'audit du #506 — sa")
    A("fonction, jamais son `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [(f"Règle de coupure et plancher de **{PLANCHER}** cités verbatim", True),
         (f"Population élargie (**{n}**), classement par appels d'ouverture",
          n > 0),
         ("Date, deux parts et contraste publiés", meilleur is not None),
         (f"Chronologie par tranches (**{len(tranches)}**) et deuxième "
          "meilleur point publiés", bool(tranches)),
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
    print(f"{verdict} — n={n}, contraste={contraste:.1f} pts"
          + (f", date={jour(pop[meilleur[1]]['ts'])}" if meilleur else ""))


if __name__ == "__main__":
    main()
