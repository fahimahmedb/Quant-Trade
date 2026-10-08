#!/usr/bin/env bash
# Read-only attestation (E B.5(f)): the code on the host equals the approved blobs, nothing else is present
# in the harness and operation packages. Verifies; changes nothing; does not import or run any of the code.
# Usage: bash <verified-script> <deploy-root> <approved-final-pins-tsv-blob>
set -euo pipefail
export LC_ALL=C
stop() { echo "STOP: $*" >&2; exit 2; }
[ "$#" -eq 2 ] || stop "racine de deploiement et blob approuve des epingles requis"
command -v git >/dev/null || stop "git absent"
ROOT=$(readlink -f -- "$1") || stop "racine indisponible"
[ -d "$ROOT" ] && [ "$ROOT" != / ] || stop "racine invalide"
PIN_BLOB="$2"
[[ "$PIN_BLOB" =~ ^[0-9a-f]{40}$ ]] || stop "blob invalide"
BASE=research/weather_forward/v4
PINS="$ROOT/$BASE/a2_operation/frozen/final_pins_d2_v1.tsv"
[ -f "$PINS" ] && [ ! -L "$PINS" ] || stop "epingles finales absentes"
[ "$(git hash-object --no-filters -- "$PINS")" = "$PIN_BLOB" ] || stop "blob des epingles discordant"
declare -A pinned
ok=0
while IFS=$'\t' read -r expected relative extra; do
  [[ "$expected" =~ ^[0-9a-f]{40}$ ]] && [ -z "$extra" ] || stop "ligne d'epingle invalide"
  f="$ROOT/$relative"
  [ -f "$f" ] && [ ! -L "$f" ] && [ "$(readlink -f -- "$f")" = "$f" ] || stop "absent, lien ou non regulier : $relative"
  [ "$(git hash-object --no-filters -- "$f")" = "$expected" ] || stop "discordance de blob : $relative"
  pinned["$f"]=1
  ok=$((ok+1))
done < "$PINS"
[ "$ok" -eq 13 ] || stop "13 objets exiges, $ok verifies"
# Executable or importable files present in the two packages but absent from the approved list.
extra_count=0
while IFS= read -r -d '' f; do
  case "$f" in "$ROOT/$BASE/a2_operation/qualification/"*|"$ROOT/$BASE/a2_operation/frozen/final_pins_d2_v1.tsv") continue;; esac
  case "$f" in *.py|*.sh|*.pth|*.so|*.pyc|*/__pycache__/*|*.json)
    [ -n "${pinned[$f]:-}" ] || { echo "UNEXPECTED_FILE=${f#$ROOT/}" >&2; extra_count=$((extra_count+1)); } ;;
  esac
done < <(find "$ROOT/$BASE/a2_harness" "$ROOT/$BASE/a2_operation" -type f -print0 2>/dev/null)
[ "$extra_count" -eq 0 ] || stop "$extra_count fichier(s) inattendu(s) dans les paquets"
echo "LOADED_CODE_MATCHES_APPROVED=13/13"
echo "UNEXPECTED_FILES=0"
echo "CODE_IMPORTED_OR_EXECUTED=0"
