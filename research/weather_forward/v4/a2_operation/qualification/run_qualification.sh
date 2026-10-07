#!/usr/bin/env bash
# L2-A qualification: runs each dummy probe once in a transient systemd unit
# with the shared A2 profile, captures systemd's own accounting, the unit
# journal and the probe observation, then summarizes per-limit verdicts.
# Probes never load the A2 harness. Run on the designated host only, with sudo.
set -uo pipefail
export LC_ALL=C

REPO=/opt/a2
V4="$REPO/research/weather_forward/v4"
OUT=/srv/a2out
PROBES="$V4/a2_operation/qualification/qualification_probes.py"
SUMMARIZER="$V4/a2_operation/qualification/summarize_qualification.py"

stop() { echo "STOP: $*" >&2; exit 2; }

[ "$(id -u)" -eq 0 ] || stop "lancer avec sudo"
# The operator supplies the externally approved manifest blob from the runbook.
[ "$#" -eq 1 ] && [[ "$1" =~ ^[0-9a-f]{40}$ ]] || stop "blob approuve des epingles requis"
PINS="$V4/a2_operation/qualification/file_pins.tsv"
[ "$(git hash-object --no-filters -- "$PINS")" = "$1" ] || stop "epingles discordantes"
while IFS=$'\t' read -r expected relative; do
  [[ "$expected" =~ ^[0-9a-f]{40}$ ]] && [[ "$relative" == research/weather_forward/v4/a2_operation/* ]] \
    && [[ "$relative" != *..* ]] || stop "epingle invalide"
  [ "$(git hash-object --no-filters -- "$REPO/$relative")" = "$expected" ] || stop "fichier deploye discordant"
done < "$PINS"
# shellcheck source=/dev/null
source "$V4/a2_operation/common/a2_unit_profile.sh" || stop "profil introuvable"
for command in systemd-run systemctl journalctl findmnt python3; do
  command -v "$command" >/dev/null || stop "$command absent"
done
getent passwd a2runner >/dev/null || stop "a2runner absent : lancer setup_host.sh"
mountpoint -q "$OUT" || stop "$OUT n'est pas monte"
[ "$(findmnt -n -o FSTYPE "$OUT")" = "tmpfs" ] || stop "$OUT n'est pas un tmpfs"
findmnt -n -o OPTIONS "$OUT" | grep -q 'size=1024k' || stop "$OUT n'a pas la taille 1 MiB"
sudo -u a2runner test -w "$REPO" && stop "$REPO est inscriptible par a2runner"
[ -z "$(find "$REPO" -name __pycache__ -print -quit)" ] || stop "__pycache__ present sous $REPO"
[ -f "$PROBES" ] || stop "sondes absentes : lancer deploy_files.sh"

owner="${SUDO_USER:-root}"
operator_home="$(getent passwd "$owner" | cut -d: -f6)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
host_netns_inode="$(stat -Lc '%i' /proc/self/ns/net)" || stop "namespace reseau indisponible"
DEST="$operator_home/a2qual-$stamp"
{ [ -e "$DEST" ] || [ -L "$DEST" ]; } && stop "destination de transcript deja presente"
install -d -m 0700 -o "$owner" "$DEST"
echo "TRANSCRIPT_DIR=$DEST"

run_probe() {
  local probe="$1" variant="$2"; shift 2
  local unit="a2qual-${probe}-${variant}-${stamp}"
  [ -z "$(find "$OUT" -mindepth 1 -print -quit)" ] || stop "repertoire non vide : ne pas supprimer un resultat retenu"
  echo "RUN $probe ($variant) ..."
  systemd-run --wait --unit "$unit" "$@" "${A2_PYTHON[@]}" "$PROBES" --probe "$probe" \
    --host-netns-inode "$host_netns_inode" \
    > "$DEST/$unit.systemd-run.txt" 2>&1
  echo "SYSTEMD_RUN_EXIT=$?" >> "$DEST/$unit.systemd-run.txt"
  systemctl show "$unit" -p Result -p ExecMainCode -p ExecMainStatus -p CPUUsageNSec \
    -p MemoryPeak -p MemorySwapPeak -p TasksMax -p MemoryMax -p MemorySwapMax -p RuntimeMaxUSec \
    -p LimitCPU -p LimitCORE -p StandardOutput -p StandardError -p PrivateNetwork \
    -p ExecMainStartTimestampMonotonic -p ExecMainExitTimestampMonotonic \
    > "$DEST/$unit.show.txt" 2>&1 || true
  journalctl --no-pager -o cat -u "$unit" > "$DEST/$unit.journal.txt" 2>&1 || true
  ls -la "$OUT" > "$DEST/$unit.outdir.txt" 2>&1
  cgroup="$(systemctl show "$unit" -p ControlGroup --value 2>/dev/null)"
  if [[ "$cgroup" == /system.slice/"$unit".service ]]; then
    for key in memory.peak memory.swap.peak; do
      value=$(cat "/sys/fs/cgroup$cgroup/$key" 2>/dev/null) || continue
      [[ "$value" =~ ^[0-9]+$ ]] && printf '%s=%s\n' "$key" "$value" >> "$DEST/$unit.cgroup.txt"
    done
  fi
  for file in "$OUT"/qual-*.json; do
    if [ -f "$file" ] && [ ! -L "$file" ]; then
      cp "$file" "$DEST/$unit.$(basename "$file")" || stop "copie de transcript echouee"
      rm -- "$file" || stop "nettoyage de cette seule observation echoue"
    fi
  done
  systemctl reset-failed "$unit" >/dev/null 2>&1 || true
}

FULL=("${A2_UNIT_BASE_PROPERTIES[@]}" "${A2_UNIT_FAMILY_RESTRICTION[@]}")

run_probe positive full "${FULL[@]}"
run_probe time full "${FULL[@]}"
run_probe cpu full "${FULL[@]}"
run_probe memory full "${FULL[@]}"
run_probe child full "${FULL[@]}"
run_probe network full "${FULL[@]}"
run_probe network private-network-only "${A2_UNIT_BASE_PROPERTIES[@]}"
run_probe write full "${FULL[@]}"
run_probe output full "${FULL[@]}"
run_probe read full "${FULL[@]}"
[ -z "$(find "$OUT" -mindepth 1 -print -quit)" ] || stop "artefact inattendu retenu : aucune suppression automatique"

"${A2_PYTHON[@]}" "$SUMMARIZER" "$DEST" "$stamp" | tee "$DEST/summary.txt"
summary_exit=${PIPESTATUS[0]}
chown -R "$owner" "$DEST"
echo "DONE: transcripts in $DEST"
exit "$summary_exit"
