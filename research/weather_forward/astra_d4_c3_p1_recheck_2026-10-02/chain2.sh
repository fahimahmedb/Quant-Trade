#!/bin/bash
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
until grep -q ALLDONE chain1.status 2>/dev/null; do sleep 20; done
nice -n 19 python3 arch_repro.py >> chain2.log 2>&1
echo "$(date -u +%FT%TZ) done arch_repro" >> chain2.status
echo ALLDONE >> chain2.status
