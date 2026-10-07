#!/usr/bin/env bash
# L2-A qualification: runs each dummy probe once in a transient systemd unit
# with the shared A2 profile, captures systemd's own accounting, the unit
# journal and the probe observation, then summarizes per-limit verdicts.
# Probes never load the A2 harness. Run on the designated host only, with sudo.
set -uo pipefail

REPO=/opt/a2
V4="$REPO/research/weather_forward/v4"
OUT=/srv/a2out
PROBES="$V4/a2_operation/qualification/qualification_probes.py"
SUMMARIZER="$V4/a2_operation/qualification/summarize_qualification.py"

stop() { echo "STOP: $*" >&2; exit 2; }

[ "$(id -u)" -eq 0 ] || stop "lancer avec sudo"
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
home="$(getent passwd "$owner" | cut -d: -f6)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$home/a2qual-$stamp"
install -d -m 0700 -o "$owner" "$DEST"
echo "TRANSCRIPT_DIR=$DEST"

run_probe() {
  local probe="$1" variant="$2"; shift 2
  local unit="a2qual-${probe}-${variant}-${stamp}"
  find "$OUT" -mindepth 1 -delete
  echo "RUN $probe ($variant) ..."
  systemd-run --wait --unit "$unit" "$@" "${A2_PYTHON[@]}" "$PROBES" --probe "$probe" \
    > "$DEST/$unit.systemd-run.txt" 2>&1
  echo "SYSTEMD_RUN_EXIT=$?" >> "$DEST/$unit.systemd-run.txt"
  systemctl show "$unit" -p Result -p ExecMainCode -p ExecMainStatus -p CPUUsageNSec \
    -p MemoryPeak -p MemorySwapPeak -p TasksMax -p MemoryMax -p RuntimeMaxUSec \
    > "$DEST/$unit.show.txt" 2>&1 || true
  journalctl --no-pager -o cat -u "$unit" > "$DEST/$unit.journal.txt" 2>&1 || true
  ls -la "$OUT" > "$DEST/$unit.outdir.txt" 2>&1
  for file in "$OUT"/qual-*.json; do
    [ -f "$file" ] && cp "$file" "$DEST/$unit.$(basename "$file")"
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
find "$OUT" -mindepth 1 -delete

"${A2_PYTHON[@]}" "$SUMMARIZER" "$DEST" "$stamp" | tee "$DEST/summary.txt"
chown -R "$owner" "$DEST"
echo "DONE: transcripts in $DEST"
