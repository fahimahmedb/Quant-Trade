#!/bin/sh
# Read-only host diagnostic. Run inside the target Compute VM, not Cloud Shell.
# No network, package installation, credentials, service changes or sudo.
set -eu

printf 'diagnostic=quant-oracle-preflight-v1\n'
printf 'observed_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'architecture=%s\n' "$(uname -m)"
printf 'uid=%s\n' "$(id -u)"
if [ -r /etc/os-release ]; then
    sed -n '/^PRETTY_NAME=/p; /^ID=/p; /^VERSION_ID=/p' /etc/os-release
fi
if command -v nproc >/dev/null 2>&1; then
    printf 'available_cpu_threads=%s\n' "$(nproc)"
fi
if [ -r /sys/fs/cgroup/cpu.max ]; then
    awk '{print "cgroup_cpu_quota_period=" $0}' /sys/fs/cgroup/cpu.max
fi
if [ -r /proc/meminfo ]; then
    awk '/^(MemTotal|MemAvailable|SwapTotal|SwapFree):/ {print $1 " " $2 " " $3}' /proc/meminfo
fi
if [ -r /sys/fs/cgroup/memory.max ]; then
    awk '{print "cgroup_memory_max_bytes=" $0}' /sys/fs/cgroup/memory.max
fi
if [ -r /sys/fs/cgroup/memory/memory.limit_in_bytes ]; then
    awk '{print "cgroup_v1_memory_max_bytes=" $0}' /sys/fs/cgroup/memory/memory.limit_in_bytes
fi
printf 'root_filesystem_kib:\n'
df -Pk /
if [ -d /var/lib ]; then
    printf 'state_filesystem_kib:\n'
    df -Pk /var/lib
fi
for tool in curl git cmake make cc python3 systemctl llama-server ollama; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf 'tool_%s=present\n' "$tool"
    else
        printf 'tool_%s=absent\n' "$tool"
    fi
done
printf 'admin_access=NOT_TESTED\n'
printf 'oracle_instance_identity=NOT_VERIFIED\n'
printf 'inference_tested=false\n'
printf 'model_ram_fit=NOT_ESTABLISHED\n'
