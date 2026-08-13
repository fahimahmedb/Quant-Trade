"""Balayage des portes de capitulation neutralisées par le plancher 1,0×
(spécification pré-enregistrée dans `PREREG_capitulation_gate_floor_sweep.md`,
committée avant ce script).

Diagnostic, pas une stratégie.

Motivation (#410) : une porte qui s'ouvre en régime de **faiblesse** combinée à
un vol-targeting `clip(20 % / vol, 1,0, CAP)` ne peut jamais s'activer — la
faiblesse et la volatilité haute coïncident, et le clip ramène l'exposition au
plancher. Le « PASS » de ce montage ne mesure que son inactivité.

Deux volets, comme pré-enregistré :

- **A — détection statique exhaustive** de la structure `clip(..., 1.0, ...)`
  dans tous les `nonml_*_backtest.py`, par analyse du code et non par convention
  de nommage.
- **B — mesure empirique** de l'activation réelle, limitée aux candidats
  disposant d'un `.npz` au schéma `pos`. Les candidats détectés mais non mesurés
  sont **comptés et listés**.

Critères FIXÉS AVANT EXÉCUTION :
- structurellement inactif : exposition > 1,0× sur **moins de 2 %** des séances
  (seuil repris tel quel du #410) ;
- PASS vide : candidat inactif dont le rapport porte un PASS.
"""
import io
import re
import sys
import token as tokmod
import tokenize
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_capitulation_gate_floor_sweep_result.md"

INACTIVE_MAX = 0.02  # repris tel quel du #410

# `np.clip(x, 1.0, CAP)` ou `np.clip(x, 1, CAP)` : plancher a l'exposition neutre
RE_CLIP_FLOOR = re.compile(r"np\.clip\(\s*[^,]+,\s*1(?:\.0+)?\s*,")


def has_floor_clip(src: str) -> bool:
    """Detecte le motif hors commentaires et chaines, via tokenize.

    Reconstruire la ligne logique a partir des tokens evite de compter un motif
    apparaissant dans une docstring -- travers rencontre deux fois (#392, #404).
    """
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        return bool(RE_CLIP_FLOOR.search(src))
    code = []
    for t in toks:
        if t.type in (tokmod.COMMENT, tokmod.STRING):
            continue
        code.append(t.string)
    return bool(RE_CLIP_FLOOR.search(" ".join(code).replace(" ", "")))


def verdict_of(name: str):
    """Lit le verdict du rapport de resultat du candidat, s'il existe."""
    for cand in (RESULTS / f"nonml_{name}_result.md",):
        if cand.exists():
            txt = cand.read_text(encoding="utf-8")
            if "**PASS" in txt or "PASS (niveau 1)" in txt:
                return "PASS"
            if "**FAIL" in txt or "FAIL —" in txt:
                return "FAIL"
            return "indéterminé"
    return "absent"


# Denominateur juge trop proche de zero pour que la division soit informative.
# Seuil FIXE AVANT CALCUL (#425). Les seances concernees sont exclues et
# comptees, jamais remplacees par une valeur par defaut.
BASKET_EPS = 1e-12


def activation_of(name: str):
    """Fraction de seances a exposition > 1,0x, depuis le .npz s'il existe.

    Deux schemas lus (extension #425) :

    - **indiciel** (`pos`) : l'exposition est stockee telle quelle ;
    - **panier** (`pnl_gross_ov` / `pnl_gross_bh`) : l'exposition est un scalaire
      par date et la jambe candidate vaut `exposure[t] x jambe de reference`
      (identite etablie et verifiee au #402, controle 1b). Elle se recupere donc
      par division. Les deux P&L stockes sont **bruts**, donc exempts du terme de
      cout qui ne suit pas cette identite.

    Retourne `(fraction, schema, n_exclues)` ou `None` si illisible.
    """
    p = RESULTS / f"nonml_{name}_pnl.npz"
    if not p.exists():
        return None
    try:
        d = np.load(p, allow_pickle=True)
    except Exception:  # noqa: BLE001
        return None
    f = set(d.files)
    if "pos" in f:
        pos = np.asarray(d["pos"], dtype=float)
        if pos.size == 0:
            return None
        return float((pos > 1.0).mean()), "indiciel", 0
    if {"pnl_gross_ov", "pnl_gross_bh"} <= f:
        ov = np.asarray(d["pnl_gross_ov"], dtype=float)
        bh = np.asarray(d["pnl_gross_bh"], dtype=float)
        if ov.shape != bh.shape or ov.size == 0:
            return None
        usable = np.isfinite(ov) & np.isfinite(bh) & (np.abs(bh) > BASKET_EPS)
        n_excl = int((~usable).sum())
        if not usable.any():
            return None
        expo = ov[usable] / bh[usable]
        return float((expo > 1.0 + 1e-9).mean()), "panier", n_excl
    return None


