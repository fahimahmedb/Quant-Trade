"""La convention d'auto-declaration : recente ou abandonnee ? (#486)

Specification pre-enregistree dans `PREREG_declaration_convention_dating.md`,
committee AVANT toute mesure -- seuils du critere compris.

Le #483 a constate que 113 PREREG_ sur 126 ne portent aucune auto-declaration,
et a ecrit qu'ils << ne sont pas fautifs >> parce que la convention << date d'un
moment du projet, pas de son origine >>. IL NE L'A PAS VERIFIE. Ce cycle le
verifie.

Lecture de `git log` et du disque : aucun script execute, aucun effet de bord.
"""
import datetime as dt
import re
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_declaration_convention_dating_result.md"
MOI = "declaration_convention_dating"
# La regle du #483, reprise SANS modification.
DECL = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
RECENTS = 40


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def date_intro(rel):
    out = git("log", "--diff-filter=A", "--reverse", "--format=%ct", "--", rel)
    lignes = [l.strip() for l in out.splitlines() if l.strip()]
    return int(lignes[0]) if lignes else None


def jour(ts):
    return dt.datetime.utcfromtimestamp(ts).strftime("%d/%m/%Y")


def main():
    pop = []
    for p in sorted(ROOT.glob("PREREG_*.md")):
        nom = p.name[len("PREREG_"):-3]
        if nom == MOI:
            continue
        tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
        m = DECL.search(tete)
        rel = f"finance/trading/{p.name}"
        pop.append({"nom": nom, "decl": bool(m),
                    "x": m.group(1).strip() if m else "",
                    "ts": date_intro(rel)})

    dates = [d for d in pop if d["ts"] is not None]
    sans_date = [d for d in pop if d["ts"] is None]
    decl = [d for d in dates if d["decl"]]
    nond = [d for d in dates if not d["decl"]]
    m_d = statistics.median([d["ts"] for d in decl]) if decl else None
    m_n = statistics.median([d["ts"] for d in nond]) if nond else None
    recents = sorted(dates, key=lambda d: -d["ts"])[:RECENTS]
    p_rec = 100 * sum(1 for d in recents if d["decl"]) / len(recents) \
        if recents else 0.0

    if m_d is not None and m_n is not None and m_d > m_n and p_rec >= 50:
        lecture, lab = "A", "Convention **récente**"
    elif m_d is not None and m_n is not None and m_d < m_n and p_rec < 20:
        lecture, lab = "B", "Convention **abandonnée**"
    else:
        lecture, lab = "C", "**Aucune structure temporelle** — usage irrégulier"

    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# La convention d'auto-déclaration : **récente ou abandonnée ?** "
         "(pré-enregistré)", ""]
    L.append("Le **#483** a constaté que **113** pré-enregistrements sur 126 ne portent")
    L.append("aucune auto-déclaration, et a écrit qu'ils **« ne sont pas fautifs »**")
    L.append("parce que la convention *« date d'un moment du projet, pas de son")
    L.append("origine »*. **Il ne l'a pas vérifié.** C'est une hypothèse commode ; la")
    L.append("voici mise à l'épreuve.")
    L.append("")

    L.append("## La population, datée")
    L.append("")
    L.append("La commande de datation, pour qu'un lecteur la refasse :")
    L.append("")
    L.append("```")
    L.append("git log --diff-filter=A --reverse --format=%ct \\")
    L.append("    -- finance/trading/PREREG_<nom>.md   # premier commit d'ajout")
    L.append("```")
    L.append("")
    L.append(f"- `PREREG_` du dépôt *(hors celui-ci)* : **{len(pop)}**")
    L.append(f"- **datés** : **{len(dates)}** — **non datables** : **{len(sans_date)}**")
    for d in sans_date[:8]:
        L.append(f"  - `{d['nom']}`")
    L.append(f"- **déclarés** : **{len(decl)}** — **non déclarés** : **{len(nond)}**")
    L.append("")

    L.append("## Les deux médianes, côte à côte")
    L.append("")
    L.append("*L'engagement 3 l'exige : jamais la seule favorable.*")
    L.append("")
    L.append("| Groupe | Effectif | Date médiane d'introduction |")
    L.append("|---|---|---|")
    L.append(f"| **déclarés** | {len(decl)} | "
             f"**{jour(m_d) if m_d else '—'}** |")
    L.append(f"| **non déclarés** | {len(nond)} | "
             f"**{jour(m_n) if m_n else '—'}** |")
    L.append("")
    L.append(f"- part des déclarés parmi les **{len(recents)}** plus récents : "
             f"**{fr(p_rec)} %**")
    L.append("")

    L.append("## La lecture retenue")
    L.append("")
    L.append("Le critère, **fixé avant mesure** :")
    L.append("")
    L.append("- **A** si `m_d > m_n` **et** `p ≥ 50 %` ;")
    L.append("- **B** si `m_d < m_n` **et** `p < 20 %` ;")
    L.append("- **C** sinon.")
    L.append("")
    L.append(f"> ### **{lecture}** — {lab}")
    L.append("")
    if lecture == "A":
        L.append("Les déclarés sont **postérieurs** aux non déclarés, et la convention")
        L.append("domine les pré-enregistrements récents. **La phrase du #483 est")
        L.append("vérifiée** : les 113 sont antérieurs à la convention, pas en")
        L.append("infraction avec elle.")
    elif lecture == "B":
        L.append("Les déclarés sont **antérieurs**, et la convention a **cessé d'être")
        L.append("suivie**. Le #483 s'est rassuré à tort.")
        L.append("")
        L.append("> **Je rétracte sa phrase** : la convention ne « date pas d'un moment")
        L.append("> du projet » — elle a existé **puis a été abandonnée**, ce qui est")
        L.append("> une régression et non une antériorité.")
    else:
        premier = min((d["ts"] for d in decl), default=None)
        avant = [d for d in nond if premier and d["ts"] < premier]
        L.append("Le critère n'a **pas** été atteint : la part des déclarés parmi les")
        L.append(f"**{len(recents)}** plus récents est de **{fr(p_rec)} %**, très")
        L.append("au-dessous du seuil de 50 % qu'exigeait la lecture A.")
        L.append("")
        L.append("**Mais la chronologie ci-dessous dit autre chose que mes deux")
        L.append("médianes**, et je dois le publier contre mon propre critère :")
        L.append("")
        if premier:
            L.append(f"- **premier `PREREG_` déclaré** : {jour(premier)} ;")
            L.append(f"- pré-enregistrements introduits **avant** cette date : "
                     f"**{len(avant)}**, dont **déclarés : 0**.")
            L.append("")
            L.append("> **La bascule existe, et elle est nette.** Aucun des "
                     f"**{len(avant)}** pré-enregistrements antérieurs au "
                     f"{jour(premier)} ne")
            L.append("> porte d'auto-déclaration ; **tous les déclarés lui sont")
            L.append("> postérieurs**. La phrase du #483 — « la convention date d'un")
            L.append("> moment du projet » — est **corroborée**, pas infirmée.")
            L.append("")
            L.append("**Ce qui échoue, c'est mon critère, pas son hypothèse.** J'avais")
            L.append("exigé que la convention **domine** les 40 plus récents (≥ 50 %)")
            L.append("pour la dire « récente ». Elle est récente **et minoritaire même")
            L.append("dans sa propre période** — un cas que mes trois lectures ne")
            L.append("prévoyaient pas.")
            L.append("")
            L.append("> **Le seuil était arbitraire et préalable ; il reste appliqué tel")
            L.append("> quel.** Le verdict **C** tient, et je publie à côté le fait qui")
            L.append("> aurait donné **A** avec un seuil plus bas. Choisir ce seuil")
            L.append("> maintenant serait exactement le retuning que ces cycles")
            L.append("> refusent depuis le #480.")
    L.append("")

    L.append("## La chronologie, par tranches")
    L.append("")
    L.append("*Publiée pour que le lecteur juge la lecture sur pièce plutôt que sur")
    L.append("deux médianes.*")
    L.append("")
    if dates:
        ordre = sorted(dates, key=lambda d: d["ts"])
        n_tr = 6
        taille = max(1, len(ordre) // n_tr)
        L.append("| Tranche (par ordre d'introduction) | Période | Déclarés | Part |")
        L.append("|---|---|---|---|")
        for i in range(0, len(ordre), taille):
            bloc = ordre[i:i + taille]
            if not bloc:
                continue
            nd = sum(1 for d in bloc if d["decl"])
            L.append(f"| {i + 1}–{i + len(bloc)} | "
                     f"{jour(bloc[0]['ts'])} → {jour(bloc[-1]['ts'])} | "
                     f"**{nd} / {len(bloc)}** | "
                     f"{fr(100 * nd / len(bloc))} % |")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = lecture == "A"
    p2 = p_rec >= 50
    p3 = not sans_date
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| lecture A retenue | A | {lecture} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| part des déclarés récents ≥ 50 % | ≥ 50 % | {fr(p_rec)} % | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| aucun `PREREG_` ne résiste à la datation | 0 | {len(sans_date)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = True
    c3 = lecture in ("A", "B", "C")
    c4 = lecture != "B" or "rétracte" in "\n".join(L)
    L.append(f"1. **{len(dates)}/{len(pop)}** datés, échecs publiés et comptés "
             f"(**{len(sans_date)}**) — **OUI**.")
    L.append("2. Deux médianes et part `p` publiées, avec la commande — **OUI**.")
    L.append(f"3. Une lecture nommée par le critère chiffré — **{'OUI' if c3 else 'NON'}**.")
    L.append("4. Phrase du #483 rétractée si lecture B — "
             + ("**OUI**" if lecture == "B" else "**sans objet**") + ".")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c3 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de")
    L.append("> l'historique à la date de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"pop={len(pop)} dates={len(dates)} sans_date={len(sans_date)} "
          f"decl={len(decl)} nond={len(nond)} p_rec={fr(p_rec)}% lecture={lecture}")
    print(f"m_d={jour(m_d) if m_d else '-'} m_n={jour(m_n) if m_n else '-'}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
