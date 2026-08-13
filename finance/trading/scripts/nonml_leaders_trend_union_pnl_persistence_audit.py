"""Audit — lever l'angle mort des balayages de doublons (cycle #419).

Trois contrôles :

1. **Non-régression** — le fichier de résultat doit être identique octet à octet
   après ré-exécution.
2. **Test de la prédiction pré-enregistrée** — le balayage doit désormais
   détecter la paire `sma200_leaders_overlay` / `leaders_trend_union_overlay`
   comme doublon exact, et le décompte corrigé passer de 1 à 2.
3. **Identité vérifiée directement**, sans passer par le balayage : les deux P&L
   sont-ils bit-à-bit égaux, et sur quelle longueur ?

Usage : python3 scripts/nonml_leaders_trend_union_pnl_persistence_audit.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_leaders_trend_union_pnl_persistence_audit.md"
BASE = Path("/tmp/claude-0/-home-user-Quant-Trade/"
            "d40e7f44-8dba-572d-ba27-6c7a61ed28ed/scratchpad/baseline_ltu.md")
CUR = RESULTS / "nonml_leaders_trend_union_overlay_result.md"

A = "nonml_leaders_trend_union_overlay"
B = "nonml_sma200_leaders_overlay"


def net(name):
    d = np.load(RESULTS / f"{name}_pnl.npz", allow_pickle=True)
    s, tag = sw.net_pnl(d)
    return s, tag


def main():
    L = ["# Audit — lever l'angle mort des balayages de doublons", ""]

    # --- 1. non-regression ---
    ok1 = BASE.exists() and CUR.exists() and BASE.read_bytes() == CUR.read_bytes()
    L.append("## 1. Non-régression")
    L.append("")
    L.append(f"- fichier de résultat identique après ré-exécution : **{'OUI' if ok1 else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — l ajout du savez n a rien perturbé.' if ok1 else 'ÉCHEC — le résultat a changé.'}**")
    L.append("")

    # --- 2. test de la prediction ---
    dup_groups, quasi, unknown = sw.main()
    names = {frozenset(g) for g in dup_groups}
    found = frozenset({A, B}) in names
    surnum_raw = sum(len(g) - 1 for g in dup_groups)
    # l'alias de nommage etape_D avait ete rejete par lecture au #406
    alias = frozenset({"etape_D_overlay_optimized", "nonml_etape_d_garch_defensive_overlay"})
    surnum_corr = surnum_raw - (1 if alias in names else 0)

    L.append("## 2. Test de la prédiction pré-enregistrée")
    L.append("")
    L.append("Le pré-enregistrement annonçait, **avant l'ajout** : « le balayage doit détecter")
    L.append("la paire comme doublon exact, et le décompte corrigé passer de 1 à 2 ».")
    L.append("")
    L.append(f"- paire détectée comme doublon exact : **{'OUI' if found else 'NON'}**")
    L.append(f"- groupes de doublons trouvés : **{len(dup_groups)}**")
    L.append(f"- entrées surnuméraires brutes : **{surnum_raw}**")
    L.append(f"- après rejet de l'alias de nommage Étape D (fait par lecture au #406) : "
             f"**{surnum_corr}**")
    L.append("")
    ok2 = found and surnum_corr == 2
    if ok2:
        L.append("**PRÉDICTION CONFIRMÉE.** Le décompte passe de 1 à 2, exactement comme")
        L.append("annoncé. Ce n'était pas une intuition : c'était la conséquence arithmétique")
        L.append("du #403, et elle se vérifie.")
        L.append("")
        L.append("Le point n'est pas d'avoir eu raison — la prédiction était déductive, pas")
        L.append("risquée. Il est que **les deux balayages précédents avaient tort de conclure")
        L.append("à 1**, et le savaient : tous deux ont écrit que leur résultat était une borne")
        L.append("inférieure. Cette borne vient de monter d'un cran.")
    else:
        L.append("**PRÉDICTION DÉMENTIE.** C'est le résultat le plus important du cycle : soit")
        L.append("le #403 se trompait en concluant à l'identité des deux stratégies, soit le")
        L.append("balayage a un second défaut. À investiguer avant toute autre conclusion.")
    L.append("")

    # --- 3. identite verifiee directement ---
    sa, tag_a = net(A)
    sb, tag_b = net(B)
    same_len = len(sa) == len(sb)
    identical = same_len and bool(np.array_equal(sa, sb))

    L.append("## 3. Identité vérifiée sans passer par le balayage")
    L.append("")
    L.append("Contrôle direct, pour ne pas dépendre du seul outil dont on teste la portée.")
    L.append("")
    L.append(f"- schéma reconnu : `{tag_a}` / `{tag_b}`")
    L.append(f"- longueurs : **{len(sa)}** / **{len(sb)}**")
    L.append(f"- P&L nets bit-à-bit identiques : **{'OUI' if identical else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — l identité établie au #403 se retrouve sur l univers d origine.' if identical else 'DIVERGENCE'}**")
    L.append("")

    # --- portee restante ---
    L.append("## Ce qui reste hors de portée")
    L.append("")
    n_npz = len(list(RESULTS.glob("*_pnl.npz")))
    L.append(f"- fichiers `*_pnl.npz` : **{n_npz}**")
    L.append(f"- schémas non reconnus par le balayage : **{len(unknown)}**")
    L.append("")
    L.append("L'angle mort **spécifique** documenté aux #406 et #418 est levé. La limite")
    L.append("**générale** ne l'est pas : le balayage ne voit toujours que les candidats ayant")
    L.append("sauvegardé un `.npz`, soit moins de la moitié du backlog. Un doublon entre deux")
    L.append("candidats dépourvus de `.npz` resterait invisible, et rien ne dit qu'il n'y en a")
    L.append("pas.")
    L.append("")

    verdict = ok1 and ok2 and identical
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME — les trois contrôles passent.' if verdict else 'NON CONFORME — au moins un contrôle échoue.'}**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
