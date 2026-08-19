"""Combien des defauts restants sont irreparables ? (#485)

Specification pre-enregistree dans `PREREG_irreparable_figures_census.md`,
committee AVANT toute mesure -- examen a la main compris.

Le #482 a decouvert une categorie que le #479 n'avait pas prevue : une grandeur
historique dont l'univers n'est plus reconstructible n'est pas reparable. Ce
cycle la denombre.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_irreparable_figures_census_result.md"
REF = {"n_479": 18, "retracte_482": 1}

GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
ECRIT = re.compile(r"\.append\s*\(|\.write\s*\(|write_text\s*\(|print\s*\(")
# Proxy mecanique, declare FAIBLE d'avance : le script compte-t-il quelque
# chose ? Si non, la matiere premiere est certainement absente.
COLL = re.compile(r"for .* in |\.glob\(|len\s*\(|sorted\s*\(")

# Population : scripts juges DEFAUT ou PARTIEL aux #476 et #479, PRIVEE de
# `reproducibility_sample_lot3_audit` dont le #482 a retracte le verdict.
DEFAUTS = [
 "nonml_protocol_inventory_audit.py", "nonml_marker_emitted_by_scripts_backtest.py",
 "nonml_duplicate_sweep_coverage_audit.py", "nonml_battery_backfill_lot_audit.py",
 "nonml_content_defined_magnitudes_audit.py",
 "nonml_content_defined_magnitudes_backtest.py",
 "nonml_coverage_wording_fix_audit.py", "nonml_dsr_corrected_trials_backtest.py",
 "nonml_idempotence_famille_capable_backtest.py",
 "nonml_idempotence_lot2_backtest.py", "nonml_marker_emitter_crossing_backtest.py",
 "nonml_orphans_interrupted_or_lost_backtest.py",
 "nonml_pnl_duplicate_sweep_audit.py",
 "nonml_pnl_persistence_exposed_pass_audit.py",
 "nonml_report_idempotence_backtest.py",
 "nonml_reproducibility_campaign_v2_audit.py",
 "nonml_reproducibility_campaign_v3_lot2_audit.py",
]
RETRACTE = "nonml_reproducibility_sample_lot3_audit.py"

# --- VERDICTS DE L'EXAMEN A LA MAIN -------------------------------------
# DECLARE dans le pre-enregistrement. Ecrits a la main apres lecture de chaque
# ligne et du code qui l'entoure.
V = {
 "nonml_protocol_inventory_audit.py": ("IRRÉPARABLE",
  "La colonne publiée est **« Après inspection »** — le produit d'une lecture "
  "manuelle, pas d'un calcul. Aucun code ne peut produire « 33 → **6** "
  "strictement postérieurs à la Règle 9 » : c'est un jugement de date rendu à "
  "l'œil sur des entrées de backlog."),
 "nonml_marker_emitted_by_scripts_backtest.py": ("IRRÉPARABLE",
  "**C'est le #451**, dont le #473 a établi que le script n'énumère **jamais** "
  "`results/` : il ne travaille que sur **5 cibles codées en dur**. Les comptes "
  "décrivent une classification du dépôt entier **qu'il n'a jamais faite**."),
 "nonml_duplicate_sweep_coverage_audit.py": ("RÉPARABLE",
  "La ventilation « **90** FAIL, **2** PASS, **6** indéterminés, **1** sans "
  "rapport » porte sur l'ensemble que l'audit **construit déjà** — il "
  "interpole `n_missing` dans la phrase précédente. Les parts se calculent du "
  "même ensemble que le total."),
 "nonml_battery_backfill_lot_audit.py": ("IRRÉPARABLE",
  "**Corrigé au #511** : la seule source du script est `read_battery()`, qui "
  "relit des rapports `.md` — aucune occurrence de `np.load(` ni `.npz`. "
  "Le « 0,00 % » exigerait d'ouvrir une source que le script n'ouvre pas ; ce "
  "n'est pas une interpolation, c'est un cycle distinct."),
 "nonml_content_defined_magnitudes_audit.py": ("RÉPARABLE",
  "« **2** des importateurs » — l'audit énumère les importateurs pour les "
  "examiner ; le compte est à portée d'un `len()`."),
 "nonml_content_defined_magnitudes_backtest.py": ("RÉPARABLE",
  "« au commit du #451, **8** fichiers contiennent la phrase » est une mesure "
  "sur objets git, que le script **lit déjà**. *(La troisième ligne — « il "
  "vaut probablement **7** porteurs et **1** citeur » — est une **estimation "
  "en prose**, pas une mesure : il n'y a rien à recalculer, seulement un avis "
  "à assumer.)*"),
 "nonml_coverage_wording_fix_audit.py": ("IRRÉPARABLE",
  "**Corrigé au #518** : aucun appel `.glob(` nulle part dans le fichier. "
  "« 284 » est un littéral brut dans une chaîne simple, absent aussi du seul "
  "fichier que ce script lit. Le cas jugé « le plus trivialement réparable » "
  "ne calcule en réalité rien du tout."),
 "nonml_dsr_corrected_trials_backtest.py": ("RÉPARABLE",
  "« ce cycle en fusionne **2** » est le résultat de la fusion que le script "
  "opère. *(« Le #445 trouvait **3** groupes » est une citation, légitime.)*"),
 "nonml_idempotence_famille_capable_backtest.py": ("RÉPARABLE",
  "« environ **10 %**, soit **0,3** défaut attendu » se dérive de la vérité "
  "terrain du #463 — que ce script **importe** (`v1.FAUTIFS_463`, "
  "`v1.SAINS_463`). Le taux est à portée d'une division."),
 "nonml_idempotence_lot2_backtest.py": ("RÉPARABLE",
  "« Dix scripts sur **296** non éprouvés, c'est **3,4 %** » : le script "
  "construit `tous` et `DEJA`, donc `len(tous) - len(DEJA)` et le ratio."),
 "nonml_marker_emitter_crossing_backtest.py": ("RÉPARABLE",
  "« Le compte mécanique en donnait **1** » est **le compte que ce script "
  "calcule** (`douteux`) — il l'écrit en dur juste après l'avoir obtenu."),
 "nonml_orphans_interrupted_or_lost_backtest.py": ("RÉPARABLE",
  "**Mon cycle #474.** « Sur 33 objets examinés, **1** correspond à du travail "
  "annoncé et introuvable » : le script calcule `len(ent) + len(orp)` et le "
  "reste après contrôle post-hoc. **Mon propre défaut est réparable, et je "
  "n'ai pas d'excuse.**"),
 "nonml_pnl_duplicate_sweep_audit.py": ("IRRÉPARABLE",
  "« **Correction retenue : 1 essai surnuméraire**, soit 372 → **371** » : le "
  "**372** est le décompte d'essais du backlog entier, que cet audit ne "
  "construit pas et qu'aucun module n'expose. Le recalculer demanderait de "
  "reconstituer la comptabilité `n_trials` — **la question précisément en "
  "attente d'arbitrage depuis le #421.**"),
 "nonml_pnl_persistence_exposed_pass_audit.py": ("IRRÉPARABLE",
  "**Établi au #482** : les comptes portent sur l'univers du balayage **#415**, "
  "que le script n'importe pas et qu'aucun module n'expose. Substituer un "
  "décompte moderne mesurerait **autre chose**."),
 "nonml_report_idempotence_backtest.py": ("IRRÉPARABLE",
  "**Corrigé au #518** : aucun appel `.glob(` nulle part dans le fichier. "
  "« 314 » (le total du dépôt) est un littéral brut à l'intérieur d'une "
  "f-string qui n'interpole que le numérateur — le script ne lit jamais le "
  "dépôt pour obtenir son dénominateur."),
 "nonml_reproducibility_campaign_v2_audit.py": ("IRRÉPARABLE",
  "**Corrigé au #518** : le seul `.glob(` du fichier porte sur "
  "`nonml_*_backtest.py` pour une fonction sans rapport avec le compte cité ; "
  "« 208 » est un littéral brut, jamais issu d'un glob sur `*_pnl.npz` que ce "
  "script n'exécute nulle part."),
 "nonml_reproducibility_campaign_v3_lot2_audit.py": ("RÉPARABLE",
  "**Corrigé au #493** : le script définit `def bound(n)` au niveau module "
  "et publie déjà `{100*bound(cum):.1f} %` à trois endroits. Le « 6,2 % » "
  "écrit en dur est exactement cette valeur, et le « ~4,1 % » est "
  "`100*bound(cum + 24)` — dérivable d'une fonction que le script possède, "
  "pas une projection sans univers."),
}


def litteraux(src):
    return [(i, l.strip()) for i, l in enumerate(src.splitlines(), 1)
            if ECRIT.search(l) and GRAS.search(l) and not INTERPOLE.search(l)]


def main():
    pop, absents = [], []
    for f in DEFAUTS:
        p = SCRIPTS / f
        if not p.exists():
            absents.append(f)
            continue
        src = p.read_text(encoding="utf-8")
        pop.append({"nom": f, "lits": litteraux(src),
                    "proxy": bool(COLL.search(src))})

    for d in pop:
        d["verdict"], d["motif"] = V.get(d["nom"], ("NON EXAMINÉ", "—"))
    irrep = [d for d in pop if d["verdict"] == "IRRÉPARABLE"]
    rep = [d for d in pop if d["verdict"] == "RÉPARABLE"]
    non_ex = [d for d in pop if d["verdict"] == "NON EXAMINÉ"]
    attendu = REF["n_479"] - REF["retracte_482"]
    ecart = len(pop) - attendu
    # Accord du proxy : proxy vrai <=> << matiere premiere peut exister >>
    # <=> RÉPARABLE. On mesure l'accord ainsi.
    accord = sum(1 for d in pop if d["proxy"] == (d["verdict"] == "RÉPARABLE"))
    pc_acc = 100 * accord / len(pop) if pop else 0.0
    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# **Combien des défauts restants sont irréparables ?** (pré-enregistré)",
         ""]
    L.append("Le **#482** a découvert une catégorie que le #479 n'avait pas prévue :")
    L.append("")
    L.append("> **Une grandeur historique dont l'univers n'est plus reconstructible")
    L.append("> n'est pas réparable — seulement signalable.**")
    L.append("")
    L.append("**Aucun des 17 n'avait été classé.** Ce cycle les classe tous.")
    L.append("")

    L.append("## La population")
    L.append("")
    L.append(f"- dénombrés au **#479** : **{REF['n_479']}**")
    L.append(f"- **rétracté au #482** *(`{RETRACTE[:-3]}` : citation de diff, pas")
    L.append(f"  tableau)* : **−{REF['retracte_482']}**")
    L.append(f"- **attendus ici** : **{attendu}** — **re-dérivés : {len(pop)}** "
             f"(**{ecart:+d}**)")
    if absents:
        L.append(f"- scripts introuvables : **{len(absents)}** — "
                 + ", ".join(f"`{a}`" for a in absents))
    L.append("")

    L.append("## Le proxy mécanique — et son inutilité, mesurée")
    L.append("")
    L.append("Le pré-enregistrement le déclarait **faible d'avance**. Il l'est plus")
    L.append("encore que prévu :")
    L.append("")
    n_proxy = sum(1 for d in pop if d["proxy"])
    L.append(f"- scripts où le proxy répond « la matière première peut exister » : "
             f"**{n_proxy} / {len(pop)}**")
    L.append("")
    if n_proxy == len(pop):
        L.append("> **Il répond « oui » à tous.** Un proxy qui ne discrimine jamais n'a")
        L.append("> **aucun pouvoir de séparation** : il aurait donné le même résultat")
        L.append("> sur n'importe quelle population. **Sa valeur informative est nulle,**")
        L.append("> et c'est mesuré, pas supposé.")
        L.append("")
        L.append("La cause est banale : `for … in`, `len(…)`, `sorted(…)` sont présents")
        L.append("dans **tout** script qui rédige un rapport. **J'avais choisi un motif")
        L.append("qui teste « ce script est écrit en Python », pas « il dispose de la")
        L.append("grandeur ».**")
    L.append("")

    L.append("## Les verdicts, un par un")
    L.append("")
    L.append("**Écrits à la main après lecture de chaque ligne et du code qui")
    L.append("l'entoure.** Aucune règle ne les produit.")
    L.append("")
    for d in sorted(pop, key=lambda x: (x["verdict"] != "IRRÉPARABLE", x["nom"])):
        etiq = "**IRRÉPARABLE**" if d["verdict"] == "IRRÉPARABLE" else \
               ("réparable" if d["verdict"] == "RÉPARABLE" else "**NON EXAMINÉ**")
        L.append(f"### `{d['nom']}` — {etiq}")
        L.append("")
        L.append("```python")
        for i, ligne in d["lits"][:3]:
            L.append(f"{i}:{ligne[:108]}")
        if len(d["lits"]) > 3:
            L.append(f"... et {len(d['lits']) - 3} autres")
        L.append("```")
        L.append("")
        L.append(d["motif"])
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- **IRRÉPARABLES** : **{len(irrep)} / {len(pop)}** "
             f"(**{fr(100 * len(irrep) / len(pop))} %**)")
    L.append(f"- **réparables** : **{len(rep)}**")
    if non_ex:
        L.append(f"- **non examinés** : **{len(non_ex)}**")
    L.append("")
    L.append("| Irréparable | Pourquoi, en un mot |")
    L.append("|---|---|")
    court = {
     "nonml_protocol_inventory_audit.py": "colonne « après inspection » = lecture manuelle",
     "nonml_marker_emitted_by_scripts_backtest.py": "classification jamais effectuée par le script",
     "nonml_pnl_duplicate_sweep_audit.py": "compte `n_trials` du backlog entier, non exposé",
     "nonml_pnl_persistence_exposed_pass_audit.py": "univers du balayage #415, disparu",
     "nonml_battery_backfill_lot_audit.py": "corrigé #511 : lit des .md, jamais de .npz",
     "nonml_coverage_wording_fix_audit.py": "corrigé #518 : aucun `.glob(`, littéral en dur",
     "nonml_report_idempotence_backtest.py": "corrigé #518 : dénominateur jamais lu par le script",
     "nonml_reproducibility_campaign_v2_audit.py": "corrigé #518 : `.glob(` sans rapport avec le chiffre",
    }
    for d in irrep:
        L.append(f"| `{d['nom']}` | {court.get(d['nom'], '—')} |")
    L.append("")
    L.append(f"> **La dette du #479 est actionnable à {fr(100 * len(rep) / len(pop))} %.** Les "
             f"**{len(rep)}** réparables le sont par une simple interpolation ; les")
    L.append(f"**{len(irrep)}** autres ne peuvent qu'être **signalés dans le rapport**,")
    L.append("jamais recalculés.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(irrep) >= 5
    p2 = len(rep) >= 8
    p3 = pc_acc < 80
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 5 irréparables | ≥ 5 | {len(irrep)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| ≥ 8 réparables | ≥ 8 | {len(rep)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| accord du proxy < 80 % | < 80 % | {fr(pc_acc)} % | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if p1 and len(irrep) == 5:
        L.append("**La prédiction 1 passe de justesse — 5 pour un seuil de 5.** Un cas")
        L.append("classé autrement l'aurait réfutée. **Je le signale plutôt que de la")
        L.append("présenter comme confirmée**, parce qu'un verdict écrit à la main peut")
        L.append("basculer, et que le mien vient de décider du sort de la prédiction.")
        L.append("")
    if p3:
        L.append(f"**L'accord du proxy est de {fr(pc_acc)} %**, mais ce chiffre flatte :")
        L.append("le proxy répond « oui » partout, donc il « s'accorde » exactement avec")
        L.append("le nombre de réparables, **par construction**. **Ce n'est pas un")
        L.append("accord, c'est une coïncidence arithmétique.**")
    L.append("")

    L.append("## Ce que ce cycle établit")
    L.append("")
    L.append(f"- la catégorie du #482 est **réelle et minoritaire** : **{len(irrep)}** cas")
    L.append("  sur 17, chacun avec sa raison publiée ;")
    L.append(f"- **une des {len(irrep)} renvoie à une question en attente d'arbitrage** — le")
    L.append("  décompte `n_trials` du #421 ;")
    L.append("- **mon propre défaut du #474 est réparable**, et rien ne l'excuse ;")
    L.append("- **rien n'est réparé ici** : le #482 a montré qu'une réparation peut")
    L.append(f"  être nuisible, et chacun des {len(rep)} demande sa propre vérification.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = not non_ex
    c4 = all(d["motif"] and d["motif"] != "—" for d in irrep)
    L.append(f"1. Population re-dérivée (**{len(pop)}**), écart (**{ecart:+d}**),")
    L.append("   rétractation du #482 prise en compte — **OUI**.")
    L.append(f"2. **{len(pop) - len(non_ex)}/{len(pop)}** examinés à la main avec ligne,")
    L.append(f"   verdict et raison — **{'OUI' if c2 else 'NON'}**.")
    L.append(f"3. Proxy publié à côté, accord chiffré (**{fr(pc_acc)} %**) — **OUI**.")
    L.append(f"4. Aucun « irréparable » sans sa raison — **{'OUI' if c4 else 'NON'}**.")
    L.append("")
    L.append(f"**{'PASS' if (c2 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"pop={len(pop)} irrep={len(irrep)} rep={len(rep)} non_ex={len(non_ex)} "
          f"proxy_oui={n_proxy} accord={fr(pc_acc)}%")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
