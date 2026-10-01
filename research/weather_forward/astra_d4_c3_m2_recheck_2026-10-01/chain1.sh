#!/bin/bash
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 astra_m2_run.py repro 20000 && echo repro_done >> chain1.log
python3 astra_m2_run.py repro100 100000 && echo repro100_done >> chain1.log
python3 astra_m2_run.py probe 20000 && echo probe_done >> chain1.log
python3 astra_m2_run.py power 20000 && echo power_done >> chain1.log
python3 astra_m2_run.py class_ 20000 && echo class_done >> chain1.log
python3 astra_m2_run.py slice 20000 && echo slice_done >> chain1.log
echo ALL_DONE >> chain1.log
