#!/usr/bin/env bash
# L2-A read-only host facts. Records versions and a bounded inventory of
# locations and services: names, counts and sizes only. It never opens file
# contents, secrets or payloads and prints no IP address.
set -uo pipefail

[ "$(id -u)" -eq 0 ] || { echo "STOP: lancer avec sudo" >&2; exit 2; }

section() { printf '\n## %s\n' "$1"; }

section "SYSTEM"
. /etc/os-release 2>/dev/null && echo "OS=${PRETTY_NAME:-UNKNOWN} VERSION_ID=${VERSION_ID:-UNKNOWN}"
echo "KERNEL=$(uname -r)"
echo "ARCH=$(uname -m)"
echo "SYSTEMD=$(systemctl --version | head -n 1)"
echo "CGROUP_FS=$(stat -fc %T /sys/fs/cgroup)"
echo "CGROUP_MEMORY_PEAK_FILE=$(ls /sys/fs/cgroup/system.slice/*/memory.peak >/dev/null 2>&1 && echo PRESENT || echo ABSENT)"
echo "PYTHON3=$(command -v python3 || echo ABSENT)"
python3 -I -S -B -c 'import sys; print("PYTHON_VERSION=" + sys.version.split()[0])' 2>/dev/null || echo "PYTHON_VERSION=UNAVAILABLE"
echo "GIT=$(command -v git >/dev/null && echo PRESENT || echo ABSENT)"

section "USERS_UID_GE_1000_NAMES"
getent passwd | awk -F: '$3 >= 1000 && $3 < 65534 {print $1}'

section "RUNNING_SERVICES"
systemctl list-units --type=service --state=running --no-legend --plain | awk '{print $1}'

section "LISTENING_PORTS_PROTOCOL_PORT_ONLY"
ss -H -lntu 2>/dev/null | awk '{n=split($5, a, ":"); print $1, a[n]}' | sort -u

section "LOCATION_SIZES"
for path in /home /root /opt /srv /var/lib /mnt /media; do
  [ -e "$path" ] && du -sh --one-file-system "$path" 2>/dev/null | awk '{print $2, $1}'
done

section "TOP_LEVEL_NAMES"
for path in /opt /srv /mnt /media /home; do
  [ -d "$path" ] && echo "$path: $(ls -1A "$path" 2>/dev/null | tr '\n' ' ')"
done

section "DATA_LIKE_FILE_COUNTS_NAMES_NOT_OPENED"
for path in /home /root /opt /srv /var/lib; do
  [ -d "$path" ] || continue
  count=$(find "$path" -xdev -maxdepth 5 -type f \( -name '*.csv' -o -name '*.parquet' -o \
          -name '*.jsonl' -o -name '*.sqlite' -o -name '*.db' -o -name '*.feather' \) \
          2>/dev/null | wc -l)
  echo "$path data_like_files=$count"
done

section "CREDENTIAL_LIKE_PATH_COUNTS_NOT_OPENED"
for path in /home /root /opt /srv; do
  [ -d "$path" ] || continue
  count=$(find "$path" -xdev -maxdepth 4 \( -name '.aws' -o -name '.netrc' -o -name '*.pem' -o \
          -name '.git-credentials' -o -name '.docker' -o -name '.kube' -o -name '.env' -o \
          -name '*.key' -o -name 'credentials*' \) 2>/dev/null | wc -l)
  echo "$path credential_like_paths=$count"
done
echo "NOTE=.ssh/authorized_keys for operator login is expected and not counted above"

section "A2_LAYOUT"
echo "A2RUNNER=$(id a2runner 2>/dev/null || echo ABSENT)"
echo "OPT_A2=$(stat -c '%U:%G %a' /opt/a2 2>/dev/null || echo ABSENT)"
echo "SRV_A2OUT_MOUNT=$(findmnt -n -o FSTYPE,OPTIONS /srv/a2out 2>/dev/null || echo ABSENT)"
echo "PYCACHE_UNDER_OPT_A2=$(find /opt/a2 -name __pycache__ 2>/dev/null | wc -l)"
