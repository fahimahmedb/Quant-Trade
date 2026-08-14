"""Lecture du verdict d'un rapport — regle unique du depot (#449).

Reprise **a l'identique** de `nonml_pnl_duplicate_sweep_backtest.py` (#448),
pour que les consommateurs cessent d'en entretenir des copies divergentes.

Historique du defaut, en trois temps :

- `"**PASS" in t` — n'importe ou dans le texte. Un rapport qui *parlait* d'un
  PASS etait compte comme en portant un (#446).
- lecture en debut de ligne brut — manquait les verdicts enonces en **titre**
  (`## Verdict : **FAIL**`, `### **FAIL**`) : 2 faux negatifs (#447).
- litteral `"PASS (niveau 1)"` compare en sous-chaine — meme defaut, subsistant
  la ou le #447 ne l'avait pas touche (#448).

Ce fichier ne se termine ni par `_backtest.py` ni par `_audit.py` : il n'entre
dans aucun `glob` du depot et n'ajoute pas de candidat fantome aux inventaires.
"""


def _nu(ln):
    """Retire la decoration Markdown d'une ligne, sans toucher a son sens."""
    s = ln.strip()
    while s.startswith("#"):
        s = s[1:]
    s = s.lstrip()
    while s.startswith(">"):
        s = s[1:].lstrip()
    if s[:2] in ("- ", "* "):
        s = s[2:].lstrip()
    tete = s[:2] == "**" and s[2:] or s
    if tete[:7].lower() == "verdict":
        reste = tete[7:]
        if reste[:6].lower() == " final":
            reste = reste[6:]
        if reste[:2] == "**":
            reste = reste[2:]
        reste = reste.lstrip()
        if reste[:1] in (":", "—", "-", "："):
            s = reste[1:].lstrip()
    return s


def porte_verdict(t, m):
    """Le rapport PORTE-t-il ce verdict, ou se contente-t-il d'en parler ?"""
    for ln in t.splitlines():
        nu = _nu(ln)
        if nu.startswith("**" + m):
            return True
        if m == "PASS" and nu.startswith("PASS (niveau 1)"):
            return True
    return False


def verdict_of(t, absent="indéterminé"):
    """Verdict porte par un rapport. Precedence : PASS l'emporte sur FAIL."""
    if porte_verdict(t, "PASS"):
        return "PASS"
    if porte_verdict(t, "FAIL"):
        return "FAIL"
    return absent
