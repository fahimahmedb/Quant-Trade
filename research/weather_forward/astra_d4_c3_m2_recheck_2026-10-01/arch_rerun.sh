#!/bin/bash
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 WF_PROCS=4
S=/tmp/claude-0/-home-user-Quant-Trade/120e1dd1-d22f-52e4-b4d7-526f1fcb6e8e/scratchpad/arch_sim.py
[ -s arch_rerun_astra_20000.jsonl ] || python3 $S astra 20000 > arch_rerun_astra_20000.jsonl
[ -s arch_rerun_cell_class_887_100000.jsonl ] || python3 $S cell class 887 100000 > arch_rerun_cell_class_887_100000.jsonl
echo ARCH_DONE >> arch_rerun.log
