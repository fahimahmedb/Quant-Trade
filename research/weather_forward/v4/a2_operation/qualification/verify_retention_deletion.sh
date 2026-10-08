#!/usr/bin/env bash
# Owner-only check of the deletion capability and the persistence class of the output directory (E B.5(c)).
# Usage: sudo bash <verified-script> <output-directory, normally /srv/a2out>
# Creates ONE synthetic probe file, checks it is visible, deletes it, checks it is gone. Never opens, hashes,
# copies or lists any other file. It does NOT and cannot demonstrate 30-day retention: it states persistence
# facts and always prints RETENTION_30D_DEMONSTRATED=NO.
set -euo pipefail
export LC_ALL=C
stop() { echo "STOP: $*" >&2; exit 2; }
[ "$#" -eq 1 ] || stop "un seul argument : le repertoire de sortie"
DIR=$(readlink -f -- "$1") || stop "repertoire indisponible"
[ -d "$DIR" ] && [ "$DIR" != / ] && [ ! -L "$1" ] || stop "repertoire invalide ou lien"
[ -w "$DIR" ] || stop "repertoire non inscriptible par cet utilisateur"
# Refuse if anything is already there: no result file may be touched or even counted by this check.
[ -z "$(find "$DIR" -mindepth 1 -print -quit)" ] || stop "repertoire non vide : aucun fichier existant n'est lu, liste ou touche"
PROBE="$DIR/q27-deletion-probe-$$.txt"
[ ! -e "$PROBE" ] || stop "sonde deja presente"
FSTYPE=$(findmnt -n -o FSTYPE -T "$DIR" 2>/dev/null || echo UNKNOWN)
printf 'SYNTHETIC_Q27_DELETION_PROBE_NOT_A_RESULT\n' > "$PROBE"
[ -f "$PROBE" ] || stop "sonde non creee"
rm -- "$PROBE" || { rm -f -- "$PROBE" 2>/dev/null || true; stop "suppression de la sonde impossible"; }
[ ! -e "$PROBE" ] && [ ! -L "$PROBE" ] || stop "la sonde existe encore apres suppression"
[ -z "$(find "$DIR" -mindepth 1 -print -quit)" ] || stop "residu apres suppression"
echo "DELETION_CAPABILITY=VERIFIED"
echo "OUTPUT_DIR_FSTYPE=$FSTYPE"
case "$FSTYPE" in
  tmpfs|ramfs) echo "PERSISTENT_ACROSS_REBOOT=NO" ;;
  UNKNOWN) echo "PERSISTENT_ACROSS_REBOOT=UNVERIFIED" ;;
  *) echo "PERSISTENT_ACROSS_REBOOT=UNVERIFIED" ;;
esac
echo "BOOT_TIME=$(uptime -s 2>/dev/null || echo UNKNOWN)"
echo "RETENTION_30D_DEMONSTRATED=NO"
echo "EXISTING_FILES_TOUCHED=0"
