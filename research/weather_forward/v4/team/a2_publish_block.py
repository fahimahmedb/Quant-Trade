#!/usr/bin/env python3
"""Extrait d'un commentaire de PR les blocs ```markdown dont le SHA-256 est annonce dans le meme commentaire.

Remplace la retranscription manuelle (scribe) : le texte est lu depuis GitHub, jamais retape.
Usage : python3 a2_publish_block.py <comment_id> <dossier_sortie> [owner/repo]
Sortie : un fichier par bloc verifie (block_<n>.md) + la liste (n, sha256, nombre d'octets) ; code 1 si un SHA annonce n'a aucun bloc correspondant.
Seul acces reseau : `gh api` (lecture d'un commentaire). Ne commite, ne pousse et ne publie rien.
"""
import hashlib
import os
import re
import subprocess
import sys


def fetch(repo, cid):
    r = subprocess.run(["gh", "api", f"repos/{repo}/issues/comments/{cid}", "--jq", ".body"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"gh api a echoue : {r.stderr.strip()[:200]}")
    return r.stdout


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cid, out = sys.argv[1], sys.argv[2]
    repo = sys.argv[3] if len(sys.argv) > 3 else "fahimahmedb/Quant-Trade"
    body = fetch(repo, cid).replace("\r\n", "\n")
    lines = body.split("\n")
    anywhere = set(re.findall(r"`([0-9a-f]{64})`", body))
    starts = [i for i, l in enumerate(lines) if l.strip() == "```markdown"]
    fences = [i for i, l in enumerate(lines) if l.strip().startswith("```")]
    # Passe 1 : delimiter les blocs dont le SHA-256 apparait quelque part ; leurs lignes sont du CONTENU, pas des annonces.
    candidates = []  # (debut, fin, sha, texte)
    for s_ in starts:
        for j in (f for f in fences if f > s_):
            text = "\n".join(lines[s_ + 1:j]) + "\n"
            sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if sha in anywhere:
                candidates.append((s_, j, sha, text))
                break
    inside_lines = {i for s_, j, _, _ in candidates for i in range(s_, j + 1)}
    # Tout autre bloc cloture (illustratif, non publie) est aussi du contenu : ses lignes `SHA-256` ne sont pas des annonces.
    opener = None
    for i, l in enumerate(lines):
        if i in inside_lines or not l.strip().startswith("```"):
            continue
        if opener is None:
            opener = i
        else:
            inside_lines.update(range(opener, i + 1))
            opener = None
    # Passe 2 : annonces = hash en backticks sur une ligne "SHA-256" (ou la suivante) HORS des blocs delimites.
    declared = []
    for i, l in enumerate(lines):
        if "SHA-256" in l and i not in inside_lines:
            nxt = lines[i + 1] if i + 1 < len(lines) and (i + 1) not in inside_lines else ""
            for h in re.findall(r"`([0-9a-f]{64})`", l + "\n" + nxt):
                if h not in declared:
                    declared.append(h)
    if os.path.isdir(out) and os.listdir(out):
        sys.exit(f"STOP : le dossier de sortie {out} n'est pas vide (aucune sortie obsolete ne doit etre republiee)")
    os.makedirs(out, exist_ok=True)
    found = {}
    for _, _, sha, text in candidates:
        if sha in declared and sha not in found:
            found[sha] = text
    for n, (sha, text) in enumerate(found.items(), 1):
        path = os.path.join(out, f"block_{n}.md")
        open(path, "w", encoding="utf-8", newline="\n").write(text)
        print(f"OK block_{n}.md sha256={sha} octets={len(text.encode('utf-8'))}")
    missing = [d for d in declared if d not in found]
    for d in missing:
        print(f"SHA ANNONCE SANS BLOC CORRESPONDANT : {d}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
