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
    declared = list(dict.fromkeys(re.findall(r"`([0-9a-f]{64})`", body)))
    lines = body.split("\n")
    starts = [i for i, l in enumerate(lines) if l.strip() == "```markdown"]
    fences = [i for i, l in enumerate(lines) if l.strip().startswith("```")]
    os.makedirs(out, exist_ok=True)
    found = {}
    for s in starts:
        for j in (f for f in fences if f > s):
            text = "\n".join(lines[s + 1:j]) + "\n"
            sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if sha in declared and sha not in found:
                found[sha] = text
                break
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
