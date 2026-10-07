# Shared systemd transient-unit profile for the Weather V4 A2 lot-2 qualification
# and the future lot-4 operation. Sourced by bash; defines arrays only.
#
# Ratified bounds (Owner configuration O section 8.3, adopted O12 sections 12.4 and 12.6):
# 60 s elapsed, 5 CPU-seconds, one process without children, 128 MiB real cgroup
# memory without swap, 1 MiB writable artifacts (host tmpfs /srv/a2out),
# 64 KiB output (enforced by the bounded writer), zero network, no core dump,
# no stdout/stderr.
#
# The exact effect of each property is QUALIFIED on the designated host by
# run_qualification.sh; a property listed here is not evidence by itself.

A2_UNIT_BASE_PROPERTIES=(
  -p User=a2runner
  -p Group=a2runner
  -p RuntimeMaxSec=60
  -p LimitCPU=5
  -p MemoryMax=128M
  -p MemorySwapMax=0
  -p TasksMax=1
  -p LimitCORE=0
  -p NoNewPrivileges=yes
  -p UMask=0077
  -p PrivateNetwork=yes
  -p ProtectSystem=strict
  -p ProtectHome=yes
  -p TemporaryFileSystem=/opt:ro
  -p BindReadOnlyPaths=/opt/a2
  -p TemporaryFileSystem=/srv:ro
  -p BindPaths=/srv/a2out
  -p ReadWritePaths=/srv/a2out
  -p TemporaryFileSystem=/var:ro
  -p InaccessiblePaths=-/tmp
  -p InaccessiblePaths=-/dev/shm
  -p InaccessiblePaths=-/mnt
  -p InaccessiblePaths=-/media
  -p InaccessiblePaths=-/snap
  -p WorkingDirectory=/srv/a2out
  -p StandardInput=null
  -p StandardOutput=null
  -p StandardError=null
  -p Environment=PYTHONDONTWRITEBYTECODE=1
)

# Second, independent network layer. Kept separate so qualification can also
# test PrivateNetwork alone (variant "private-network-only").
A2_UNIT_FAMILY_RESTRICTION=(
  -p RestrictAddressFamilies=AF_UNIX
)

A2_PYTHON=(/usr/bin/python3 -I -S -B -X pycache_prefix=/nonexistent)
