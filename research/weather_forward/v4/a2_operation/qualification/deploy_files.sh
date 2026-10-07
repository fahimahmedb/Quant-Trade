#!/usr/bin/env bash
# Owner-only first deployment of the qualification files, never the harness.
# Usage: sudo bash <verified-script> <partial-reception-root> <approved-pins-blob>
# No network, clone, service start, root activation or overwrite is performed.
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
BASE=research/weather_forward/v4/a2_operation
PINS="$STAGE/$BASE/qualification/file_pins.tsv"
[ -f "$PINS" ] && [ ! -L "$PINS" ] || stop "epingles absentes"
[ "$(git hash-object --no-filters -- "$PINS")" = "$PIN_BLOB" ] || stop "blob des epingles discordant"
[ -d /opt/a2 ] && [ ! -L /opt/a2 ] || stop "setup_host.sh requis"
[ "$(readlink -f /opt/a2)" = /opt/a2 ] || stop "lien dans le chemin cible"
[ "$(stat -c '%u:%g:%a' /opt/a2)" = 0:0:755 ] || stop "propriete ou permissions de /opt/a2 discordantes"
[ -z "$(find /opt/a2 -mindepth 1 -print -quit)" ] || stop "/opt/a2 non vide : aucun remplacement"
declare -A allowed seen
for suffix in __init__.py common/__init__.py common/bounded_output.py common/a2_unit_profile.sh \
  qualification/__init__.py qualification/host_facts.sh qualification/qualification_probes.py \
  qualification/run_qualification.sh qualification/setup_host.sh qualification/summarize_qualification.py \
  qualification/deploy_files.sh; do
  allowed["$BASE/$suffix"]=1
done
while IFS=$'\t' read -r expected relative extra; do
  [[ "$expected" =~ ^[0-9a-f]{40}$ ]] && [ -z "$extra" ] || stop "ligne d'epingle invalide"
  [ -n "${allowed[$relative]:-}" ] && [ -z "${seen[$relative]:-}" ] || stop "chemin hors liste ou repete"
  source_file="$STAGE/$relative"
  [ -f "$source_file" ] && [ ! -L "$source_file" ] || stop "source non reguliere"
  [ "$(readlink -f -- "$source_file")" = "$source_file" ] || stop "lien dans la reception"
  [ "$(git hash-object --no-filters -- "$source_file")" = "$expected" ] || stop "source discordante : $relative"
  seen["$relative"]=1
done < "$PINS"
[ "${#seen[@]}" -eq "${#allowed[@]}" ] || stop "liste de sources incomplete"
# All sources and targets are checked before the first installation.
for relative in "${!seen[@]}"; do
  install -d -m 0755 -o root -g root "/opt/a2/$(dirname "$relative")"
  install -m 0444 -o root -g root "$STAGE/$relative" "/opt/a2/$relative"
done
install -m 0444 -o root -g root "$PINS" "/opt/a2/$BASE/qualification/file_pins.tsv"
while IFS=$'\t' read -r expected relative; do
  [ "$(git hash-object --no-filters -- "/opt/a2/$relative")" = "$expected" ] || stop "copie discordante"
done < "$PINS"
echo "QUALIFICATION_FILES_DEPLOYED=11"
echo "HARNESS_FILES_DEPLOYED=0"
echo "PROBES_EXECUTED=0"
