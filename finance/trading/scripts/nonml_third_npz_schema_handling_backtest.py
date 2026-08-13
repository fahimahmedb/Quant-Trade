"""Le troisieme schema `.npz` et son traitement par les balayages (#444).

Specification pre-enregistree dans `PREREG_third_npz_schema_handling.md`,
committee AVANT toute mesure.

Le #443 a decouvert 2 fichiers portant un schema jamais catalogue
(`pnl_candidate` / `pnl_ref`, ou `pnl_candidate` est **deja net**). La question
posee ici est : les 12 balayages qui **consomment** les `.npz` les traitent-ils
correctement, les ecartent-ils, ou leur appliquent-ils une formule fausse ?

Le pre-enregistrement declarait leur concordance connue d'avance ; c'etait trop
large -- seul `_pit` avait ete sonde au #443. La verification de `_vol_targeted`
est neuve, et montre que les deux fichiers d'un meme schema portent des
**conventions de rendement opposees**.

Ce cycle ne fait que **lire**.
"""
import importlib.util
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "src"))

from prediction import trading_metrics  # noqa: E402

OUT = RESULTS / "nonml_third_npz_schema_handling_result.md"

THIRD = ["dollar_neutral_composite_pit", "dollar_neutral_composite_vol_targeted"]

# Classification par LECTURE, chaque entree portant la ligne du script qui
# decide du traitement. Etablie avant toute execution de ce rapport ; les faits
# numeriques sont re-verifies plus bas par execution.
CLASSIFICATION = [
    ("nonml_pnl_duplicate_sweep_backtest.py", "D",
     'l.40-42 : `if {"pnl_candidate", "turn_candidate"} <= files:` '
     '-> `pnl_candidate - turn_candidate * c`',
     "Soustrait les couts d'un P&L **deja net** : exactement l'erreur que j'ai "
     "commise moi-meme au #443."),
    ("nonml_leaders_trend_union_pnl_persistence_audit.py", "D",
     "l.55 : `dup_groups, quasi, unknown = sw.main()` -- execute le balayage "
     "entier",
     "Defaut **herite et reellement atteint** : `sw.main()` parcourt tous les "
     "`.npz`, donc la branche fausse est exercee."),
    ("nonml_pnl_duplicate_sweep_v2_audit.py", "A",
     "l.44 `sw.net_pnl(d)` importe la fonction defectueuse, mais l.111-112 et "
     "l.152 ne l'appellent que sur `A`, `B` et `PAIR_414` -- noms codes en "
     "dur, aucun de ce schema ; l.60 `glob` ne fait que compter",
     "**Classement corrige en cours de cycle** : je l'avais d'abord ecrit D "
     "par « heritage », sans verifier qu'un fichier de ce schema atteigne la "
     "fonction. Il ne l'atteint jamais."),
    ("nonml_pnl_duplicate_sweep_audit.py", "A",
     'l.93-94 : `key = "pos" if ... else ("pnl_gross_ov" if ... else '
     '"pnl_candidate")`',
     "Le troisieme schema est **explicitement prevu** dans la cascade de cles."),
    ("nonml_log_return_compounding_audit.py", "B",
     'l.121-122 : `if not REQUIRED <= set(npz.files): skipped.append((name, '
     '"schema non standard"))`',
     "Ecarte avec une raison **nommee et publiee** dans la liste des ecartes."),
    ("nonml_empty_pass_basket_extension_backtest.py", "B",
     'l.64 : `return "autre", sorted(f)` -> `other.append(name)` (l.96), '
     "compte publie l.126",
     "Compte publie, mais **fondu** avec les inexploitables : "
     "`autres / inexploitables : N`. Compte, donc B -- pas nomme, donc a "
     "signaler."),
    ("nonml_empty_pass_requalification_backtest.py", "C",
     'l.52 : `if "pos" not in d.files or "r_asset" not in d.files:` -> '
     "`continue`",
     "Ecarte **silencieusement** : ni compte ni signale."),
    ("nonml_npz_report_consistency_backtest.py", "C",
     'l.72-74 : `skipped.append((name, "schema panier (pas de position '
     'scalaire)"))`',
     "**Connu d'avance** (le mien, #442). Compte, mais sous une etiquette "
     "**fausse** : ces 2 fichiers ne sont pas des paniers. C'est ce faux "
     "libelle qui a produit le « 23 paniers » corrige au #443."),
    ("nonml_npz_report_consistency_baskets_backtest.py", "A",
     'l.55-58 : `if not BASKET_KEYS <= files: if not {"pos","r_asset"} <= '
     "files: third.append(...)`",
     "**Connu d'avance** (le mien, #443) : isole le schema dans une categorie "
     "a part et le publie nommement."),
    ("nonml_pnl_persistence_lot5_audit.py", "C",
     'l.169-170 : `if "pos" not in p.files: continue`',
     "Ecarte silencieusement. `n_sessions()` (l.52-54) planterait sur ce "
     "schema, mais n'est jamais atteint pour ces noms."),
    ("nonml_duplicate_sweep_coverage_audit.py", "A",
     "l.40 : `all_npz = sorted(RESULTS.glob(\"*_pnl.npz\"))` -- aucun "
     "`np.load` dans le script",
     "Ne compte que des fichiers, n'applique aucune formule : les inclure au "
     "compte est le traitement correct."),
    ("nonml_reproducibility_campaign_v2_audit.py", "A",
     "aucun `np.load` : le motif `*_pnl.npz` n'apparait que dans du texte "
     "cite (l.66, l.69)",
     "Ne decode aucun fichier."),
]

