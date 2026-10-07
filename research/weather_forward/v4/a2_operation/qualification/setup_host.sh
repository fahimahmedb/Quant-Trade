#!/usr/bin/env bash
# L2-A host mutations permitted by the ratified lot-2 decision (section 4, L2-A):
#   - dedicated system user/group a2runner, no sudo, no login shell;
#   - /opt/a2 code directory owned by root, not writable by a2runner;
#   - dedicated tmpfs /srv/a2out: size 1 MiB, mode 0700, a2runner uid/gid,
#     nosuid,nodev,noexec. Not added to /etc/fstab: lost at reboot (recorded).
# Nothing that already exists is removed or replaced: an existing user or path
# is a STOP and an Owner decision.
set -euo pipefail

stop() { echo "STOP: $*" >&2; exit 2; }

[ "$(id -u)" -eq 0 ] || stop "lancer avec sudo"
command -v useradd >/dev/null || stop "useradd absent"
command -v mount >/dev/null || stop "mount absent"

getent passwd a2runner >/dev/null && stop "l'utilisateur a2runner existe deja"
getent group a2runner >/dev/null && stop "le groupe a2runner existe deja"
{ [ -e /opt/a2 ] || [ -L /opt/a2 ]; } && stop "/opt/a2 existe deja"
{ [ -e /srv/a2out ] || [ -L /srv/a2out ]; } && stop "/srv/a2out existe deja"

useradd --system --user-group --no-create-home --home-dir /nonexistent \
        --shell /usr/sbin/nologin a2runner
uid=$(id -u a2runner)
gid=$(id -g a2runner)

install -d -m 0755 -o root -g root /opt/a2
install -d -m 0755 -o root -g root /srv/a2out
mount -t tmpfs -o "size=1m,mode=0700,uid=${uid},gid=${gid},nosuid,nodev,noexec" a2out /srv/a2out

echo "SETUP_DONE"
echo "A2RUNNER_UID=${uid}"
echo "A2RUNNER_GID=${gid}"
echo "A2RUNNER_SUDO=$(sudo -l -U a2runner 2>/dev/null | grep -q 'may run' && echo PRESENT || echo NONE)"
echo "OPT_A2=$(stat -c '%U:%G %a' /opt/a2)"
echo "SRV_A2OUT_MOUNT=$(findmnt -n -o FSTYPE,OPTIONS /srv/a2out)"
echo "FSTAB_MODIFIED=NO"
