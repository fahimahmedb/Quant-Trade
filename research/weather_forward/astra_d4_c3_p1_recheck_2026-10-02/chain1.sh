#!/bin/bash
# resumable chain: each plan skips completed cells. nice 19, 3 processes.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
for step in "repro_p1 20000" "gorate 20000" "verify_old 20000" "verify_new 20000" "repro_m3 100000" "derive_t2 20000" "derive_neg 20000" "persist 20000" "level 20000" "probe 20000"; do
  set -- $step
  nice -n 19 python3 astra_c3_run.py $1 $2 3 >> chain1.log 2>&1
  echo "$(date -u +%FT%TZ) done $1 $2" >> chain1.status
done
echo ALLDONE >> chain1.status