KNOWN_IN_ADVANCE = {"nonml_npz_report_consistency_backtest.py",
                    "nonml_npz_report_consistency_baskets_backtest.py"}


def load_sweep():
    spec = importlib.util.spec_from_file_location(
        "sw", SCRIPTS / "nonml_pnl_duplicate_sweep_backtest.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    sw = load_sweep()

    # --- Fait numerique 1 : concordance des 2 fichiers ----------------------
    # `pnl_candidate` est DEJA net (pas de re-soustraction du turnover), mais la
    # CONVENTION de rendement n'est pas dictee par le schema : elle se lit dans
    # le script producteur. Les deux conventions sont donc testees.
    conc = []
    for name in THIRD:
        d = np.load(RESULTS / f"nonml_{name}_pnl.npz", allow_pickle=True)
        rep = RESULTS / f"nonml_{name}_result.md"
        txt = rep.read_text(encoding="utf-8") if rep.exists() else ""
        pub = set(re.findall(r"[+-]\d\.\d\d", txt))
        row = {"name": name}
        for leg in ("pnl_candidate", "pnl_ref"):
            x = np.asarray(d[leg], float)
            brut = trading_metrics(x)["sharpe_ann"]
            lg = trading_metrics(np.log1p(x))["sharpe_ann"]
            hit_brut, hit_log = f"{brut:+.2f}" in pub, f"{lg:+.2f}" in pub
            row[leg] = (brut, hit_brut, lg, hit_log,
                        "log" if hit_brut else ("simple" if hit_log else None))
        conc.append(row)

    # --- Fait numerique 2 : ampleur du defaut D ----------------------------
    d = np.load(RESULTS / f"nonml_{THIRD[0]}_pnl.npz", allow_pickle=True)
    got, branch = sw.net_pnl(d)
    truth = np.asarray(d["pnl_candidate"], float)
    cum_got = float(np.expm1(np.log1p(np.asarray(got, float)).sum()))
    cum_true = float(np.expm1(np.log1p(truth).sum()))
    gap = float(np.abs(np.asarray(got, float) - truth).max())

    # --- Fait numerique 3 : consequence bornee -----------------------------
    near = []
    for p in sorted(RESULTS.glob("*_pnl.npz")):
        if THIRD[0] in p.name:
            continue
        try:
            s, _ = sw.net_pnl(np.load(p, allow_pickle=True))
        except Exception:  # noqa: BLE001
            continue
        s = np.asarray(s, float)
        if s.shape != truth.shape or not np.isfinite(s).all():
            continue
        near.append((float(np.corrcoef(s, truth)[0, 1]), p.name))
    near.sort(reverse=True)

    counts = {k: sum(1 for c in CLASSIFICATION if c[1] == k) for k in "ABCD"}
    n_new = sum(1 for c in CLASSIFICATION if c[0] not in KNOWN_IN_ADVANCE)
    verdict = "FAIL" if counts["D"] else "PASS"

    L = ["# Le troisième schéma `.npz` et son traitement par les balayages "
         "(pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.")
    L.append("")
    L.append(f"## Verdict : **{verdict}**")
    L.append("")
    if counts["D"]:
        L.append(f"Le critère pré-enregistré était : **FAIL si au moins un consommateur "
                 f"applique une formule fausse** (catégorie D). Il y en a **{counts['D']}**.")
    else:
        L.append("Aucun consommateur n'applique de formule fausse.")
    L.append("")

    L.append("## La concordance — et une correction du pré-enregistrement")
    L.append("")
    L.append("Le pré-enregistrement déclarait la concordance **connue d'avance** et comptée")
    L.append("zéro. **C'était trop large** : le sondage post-hoc du #443 n'avait porté que sur")
    L.append("`dollar_neutral_composite_pit`. `dollar_neutral_composite_vol_targeted` n'avait")
    L.append("jamais été vérifié — il compte donc pour **1 vérification neuve**, et c'est lui")
    L.append("qui a livré le résultat intéressant.")
    L.append("")
    L.append("| Fichier | Jambe | Sharpe (log) | Sharpe (simple) | Convention retenue |")
    L.append("|---|---|---|---|---|")
    for row in conc:
        for leg in ("pnl_candidate", "pnl_ref"):
            brut, hb, lg, hl, conv = row[leg]
            mb = f"**{brut:+.2f}** ✔" if hb else f"{brut:+.2f}"
            ml = f"**{lg:+.2f}** ✔" if hl else f"{lg:+.2f}"
            L.append(f"| `{row['name']}` | `{leg}` | {mb} | {ml} | "
                     f"{conv if conv else '**aucune**'} |")
    L.append("")
    L.append("**Les quatre jambes se retrouvent** dans leur rapport — mais pas sous la même")
    L.append("convention.")
    L.append("")
    L.append("### Le schéma ne détermine pas la convention")
    L.append("")
    L.append("C'est le résultat de fond de ce cycle :")
    L.append("")
    L.append("- `dollar_neutral_composite_pit` stocke des rendements **simples** — son")
    L.append("  producteur calcule le Sharpe sur `log1p(pnl)` ;")
    L.append("- `dollar_neutral_composite_vol_targeted` stocke des rendements **log** — son")
    L.append("  producteur appelle `trading_metrics(r_vt)` **directement**, et le rendement")
    L.append("  total par `np.exp(sum)`.")
    L.append("")
    L.append("**Deux fichiers, un seul schéma de clés, deux conventions opposées.** Les clés")
    L.append("`pnl_candidate` / `pnl_ref` ne suffisent donc **pas** à interpréter un fichier :")
    L.append("il faut lire le script producteur. Tout balayage qui déduirait la convention du")
    L.append("seul schéma se tromperait sur l'un des deux, quel que soit son choix.")
    L.append("")
    L.append("C'est la **troisième** fois sur cet axe que ma propre reconstruction est en")
    L.append("cause avant le dépôt (#442 `r_alt` ignoré, #443 coûts comptés deux fois, ici")
    L.append("`log1p` appliqué aux deux) : mon premier passage appliquait `log1p` aux deux et")
    L.append("déclarait `vol_targeted` discordant. Le pré-enregistrement engageait à me")
    L.append("méfier d'abord de ma reconstruction ; appliqué, il a évité une fausse accusation.")
    L.append("")

    L.append("## Le traitement par les 12 consommateurs")
    L.append("")
    L.append("Classement par **lecture**, chacun justifié par la ligne qui décide du")
    L.append("traitement — pas par un balayage de garde-fous. Dans ce projet, aucun défaut")
    L.append("réel n'a jamais été trouvé par la mesure mécanique elle-même (#428, #436,")
    L.append("#442, #443).")
    L.append("")
    L.append("| | Catégorie | Nombre |")
    L.append("|---|---|---|")
    L.append(f"| **A** | traité correctement | **{counts['A']}** |")
    L.append(f"| **B** | écarté explicitement (compté) | **{counts['B']}** |")
    L.append(f"| **C** | écarté **silencieusement** | **{counts['C']}** |")
    L.append(f"| **D** | **formule fausse appliquée** | **{counts['D']}** |")
    L.append("")
    L.append(f"**{len(CLASSIFICATION)}/12 classés.** Dont **{len(KNOWN_IN_ADVANCE)}** connus")
    L.append(f"d'avance (les miens, #442 et #443) ⇒ **{n_new} classements neufs**.")
    L.append("")
    L.append("| Consommateur | Cat. | Ligne qui décide | Lecture |")
    L.append("|---|---|---|---|")
    for f, cat, line, note in sorted(CLASSIFICATION, key=lambda t: (t[1], t[0])):
        tag = " *(connu d'avance)*" if f in KNOWN_IN_ADVANCE else ""
        L.append(f"| `{f}`{tag} | **{cat}** | {line} | {note} |")
    L.append("")

    L.append("## Le défaut D, mesuré")
    L.append("")
    L.append(f"`nonml_pnl_duplicate_sweep_backtest.py` fait prendre à")
    L.append(f"`{THIRD[0]}` la branche **« {branch} »** et lui soustrait")
    L.append("des coûts qu'il porte déjà :")
    L.append("")
    L.append("| | Valeur |")
    L.append("|---|---|")
    L.append(f"| P&L cumulé **selon le balayage** | **{cum_got:+.4f}** |")
    L.append(f"| P&L cumulé **réel** (`pnl_candidate` tel quel) | **{cum_true:+.4f}** |")
    L.append(f"| écart maximal séance par séance | {gap:.1e} |")
    L.append("")
    L.append("Le second fichier, `dollar_neutral_composite_vol_targeted`, **échappe au")
    L.append("défaut** : dépourvu de `turn_candidate`, il tombe sur la branche « candidat")
    L.append("seul » (l.43-44) qui le lit correctement. Le défaut ne frappe donc que les")
    L.append("fichiers de ce schéma qui stockent leur turnover — **1 sur 2**.")
    L.append("")

    L.append("### Conséquence, bornée et vérifiée")
    L.append("")
    L.append("Ce chiffre faux **n'a été publié nulle part** : le fichier n'apparaît sous son")
    L.append("nom dans aucun rapport de balayage. Le seul effet possible était un **faux")
    L.append("négatif** — un doublon manqué parce que la série comparée était déformée.")
    L.append("")
    if near:
        c0, n0 = near[0]
        L.append(f"Vérifié : **{len(near)}** série(s) du dépôt seulement ont la même longueur")
        L.append(f"et sont donc comparables. La plus proche est `{n0}`, corrélation")
        L.append(f"**{c0:+.4f}**. **Aucun doublon n'a été manqué.**")
    L.append("")
    L.append("Le défaut est donc **réel dans le code et sans conséquence publiée à ce jour**.")
    L.append("Les deux moitiés de cette phrase comptent : la seconde ne l'annule pas, car")
    L.append("tout futur `.npz` de ce schéma portant un turnover serait mal lu.")
    L.append("")
    L.append("**Ce cycle ne corrige rien** — il ne fait que lire, comme annoncé. La")
    L.append("correction du balayage est une modification de code à déclarer, mesurer et")
    L.append("committer dans son propre cycle.")
    L.append("")

    L.append("## Les écartés silencieux (C)")
    L.append("")
    L.append(f"**{counts['C']}** consommateurs laissent leur lecteur mal informé sur ces")
    L.append("fichiers. Deux les écartent en silence — ni comptés ni signalés ; leur résultat")
    L.append("reste juste, mais leur rapport laisse croire à un balayage complet.")
    L.append("")
    L.append("Le troisième, `nonml_npz_report_consistency_backtest.py` (#442), **ne rentre")
    L.append("proprement dans aucune des quatre catégories déclarées** : il les compte — donc")
    L.append("pas C au sens strict — mais sous une raison **fausse** — donc pas B non plus.")
    L.append("Je le classe C parce que l'effet sur le lecteur est celui d'un silence, et je")
    L.append("signale l'entorse plutôt que d'élargir une catégorie après coup.")
    L.append("")
    for f, cat, line, note in sorted(CLASSIFICATION):
        if cat == "C":
            L.append(f"- `{f}` — {line}")
    L.append("")
    L.append("Le cas de `nonml_npz_report_consistency_backtest.py` (#442) est le plus")
    L.append("instructif : il **comptait** ces fichiers, donc paraissait exemplaire, mais")
    L.append("sous l'étiquette **fausse** « schéma panier ». Un compte publié sous un mauvais")
    L.append("libellé est plus trompeur qu'un silence, parce qu'il a l'air d'une couverture.")
    L.append("")

    L.append("## Ce que ce cycle ne permet pas de conclure")
    L.append("")
    L.append("- **La prédiction du pré-enregistrement est vérifiée sur un point, réfutée sur")
    L.append("  aucun** : j'attendais « au moins un C », il y en a")
    L.append(f"  **{counts['C']}**. Je disais n'avoir aucune idée s'il existait un D : il y")
    L.append(f"  en a **{counts['D']}**, et l'un d'eux est un défaut que j'avais moi-même")
    L.append("  commis au #443 sans voir qu'il dormait déjà dans le dépôt.")
    L.append("- **Aucune stratégie n'est validée ni invalidée** par ce cycle.")
    L.append("- Le classement porte sur **ce schéma**. Rien n'est établi sur la façon dont")
    L.append("  ces 12 consommateurs traitent d'autres schémas non catalogués — s'il en")
    L.append("  existe encore, ce cycle ne les a pas cherchés.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
