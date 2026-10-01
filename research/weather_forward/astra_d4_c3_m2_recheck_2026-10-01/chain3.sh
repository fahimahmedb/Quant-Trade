#!/bin/bash
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 astra_m2_run.py probe100 100000 && echo probe100_done >> chain3.log
python3 astra_m2_run.py power 20000 && echo power_done >> chain3.log
python3 astra_m2_run.py sample 20000 && echo sample_done >> chain3.log
python3 astra_t1b.py 20000 2000 && echo t1b_done >> chain3.log
echo ALL_DONE >> chain3.log
