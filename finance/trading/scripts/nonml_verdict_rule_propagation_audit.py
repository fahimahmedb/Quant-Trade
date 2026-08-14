"""Audit independant — propagation de la regle (#449).

Critere 4 du pre-enregistrement : **aucune reimplementation historique
modifiee**. Un cycle qui corrige une regle partout risque d'ecraser les
scripts qui reproduisent VOLONTAIREMENT l'ancienne — et de detruire ainsi la
mesure qu'ils portent.

Cet audit verifie la chose la plus simple et la plus difficile a truquer :
ces scripts contiennent-ils ENCORE l'ancienne regle, sous forme executable ?
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_verdict  # noqa: E402

OUT = RESULTS / "nonml_verdict_rule_propagation_audit.md"

DOIVENT_GARDER = {
    "nonml_verdict_detector_fix_backtest.py": "verdict_avant",
    "nonml_verdict_detector_fix_audit.py": "ancienne",
    "nonml_sweep_pass_prose_fix_audit.py": None,
}
CONVERTIS = [
    "nonml_capitulation_gate_floor_sweep_backtest.py",
    "nonml_empty_pass_basket_extension_backtest.py",
    "nonml_empty_pass_requalification_backtest.py",
    "nonml_pnl_persistence_lot4_audit.py",
    "nonml_protocol_inventory_backtest.py",
    "nonml_sameday_timestamp_resolution_backtest.py",
]
ANCIENNE_EXEC = re.compile(r'^\s*(if|return).*"\*\*PASS" in ', re.M)


def main():
    # 1. Les historiques ont-ils garde l'ancienne regle EXECUTABLE ?
    gardes = []
    for f in DOIVENT_GARDER:
        src = (SCRIPTS / f).read_text(encoding="utf-8")
        gardes.append((f, bool(ANCIENNE_EXEC.search(src))))
    tous_gardes = all(ok for _, ok in gardes)

    # 2. Les convertis n'ont-ils PLUS l'ancienne regle executable ?
    nets = []
    for f in CONVERTIS:
        src = (SCRIPTS / f).read_text(encoding="utf-8")
        nets.append((f, not ANCIENNE_EXEC.search(src),
                     "import nonml_verdict" in src))
    tous_nets = all(a and b for _, a, b in nets)

    # 3. Les convertis s'importent-ils et s'executent-ils encore ?
    importables = []
    for f in CONVERTIS:
        r = subprocess.run([sys.executable, "-c",
                            f"import ast,sys; ast.parse(open('{SCRIPTS / f}',encoding='utf-8').read())"],
                           capture_output=True, text=True)
        importables.append((f, r.returncode == 0))
    tous_importables = all(ok for _, ok in importables)

    # 4. Le module donne-t-il le meme verdict que la fonction du #448 ?
    import nonml_pnl_duplicate_sweep_backtest as sw
    rapports = sorted(RESULTS.glob("nonml_*_result.md"))
    div = sum(1 for p in rapports
              for m in ("PASS", "FAIL")
              if nonml_verdict.porte_verdict(p.read_text(encoding="utf-8"), m)
              != sw.porte_verdict(p.read_text(encoding="utf-8"), m))

    L = ["# Audit indépendant — propagation de la règle (#449)", ""]
    L.append("**Critère 4** : aucune réimplémentation historique modifiée. Un cycle qui")
    L.append("corrige une règle partout risque d'écraser les scripts qui reproduisent")
    L.append("**volontairement** l'ancienne — et de détruire la mesure qu'ils portent.")
    L.append("")

    L.append("## Contrôle 1 — les historiques ont-ils gardé l'ancienne règle ?")
    L.append("")
    L.append("Recherche de la forme **exécutable** (`if`/`return` … `\"**PASS\" in `), pas")
    L.append("de la sous-chaîne : au #447 ce même contrôle s'était trompé en retrouvant la")
    L.append("règle dans un *commentaire* qui la citait.")
    L.append("")
    L.append("| Script | Ancienne règle encore exécutable |")
    L.append("|---|---|")
    for f, ok in gardes:
        L.append(f"| `{f}` | {'**oui**' if ok else '**NON — détruite**'} |")
    L.append("")

    L.append("## Contrôle 2 — les convertis en sont-ils débarrassés ?")
    L.append("")
    L.append("| Script | Ancienne règle absente | Importe le module |")
    L.append("|---|---|---|")
    for f, a, b in nets:
        L.append(f"| `{f}` | {'✔' if a else '**non**'} | {'✔' if b else '**non**'} |")
    L.append("")

    L.append("## Contrôle 3 — les convertis restent-ils valides ?")
    L.append("")
    L.append(f"**{sum(1 for _, ok in importables if ok)}/{len(importables)}** analysables")
    L.append("sans erreur de syntaxe. Une conversion qui casserait un script serait pire")
    L.append("que le défaut qu'elle corrige.")
    L.append("")

    L.append("## Contrôle 4 — le module est-il bien la règle du #448 ?")
    L.append("")
    L.append(f"- rapports comparés : **{len(rapports)}** (× 2 marqueurs)")
    L.append(f"- verdicts divergents : **{div}**")
    L.append("")
    L.append("Le module a été **copié** du balayage ; ce contrôle vérifie que la copie n'a")
    L.append("pas dérivé en cours de route. C'est précisément la divergence entre copies")
    L.append("que ce cycle existe pour empêcher à l'avenir.")
    L.append("")

    ok = tous_gardes and tous_nets and tous_importables and div == 0
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME' if ok else 'NON CONFORME'}**")
    L.append("")
    L.append(f"- historiques préservés : **{'oui' if tous_gardes else 'non'}**")
    L.append(f"- convertis assainis : **{'oui' if tous_nets else 'non'}**")
    L.append(f"- convertis valides : **{'oui' if tous_importables else 'non'}**")
    L.append(f"- module fidèle au #448 : **{'oui' if div == 0 else 'non'}**")
    L.append("")
    L.append("### Ce que cet audit ne prouve pas")
    L.append("")
    L.append("Il vérifie que les scripts **contiennent** ce qu'ils doivent contenir, pas")
    L.append("que leurs **rapports publiés** aient été mis à jour — ils ne l'ont pas été,")
    L.append("délibérément et de façon déclarée. L'écart entre le code et les rapports de")
    L.append("ces six scripts est **réel et assumé**, pas couvert par ce CONFORME.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
