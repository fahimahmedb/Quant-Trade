"""Concordance entre le P&L sauvegardé et les chiffres publiés (#442).

Spécification pré-enregistrée dans `PREREG_npz_report_consistency.md`,
committée avant toute mesure d'ensemble.

La campagne #434-#441 comparait le **rapport à son code**. Ce cycle pose une
question différente : le `.npz` sauvegardé produit-il **les chiffres que le
rapport annonce** ?

Ce cycle ne fait que **lire** — aucun rapport ni `.npz` n'est modifié.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
FINANCE = ROOT.parent
sys.path.insert(0, str(FINANCE / "src"))

from prediction import trading_metrics  # noqa: E402

OUT = RESULTS / "nonml_npz_report_consistency_result.md"

# Testes AVANT le pre-enregistrement pour valider la methode : leur concordance
# etait connue d'avance et ne compte pas comme verification neuve.
PRE_KNOWN = {"acf_lag1_vol_targeting_overlay", "arch_clustering_vol_targeting_overlay",
             "auto_loan_delinquency_overlay", "beta_dispersion_vol_targeting_overlay",
             "bitcoin_momentum_overlay"}

MULTI_MARKET = re.compile(r"^\|\s*(Composite|NDX|Russell|S&P|DAX)", re.M)


def net_pnl(d):
    """P&L net, selon le schema REELLEMENT porte par le fichier.

    Defaut attrape par l'inspection des discordants (#442) : mon filtre initial
    acceptait tout `.npz` portant `pos` et `r_asset`, y compris les fichiers
    « deux jambes » qui portent en plus `r_alt`. La formule indicielle y ignore
    la jambe alternative et produit un Sharpe qui n'est celui de personne. Les
    7 discordants du premier passage etaient tous de ce type, et redeviennent
    concordants avec la formule du #406.
    """
    pos = np.asarray(d["pos"], float)
    r = np.asarray(d["r_asset"], float)
    c = float(d["cost_bps"]) / 1e4
    turn = np.abs(np.diff(pos, prepend=pos[:1]))
    if "r_alt" in d.files:
        r_alt = np.asarray(d["r_alt"], float)
        return pos * r + (1.0 - pos) * r_alt - turn * c, "deux jambes"
    return pos * r - turn * c, "indiciel"


def main():
    concordant, discordant, skipped = [], [], []
    schemas = {}

    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        name = p.name.replace("nonml_", "").replace("_pnl.npz", "")
        rep = RESULTS / f"nonml_{name}_result.md"
        if not rep.exists():
            skipped.append((name, "aucun rapport publié"))
            continue
        try:
            d = np.load(p, allow_pickle=True)
        except Exception as exc:  # noqa: BLE001
            skipped.append((name, f"`.npz` illisible : {exc}"))
            continue
        if "pos" not in d.files or "r_asset" not in d.files:
            skipped.append((name, "schéma panier (pas de position scalaire)"))
            continue
        pnl, schema = net_pnl(d)
        if pnl.size < 2 or not np.isfinite(pnl).all():
            skipped.append((name, "série inexploitable"))
            continue
        schemas[schema] = schemas.get(schema, 0) + 1
        sharpe = trading_metrics(pnl)["sharpe_ann"]
        txt = rep.read_text(encoding="utf-8")
        published = set(re.findall(r"[+-]\d\.\d\d", txt))
        target = f"{sharpe:+.2f}"
        if target in published:
            concordant.append((name, sharpe))
        else:
            discordant.append((name, sharpe, sorted(published)[:6],
                               bool(MULTI_MARKET.search(txt))))

    n_exam = len(concordant) + len(discordant)

    L = ["# Concordance entre le P&L sauvegardé et les chiffres publiés (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.")
    L.append("")
    L.append("## La question posée, et pourquoi elle est neuve")
    L.append("")
    L.append("La campagne #434-#441 comparait le **rapport à son code** : ré-exécuté, le script")
    L.append("reproduit-il son rapport ? Oui, borne 4,2 % sur 69 tirages.")
    L.append("")
    L.append("**Ce cycle pose une question différente** : le `.npz` sauvegardé produit-il les")
    L.append("chiffres que le rapport annonce ? Un script peut se reproduire parfaitement et")
    L.append("sauvegarder une série qui ne correspond pas à la stratégie décrite. Les balayages")
    L.append("qui consomment ces `.npz` (doublons #406, activation #415, batterie Règle 9)")
    L.append("seraient alors alimentés par des séries fausses **sans qu'aucun ne s'en aperçoive**.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- `.npz` trouvés : **{len(concordant) + len(discordant) + len(skipped)}**")
    L.append(f"- **examinés** (position scalaire + rapport publié) : **{n_exam}**")
    L.append(f"- écartés : **{len(skipped)}**")
    L.append("")
    reasons = {}
    for _, why in skipped:
        reasons[why] = reasons.get(why, 0) + 1
    if reasons:
        L.append("| Raison d'écartement | Nombre |")
        L.append("|---|---|")
        for why, k in sorted(reasons.items(), key=lambda t: -t[1]):
            L.append(f"| {why} | **{k}** |")
        L.append("")

    L.append("## Résultat")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| **concordants** (Sharpe du `.npz` publié au rapport) | **{len(concordant)}** |")
    L.append(f"| **discordants** | **{len(discordant)}** |")
    L.append("")
    if n_exam:
        L.append(f"**Taux de concordance : {100*len(concordant)/n_exam:.1f} %** sur {n_exam} examinés.")
    L.append("")
    n_pre = len(set(n for n, _ in concordant) & PRE_KNOWN)
    L.append(f"Dont **{n_pre}** dont la concordance était **connue d'avance** (essais de")
    L.append("faisabilité menés avant le pré-enregistrement) : ils restent comptés, mais ne")
    L.append(f"constituent pas une vérification neuve. Vérifications neuves : **{n_exam - n_pre}**.")
    L.append("")

    if discordant:
        L.append("## Discordants — à inspecter, pas à conclure")
        L.append("")
        L.append("Le pré-enregistrement annonçait que ce compte **ne se conclut pas")
        L.append("mécaniquement** : un rapport multi-marchés publie une ligne par marché alors")
        L.append("que le `.npz` n'en sauvegarde qu'une (convention NDX du #416).")
        L.append("")
        L.append("| Candidat | Sharpe du `.npz` | Sharpes publiés (extrait) | Rapport multi-marchés |")
        L.append("|---|---|---|---|")
        for n, sh, pub, multi in sorted(discordant):
            L.append(f"| `{n}` | {sh:+.2f} | {', '.join(pub)} | {'**oui**' if multi else 'non'} |")
        L.append("")
        n_multi = sum(1 for _, _, _, m in discordant if m)
        L.append(f"- discordants dont le rapport est **multi-marchés** : **{n_multi}** — "
                 f"faux positifs attendus, la convention #416 ne sauvegardant que la branche NDX")
        L.append(f"- discordants sur rapport **mono-marché** : **{len(discordant) - n_multi}** — "
                 f"ceux-là méritent une inspection individuelle")
        L.append("")
    else:
        L.append("## Aucun discordant")
        L.append("")
        L.append("Tous les `.npz` examinés produisent un Sharpe qui figure dans leur rapport.")
        L.append("**C'est une absence, pas un exploit** : elle signifie que les séries")
        L.append("consommées par les balayages correspondent bien aux stratégies décrites, sur")
        L.append("le périmètre examiné.")
        L.append("")

    L.append("## Portée")
    L.append("")
    L.append(f"Le contrôle porte sur **{n_exam}** `.npz` à position scalaire, dont")
    L.append(f"**{schemas.get('indiciel', 0)}** au schéma indiciel et **{schemas.get('deux jambes', 0)}**")
    L.append("au schéma « deux jambes », chacun reconstruit avec **sa** formule.")
    L.append("")
    L.append("**Défaut attrapé par l'inspection des discordants** : le premier passage")
    L.append("appliquait la formule indicielle à tous les fichiers portant `pos` et `r_asset`,")
    L.append("y compris ceux qui portent en plus `r_alt`. Il produisait **7 discordants**, tous")
    L.append("de ce type, tous redevenus concordants avec la formule du #406. Le")
    L.append("pré-enregistrement annonçait des faux positifs — il en attendait d'un rapport")
    L.append("multi-marchés, ils sont venus d'ailleurs.")
    L.append("")
    L.append("Les schémas **panier** n'ont pas de position scalaire et restent **écartés, pas")
    L.append("ignorés** : leur nombre figure au tableau de couverture.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