def main():
    scripts = sorted(SCRIPTS.glob("nonml_*_backtest.py"))
    unreadable, structured = [], []

    for p in scripts:
        try:
            src = p.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            unreadable.append((p.name, str(exc)))
            continue
        if has_floor_clip(src):
            structured.append(p.name.replace("nonml_", "").replace("_backtest.py", ""))

    measured, unmeasured = [], []
    for name in structured:
        got = activation_of(name)
        if got is None:
            unmeasured.append(name)
        else:
            act, schema, n_excl = got
            measured.append((name, act, verdict_of(name), schema, n_excl))

    inactive = [m for m in measured if m[1] < INACTIVE_MAX]
    empty_pass = [m for m in inactive if m[2] == "PASS"]
    n_basket = sum(1 for m in measured if m[3] == "panier")

    L = ["# Balayage des portes de capitulation neutralisées par le plancher 1,0× (pré-enregistré)", ""]
    L.append("Diagnostic, pas une stratégie. Cherche les candidats dont la structure interdit")
    L.append("à l'overlay de s'activer : une porte qui s'ouvre en régime de faiblesse combinée")
    L.append("à un vol-targeting dont le plancher est l'exposition neutre.")
    L.append("")
    L.append(f"Seuil d'inactivité **repris tel quel du #410** : exposition > 1,0× sur moins de "
             f"{100*INACTIVE_MAX:.0f} % des séances.")
    L.append("")

    L.append("## Volet A — détection statique")
    L.append("")
    L.append(f"- scripts `nonml_*_backtest.py` examinés : **{len(scripts)}**")
    L.append(f"- illisibles : **{len(unreadable)}**")
    L.append(f"- portant la structure `clip(…, 1.0, …)` : **{len(structured)}**")
    L.append("")
    if unreadable:
        for n, why in unreadable:
            L.append(f"- `{n}` : {why}")
        L.append("")
    L.append(f"**Couverture {'100 %' if not unreadable else 'incomplète'}** — critère 1 du "
             f"pré-enregistrement {'atteint' if not unreadable else 'NON atteint'}.")
    L.append("")

    L.append("## Volet B — mesure empirique de l'activation")
    L.append("")
    L.append(f"- candidats mesurés : **{len(measured)}**, dont **{len(measured) - n_basket}** au "
             f"schéma indiciel et **{n_basket}** au schéma **panier** (extension #425)")
    L.append(f"- candidats détectés mais **non mesurés** faute de `.npz` : **{len(unmeasured)}**")
    L.append("")
    L.append("Ce second chiffre est un **résultat du cycle**, pas une excuse : il quantifie")
    L.append("exactement ce que la lacune mesurée au #406 coûte à ce diagnostic.")
    L.append("")
    L.append("Sur un panier, l'exposition n'est pas stockée : elle est **récupérée par division**")
    L.append("`pnl_gross_ov / pnl_gross_bh`, la jambe candidate valant `exposition × jambe de")
    L.append("référence` (identité établie et vérifiée au #402, contrôle 1b). Les séances à")
    L.append("dénominateur quasi nul sont exclues et comptées, jamais remplacées par un défaut.")
    L.append("")
    if n_basket:
        L.append("| Candidat panier | Exposition > 1,0× | Séances exclues (dénominateur nul) |")
        L.append("|---|---|---|")
        for n, a, v, s, e in sorted(measured, key=lambda t: t[0]):
            if s == "panier":
                L.append(f"| `{n}` | {100*a:.2f} % | {e} |")
        L.append("")
    if unmeasured:
        L.append("Non mesurés :")
        L.append("")
        for n in unmeasured:
            L.append(f"- `{n}` (verdict au rapport : {verdict_of(n)})")
        L.append("")

    L.append("### Candidats mesurés, par activation croissante")
    L.append("")
    L.append("| Candidat | Séances à exposition > 1,0× | Schéma | Verdict au rapport |")
    L.append("|---|---|---|---|")
    for n, a, v, s, e in sorted(measured, key=lambda t: t[1]):
        mark = " ← **inactif**" if a < INACTIVE_MAX else ""
        L.append(f"| `{n}` | {100*a:.2f} %{mark} | {s} | {v} |")
    L.append("")

    L.append("## Verdict du balayage")
    L.append("")
    L.append(f"- candidats structurellement **inactifs** (< {100*INACTIVE_MAX:.0f} %) : "
             f"**{len(inactive)}**")
    L.append(f"- dont **PASS vides** : **{len(empty_pass)}**")
    L.append("")
    if empty_pass:
        for n, a, v, s, e in empty_pass:
            L.append(f"- `{n}` — activation {100*a:.2f} %, rapport : {v}")
        L.append("")
        L.append("Chacun doit être **confirmé par lecture** de son script et de son rapport")
        L.append("avant toute conclusion — critère 2 du pré-enregistrement. Voir l'audit.")
    else:
        L.append("**Aucun PASS vide parmi les candidats mesurés.**")
    L.append("")
    L.append("**Aucune correction du backlog n'est appliquée ici**, conformément au")
    L.append("pré-enregistrement : requalifier des PASS est une seconde opération, à déclarer")
    L.append("séparément.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return structured, measured, unmeasured, inactive, empty_pass


if __name__ == "__main__":
    main()
