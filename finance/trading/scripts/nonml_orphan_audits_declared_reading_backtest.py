"""La regle de lecture declaree, et son application elargie (#483).

Specification pre-enregistree dans `PREREG_orphan_audits_declared_reading.md`,
committee AVANT toute mesure -- liste de mots, population et echantillon
d'examen compris.

Sur les TROIS du #480, ce cycle RATIFIE et ne teste rien : la reponse etait
deja connue et publiee. Le contenu reel porte sur la population elargie.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_orphan_audits_declared_reading_result.md"
MOI = "orphan_audits_declared_reading"
TAILLE = 5
TROIS = ["n_trials_dependence_correction", "pnl_duplicate_sweep_v2",
         "pnl_persistence_exposed_pass"]

# Liste FIGEE par le pre-enregistrement. L'elargir apres mesure serait le
# retuning exact que le #480 a refuse.
MOTS = ["audit", "correction", "diagnostic", "infrastructure", "inventaire",
        "vérification", "verification", "modification", "réparation",
        "arbitrage"]
DECL = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)

# --- VERDICTS DE L'EXAMEN A LA MAIN -------------------------------------
# DECLARE dans le pre-enregistrement : jusqu'a 5 cycles classes RESULTAT
# ATTENDU, dans l'ordre alphabetique. Ecrits a la main apres lecture.
V = {
 "coverage_wording_fix": ("MAL CLASSÉ",
  "Se déclare **« Cycle d'outillage documentaire »** et ajoute, dans la même "
  "phrase : *« Aucune stratégie évaluée, aucun verdict recalculé, aucun seuil "
  "touché. »* **Il n'attend aucun `_result.md`.** Ma liste de mots ne contient "
  "pas « outillage »."),
 "duplicate_sweep_coverage": ("MAL CLASSÉ",
  "Même auto-déclaration — **« outillage documentaire »** — et même absence de "
  "promesse de résultat. Même cause : le mot manque à ma liste."),
 "sessions_column_backfill": ("MAL CLASSÉ",
  "Même auto-déclaration **« outillage documentaire »**. Trois cycles d'une "
  "même famille, tous manqués par le même mot absent."),
 "sweep_basket_schema_support": ("MAL CLASSÉ",
  "Se déclare **« Cycle d'outillage »** — variante courte du même terme — avec "
  "la mention *« aucune stratégie évaluée, aucun verdict recalculé »*. "
  "**Quatre sur quatre.**"),
}


def classer(nom):
    tete = "\n".join((ROOT / f"PREREG_{nom}.md")
                     .read_text(encoding="utf-8").splitlines()[:12])
    m = DECL.search(tete)
    if not m:
        return "NON DÉCLARÉ", ""
    x = m.group(1).strip()
    if any(w in x.lower() for w in MOTS):
        return "SANS RÉSULTAT ATTENDU", x
    return "RÉSULTAT ATTENDU", x


def main():
    pop = []
    for p in sorted(ROOT.glob("PREREG_*.md")):
        nom = p.name[len("PREREG_"):-3]
        if (RESULTS / f"nonml_{nom}_result.md").exists() or nom == MOI:
            continue
        cl, decl = classer(nom)
        pop.append({"nom": nom, "classe": cl, "decl": decl})

    sans = [d for d in pop if d["classe"] == "SANS RÉSULTAT ATTENDU"]
    avec = [d for d in pop if d["classe"] == "RÉSULTAT ATTENDU"]
    nond = [d for d in pop if d["classe"] == "NON DÉCLARÉ"]
    declares = len(sans) + len(avec)
    echantillon = sorted(avec, key=lambda d: d["nom"])[:TAILLE]
    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# La **règle de lecture déclarée**, et son application élargie "
         "(pré-enregistré)", ""]
    L.append("## L'aveu qui commande ce cycle")
    L.append("")
    L.append("Le **#480** a classé trois cycles mécaniquement (**A/C/?**), puis — hors")
    L.append("protocole — **je les ai lus à la main et j'ai publié que les trois")
    L.append("relevaient de C**, sans retenir cette version faute d'examen déclaré.")
    L.append("")
    L.append("> **Je connais donc déjà la réponse sur ces trois-là.** Annoncer")
    L.append("> « prédiction vérifiée : 3/3 » serait **prédire ce que j'ai déjà vu**.")
    L.append("> Sur les trois, ce cycle **ratifie et ne teste rien** — et **aucune")
    L.append("> prédiction n'a été formulée à leur sujet.**")
    L.append("")

    L.append("## Ratification des trois du #480 — **résultat non informatif**")
    L.append("")
    L.append("| `<nom>` | Auto-déclaration lue | Classe |")
    L.append("|---|---|---|")
    for n in TROIS:
        d = next((x for x in pop if x["nom"] == n), None)
        if d:
            L.append(f"| `{n}` | « {d['decl']} » | **{d['classe']}** |")
    ratifies = [d for d in pop if d["nom"] in TROIS
                and d["classe"] == "SANS RÉSULTAT ATTENDU"]
    L.append("")
    L.append(f"**{len(ratifies)} / {len(TROIS)}** classés SANS RÉSULTAT ATTENDU par la")
    L.append("règle déclarée d'avance — **ce qui confirme la lecture à la main du")
    L.append("#480 sans rien apprendre de neuf**. Le classement est désormais")
    L.append("**légitime** parce que la règle précède la lecture, non parce qu'un")
    L.append("fait nouveau l'établirait.")
    L.append("")
    L.append("> **La dette « 3 audits orphelins » est levée par requalification.** Le")
    L.append("> verdict A/C/? du #480 n'est pas effacé : il reste inscrit, avec la")
    L.append("> mention qu'une règle déclarée le corrige.")
    L.append("")

    L.append("## La population élargie — là où rien n'était connu")
    L.append("")
    L.append("Tout `PREREG_<nom>.md` sans `results/nonml_<nom>_result.md`.")
    L.append("")
    L.append("La liste de mots, **citée verbatim** telle que le pré-enregistrement")
    L.append("l'a figée :")
    L.append("")
    L.append("```")
    L.append(", ".join(MOTS))
    L.append("```")
    L.append("")
    L.append("| Classe | Nombre | Part |")
    L.append("|---|---|---|")
    for lab, lst in (("SANS RÉSULTAT ATTENDU", sans), ("RÉSULTAT ATTENDU", avec),
                     ("NON DÉCLARÉ", nond)):
        L.append(f"| **{lab}** | **{len(lst)}** | "
                 f"{fr(100 * len(lst) / len(pop))} % |")
    L.append(f"| *total* | *{len(pop)}* | *100 %* |")
    L.append("")
    L.append(f"> **Les {len(nond)} NON DÉCLARÉS ne sont dans aucun total de dette.**")
    L.append("> Ma règle ne sait lire qu'une convention — `Cycle de **X**` dans les")
    L.append("> douze premières lignes — et **l'absence de cette convention n'est pas")
    L.append("> une faute** : elle date d'un moment du projet, pas de son origine.")
    L.append("")
    L.append(f"**C'est le fait dominant de ce cycle** : la convention d'auto-déclaration")
    L.append(f"ne couvre que **{declares} des {len(pop)}** pré-enregistrements sans")
    L.append(f"résultat, soit **{fr(100 * declares / len(pop))} %**. Ma règle est donc")
    L.append("**muette sur la quasi-totalité de la population** qu'elle prétendait")
    L.append("classer.")
    L.append("")

    L.append(f"## L'examen à la main — {len(echantillon)} cas, **déclarés avant mesure**")
    L.append("")
    L.append("Les cycles classés RÉSULTAT ATTENDU sont les seuls candidats à être de")
    L.append("vrais cycles inachevés. Ordre fixé d'avance : alphabétique du `<nom>`.")
    L.append("")
    mal = []
    for d in echantillon:
        etat, motif = V.get(d["nom"], ("NON EXAMINÉ", "—"))
        if etat == "MAL CLASSÉ":
            mal.append(d["nom"])
        L.append(f"### `{d['nom']}` — **{etat}**")
        L.append("")
        L.append(f"Auto-déclaration lue : « {d['decl']} »")
        L.append("")
        L.append(motif)
        L.append("")
    L.append(f"- **MAL CLASSÉS** : **{len(mal)} / {len(echantillon)}**")
    L.append(f"- **INACHEVÉS établis** : "
             f"**{len(echantillon) - len(mal)} / {len(echantillon)}**")
    L.append("")
    if len(mal) == len(echantillon) and echantillon:
        L.append("> **Ma règle déclarée s'est trompée sur la totalité de son")
        L.append("> échantillon.** Les quatre se déclarent cycles d'**« outillage »** ou")
        L.append("> d'**« outillage documentaire »**, et trois d'entre eux ajoutent")
        L.append("> explicitement *« aucune stratégie évaluée, aucun verdict")
        L.append("> recalculé »*. **Aucun n'attendait de `_result.md`.**")
        L.append("")
        L.append("Le mot **« outillage » manque à ma liste**. Elle avait été écrite en")
        L.append("regardant les trois cycles du #480 — donc **taillée sur trois cas**,")
        L.append(f"et appliquée à **{len(pop)}**.")
        L.append("")
        L.append("> **Elle n'est pas corrigée ici.** L'élargir après avoir vu le")
        L.append("> résultat serait le retuning exact que le #480 avait refusé. La")
        L.append("> liste figée reste publiée, et son défaut avec elle.")
        L.append("")
        L.append("**Aucun cycle inachevé n'est donc établi par ce cycle** — et c'est")
        L.append("une bonne nouvelle sur le dépôt, obtenue par une mauvaise règle.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    pc_sans = 100 * len(sans) / len(pop) if pop else 0.0
    p1 = pc_sans >= 60
    p2 = len(avec) >= 1
    p3 = len(mal) >= 1
    L.append("*(Aucune ne porte sur les trois du #480 — c'était l'engagement 3.)*")
    L.append("")
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 60 % sans résultat attendu | ≥ 60 % | {fr(pc_sans)} % | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| ≥ 1 classé résultat attendu | ≥ 1 | {len(avec)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| ≥ 1 mal classé à l'examen | ≥ 1 | {len(mal)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée, et de très loin** : j'annonçais 60 %,")
        L.append(f"la mesure donne **{fr(pc_sans)} %**. Je raisonnais comme si la")
        L.append("convention d'auto-déclaration était **générale** ; elle ne couvre")
        L.append(f"que **{fr(100 * declares / len(pop))} %** de la population.")
        L.append("")
        L.append("> **J'avais confondu « les cycles que je viens de lire » avec « les")
        L.append("> cycles du dépôt ».** Les trois du #480 se déclarent tous les trois ;")
        L.append("> c'est ce qui m'a fait croire la convention répandue. **Trois cas")
        L.append(f"> lus ne décrivent pas {len(pop)}.**")
        L.append("")
        L.append("*(Ces deux nombres sont **interpolés**, pas écrits en toutes lettres.")
        L.append("Après les #479 et #482, publier « cent vingt-sept » dans une chaîne")
        L.append("littérale serait ajouter un dix-huitième cas à la liste que je viens")
        L.append("de dénombrer.)*")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = len(pop) == len(sans) + len(avec) + len(nond)
    c4 = all(d["nom"] in V for d in echantillon)
    L.append(f"1. Population énumérée (**{len(pop)}**), les 3 du #480 identifiés comme")
    L.append("   **ratifiés et non testés** — **OUI**.")
    L.append(f"2. **{len(pop)}/{len(pop)}** classés, liste de mots citée verbatim — "
             f"**{'OUI' if c2 else 'NON'}**.")
    L.append(f"3. **{len(nond)}** NON DÉCLARÉS comptés à part et exclus de tout total")
    L.append("   de dette — **OUI**.")
    L.append(f"4. **{len(echantillon)}** examinés à la main avec verdict — "
             f"**{'OUI' if c4 else 'NON'}**.")
    L.append("5. Caractère non informatif du résultat sur les trois écrit à l'endroit")
    L.append("   du chiffre — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c2 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"pop={len(pop)} sans={len(sans)} avec={len(avec)} nondecl={len(nond)} "
          f"ratifies={len(ratifies)} mal={len(mal)}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
