#!/usr/bin/env bash
# Owner-only deployment of the 13 approved operation files (E B.5(f)): 4 harness files incl. the candidate
# trusted_root.py, 7 operation sources, the pre-effect context and the unit profile.
# Usage: sudo bash <verified-script> <partial-reception-root> <approved-final-pins-tsv-blob>
# No network, clone, service start, root activation, execution or deletion is performed.
# An existing target file is accepted only when it is byte-identical to the approved blob (never replaced).
set -euo pipefail
export LC_ALL=C
stop() { echo "STOP: $*" >&2; exit 2; }
[ "$(id -u)" -eq 0 ] || stop "lancer avec sudo"
[ "$#" -eq 2 ] || stop "reception partielle et blob approuve des epingles requis"
command -v git >/dev/null || stop "git absent : aucune installation automatique"
STAGE=$(readlink -f -- "$1") || stop "reception indisponible"
[ -d "$STAGE" ] && [ "$STAGE" != / ] || stop "reception invalide"
PIN_BLOB="$2"
[[ "$PIN_BLOB" =~ ^[0-9a-f]{40}$ ]] || stop "blob invalide"
BASE=research/weather_forward/v4
PINS="$STAGE/$BASE/a2_operation/frozen/final_pins_d2_v1.tsv"
[ -f "$PINS" ] && [ ! -L "$PINS" ] || stop "epingles finales absentes"
[ "$(git hash-object --no-filters -- "$PINS")" = "$PIN_BLOB" ] || stop "blob des epingles discordant"
TARGET=/opt/a2
[ -d "$TARGET" ] && [ ! -L "$TARGET" ] && [ "$(readlink -f "$TARGET")" = "$TARGET" ] || stop "setup_host.sh requis"
[ "$(stat -c '%u:%g:%a' "$TARGET")" = 0:0:755 ] || stop "propriete ou permissions de $TARGET discordantes"
n=0
while IFS=$'\t' read -r expected relative extra; do
  [[ "$expected" =~ ^[0-9a-f]{40}$ ]] && [ -z "$extra" ] || stop "ligne d'epingle invalide"
  case "$relative" in "$BASE"/a2_harness/*|"$BASE"/a2_operation/*) ;; *) stop "chemin hors perimetre : $relative";; esac
  case "$relative" in *..*|/*) stop "chemin suspect : $relative";; esac
  source_file="$STAGE/$relative"
  [ -f "$source_file" ] && [ ! -L "$source_file" ] || stop "source non reguliere : $relative"
  [ "$(readlink -f -- "$source_file")" = "$source_file" ] || stop "lien dans la reception"
  [ "$(git hash-object --no-filters -- "$source_file")" = "$expected" ] || stop "source discordante : $relative"
  target="$TARGET/$relative"
  if [ -e "$target" ] || [ -L "$target" ]; then
    [ -f "$target" ] && [ ! -L "$target" ] && [ "$(git hash-object --no-filters -- "$target")" = "$expected" ] \
      || stop "cible existante differente : aucun remplacement ($relative)"
  fi
  n=$((n+1))
done < "$PINS"
[ "$n" -eq 13 ] || stop "13 objets exiges, $n lus"
# Every source and target is checked above; installation starts only now.
while IFS=$'\t' read -r expected relative; do
  install -d -m 0755 -o root -g root "$TARGET/$(dirname "$relative")"
  [ -e "$TARGET/$relative" ] || install -m 0444 -o root -g root "$STAGE/$relative" "$TARGET/$relative"
done < "$PINS"
install -d -m 0755 -o root -g root "$TARGET/$BASE/a2_operation/frozen"
[ -e "$TARGET/$BASE/a2_operation/frozen/final_pins_d2_v1.tsv" ] || install -m 0444 -o root -g root "$PINS" "$TARGET/$BASE/a2_operation/frozen/final_pins_d2_v1.tsv"
echo "OPERATION_FILES_DEPLOYED_OR_IDENTICAL=13"
echo "OPERATION_SCRIPT_EXECUTED=0"
