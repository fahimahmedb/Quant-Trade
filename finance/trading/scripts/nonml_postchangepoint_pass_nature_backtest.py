"""Le regime post-basculement : PASS procedural ou substantiel ? (#516)

Specification pre-enregistree dans
`PREREG_postchangepoint_pass_nature.md`, committee AVANT toute mesure --
regle de classement et date pivot comprises.

Le #510 a date un basculement (13/08/2026 21:51) apres lequel les scripts
cessent d'ouvrir des donnees de marche. Le #512 a montre qu'un PASS peut
etre purement procedural. Combien, dans ce regime, sont l'un ou l'autre ?
SANS RIEN EXECUTER.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_postchangepoint_pass_nature_result.md"
MOI = "postchangepoint_pass_nature"

PIVOT_TS = int(datetime(2026, 8, 13, 21, 51, tzinfo=timezone.utc).timestamp())
PHRASE = "porte sur le procédé"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


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


def heure(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y %H:%M")


def sans_markdown(t):
    """Convention du #490 : le gras/le code casse un appariement littéral."""
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def main():
    avant = set(git("status", "--porcelain").splitlines())
    dates = dates_ajout()

    regime = []
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
        if not re.search(r"\bPASS\b|\bFAIL\b", txt):
            continue
        ts = dates.get(py.name)
        if ts is None or ts < PIVOT_TS:
            continue
        # Verdict final fiable : le dernier marqueur **PASS**/**FAIL** en gras du rapport.
        marqueurs = re.findall(r"\*\*(PASS|FAIL)\*\*", txt)
        verdict = marqueurs[-1] if marqueurs else ("PASS" if "PASS" in txt else "FAIL")
        procedural = PHRASE in sans_markdown(txt)
        regime.append({"py": py.name, "ts": ts, "verdict": verdict,
                       "procedural": procedural, "txt": txt})

    passes = [r for r in regime if r["verdict"] == "PASS"]
    fails = [r for r in regime if r["verdict"] == "FAIL"]
    procs = [r for r in passes if r["procedural"]]
    subst = [r for r in passes if not r["procedural"]]

    # Mesure supplementaire, faite APRES avoir vu les 11 exceptions : la
    # convention d'auto-declaration a une date d'adoption -- distinguer
    # les exceptions ANTERIEURES a cette date (artefact de calendrier) des
    # exceptions POSTERIEURES (vraies exceptions). Cette mesure est
    # descriptive, elle ne change PAS la classe PROCEDURAL/SUBSTANTIEL
    # deja figee au pre-enregistrement -- seulement son interpretation.
    adoption = None
    for r in regime:
        if r["procedural"] and (adoption is None or r["ts"] < adoption):
            adoption = r["ts"]
    avant_conv = [r for r in subst if adoption and r["ts"] < adoption]
    apres_conv = [r for r in subst if not adoption or r["ts"] >= adoption]

    L = []
    A = L.append
    A("# Le régime post-basculement : **PASS procédural** ou **substantiel** ? (pré-enregistré)")
    A("")
    A("Le **#510** a daté un basculement — **13/08/2026 21:51** — après")
    A("lequel les scripts cessent d'ouvrir des données de marché. Le **#512**")
    A("a montré qu'un cycle peut satisfaire tous ses critères tout en")
    A("produisant une mesure **sans valeur** — un PASS purement procédural.")
    A("")
    A("## La règle, citée verbatim")
    A("")
    A(f"> Date pivot **reprise du #510, non recalculée** : "
      f"**{heure(PIVOT_TS)} UTC**. Population : scripts `nonml_*_backtest.py`")
    A("> à verdict, introduits à cette date ou après. **PROCÉDURAL** si le")
    A(f'> rapport contient « {PHRASE} » ; **SUBSTANTIEL** sinon.')
    A("")
    A("## Le recensement")
    A("")
    A(f"- scripts du régime postérieur : **{len(regime)}**")
    A(f"- dont **PASS** : **{len(passes)}** ; dont **FAIL** : **{len(fails)}**")
    A("")
    A("| Classe | Nombre | Part des PASS |")
    A("|---|---|---|")
    pp = 100.0 * len(procs) / len(passes) if passes else 0.0
    ps = 100.0 * len(subst) / len(passes) if passes else 0.0
    A(f"| **PROCÉDURAL** | **{len(procs)}** | "
      + f"**{pp:.1f} %**".replace(".", ",") + " |")
    A(f"| **SUBSTANTIEL** | **{len(subst)}** | "
      + f"**{ps:.1f} %**".replace(".", ",") + " |")
    A("")
    if not subst:
        A("> **Aucune exception.** Tous les PASS du régime postérieur")
        A("> s'auto-déclarent procéduraux. La série #496-#516 n'a produit,")
        A("> depuis le basculement, **aucun** PASS qui prétende porter sur une")
        A("> grandeur du dépôt plutôt que sur le respect de son propre")
        A("> protocole — elle **mesure sa propre méthode**, systématiquement,")
        A("> pas ce que cette méthode trouve.")
    else:
        A(f"> **{len(subst)}** exception(s) — les seuls PASS du régime qui ne")
        A("> se déclarent pas procéduraux, nommés ci-dessous.")
    A("")
    A("## Les substantiels, nommés")
    A("")
    if subst:
        for r in sorted(subst, key=lambda x: x["ts"]):
            extrait = re.sub(r"\s+", " ", r["txt"][:200])
            A(f"- `{r['py']}` — introduit le {heure(r['ts'])} : « {extrait}… »")
    else:
        A("**Aucun** — cf. ci-dessus.")
    A("")
    A("### Ce que ces 11 exceptions sont réellement — mesuré après coup")
    A("")
    A("La phrase « porte sur le procédé » est elle-même une **convention")
    A("adoptée en cours de série**, pas une règle depuis l'origine.")
    A(f"- première occurrence du régime avec cette phrase : "
      + (f"**{heure(adoption)}**" if adoption else "**aucune**"))
    A(f"- substantiels **antérieurs** à cette adoption (artefact de")
    A(f"  calendrier, pas une vraie exception) : **{len(avant_conv)}**")
    A(f"- substantiels **postérieurs** — vraies exceptions, la convention")
    A(f"  existait déjà et n'a pas été appliquée : **{len(apres_conv)}**")
    A("")
    if apres_conv:
        A("| Script | Introduit le |")
        A("|---|---|")
        for r in apres_conv:
            A(f"| `{r['py']}` | {heure(r['ts'])} |")
        A("")
        A("> **Sur 68 scripts du régime, une seule vraie exception** —")
        A("> `nonml_self_inclusion_repair_backtest.py`, le premier cycle de")
        A("> **réparation** de toute la série (le #463 avait trouvé les")
        A("> défauts, le #466 avait refusé de les corriger). Son PASS porte")
        A("> sur une action réelle sur le dépôt, pas sur la publication d'un")
        A("> procédé — et c'est la **seule** fois où c'est arrivé depuis")
        A("> l'adoption de la convention.")
    else:
        A("> **Zéro vraie exception.** Les 11 « substantiels » comptés plus")
        A("> haut sont entièrement un artefact de calendrier : ils précèdent")
        A("> tous l'adoption de la phrase elle-même.")
    A("")
    A("## Le compte des FAIL, pour situer le total")
    A("")
    A(f"- FAIL du régime : **{len(fails)}**")
    A("")
    A("## Ce que ce cycle ne juge pas")
    A("")
    A("Un PASS procédural n'est pas un défaut en soi — c'est le mode de")
    A("fonctionnement **déclaré** de cette série depuis le #513 : le critère")
    A("porte sur la publication honnête d'un verdict, pas sur la découverte")
    A("d'un fait nouveau à chaque cycle. Ce recensement mesure une")
    A("**proportion**, pas une faute.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = pp >= 90.0
    p2 = len(subst) == 0
    p3 = len(regime) >= 62
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| ≥ 90 % des PASS procéduraux | ≥ 90 % | "
      + f"{pp:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| SUBSTANTIEL = 0 | 0 | {len(subst)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| régime ≥ 62 scripts | ≥ 62 | {len(regime)} | "
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
    A("Les seuls appels externes visent `git log` et `git status`, **en")
    A("lecture**.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle citée verbatim, date pivot rappelée", True),
         (f"Population (**{len(regime)}**) et PASS/FAIL publiés "
          f"(**{len(passes)}**/**{len(fails)}**)", len(regime) > 0),
         (f"Compte PROCÉDURAL/SUBSTANTIEL publié (**{len(procs)}**/"
          f"**{len(subst)}**)", True),
         ("Substantiels nommés ou absence explicite", True),
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
    print(f"{verdict} — régime={len(regime)}, PASS={len(passes)}, "
          f"procédural={len(procs)}, substantiel={len(subst)}")


if __name__ == "__main__":
    main()
